# -*- coding: utf-8 -*-
"""
Checagens de integridade do projeto PBIP, rodadas antes de publicar.

Publicar sem erro não significa que funciona: schemas 1.0.0 são aceitos no import
e o relatório abre em branco. Este script confere o que falha em silêncio.

    python3 validar.py
"""
import json, os, re, sys, glob

ERR = []
def check(cond, msg):
    if not cond: ERR.append(msg)

MODEL = "Hospitalar.SemanticModel/definition"
REPORT = "Hospitalar.Report"

# ── 1. modelo: tabelas, colunas e medidas declaradas ────────────────────────
tables = {}
measures = set()
for path in glob.glob(os.path.join(MODEL, "tables", "*.tmdl")):
    txt = open(path, encoding="utf-8").read()
    tname = re.search(r"^table (\S+)", txt, re.M).group(1)
    cols = set()
    for m in re.finditer(r"^\tcolumn ('[^']+'|\S+)", txt, re.M):
        cols.add(m.group(1).strip("'"))
    tables[tname] = cols
    for m in re.finditer(r"^\tmeasure ('[^']+'|\S+)", txt, re.M):
        measures.add(m.group(1).strip("'"))

print("modelo: %d tabelas, %d colunas, %d medidas"
      % (len(tables), sum(len(c) for c in tables.values()), len(measures)))

# ── 2. relacionamentos apontam para colunas que existem ─────────────────────
rel = open(os.path.join(MODEL, "relationships.tmdl"), encoding="utf-8").read()
nrel = 0
for m in re.finditer(r"(from|to)Column: (\w+)\.(\S+)", rel):
    t, c = m.group(2), m.group(3)
    check(t in tables, "relacionamento referencia tabela inexistente: %s" % t)
    check(c in tables.get(t, ()), "relacionamento referencia coluna inexistente: %s.%s" % (t, c))
    nrel += 1
