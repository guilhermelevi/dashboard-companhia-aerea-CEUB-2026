# -*- coding: utf-8 -*-
"""
Gera as páginas e visuais PBIR de Hospitalar.Report.

Cada página demonstra um dos cinco tipos de visualização especializada da aula 05
(Cartões/KPIs, Treemap, Mapa, Matriz, Tabela), aplicados à base de 100 mil atendimentos.

    python3 build_report.py

Reescreve definition/pages/ por completo. Os nomes dos visuais são derivados de um
contador determinístico, então rodar de novo produz exatamente os mesmos arquivos.
"""
import os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pbir import *

R = "Hospitalar.Report"
X0, W = 24, 1232

def cols(n, gap=8):
    w = (W - gap * (n - 1)) // n
    return [(X0 + i * (w + gap), w) for i in range(n)]

def filtros():
    """Três segmentadores na faixa de título — 50px é o mínimo para o dropdown não cortar."""
    return [slicer((700, 14, 3, 178, 54), "dCalendario", "Ano", "Ano"),
            slicer((886, 14, 4, 178, 54), "dHospital", "Hospital", "Unidade"),
            slicer((1072, 14, 5, 184, 54), "dTipoAtendimento", "Tipo", "Tipo de atendimento")]

def faixa_kpi(defs, y=88, h=76, fontsize=18):
    out = []
    for (x, w), (mea, tit, cor, units) in zip(cols(len(defs)), defs):
        out.append(card((x, y, 6, w, h), mea, tit, color=cor, fontsize=fontsize, units=units))
    return out

# ═════════════════════ PÁGINA 1 — CARTÕES / KPIs ═════════════════════
def pagina1():
    v = [header(80, "Rede Hospitalar — Painel de Indicadores",
                "Aula 05 · Visualizações especializadas  •  100 mil atendimentos  •  jan/2024 a jul/2026")]
    v += filtros()
    v += faixa_kpi([
        ("Atendimentos", "Atendimentos", INST, 1000),
        ("Taxa de Internação", "Taxa de internação", INST, 0),
        ("Espera Média (min)", "Espera média (min)", WARN, 0),
        ("Satisfação Média", "Satisfação (1 a 5)", INST, 0),
        ("Receita", "Receita", INST, 1000),
        ("Margem %", "Margem", OK, 0),
        ("Taxa de Mortalidade", "Mortalidade", BAD, 0),
        ("% Não Programado", "Não programado", WARN, 0)], y=88, h=84)

    # três KPIs com a anatomia completa: valor · meta · variação · tendência
    ctx = [("Espera Média (min)", "Rótulo Espera vs Meta", "Espera até o atendimento",
            WARN, "Espera Média (min)"),
           ("Satisfação Média", "Rótulo Satisfação vs Meta", "Satisfação do paciente",
            INST, "Satisfação Média"),
           ("Margem %", "Rótulo Margem vs Meta", "Margem sobre a receita",
            OK, "Margem %")]
    for (x, w), (mea, rot, tit, cor, trend) in zip(cols(3), ctx):
        v.append(textbox(vid("txt"), (x, 180, 7, w, 250), [par([run("", size="4pt", color=CARD)])],
                         bg=CARD, border=True, pad=(0, 0, 0, 0)))
        v.append(card((x, 184, 8, w, 92), mea, tit, color=cor, fontsize=30, align="left"))
        v.append(card_text((x, 276, 9, w, 32), rot, color=MUTED, fontsize=9))
        v.append(linha((x + 6, 308, 10, w - 12, 118), ("dCalendario", "Ano-Mes", "Competência"),
                       [(trend,)], None, None, colors=[(trend, cor)],
                       sort_column=("dCalendario", "Ano-Mes"), show_axes=False, frame_on=False))

    v.append(textbox(vid("txt"), (X0, 440, 12, 604, 260), [
        par([run("Por que os cartões vêm primeiro", size="12pt", bold=True)]),
        spacer("6pt"),
        par([run("Um número isolado informa. ", size="9pt", color=MUTED),
             run("Um número com contexto ajuda a decidir.", size="9pt", color=INST, bold=True)]),
        spacer("6pt"),
        par([run("✕  Sem contexto   ", size="9pt", color=BAD, bold=True),
             run("“Espera média: 37 min.”  É bom ou ruim? O número existe, mas não orienta decisão.",
                 size="9pt", color=MUTED)]),
        spacer("4pt"),
        par([run("✓  Com contexto   ", size="9pt", color=OK, bold=True),
             run("“37 min — meta de 30 — 7 min acima, com a curva subindo.”  Agora há o que decidir.",
                 size="9pt", color=INST)]),
        spacer("6pt"),
        par([run("Os três cartões acima carregam os cinco elementos que a aula exige: "
                 "valor atual, meta, variação, período anterior e tendência.",
                 size="8.5pt", color=MUTED, italic=True)])],
        bg=CARD, border=True, pad=(18, 18, 14, 14)))

    v.append(linha((652, 440, 12, 604, 260), ("dCalendario", "Ano-Mes", "Competência"),
                   [("Atendimentos",), ("Média Móvel 3M Atendimentos", "Média móvel 3M")],
                   "Como o volume evoluiu no período",
                   "a média móvel de 3 meses separa tendência de ruído mensal",
                   colors=[("Atendimentos", INST), ("Média Móvel 3M Atendimentos", WARN)],
                   sort_column=("dCalendario", "Ano-Mes")))
    return page(R, "pagina1", "1 · Cartões e KPIs", v)

