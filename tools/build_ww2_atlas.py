"""Territori e fronti europei del 1945 dalle tavole dell'Atlas of the World Battle Fronts (Army Map Service, pubblico dominio).

Legge i contorni ricavati nel browser da maps/trace.js (un JSON per tavola: Asse, Alleati, georeferenziazione) e:
- aggiunge a territories.js, per il mese della tavola, il territorio tenuto dall'Asse e quello tenuto dagli Alleati (voci "ww2a");
- scrive ww2atlas.js con i fronti: i tratti del contorno dell'Asse che toccano quello alleato, al posto dei fronti a mano.

Uso: python -I tools/build_ww2_atlas.py cartella_tavole territories.js ww2atlas.js atlas10.json ungheria_1940_ohm.json
"""
import json
import math
import os
import sys
from collections import defaultdict

TOUCH_KM = 5
REPLACED = ["Fronte orientale", "Fronte occidentale", "Linea Gotica", "Sacca di Curlandia", "Prussia Orientale"]
SRC = "Atlas of the World Battle Fronts in Semimonthly Phases, Army Map Service 1945 (pubblico dominio); tavola del 15 del mese, georeferenziata"


def km(a, b):
    return math.hypot((a[0] - b[0]) * math.cos(math.radians((a[1] + b[1]) / 2)), a[1] - b[1]) * 111.32


def fronts(axis, allied):
    grid = defaultdict(list)
    for r in allied:
        for a, b in zip(r, r[1:] + r[:1]):
            n = max(1, int(km(a, b) / 1))
            for i in range(n + 1):
                p = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
                grid[int(p[0] * 10), int(p[1] * 10)].append(p)

    def touch(p):
        cx, cy = int(p[0] * 10), int(p[1] * 10)
        return any(km(p, q) <= TOUCH_KM for gx in range(cx - 1, cx + 2) for gy in range(cy - 1, cy + 2) for q in grid.get((gx, gy), ()))

    lines = []
    for r in axis:
        flags = [touch(p) for p in r]
        if all(flags):
            lines.append(r + [r[0]])
            continue
        start = flags.index(False)  # Si parte da un punto lontano dal fronte, così un tratto non resta spezzato
        run = []
        for i in range(len(r) + 1):
            j = (start + i) % len(r)
            if flags[j]:
                run.append(r[j])
            else:
                if len(run) >= 3:
                    lines.append(run)
                run = []
        if len(run) >= 3:
            lines.append(run)
    return [l for l in lines if sum(km(a, b) for a, b in zip(l, l[1:])) > 15]


# Dove l'Asse può essere: fuori di qui un bianco della tavola è un errore di lettura (scritte, cornici, Irlanda)
AXIS_POSSIBLE = ["Germany", "Austria", "Poland", "Czechia", "Slovakia", "Netherlands", "Slovenia", "Croatia", "Bosnia and Herz.", "Serbia", "Montenegro", "Kosovo",
                 "Luxembourg", "Italy", "Denmark", "Norway", "Latvia", "Lithuania", "Greece", "Albania", "Macedonia", "Hungary", "Belgium", "France"]
AXIS_CORE = ["Germany", "Austria", "Slovakia", "Croatia", "Bosnia and Herz.", "Italy"]
# Fino al 25 aprile (Torgau) le zone angloamericana e sovietica sono separate: ogni anello alleato va per intero a una delle due
EAST_FROM_LON = 14


def halfplane(ring, lon, west):
    """Sutherland-Hodgman su un semipiano di longitudine: basta per un clipPath."""
    keep = (lambda p: p[0] <= lon) if west else (lambda p: p[0] >= lon)
    out = []
    for a, b in zip(ring, ring[1:] + ring[:1]):
        if keep(a):
            out.append(a)
        if keep(a) != keep(b):
            t = (lon - a[0]) / (b[0] - a[0])
            out.append([lon, a[1] + t * (b[1] - a[1])])
    return out


BOXES = {}


def inside(p, rings):
    x, y = p
    c = False
    for r in rings:
        b = BOXES.get(id(r)) or BOXES.setdefault(id(r), (min(q[0] for q in r), min(q[1] for q in r), max(q[0] for q in r), max(q[1] for q in r)))
        if not (b[0] <= x <= b[2] and b[1] <= y <= b[3]):
            continue
        for (ax, ay), (bx, by) in zip(r, r[1:] + r[:1]):
            if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
                c = not c
    return c


def atlas_rings(path, names, extra_box=None):
    """Anelli esterni dei Paesi di Natural Earth; extra_box prende i pezzi della Russia in quel riquadro (Kaliningrad)."""
    t = json.load(open(path, encoding="utf8"))
    sx, sy = t["transform"]["scale"]; tx, ty = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0; p = []
        for dx, dy in a:
            x += dx; y += dy
            p.append([round(x * sx + tx, 4), round(y * sy + ty, 4)])
        arcs.append(p)
    out = []
    for g in t["objects"]["countries"]["geometries"]:
        name = g["properties"]["name"]
        for poly in ([g["arcs"]] if g["type"] == "Polygon" else g["arcs"]):
            r = []
            for a in poly[0]:
                r += arcs[a] if a >= 0 else arcs[~a][::-1]
            if name in names or (extra_box and name == "Russia" and all(extra_box[0] <= p[0] <= extra_box[2] and extra_box[1] <= p[1] <= extra_box[3] for p in r)):
                out.append(r)
    return out