check(nrel % 2 == 0, "relacionamento com lados ímpares")
print("relacionamentos: %d" % (nrel // 2))

# ── 3. toda tabela declarada no model.tmdl existe como arquivo ──────────────
model_txt = open(os.path.join(MODEL, "model.tmdl"), encoding="utf-8").read()
refs = set(re.findall(r"^ref table (\S+)", model_txt, re.M))
check(refs == set(tables), "ref table divergente dos arquivos: %s" % (refs ^ set(tables)))

# ── 4. sourceColumn usa o nome DEPOIS do rename no Power Query ──────────────
#     (com o nome antigo o modelo importa e só o refresh falha)
for path in glob.glob(os.path.join(MODEL, "tables", "*.tmdl")):
    txt = open(path, encoding="utf-8").read()
    if "partition" not in txt or "= m" not in txt: continue
    tname = re.search(r"^table (\S+)", txt, re.M).group(1)
    renamed = {}
    for bloco in re.findall(r"Table\.RenameColumns\((.*?)\)", txt, re.S):
        renamed.update(re.findall(r'\{"([^"]+)","([^"]+)"\}', bloco))
    for old in renamed:
        check(("sourceColumn: %s\n" % old) not in txt,
              "%s: sourceColumn usa o nome anterior ao rename (%s -> %s)"
              % (tname, old, renamed[old]))

# ── 5. schemas do PBIR nas versões que renderizam ───────────────────────────
esperado = {
    os.path.join(REPORT, "definition.pbir"): "report/definitionProperties/1.0.0",
    os.path.join(REPORT, "definition/version.json"): "report/definition/versionMetadata/1.0.0",
    os.path.join(REPORT, "definition/report.json"): "report/definition/report/3.3.0",
    os.path.join(REPORT, "definition/pages/pages.json"): "report/definition/pagesMetadata/1.1.0",
}
for path, frag in esperado.items():
    j = json.load(open(path, encoding="utf-8"))
    check(frag in j["$schema"], "%s: schema fora da versão que renderiza (%s)" % (path, j["$schema"]))
ver = json.load(open(os.path.join(REPORT, "definition/version.json"), encoding="utf-8"))
check(ver["version"] == "2.0.0", "version.json deve ser 2.0.0, está %s" % ver["version"])

rep = json.load(open(os.path.join(REPORT, "definition/report.json"), encoding="utf-8"))
check("themeCollection" in rep, "themeCollection ausente — obrigatório")
bt = rep["themeCollection"]["baseTheme"]
check(isinstance(bt.get("reportVersionAtImport"), dict), "reportVersionAtImport deve ser objeto, não string")
theme_file = os.path.join(REPORT, "StaticResources/SharedResources",
                          rep["resourcePackages"][0]["items"][0]["path"])
check(os.path.exists(theme_file), "arquivo físico do baseTheme ausente: %s" % theme_file)

# ── 6. páginas, visuais, campos e geometria ─────────────────────────────────
pages = json.load(open(os.path.join(REPORT, "definition/pages/pages.json"), encoding="utf-8"))
check(pages["activePageName"] in pages["pageOrder"], "activePageName fora do pageOrder")

nvis, tipos = 0, {}
for pname in pages["pageOrder"]:
    pdir = os.path.join(REPORT, "definition/pages", pname)
    check(os.path.exists(os.path.join(pdir, "page.json")), "página sem page.json: %s" % pname)
    pj = json.load(open(os.path.join(pdir, "page.json"), encoding="utf-8"))
    check("page/2.1.0" in pj["$schema"], "%s: schema de página errado" % pname)
    PW, PH = pj["width"], pj["height"]

    for vpath in glob.glob(os.path.join(pdir, "visuals", "*", "visual.json")):
        vj = json.load(open(vpath, encoding="utf-8"))
        vname = vj["name"]
        check("visualContainer/2.12.0" in vj["$schema"], "%s/%s: schema de visual errado" % (pname, vname))
        check(os.path.basename(os.path.dirname(vpath)) == vname,
              "%s: nome do visual difere da pasta" % vname)
        p = vj["position"]
        check(p["x"] >= 0 and p["y"] >= 0, "%s/%s: posição negativa" % (pname, vname))
        check(p["width"] > 0 and p["height"] > 0, "%s/%s: dimensão zero ou negativa" % (pname, vname))
        check(p["x"] + p["width"] <= PW, "%s/%s: extrapola a largura (%d)" % (pname, vname, p["x"] + p["width"]))
        check(p["y"] + p["height"] <= PH, "%s/%s: extrapola a altura (%d)" % (pname, vname, p["y"] + p["height"]))

        vt = vj["visual"]["visualType"]
        tipos[vt] = tipos.get(vt, 0) + 1
        nvis += 1

        # slicer em dropdown precisa de ~50px para o cabeçalho e a caixa caberem
        if vt == "slicer":
            check(p["height"] >= 50, "%s/%s: slicer com %dpx — dropdown sai cortado"
                  % (pname, vname, p["height"]))

        # todo campo referenciado precisa existir no modelo
        blob = json.dumps(vj, ensure_ascii=False)
        for ent, prop in re.findall(r'"Entity":\s*"([^"]+)"\}\},\s*"Property":\s*"([^"]+)"', blob):
            if ent == "_Medidas":
                check(prop in measures, "%s/%s: medida inexistente _Medidas[%s]" % (pname, vname, prop))
            else:
                check(ent in tables, "%s/%s: tabela inexistente %s" % (pname, vname, ent))
                check(prop in tables.get(ent, ()), "%s/%s: coluna inexistente %s[%s]" % (pname, vname, ent, prop))

        # títulos: o enunciado exige título explicativo em cada visual
        if vt not in ("textbox", "slicer", "card"):
            vco = vj["visual"].get("visualContainerObjects", {})
            def _show(obj):
                return vco.get(obj, [{}])[0].get("properties", {}) \
                          .get("show", {}).get("expr", {}).get("Literal", {}).get("Value")
            componente = _show("background") is None   # sem moldura = peça de um painel composto
            check(componente or _show("title") == "true",
                  "%s/%s (%s): sem título explicativo" % (pname, vname, vt))

print("relatório: %d páginas, %d visuais" % (len(pages["pageOrder"]), nvis))
print("tipos: " + ", ".join("%s=%d" % kv for kv in sorted(tipos.items(), key=lambda k: -k[1])))

# ── 7. os cinco visuais especializados da aula 05 estão presentes ───────────
for vt, nome in [("card", "Cartões/KPIs"), ("treemap", "Treemap"), ("map", "Mapa"),
                 ("pivotTable", "Matriz"), ("tableEx", "Tabela")]:
    check(tipos.get(vt, 0) > 0, "visual especializado ausente: %s (%s)" % (nome, vt))

# ── 8. todo JSON do projeto é parseável ─────────────────────────────────────
for path in glob.glob("**/*.json", recursive=True) + ["Hospitalar.pbip", os.path.join(REPORT, "definition.pbir")]:
    try: json.load(open(path, encoding="utf-8"))
    except Exception as e: ERR.append("JSON inválido: %s — %s" % (path, e))

if ERR:
    print("\n%d PROBLEMA(S):" % len(ERR))
    for e in ERR: print("  ✗ " + e)
    sys.exit(1)
print("\n✓ todas as checagens passaram")
