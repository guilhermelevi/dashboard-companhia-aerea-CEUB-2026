# -*- coding: utf-8 -*-
"""Construtor dos visuais PBIR do painel hospitalar."""
import json, os, hashlib

SCHEMA_VIS  = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json"
SCHEMA_PAGE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PGS  = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"

# paleta funcional — cor com significado, nunca decoração
INST, OK, WARN, BAD = "#134E5C", "#2E9B6B", "#E8A33D", "#C8414F"
MUTED, BG, OUT, CARD, BORDER = "#63768A", "#F4F6F9", "#DFE5EC", "#FFFFFF", "#E2E8EF"
FONT = "Segoe UI, wf_segoe-ui_normal, helvetica, arial, sans-serif"

def lit(v):      return {"expr": {"Literal": {"Value": v}}}
def s(v):        return lit("'%s'" % v)
def d(v):        return lit("%sD" % v)
def b(v):        return lit("true" if v else "false")
def solid(hexc): return {"solid": {"color": {"expr": {"Literal": {"Value": "'%s'" % hexc}}}}}
def props(**kw): return [{"properties": dict(kw)}]

_seq = [0]
def vid(prefix="v"):
    _seq[0] += 1
    h = hashlib.md5(("hosp%d" % _seq[0]).encode()).hexdigest()[:13]
    return "%s%s" % (prefix, h)

# ---------- campos ----------
def fcol(entity, prop, alias=None):
    return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}},
            "queryRef": "%s.%s" % (entity, prop), "nativeQueryRef": alias or prop}

def fmea(prop, alias=None, entity="_Medidas"):
    return {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}},
            "queryRef": "%s.%s" % (entity, prop), "nativeQueryRef": alias or prop}

def favg(entity, prop, alias=None):
    return {"field": {"Aggregation": {"Expression": {"Column": {
                "Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}, "Function": 1}},
            "queryRef": "Average(%s.%s)" % (entity, prop), "nativeQueryRef": alias or prop}

def sort_by_measure(prop, direction="Descending", entity="_Medidas"):
    return {"sort": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": entity}},
            "Property": prop}}, "direction": direction}], "isDefaultSort": True}

def sort_by_column(entity, prop, direction="Ascending"):
    return {"sort": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": entity}},
            "Property": prop}}, "direction": direction}], "isDefaultSort": True}

# ---------- moldura padrão ----------
def frame(title=None, subtitle=None, bg=CARD, border=True, pad=(10, 10, 6, 6), header=False):
    o = {}
    if bg:
        o["background"] = props(show=b(True), color=solid(bg), transparency=d(0))
    o["visualHeader"] = props(show=b(header))
    o["border"] = props(show=b(True), color=solid(BORDER), radius=d(8), width=d(1)) if border \
                  else props(show=b(False))
    if title:
        o["title"] = props(show=b(True), text=s(title), fontSize=d(11), fontColor=solid(INST),
                           bold=b(True), alignment=s("left"), titleWrap=b(False))
    else:
        o["title"] = props(show=b(False))
    if subtitle:
        o["subTitle"] = props(show=b(True), text=s(subtitle), fontSize=d("8.5"),
                              fontColor=solid(MUTED), alignment=s("left"), titleWrap=b(False))
    l, r, t, bo = pad
    o["padding"] = props(left=d(l), right=d(r), top=d(t), bottom=d(bo))
    return o

def visual(name, pos, vtype, query=None, objects=None, vco=None):
    v = {"visualType": vtype, "drillFilterOtherVisuals": True}
    if query: v["query"] = query
    if objects: v["objects"] = objects
    if vco: v["visualContainerObjects"] = vco
    return {"$schema": SCHEMA_VIS, "name": name,
            "position": {"x": pos[0], "y": pos[1], "z": pos[2], "width": pos[3], "height": pos[4]},
            "visual": v}

def qs(**roles):
    return {"queryState": {k: {"projections": v} for k, v in roles.items() if v}}

# ---------- fábricas por tipo ----------
def card(pos, measure, title, *, color=INST, fontsize=20, units=0, alias=None, align="center"):
    o = {"labels": props(color=solid(color), fontSize=d(fontsize), bold=b(True),
                         labelDisplayUnits=d(units)),
         "categoryLabels": props(show=b(False)),
         "wordWrap": props(show=b(False))}
    vco = frame(pad=(4, 4, 4, 4))
    vco["title"] = props(show=b(True), text=s(title), fontSize=d("8.5"), fontColor=solid(MUTED),
                         alignment=s(align), titleWrap=b(True))
    return visual(vid(), pos, "card", qs(Values=[fmea(measure, alias)]), o, vco)