def main(folder, territories, dst, atlas, hungary):
    hun = json.load(open(hungary, encoding="utf8"))["rings"]
    kalin = atlas_rings(atlas, [], (19, 54, 23, 55.5))
    possible = atlas_rings(atlas, AXIS_POSSIBLE) + kalin + hun
    # Tinta uniforme per i Paesi dell'Asse, righe di occupazione per quelli occupati, come per gli Stati interi
    clips = {"axisPossible": possible,
             "axisCore": atlas_rings(atlas, AXIS_CORE) + kalin,
             "axisOccupied": atlas_rings(atlas, [n for n in AXIS_POSSIBLE if n not in AXIS_CORE and n != "Hungary"]) + hun}  # Ungheria occupata dai tedeschi dal marzo 1944
    clips = {k: [r for r in v if len(r) >= 3] for k, v in clips.items()}  # Il taglio sul meridiano può lasciare anelli vuoti
    text = open(territories, encoding="utf8").read()
    terr = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("ww2a")]
    for x in terr:  # Con i territori colorati, dell'Ungheria del 1940 resta il confine
        if x["n"] == "Ungheria, confini del 1940":
            x.pop("code", None)
            x["look"] = "t-line"
    add, lines, months = [], [], []
    for f in sorted(os.listdir(folder)):
        if not f.endswith("Ger.json"):
            continue
        t = json.load(open(os.path.join(folder, f), encoding="utf8"))
        month = t["name"][:7]
        months.append(month)
        day = t["name"][8:10]
        note = f"Situazione al {int(day)} del mese secondo la tavola dell'Army Map Service del 1945. Georeferenziata su {t['n']} città, errore medio {t['rms'] * 1.2:.0f} km."
        add.append({"n": "Tenuto dall'Asse", "from": month, "to": month, "look": "st-X t-fill", "rings": t["axis"], "ww2a": 1, "clipKey": "axisCore", "d": note})
        add.append({"n": "Occupato dall'Asse", "from": month, "to": month, "look": "st-O t-fill", "rings": t["axis"], "ww2a": 1, "clipKey": "axisOccupied", "d": note})
        east = [r for r in t["allied"] if sum(p[0] for p in r) / len(r) >= EAST_FROM_LON]
        west = [r for r in t["allied"] if sum(p[0] for p in r) / len(r) < EAST_FROM_LON]
        add.append({"n": "Occupazione sovietica", "from": month, "to": month, "look": "st-s t-fill", "rings": east, "ww2a": 1, "clipKey": "axisPossible", "d": note})
        add.append({"n": "Occupazione angloamericana", "from": month, "to": month, "look": "st-A t-fill", "rings": west, "ww2a": 1, "clipKey": "axisPossible", "d": note})
        for l in fronts(t["axis"], t["allied"]):
            # Solo i tratti dentro i Paesi dove poteva esserci l'Asse: i falsi bianchi nel Regno Unito non danno fronti
            run = []
            for p in l + [None]:
                if p is not None and inside(p, possible):
                    run.append(p)
                    continue
                if len(run) >= 3 and sum(km(a, b) for a, b in zip(run, run[1:])) > 15:
                    lines.append({"n": "Fronte europeo", "from": month, "to": month, "k": "front", "src": SRC, "d": note, "p": run})
                run = []
        print(month, "Asse", len(t["axis"]), "anelli", sum(map(len, t["axis"])), "punti; Alleati", len(t["allied"]), "; fronti", sum(1 for l in lines if l["from"] == month))
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr + add, separators=(",", ":"), ensure_ascii=False) + ";\n")
    js = ("/* Fronti europei 1945 dalle tavole dell'Army Map Service: sostituiscono quelli a mano nei mesi coperti. */\n"
          f"window.TERR_CLIPS = Object.assign(window.TERR_CLIPS || {{}}, {json.dumps(clips, separators=(',', ':'))});\n"
          f"(function () {{ var M = {json.dumps(months)}, R = {json.dumps(REPLACED, ensure_ascii=False)};\n"
          "  window.LINES = window.LINES.filter(function (l) { return !(R.indexOf(l.n) >= 0 && M.indexOf(l.from) >= 0); });\n"
          "})();\n")  # il fronte è il bordo dei riempimenti: le linee ricavate dalle tavole erano rumorose e non si scrivono
    with open(dst, "w", encoding="utf8") as h:
        h.write(js)


if __name__ == "__main__":
    main(*sys.argv[1:6])