# ═════════════════════ PÁGINA 2 — TREEMAP ═════════════════════
def pagina2():
    v = [header(80, "Participação — quem absorve os recursos da rede",
                "TREEMAP · a área de cada retângulo é proporcional ao volume de atendimentos")]
    v += filtros()
    v += faixa_kpi([("Atendimentos", "Atendimentos da seleção", INST, 0),
                    ("Participação nos Atendimentos", "Participação no total", INST, 0),
                    ("Especialidades", "Especialidades na seleção", MUTED, 0),
                    ("Receita", "Receita da seleção", INST, 1000)])

    v.append(treemap((X0, 172, 7, 810, 528),
                     [("dEspecialidade", "Bloco", "Bloco assistencial"),
                      ("dEspecialidade", "Especialidade", "Especialidade"),
                      ("dDiagnostico", "Diagnostico", "Diagnóstico")],
                     [("Atendimentos",)],
                     "Atendimentos por bloco, especialidade e diagnóstico",
                     "clique duas vezes num retângulo para descer o nível · a área revela quem domina",
                     cores=["Clinicas", "Materno-infantil", "Cirurgicas", "Ambulatoriais"],
                     sort_measure="Atendimentos"))

    v.append(treemap((850, 172, 8, 406, 256),
                     [("dConvenio", "Natureza", "Natureza"), ("dConvenio", "Convenio", "Convênio")],
                     [("Receita",)],
                     "Receita por fonte pagadora",
                     "a mesma lógica aplicada ao faturamento",
                     cores=["Suplementar", "Publico", "Particular"],
                     sort_measure="Receita"))

    v.append(textbox(vid("txt"), (850, 436, 9, 406, 264), [
        par([run("Quando o treemap é a escolha certa", size="11pt", bold=True)]),
        spacer("6pt"),
        par([run("✓  Funciona bem quando", size="9pt", color=OK, bold=True)]),
        par([run("há várias categorias para comparar, a proporção relativa importa mais que o valor "
                 "exato e existe hierarquia nos dados.", size="8.5pt", color=MUTED)]),
        spacer("6pt"),
        par([run("✕  Evite quando", size="9pt", color=BAD, bold=True)]),
        par([run("há muitas categorias minúsculas, excesso de cores, ou quando diferenças sutis "
                 "precisam ser comparadas com precisão — aí use barras ou tabela.",
                 size="8.5pt", color=MUTED)]),
        spacer("6pt"),
        par([run("Pergunta respondida:  ", size="8.5pt", color=INST, bold=True),
             run("quais categorias possuem maior participação no conjunto?",
                 size="8.5pt", color=MUTED, italic=True)])],
        bg=CARD, border=True, pad=(16, 16, 12, 12)))
    return page(R, "pagina2", "2 · Treemap", v)

