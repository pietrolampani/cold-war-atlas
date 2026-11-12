"""Hong Kong e Macao dalle relazioni OSM, costa del Manciukuò, isole di quell'area e confine di Gorizia.

Scrive le voci in territories.js (segnate "hk", si sostituiscono rilanciando), corregge land/19_7.js e crea gorizia.js.

Uso: python -I tools/build_hk_gorizia.py rel_913110.json rel_1867188.json world_borders.json territories.js land/19_7.js gorizia.js
"""
import json
import math
import sys

CODES = {"hk": 3925, "macao": 3924, "cina": 710}
SCALE = 1e4
# Mare davanti alla costa da Shanhaiguan allo Yalu: la terra OSM ritaglia, e il riempimento arriva alla riva senza toccare Hebei e Corea
URBAN = (45.925, 45.968)
CROSSINGS = [
    ("Valico di Casa Rossa", 45.94178, 13.63509, "Rožna Dolina, il valico internazionale di Gorizia. Posizione dal nodo OSM del controllo di frontiera."),
    ("Valico di San Gabriele", 45.95247, 13.63395, "Verso Erjavčeva ulica a Nova Gorica. Posizione dal nodo OSM del controllo di frontiera."),
    ("Valico del Rafut", 45.9472, 13.6328, "Valico secondario su via del Rafut, oggi sede di un'esposizione sul confine. Posizione dalla strada in OSM."),
    ("Valico di Sant'Andrea", 45.91828, 13.61876, "Verso Vrtojba, a sud della città. Posizione dalla stazione confinaria in OSM, che può essere successiva al periodo."),
    ("Piazza della Transalpina", 45.9553, 13.6349, "La recinzione divideva la piazza davanti alla stazione, rimasta in Jugoslavia. Non era un valico ordinario."),
]
MANCHU_COAST = [[119.75, 39.99], [120.0, 39.6], [120.8, 39.1], [120.6, 38.5], [121.2, 38.4], [122.5, 38.4], [124.3, 39.6], [124.35, 39.98], [125, 41], [121, 41.5], [120, 40.5], [119.75, 39.99]]


def stitch(lines):
    rings, loose = [], []
    while lines:
        line = lines.pop()
        grown = True
        while grown and line[0] != line[-1]:
            grown = False
            for i, o in enumerate(lines):
                if o[0] == line[-1]:
                    line = line + o[1:]
                elif o[-1] == line[-1]:
                    line = line + o[::-1][1:]
                elif o[-1] == line[0]:
                    line = o + line[1:]
                elif o[0] == line[0]:
                    line = o[::-1] + line[1:]
                else:
                    continue
                lines.pop(i)
                grown = True
                break
        (rings if line[0] == line[-1] else loose).append(line)
    return rings, loose


def relation(path, rel):
    els = json.load(open(path, encoding="utf8"))["elements"]
    nodes = {e["id"]: [round(e["lon"], 6), round(e["lat"], 6)] for e in els if e["type"] == "node"}
    ways = {e["id"]: e for e in els if e["type"] == "way"}
    head = next(e for e in els if e["type"] == "relation" and e["id"] == rel)
    outer = [[nodes[n] for n in ways[m["ref"]]["nodes"]] for m in head["members"] if m["type"] == "way" and m.get("role") == "outer" and m["ref"] in ways]
    rings, loose = stitch(outer)
    print(rel, "anelli", len(rings), "aperti", len(loose), "punti", sum(map(len, rings)))
    return rings


def inside(p, rings):
    x, y = p
    c = False
    for r in rings:
        for (a, b), (e, f) in zip(r, r[1:]):
            if (b > y) != (f > y) and x < (e - a) * (y - b) / (f - b) + a:
                c = not c
    return c


def decode(a):
    x = y = 0
    out = []
    for i in range(0, len(a), 2):
        x += a[i]
        y += a[i + 1]
        out.append((x / SCALE, y / SCALE))
    return out


def centre(pts):
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


def patch_tile(path, hk, macau):
    text = open(path, encoding="utf8").read()
    head, body = text[:text.index("{")], text[text.index("{"): text.rindex("}") + 1]
    t = json.loads(body)
    moved = 0
    new = {}
    for code, block in t["isl"].items():
        for a in block:
            pts = decode(a)
            c = centre(pts)
            target = code
            if 113.3 < c[0] < 114.7 and 21.7 < c[1] < 22.7 and code in ("710", "3925", "3924"):
                target = "3925" if inside(c, hk) else "3924" if inside(c, macau) else "710"
                moved += target != code
            new.setdefault(target, []).append(a)
    t["isl"] = new
    with open(path, "w", encoding="utf8") as h:
        h.write(head + json.dumps(t, separators=(",", ":")) + ");\n")
    print("isole riassegnate", moved)