def card_text(pos, measure, *, color=MUTED, fontsize=9):
    """Cartão que exibe uma medida de texto — o contexto ao lado do número."""
    o = {"labels": props(color=solid(color), fontSize=d(fontsize), bold=b(False)),
         "categoryLabels": props(show=b(False)),
         "wordWrap": props(show=b(True))}
    vco = frame(bg=None, border=False, pad=(8, 8, 2, 2))
    return visual(vid(), pos, "card", qs(Values=[fmea(measure)]), o, vco)

def slicer(pos, entity, prop, header_text, *, single=False):
    o = {"data": props(mode=s("Dropdown")),
         "header": props(show=b(True), fontColor=solid(INST), fontSize=d("8.5"),
                         text=s(header_text), background=solid(CARD), outline=s("None")),
         "items": props(fontColor=solid(INST), fontSize=d("8.5"), background=solid(CARD)),
         "selection": props(selectAllCheckboxEnabled=b(True), singleSelect=b(single))}
    return visual(vid(), pos, "slicer", qs(Values=[fcol(entity, prop, header_text)]), o, frame())

def textbox(name, pos, paragraphs, *, bg=None, border=False, pad=(24, 24, 15, 10)):
    vco = {"visualHeader": props(show=b(False)), "title": props(show=b(False))}
    if bg: vco["background"] = props(show=b(True), color=solid(bg), transparency=d(0))
    vco["border"] = props(show=b(True), color=solid(BORDER), radius=d(8), width=d(1)) if border \
                    else props(show=b(False))
    l, r, t, bo = pad
    vco["padding"] = props(left=d(l), top=d(t), right=d(r), bottom=d(bo))
    return {"$schema": SCHEMA_VIS, "name": name,
            "position": {"x": pos[0], "y": pos[1], "z": pos[2], "width": pos[3], "height": pos[4]},
            "visual": {"visualType": "textbox",
                       "objects": {"general": props(paragraphs=paragraphs)},
                       "visualContainerObjects": vco, "drillFilterOtherVisuals": True}}

def par(runs, align="left"):
    return {"horizontalTextAlignment": align, "textRuns": runs}

def run(text, *, size="9pt", color=INST, bold=False, italic=False):
    st = {"fontSize": size, "color": color, "fontFamily": FONT}
    if bold: st["fontWeight"] = "bold"
    if italic: st["fontStyle"] = "italic"
    return {"value": text, "textStyle": st}

def spacer(size="4pt"):
    return par([run("", size=size, color="#FFFFFF")])

# ---------- os cinco visuais especializados da aula 05 ----------

def treemap(pos, group, values, title, subtitle, *, details=None, colors=None, sort_measure=None):
    """TREEMAP — participação e hierarquia. group: lista de (entity, prop, alias)."""
    q = qs(Group=[fcol(*g) for g in group],
           Details=[fcol(*d_) for d_ in (details or [])],
           Values=[fmea(*v) for v in values])
    if sort_measure: q["sortDefinition"] = sort_by_measure(sort_measure)
    o = {"labels": props(show=b(True), fontSize=d(9), color=solid("#FFFFFF"), bold=b(True)),
         "categoryLabels": props(show=b(True), fontSize=d("8.5"), color=solid("#FFFFFF")),
         "legend": props(show=b(False))}
    if colors:
        o["dataPoint"] = [{"properties": {"fill": solid(c)},
                           "selector": {"data": [{"dataViewWildcard": {"matchingOption": 0}}]}}
                          for c in colors[:1]]
    return visual(vid(), pos, "treemap", q, o, frame(title, subtitle))

def mapa(pos, category, lat, lon, size, title, subtitle, *, bubble=-10, color=INST):
    """MAPA — onde o fenômeno acontece. Lat/Lon entram como agregação Average."""
    q = qs(Category=[fcol(*category)],
           Y=[favg(*lat)], X=[favg(*lon)],
           Size=[fmea(*size)])
    o = {"bubbles": props(bubbleSize=d(bubble)),
         "dataPoint": props(fill=solid(color)),
         "mapStyles": props(mapTheme=s("normal")),
         "legend": props(show=b(False), position=s("Top"), fontSize=d(9),
                         labelColor=solid(MUTED), showTitle=b(False))}
    return visual(vid(), pos, "map", q, o, frame(title, subtitle))