# ═════════════════════ PÁGINA 3 — MAPA ═════════════════════
def pagina3():
    v = [header(80, "Território — onde a rede atende",
                "MAPA · o tamanho da bolha indica o volume de atendimentos de cada unidade")]
    v += filtros()
    v += faixa_kpi([("Atendimentos", "Atendimentos", INST, 1000),
                    ("Espera Média (min)", "Espera média (min)", WARN, 0),
                    ("Satisfação Média", "Satisfação", INST, 0),
                    ("Taxa de Internação", "Taxa de internação", INST, 0)])

    v.append(mapa((X0, 172, 7, 750, 528),
                  ("dHospital", "Unidade", "Unidade"),
                  ("dHospital", "Latitude", "Latitude"),
                  ("dHospital", "Longitude", "Longitude"),
                  ("Atendimentos",),
                  "Distribuição das unidades no Distrito Federal",
                  "clique numa bolha para filtrar o painel inteiro por unidade"))

    v.append(tabela((790, 172, 8, 466, 264),
                    [fcol("dHospital", "Hospital", "Unidade"),
                     fmea("Atendimentos", "Atend."),
                     fmea("Espera Média (min)", "Espera"),
                     fmea("Satisfação Média", "Satisf.")],
                    "O que o mapa não mostra com precisão",
                    "a bolha compara grandeza; a tabela dá o valor exato",
                    sort_measure="Atendimentos"))

    v.append(textbox(vid("txt"), (790, 444, 9, 466, 256), [
        par([run("A localização precisa ter significado", size="11pt", bold=True)]),
        spacer("6pt"),
        par([run("Nem todo dado geográfico pede um mapa. A presença de uma coluna “Cidade” não "
                 "justifica, sozinha, uma visualização cartográfica.", size="8.5pt", color=MUTED)]),
        spacer("6pt"),
        par([run("Nesta base, a geografia é rasa", size="9pt", color=WARN, bold=True)]),
        par([run("são 4 unidades, 2 municípios e 1 UF. O mapa responde bem a “onde a rede está "
                 "instalada e qual unidade concentra volume”, que é um uso legítimo — localização "
                 "de unidades de atendimento. Ele ", size="8.5pt", color=MUTED),
             run("não", size="8.5pt", color=BAD, bold=True),
             run(" responde “qual unidade atende mais”: para isso a tabela ao lado é mais precisa.",
                 size="8.5pt", color=MUTED)]),
        spacer("6pt"),
        par([run("Pergunta respondida:  ", size="8.5pt", color=INST, bold=True),
             run("onde o fenômeno está acontecendo?", size="8.5pt", color=MUTED, italic=True)])],
        bg=CARD, border=True, pad=(16, 16, 12, 12)))
    return page(R, "pagina3", "3 · Mapa", v)

# ═════════════════════ PÁGINA 4 — MATRIZ ═════════════════════
def pagina4():
    v = [header(80, "Cruzamentos — duas dimensões de uma vez",
                "MATRIZ · linhas em hierarquia, colunas por tipo de atendimento, com drill-down")]
    v += filtros()
    v += faixa_kpi([("Atendimentos", "Atendimentos", INST, 1000),
                    ("Emergências", "Emergências", BAD, 0),
                    ("Permanência Média (dias)", "Permanência média", INST, 0),
                    ("% Alta", "Resolvidos com alta", OK, 0)])

    v.append(matriz((X0, 172, 7, W, 440),
                    [("dHospital", "Hospital", "Unidade"),
                     ("dEspecialidade", "Especialidade", "Especialidade"),
                     ("dDiagnostico", "Diagnostico", "Diagnóstico"),
                     ("dProcedimento", "Procedimento", "Procedimento")],
                    [("Atendimentos",), ("Espera Média (min)", "Espera"),
                     ("Satisfação Média", "Satisfação")],
                    "Da unidade ao procedimento, sem sair do mesmo visual",
                    "colunas = tipo de atendimento · expanda a linha para descer "
                    "Unidade → Especialidade → Diagnóstico → Procedimento",
                    columns=[("dTipoAtendimento", "Tipo", "Tipo")],
                    sort_measure="Atendimentos"))

    v.append(textbox(vid("txt"), (X0, 620, 8, W, 80), [
        par([run("Por que matriz e não tabela aqui.   ", size="9pt", color=INST, bold=True),
             run("A tabela lista registros lado a lado; a matriz ", size="8.5pt", color=MUTED),
             run("cruza", size="8.5pt", color=INST, bold=True),
             run(" duas dimensões ao mesmo tempo e permite navegar do nível mais agregado "
                 "(unidade) até o mais granular (procedimento) sem trocar de visual — é a tabela "
                 "dinâmica do Excel dentro do dashboard.", size="8.5pt", color=MUTED)]),
        par([run("Pergunta respondida:  ", size="8.5pt", color=INST, bold=True),
             run("como os valores se comportam quando cruzamos diferentes categorias simultaneamente?",
                 size="8.5pt", color=MUTED, italic=True)])],
        bg=CARD, border=True, pad=(16, 16, 10, 10)))
    return page(R, "pagina4", "4 · Matriz", v)