def gorizia(world, dst):
    lines = []
    for r in json.load(open(world))["elements"]:
        g = [[p["lon"], p["lat"]] for p in r["geometry"]]
        if any(13.55 < x < 13.72 and 45.88 < y < 46.02 for x, y in g):
            lines.append([p for p in g if 13.55 < p[0] < 13.72 and 45.88 < p[1] < 46.02])
    rings, loose = stitch([l for l in lines if len(l) > 1])
    parts = rings + loose
    parts.sort(key=len, reverse=True)
    # Solo il tratto urbano, tra Salcano e San Pietro: l'estensione esatta della recinzione non è documentata in dati aperti
    p = [[round(x, 5), round(y, 5)] for x, y in parts[0] if URBAN[0] <= y <= URBAN[1]]
    print("Gorizia: punti", len(p), "da", p[0], "a", p[-1])
    line = {"n": "Muro di Gorizia", "from": "1947-09", "to": "1991-12", "k": "line", "src": "Tracciato del confine di oggi, da OpenStreetMap; estensione della recinzione stimata",
            "d": "Il trattato di pace del 1947 divide la città: Gorizia all'Italia, a est la jugoslava Nova Gorica. Reti e muretti lungo il confine urbano, tolti nel 2004.", "p": p}
    places = [{"n": n, "from": "1947-09", "to": "1991-12", "lat": la, "lon": lo, "min": 400, "c": "cp", "d": d} for n, la, lo, d in CROSSINGS]
    with open(dst, "w", encoding="utf8") as h:
        h.write("/* Muro e valichi di Gorizia: tracciato e posizioni da OSM; descrizioni a memoria, date di apertura dei singoli valichi non verificate. */\nwindow.LINES.push(" + json.dumps(line, ensure_ascii=False, separators=(",", ":")) + ");\nwindow.PLACES.push(..." + json.dumps(places, ensure_ascii=False, separators=(",", ":")) + ");\n")


def main(hk_path, macau_path, world, territories, tile, gor, slovenia, croatia):
    hk, macau = relation(hk_path, 913110), relation(macau_path, 1867188)
    text = open(territories, encoding="utf8").read()
    old = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("hk") and x["n"] != "Macao"]
    for x in old:  # I contorni OSM comprendono il mare: valgono solo dove la terra OSM lo ritaglia. Sotto restano quelli generali
        if x["n"] in ("Slovenia", "Croazia"):
            x["look"] = "t-conf t-low"
    add = [
        {"n": "Manciukuò, costa", "from": "1945-01", "to": "1945-08", "look": "st-X t-fill t-land", "rings": [MANCHU_COAST], "d": "Stato fantoccio giapponese; il Kwantung, con Dalian e Port Arthur, è possesso giapponese."},
        {"n": "Hong Kong", "from": "1945-01", "to": "1945-08", "look": "st-O t-land", "rings": hk, "d": "Occupata dal Giappone dal dicembre 1941 all'agosto 1945. Contorno OSM di oggi."},
        {"n": "Hong Kong", "from": "1945-09", "to": "1991-12", "look": "emp-uk t-land", "rings": hk, "d": "Colonia britannica fino al 1997, con i Nuovi Territori in affitto dal 1898. Confine OSM di oggi, che dal 1997 include il tratto rivisto sul fiume Shenzhen."},
        {"n": "Macao", "from": "1945-01", "to": "1991-12", "look": "emp-pt t-land", "rings": macau, "d": "Portoghese fino al 1999. Confine OSM di oggi; la costa è quella di oggi, con le bonifiche successive."},
        {"n": "Slovenia", "from": "1991-06", "to": "1991-12", "look": "t-conf t-land", "rings": relation(slovenia, 218657), "d": "Indipendenza proclamata il 25 giugno 1991, riconosciuta dagli altri Stati solo nel gennaio 1992. Contorno OSM."},
        {"n": "Croazia", "from": "1991-06", "to": "1991-12", "look": "t-conf t-land", "rings": relation(croatia, 214885), "d": "Indipendenza proclamata il 25 giugno 1991, guerra con la Jugoslavia, riconoscimento nel gennaio 1992. Contorno OSM."},
    ]
    for x in add:
        x["hk"] = 1
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(old + add, separators=(",", ":"), ensure_ascii=False) + ";\n")
    patch_tile(tile, hk, macau)
    gorizia(world, gor)


if __name__ == "__main__":
    main(*sys.argv[1:9])
