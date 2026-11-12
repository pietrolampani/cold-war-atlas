"""Linee del fronte 1945 dalle tavole dell'Army Map Service, senza i tratti lungo la costa.

Il fronte è il bordo dell'area dell'Asse così come si vede sulla carta. Se ne tengono solo i punti
dentro la zona in cui l'Asse può stare (TERR_CLIPS axisPossible / japanHeld) e ad almeno COAST_KM dalla costa OSM
(bordi dei pezzi di terra nei tasselli land/, esclusi i lati dei tasselli); restano i tratti lunghi almeno MIN_KM,
semplificati. Agosto 1945 nel Pacifico è scritto a mano a parte e non ha linea.

Uso: python -I tools/build_ww2_fronts.py territories.js cartella_tavole ww2atlas.js ww2pacific.js cartella_land fronts45.js
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_ww2_atlas import fronts, inside, km  # noqa: E402
from fetch_ohm import area_km2  # noqa: E402

COAST_KM = 10
TOUCH = 30
MIN_KM = 25
SRC = "Atlas of the World Battle Fronts in Semimonthly Phases, Army Map Service 1945 (pubblico dominio); tavola del 15 del mese"


def clips_of(path):
    t = open(path, encoding="utf8").read()
    m = re.search(r"window\.TERR_CLIPS = Object\.assign\(window\.TERR_CLIPS \|\| \{\}, (\{.*?\})\);\n", t, re.S)
    return json.loads(m.group(1))


def coast_grid(land_dir, box):
    grid = {}
    for f in os.listdir(land_dir):
        mm = re.fullmatch(r"(-?\d+)_(-?\d+)\.js", f)
        if not mm:
            continue
        kx, ky = int(mm.group(1)), int(mm.group(2))
        lon0, lat0 = kx * 15 - 180, ky * 15 - 90
        if lon0 + 15 < box[0] or lon0 > box[2] or lat0 + 15 < box[1] or lat0 > box[3]:
            continue
        src = open(os.path.join(land_dir, f), encoding="utf8").read()
        t = json.loads(src[src.index("{", src.index("LAND_TILE")):src.rindex("}") + 1])
        pieces = t["land"] + [a for l in t.get("isl", {}).values() for a in l]
        for a in pieces:
            pts, x, y = [], 0, 0
            for i in range(0, len(a), 2):
                x += a[i]; y += a[i + 1]
                pts.append((x / 1e4, y / 1e4))
            for p, q in zip(pts, pts[1:] + pts[:1]):
                edge = lambda v, o: abs(v - o) < 1e-3 or abs(v - o - 15) < 1e-3
                if (edge(p[0], lon0) and edge(q[0], lon0)) or (edge(p[1], lat0) and edge(q[1], lat0)):
                    continue  # lato del tassello, non costa
                n = max(1, int(km(p, q) / 2))
                for i in range(n + 1):
                    c = (p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n)
                    grid.setdefault((int(c[0] * 5), int(c[1] * 5)), []).append(c)
    return grid


def simplify(pts, tol=0.015):
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    st = [(0, len(pts) - 1)]
    while st:
        a, b = st.pop()
        (x0, y0), (x1, y1) = pts[a], pts[b]
        L = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** .5 or 1e-12
        best, bd = -1, 0
        for i in range(a + 1, b):
            d = abs((x1 - x0) * (y0 - pts[i][1]) - (x0 - pts[i][0]) * (y1 - y0)) / L
            if d > bd:
                best, bd = i, d
        if bd > tol:
            keep[best] = True; st += [(a, best), (best, b)]
    return [p for p, k in zip(pts, keep) if k]


def main(territories, frames, atlas_js, pacific_js, land_dir, dst):
    terr = json.loads(open(territories, encoding="utf8").read().split("=", 1)[1].rstrip().rstrip(";"))
    regions = {"Ger": ("Fronte europeo", clips_of(atlas_js)["axisPossible"], (-15, 30, 45, 72)),
               "Jap": ("Fronte del Pacifico", clips_of(pacific_js)["japanHeld"], (70, -12, 160, 56))}
    out = []
    for key, (name, possible, box) in regions.items():
        grid = coast_grid(land_dir, box)
        print(name, "punti di costa", sum(map(len, grid.values())), flush=True)

        def ok(p):
            cx, cy = int(p[0] * 5), int(p[1] * 5)
            if any(km(p, q) < COAST_KM for gx in range(cx - 1, cx + 2) for gy in range(cy - 1, cy + 2) for q in grid.get((gx, gy), ())):
                return False
            return inside(p, possible)

        names = {"Ger": "Tenuto dall'Asse", "Jap": "Tenuto dal Giappone"}
        for x in terr:
            if x["n"] != names[key] or x["from"] >= "1945-08":
                continue
            month = x["from"]
            n = 0
            # Solo dove l'Asse confina con un'area alleata vera (almeno 2500 km2): niente fronti attorno alle chiazze della carta
            allied = [r for r in json.load(open(os.path.join(frames, f"{month}-15{key}.json"), encoding="utf8"))["allied"] if area_km2(r) >= 2500]
            near = {}
            for r in allied:
                for a, b in zip(r, r[1:] + r[:1]):
                    m = max(1, int(km(a, b) / 3))
                    for i in range(m + 1):
                        c = (a[0] + (b[0] - a[0]) * i / m, a[1] + (b[1] - a[1]) * i / m)
                        near.setdefault((int(c[0] * 5), int(c[1] * 5)), []).append(c)
            touch = lambda p: any(km(p, q) <= TOUCH for gx in range(int(p[0] * 5) - 1, int(p[0] * 5) + 2) for gy in range(int(p[1] * 5) - 1, int(p[1] * 5) + 2) for q in near.get((gx, gy), ()))
            # Il fronte è il bordo stesso dell'area dell'Asse (quello che si vede), dove corre nell'interno della zona possibile
            for r0 in x["rings"]:
                r = []  # bordo infittito ogni 2 km: i tratti lunghi tra due vertici non spezzano il fronte
                for a, b in zip(r0, r0[1:] + r0[:1]):
                    m = max(1, int(km(a, b) / 2))
                    r += [[a[0] + (b[0] - a[0]) * i / m, a[1] + (b[1] - a[1]) * i / m] for i in range(m)]
                flags = [ok(p) and touch(p) for p in r]
                if all(flags) or not any(flags):
                    continue
                flags_of = {id(p): g for p, g in zip(r, flags)}
                s = flags.index(False)  # si parte da un punto escluso, così un tratto non resta spezzato in due
                l = r[s:] + r[:s] + [r[s]]
                run = []
                for p in l + [None]:
                    if p is not None and flags_of.get(id(p)):
                        run.append([round(p[0], 4), round(p[1], 4)])
                        continue
                    if len(run) >= 2 and sum(km(a, b) for a, b in zip(run, run[1:])) >= MIN_KM:
                        out.append({"n": name, "from": month, "to": month, "k": "front", "src": SRC, "p": simplify(run),
                                    "d": "Linea del fronte a metà mese secondo la tavola dell'Army Map Service; lungo le coste non è tracciata."})
                        n += 1
                    run = []
            print(month, name, n, "tratti", flush=True)
    # Agosto 1945: limite dell'avanzata sovietica a fine mese, il 38° parallelo e il confine sud-occidentale del Manciukuò
    aug = "Limite dell'avanzata sovietica a fine agosto 1945 (resa giapponese il 15, firmata il 2 settembre)."
    out.append({"n": "Fronte sovietico in Corea", "from": "1945-08", "to": "1945-08", "k": "front", "src": "Ricostruzione", "d": aug + " In Corea i sovietici si fermano al 38° parallelo.",
                "p": [[124.65, 38.0], [125.5, 38.0], [126.5, 38.0], [127.5, 38.0], [128.65, 38.0]]})
    grid = coast_grid(land_dir, (110, 35, 135, 55))
    man = next(x for x in terr if x["n"] == "Manciukuò")
    for r in man["rings"]:
        good = [p[1] < 43.7 and p[0] < 121.7 and not any(km(p, q) < COAST_KM for gx in range(int(p[0] * 5) - 1, int(p[0] * 5) + 2) for gy in range(int(p[1] * 5) - 1, int(p[1] * 5) + 2) for q in grid.get((gx, gy), ())) for p in r]
        if not any(good) or all(good):
            continue
        s = good.index(False)
        l, f = r[s:] + r[:s], good[s:] + good[:s]
        run = []
        for p, g in zip(l + [None], f + [False]):
            if g:
                run.append(p); continue
            if len(run) > 10:
                out.append({"n": "Fronte sovietico in Cina", "from": "1945-08", "to": "1945-08", "k": "front", "src": "Ricostruzione", "p": simplify(run),
                            "d": aug + " L'Armata Rossa occupa il Manciukuò fino al Rehe; oltre, la Cina occupata resta ai giapponesi fino alle rese di settembre."})
            run = []
    with open(dst, "w", encoding="utf8") as h:
        h.write("/* Fronti 1945 dalle tavole dell'Army Map Service, solo nell'interno (tools/build_ww2_fronts.py). */\n"
                f"window.LINES.push.apply(window.LINES, {json.dumps(out, ensure_ascii=False, separators=(',', ':'))});\n")
    print(len(out), "linee;", round(os.path.getsize(dst) / 1e3), "kB")


if __name__ == "__main__":
    main(*sys.argv[1:7])