# ═════════════════════ PÁGINA 5 — TABELA ═════════════════════
def pagina5():
    v = [header(80, "Detalhamento — os valores exatos",
                "TABELA · consulta precisa, múltiplas métricas por linha, pronta para exportar")]
    v += filtros()

    v.append(tabela((X0, 88, 6, W, 332),
                    [fcol("dEspecialidade", "Especialidade", "Especialidade"),
                     fcol("dEspecialidade", "Bloco", "Bloco"),
                     fmea("Atendimentos", "Atendimentos"),
                     fmea("Participação nos Atendimentos", "Participação"),
                     fmea("Espera Média (min)", "Espera (min)"),
                     fmea("Taxa de Internação", "Internação"),
                     fmea("Satisfação Média", "Satisfação"),
                     fmea("Ticket Médio", "Ticket médio"),
                     fmea("Margem %", "Margem")],
                    "Indicadores por especialidade",
                    "nove métricas por linha · clique no cabeçalho para reordenar",
                    sort_measure="Atendimentos"))

    v.append(tabela((X0, 428, 7, 604, 272),
                    [fcol("dHospital", "Hospital", "Unidade"),
                     fmea("Atendimentos", "Atendimentos"),
                     fmea("Espera Média (min)", "Espera"),
                     fmea("Satisfação Média", "Satisfação"),
                     fmea("% Dentro da Meta de Espera", "Dentro da meta")],
                    "Indicadores por unidade",
                    "o número exato que o mapa da página 3 só aproxima",
                    sort_measure="Atendimentos"))

    v.append(textbox(vid("txt"), (652, 428, 7, 604, 272), [
        par([run("Tabela ou gráfico? Depende da pergunta", size="11pt", bold=True)]),
        spacer("6pt"),
        par([run("📊  Use o gráfico quando…", size="9pt", color=INST, bold=True)]),
        par([run("“Qual especialidade tem mais atendimentos?”", size="8.5pt", color=MUTED, italic=True)]),
        par([run("→ padrões, tendências e comparações visuais são captados instantaneamente pelo olho.",
                 size="8.5pt", color=MUTED)]),
        spacer("6pt"),
        par([run("📋  Use a tabela quando…", size="9pt", color=INST, bold=True)]),
        par([run("“Quantos atendimentos exatamente cada especialidade realizou?”",
                 size="8.5pt", color=MUTED, italic=True)]),
        par([run("→ valores precisos, várias métricas por linha e necessidade de consulta detalhada "
                 "exigem o formato tabular.", size="8.5pt", color=MUTED)]),
        spacer("6pt"),
        par([run("Evite tabelas gigantes", size="9pt", color=BAD, bold=True)]),
        par([run("dezenas de colunas sem hierarquia, ou informação que um gráfico revelaria mais rápido.",
                 size="8.5pt", color=MUTED)]),
        spacer("6pt"),
        par([run("Pergunta respondida:  ", size="8.5pt", color=INST, bold=True),
             run("qual é exatamente o valor de cada informação?", size="8.5pt", color=MUTED, italic=True)])],
        bg=CARD, border=True, pad=(16, 16, 12, 12)))
    return page(R, "pagina5", "5 · Tabela", v)

