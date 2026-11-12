"""Zona del Canale e Ungheria del 1940 da OpenHistoricalMap, invasione di Panama del 1989. Aggiorna territories.js e scrive panama.js.

Le voci si segnano con "pz" e si sostituiscono rilanciando; la vecchia Zona del Canale, una fascia calcolata, viene tolta.
Le posizioni delle battaglie di Just Cause sono a memoria, approssimate.

Uso: python -I tools/build_panama_hungary.py cartella_ohm atlas10.json territories.js panama.js
"""
import json
import math
import os
import sys


def thin(r, metres=40):
    out = [r[0]]
    for p in r[1:-1]:
        k = math.cos(math.radians(p[1]))
        if math.hypot((p[0] - out[-1][0]) * k, p[1] - out[-1][1]) * 111320 >= metres:
            out.append(p)
    out.append(r[-1])
    return [[round(x, 5), round(y, 5)] for x, y in out]


def atlas_rings(path, name):
    t = json.load(open(path, encoding="utf8"))
    sx, sy = t["transform"]["scale"]; tx, ty = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0; p = []
        for dx, dy in a:
            x += dx; y += dy
            p.append([round(x * sx + tx, 4), round(y * sy + ty, 4)])
        arcs.append(p)
    g = next(g for g in t["objects"]["countries"]["geometries"] if g["properties"]["name"] == name)
    rings = []
    for poly in ([g["arcs"]] if g["type"] == "Polygon" else g["arcs"]):
        r = []
        for a in poly[0]:
            r += arcs[a] if a >= 0 else arcs[~a][::-1]
        rings.append(r)
    return rings


BATTLES = [
    ["La Comandancia", "1989-12", "1989-12", 8.9512, -79.5446, "20 dicembre: quartier generale delle Forze di difesa di Noriega a El Chorrillo, distrutto nei combattimenti e negli incendi del quartiere."],
    ["Río Hato", "1989-12", "1989-12", 8.3750, -80.1272, "Lancio dei Ranger sulla base dei battaglioni 6 e 7 delle Forze di difesa."],
    ["Aeroporto Torrijos-Tocumen", "1989-12", "1989-12", 9.0714, -79.3835, "Lancio dei Ranger e dell'82ª aviotrasportata."],
    ["Aeroporto di Paitilla", "1989-12", "1989-12", 8.9734, -79.5555, "I SEAL distruggono il jet di Noriega; quattro SEAL uccisi."],
    ["Nunziatura apostolica", "1989-12", "1990-01", 8.9795, -79.5215, "Noriega vi si rifugia il 24 dicembre e si arrende il 3 gennaio 1990."],
]


def main(folder, atlas, territories, dst):
    load = lambda r: [thin(x) for x in json.load(open(os.path.join(folder, f"{r}.json"), encoding="utf8"))["rings"]]
    text = open(territories, encoding="utf8").read()
    old = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("pz") and x["n"] != "Zona del Canale di Panama"]
    add = [
        {"n": "Zona del Canale di Panama", "from": "1945-01", "to": "1979-09", "look": "st-U", "rings": load(2873302),
         "d": "Sotto giurisdizione USA dal 1903. Cessa il 1° ottobre 1979 con i trattati Torrijos-Carter; il canale passa a Panama nel 1999. Contorno 1935-1979 da OpenHistoricalMap."},
        {"n": "Ungheria, confini del 1940", "from": "1945-01", "to": "1945-04", "code": 310, "rings": load(2747817),
         "d": "Dopo il secondo arbitrato di Vienna (agosto 1940): con la Transilvania del nord, la Slovacchia meridionale e la Rutenia subcarpatica. Senza la Bačka, annessa nel 1941. Contorno da OpenHistoricalMap."},
        {"n": "Invasione USA di Panama", "from": "1989-12", "to": "1990-01", "look": "t-usocc", "rings": atlas_rings(atlas, "Panama"),
         "d": "Operazione Just Cause, dal 20 dicembre 1989: circa 27.000 soldati USA rovesciano Noriega, che si arrende il 3 gennaio 1990. Le operazioni di combattimento finiscono il 31 gennaio."},
    ]
    for x in add:
        x["pz"] = 1
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(old + add, separators=(",", ":"), ensure_ascii=False) + ";\n")
    with open(dst, "w", encoding="utf8") as h:
        h.write("/* Operazione Just Cause: luoghi e date a memoria, posizioni approssimate. */\nwindow.BATTLES.push(..." + json.dumps(BATTLES, ensure_ascii=False) + ");\n")
    for x in add:
        print(x["n"], len(x["rings"]), "anelli", sum(map(len, x["rings"])), "punti")


if __name__ == "__main__":
    main(*sys.argv[1:5])