def _grid_objects(*, vertical=True, stepped=None, row_subtotals=None, col_subtotals=None, totals=None):
    o = {"grid": props(gridVertical=b(vertical), gridVerticalColor=solid(BORDER),
                       gridHorizontal=b(True), gridHorizontalColor=solid(BORDER),
                       rowPadding=d(3), outlineColor=solid(BORDER)),
         "columnHeaders": props(fontColor=solid("#FFFFFF"), backColor=solid(INST),
                                fontSize=d(9), bold=b(True), alignment=s("Center"), wordWrap=b(True)),
         "values": props(fontColor=solid(INST), fontSize=d(9),
                         backColorPrimary=solid(CARD), backColorSecondary=solid("#F8FAFC"))}
    if stepped is not None:
        o["rowHeaders"] = props(fontColor=solid(INST), fontSize=d(9),
                                steppedLayout=b(stepped), backColor=solid(CARD))
    if row_subtotals is not None or col_subtotals is not None:
        o["subTotals"] = props(rowSubtotals=b(bool(row_subtotals)),
                               columnSubtotals=b(bool(col_subtotals)))
    tot = {"fontColor": solid(INST), "backColor": solid(BG), "bold": b(True)}
    if totals is not None: tot["totals"] = b(totals)
    o["total"] = props(**tot)
    return o

def matriz(pos, rows, values, title, subtitle, *, columns=None, sort_measure=None):
    """MATRIZ — cruzamento de categorias com hierarquia e drill-down."""
    q = qs(Rows=[fcol(*r) for r in rows],
           Columns=[fcol(*c) for c in (columns or [])],
           Values=[fmea(*v) for v in values])
    if sort_measure: q["sortDefinition"] = sort_by_measure(sort_measure)
    o = _grid_objects(stepped=True, row_subtotals=True, col_subtotals=bool(columns))
    return visual(vid(), pos, "pivotTable", q, o, frame(title, subtitle))

def tabela(pos, values, title, subtitle, *, sort_measure=None, sort_column=None, totals=True):
    """TABELA — consulta precisa de valores exatos e múltiplas métricas."""
    q = qs(Values=values)
    if sort_measure: q["sortDefinition"] = sort_by_measure(sort_measure)
    elif sort_column: q["sortDefinition"] = sort_by_column(*sort_column)
    o = _grid_objects(vertical=False, totals=totals)
    return visual(vid(), pos, "tableEx", q, o, frame(title, subtitle))

# ---------- apoio: a tendência que completa o KPI ----------
def linha(pos, category, values, title, subtitle, *, colors=None, sort_column=None,
          show_axes=True, frame_on=True):
    q = qs(Category=[fcol(*category)], Y=[fmea(*v) for v in values])
    if sort_column: q["sortDefinition"] = sort_by_column(*sort_column)
    o = {"legend": props(show=b(len(values) > 1), position=s("Top"), fontSize=d(9),
                         labelColor=solid(MUTED), showTitle=b(False)),
         "categoryAxis": props(show=b(show_axes), fontSize=d(8), labelColor=solid(MUTED),
                               showAxisTitle=b(False), gridlineShow=b(False)),
         "valueAxis": props(show=b(show_axes), fontSize=d(8), labelColor=solid(MUTED),
                            showAxisTitle=b(False), gridlineShow=b(show_axes),
                            gridlineColor=solid(BORDER)),
         "labels": props(show=b(False))}
    if colors:
        o["dataPoint"] = [{"properties": {"fill": solid(c)},
                           "selector": {"metadata": "_Medidas.%s" % mname}}
                          for mname, c in colors]
    vco = frame(title, subtitle) if frame_on else frame(bg=None, border=False, pad=(2, 2, 2, 2))
    return visual(vid(), pos, "lineChart", q, o, vco)

# ---------- escrita ----------
def page(root, name, display, visuals, *, bg=BG, out=OUT):
    pdir = os.path.join(root, "definition", "pages", name)
    os.makedirs(os.path.join(pdir, "visuals"), exist_ok=True)
    pj = {"$schema": SCHEMA_PAGE, "name": name, "displayName": display,
          "displayOption": "FitToPage", "height": 720, "width": 1280,
          "objects": {"background": props(color=solid(bg), transparency=d(0)),
                      "outspace": props(color=solid(out), transparency=d(0))}}
    with open(os.path.join(pdir, "page.json"), "w", encoding="utf-8") as f:
        json.dump(pj, f, ensure_ascii=False, indent=2); f.write("\n")
    for v in visuals:
        vdir = os.path.join(pdir, "visuals", v["name"])
        os.makedirs(vdir, exist_ok=True)
        with open(os.path.join(vdir, "visual.json"), "w", encoding="utf-8") as f:
            json.dump(v, f, ensure_ascii=False, indent=2); f.write("\n")
    return len(visuals)

def pages_json(root, order, active):
    p = os.path.join(root, "definition", "pages", "pages.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"$schema": SCHEMA_PGS, "pageOrder": order, "activePageName": active},
                  f, ensure_ascii=False, indent=2); f.write("\n")

def header(pos_y_height, title, subtitle, *, width=1280):
    return textbox(vid("txt"), (0, 0, 0, width, pos_y_height),
                   [par([run(title, size="16pt", color="#FFFFFF", bold=True)]),
                    par([run(subtitle, size="9pt", color="#BFD4DC")])], bg=INST)