# ═════════════════════ PÁGINA 6 — LEITURA E INSIGHTS ═════════════════════
def pagina6():
    v = [header(80, "Leitura do painel — qual pergunta cada visual responde",
                "a visualização se escolhe pela pergunta, não pelo estilo visual")]

    guia = [("Cartões / KPIs", "Qual é o valor atual do indicador mais importante?",
             "Página 1 · 8 cartões de leitura rápida + 3 com meta, variação e tendência.", INST),
            ("Treemap", "Quais categorias possuem maior participação no conjunto?",
             "Página 2 · Bloco → Especialidade → Diagnóstico, com drill-down.", OK),
            ("Mapa", "Onde determinado fenômeno está acontecendo?",
             "Página 3 · as 4 unidades da rede no DF, bolha proporcional ao volume.", WARN),
            ("Matriz", "Como os valores se comportam ao cruzar categorias?",
             "Página 4 · Unidade → Especialidade → Diagnóstico → Procedimento × tipo de atendimento.", INST),
            ("Tabela", "Qual é exatamente o valor de cada informação?",
             "Página 5 · 12 métricas por especialidade e 7 por unidade.", MUTED)]
    for i, (x, w) in enumerate(cols(5, gap=10)):
        tipo, pergunta, onde, cor = guia[i]
        v.append(textbox(vid("txt"), (x, 96, 1, w, 196), [
            par([run(tipo, size="11pt", color=cor, bold=True)]),
            spacer("6pt"),
            par([run(pergunta, size="9pt", color=INST, italic=True)]),
            spacer("6pt"),
            par([run(onde, size="8.5pt", color=MUTED)])],
            bg=CARD, border=True, pad=(14, 14, 12, 12)))

    v.append(textbox(vid("txt"), (X0, 304, 1, W, 80), [
        par([run("Antes de escolher, pergunte:   ", size="9pt", color=INST, bold=True),
             run("1) qual pergunta quero responder?   2) quem vai consumir essa informação?   "
                 "3) o usuário precisa identificar um padrão ou consultar um valor?   "
                 "4) a visualização reduz ou aumenta o esforço de interpretação?",
                 size="8.5pt", color=MUTED)]),
        par([run("A melhor visualização é a que responde à pergunta certa, para o público certo, "
                 "com o menor esforço de interpretação possível.",
                 size="8.5pt", color=INST, italic=True)])],
        bg="#E8EEF1", border=True, pad=(16, 16, 10, 10)))

    insights = [
        ("01", "A porta aberta responde por metade da operação",
         "Urgência e emergência somam 51,8% dos 100 mil atendimentos (37.848 + 13.974). "
         "Metade do movimento da rede não é agendável — o dimensionamento de plantão não pode "
         "ser calculado sobre a média do eletivo.", WARN),
        ("02", "Clínica Médica sozinha absorve um quarto da rede",
         "24.174 atendimentos, 24,2% do total — 1,5 vez a Ortopedia, que vem em segundo, e mais "
         "que Cirurgia Geral, Neurologia, Oftalmologia e Dermatologia somadas (23.859). Um ganho "
         "de 5% de eficiência ali vale mais que zerar a fila da Dermatologia.", INST),
        ("03", "A espera está 7 minutos acima da meta, e isso aparece na nota",
         "Espera média de 37,0 min contra meta de 30, e satisfação de 3,77 contra meta de 4,0. "
         "São os dois únicos indicadores fora da meta — a margem, a 32,9%, está acima dos 30% "
         "pactuados. O problema da rede é de fluxo, não financeiro.", BAD)]
    for i, (x, w) in enumerate(cols(3)):
        num, tit, txt, cor = insights[i]
        v.append(textbox(vid("txt"), (x, 392, 1, w, 308), [
            par([run(num + "   ", size="15pt", color=cor, bold=True)]),
            par([run(tit, size="12pt", color=INST, bold=True)]),
            spacer("8pt"),
            par([run(txt, size="9pt", color=MUTED)]),
            spacer("8pt"),
            par([run("Decisão que isso apoia", size="8.5pt", color=cor, bold=True)]),
            par([run({"01": "Escalar equipe de plantão pela curva de urgência, não pela média geral.",
                      "02": "Concentrar o próximo projeto de eficiência em Clínica Médica.",
                      "03": "Atacar o tempo de triagem antes de qualquer ação sobre custo."}[num],
                     size="8.5pt", color=MUTED, italic=True)])],
            bg=CARD, border=True, pad=(16, 16, 14, 14)))
    return page(R, "pagina6", "6 · Leitura e insights", v)


if __name__ == "__main__":
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), R, "definition", "pages")
    if os.path.isdir(base): shutil.rmtree(base)
    os.makedirs(base, exist_ok=True)
    total = 0
    for fn in (pagina1, pagina2, pagina3, pagina4, pagina5, pagina6):
        n = fn(); total += n
        print("  %-9s %3d visuais" % (fn.__name__, n))
    pages_json(R, ["pagina%d" % i for i in range(1, 7)], "pagina1")
    print("total: %d visuais em 6 páginas" % total)
