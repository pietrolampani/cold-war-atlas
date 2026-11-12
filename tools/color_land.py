"""Assegna a ogni pezzo di terra dei tasselli lo Stato prevalente nel 1975 o, se scoperto, il più vicino.

Aggiunge a ogni tassello "col": {codice: [indici dei pezzi]}. La pagina li colora sotto gli Stati, così non resta terra neutra.
Antartide e Caspio restano fuori. OVERRIDE corregge le isole lontane, dove lo Stato più vicino non è quello giusto.

Uso: python -I tools/color_land.py borders-hi.js cartella_land report.txt
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

CELL = 0.05
SCALE = 1e4
YEAR = 1975 * 12 + 5
# lon min, lon max, lat min, lat max, codice
OVERRIDE = [(-39, -34, -56, -53, 200), (68, 71, -50, -48, 220), (50, 53, -47, -45, 220), (76, 78.5, -39, -37, 220), (10, 35, 74, 81, 385), (72, 74.5, -54, -52.5, 900), (37, 38.5, -47.5, -46, 560),
            (-180, -170, 51, 53, 2), (172, 180, 51, 54, 2), (-10, -7, 70.5, 71.5, 385), (3, 4, -55, -54, 385), (-160, -150, -25, -5, 220), (-180, -176, -32, -29, 920)]
NOT_LAND = [(45, 56, 36, 48)]  # Il Caspio risulta terra nei poligoni OSM


def fill(rings):
    rows = defaultdict(list)
    for r in rings:
        for a, b in zip(r, r[1:] + r[:1]):
            y0, y1 = a[1], b[1]
            if y0 == y1:
                continue
            lo, hi = sorted((y0, y1))
            for iy in range(math.ceil(lo / CELL - .5), math.ceil(hi / CELL - .5)):
                y = (iy + .5) * CELL
                rows[iy].append(a[0] + (y - y0) * (b[0] - a[0]) / (y1 - y0))
    out = {}
    for iy, xs in rows.items():
        xs.sort()
        out[iy] = [(math.ceil(xs[i] / CELL - .5), math.ceil(xs[i + 1] / CELL - .5)) for i in range(0, len(xs) - 1, 2)]
    return out


def states(path):
    t = json.loads(open(path, encoding="utf8").read().split("=", 1)[1].rstrip().rstrip(";"))
    sx, sy = t["transform"]["scale"]; tx, ty = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0; pts = []
        for dx, dy in a:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    out = []
    for g in t["objects"]["states"]["geometries"]:
        p = g["properties"]
        if p["s"] <= YEAR <= p["e"]:
            rings = []
            for poly in (g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]):
                for ring in poly:
                    r = []
                    for i in ring:
                        r += arcs[i] if i >= 0 else arcs[~i][::-1]
                    rings.append(r)
            out.append((p["c"], rings))
    return out


def decode(a):
    x = y = 0; pts = []
    for i in range(0, len(a), 2):
        x += a[i]; y += a[i + 1]
        pts.append((x / SCALE, y / SCALE))
    return pts


def main(borders, folder, report):
    index = defaultdict(list)
    near = defaultdict(list)
    for code, rings in states(borders):
        for iy, spans in fill(rings).items():
            index[iy] += [(s, e, code) for s, e in spans]
        for r in rings:
            for x, y in r:
                near[int(x // 2), int(y // 2)].append((x, y, code))

    def nearest(p):
        for reach in range(1, 40):
            best, bd = None, 1e9
            cx, cy = int(p[0] // 2), int(p[1] // 2)
            for gx in range(cx - reach, cx + reach + 1):
                for gy in range(cy - reach, cy + reach + 1):
                    for x, y, code in near.get((gx, gy), ()):
                        d = math.hypot((x - p[0]) * math.cos(math.radians(p[1])), y - p[1])
                        if d < bd:
                            best, bd = code, d
            if best is not None:
                return best, bd * 111.32
        return None, 1e9

    log = []
    counts = Counter()
    for f in sorted(os.listdir(folder)):
        path = os.path.join(folder, f)
        text = open(path, encoding="utf8").read()
        head, t = text[:text.index("{")], json.loads(text[text.index("{"): text.rindex("}") + 1])
        col = {}

        def caspian(a):
            r = decode(a)
            lon, lat = sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r)
            return any(w <= lon <= e and s <= lat <= n for w, e, s, n in NOT_LAND) and sum(e0 - s0 for spans in fill([r]).values() for s0, e0 in spans) * (CELL * 111.32) ** 2 > 40000 and not votes_of(r)

        def votes_of(r):
            return sum(min(e0, b0) - max(s0, a0) > 0 for iy, spans in fill([r]).items() for s0, e0 in spans for a0, b0, _ in index.get(iy, ())) > 200

        kept = [a for a in t["land"] if not caspian(a)]
        counts["caspio"] += len(t["land"]) - len(kept)
        t["land"] = kept  # Il Caspio diventa mare: senza il pezzo, la maschera del mare lo copre
        for i, a in enumerate(t["land"]):
            r = decode(a)
            lon, lat = sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r)
            if lat < -60:
                counts["antartide"] += 1
                continue
            cells = fill([r])
            over = next((c for w, e, s, n, c in OVERRIDE if w <= lon <= e and s <= lat <= n), None)
            votes = Counter()
            for iy, spans in cells.items():
                for s, e in spans:
                    for a0, b0, code in index.get(iy, ()):
                        n = min(e, b0) - max(s, a0)
                        if n > 0:
                            votes[code] += n
            if over is not None:
                code, how = over, "a mano"
            elif votes:
                code, how = votes.most_common(1)[0][0], "prevalente"
            else:
                code, km = nearest((lon, lat))
                how = "vicino"
                if km > 300:
                    log.append(f"{f}\t{lat:.2f}\t{lon:.2f}\t{code}\t{km:.0f} km")
            counts[how] += 1
            col.setdefault(str(code), []).append(i)
        t["col"] = col
        with open(path, "w", encoding="utf8") as h:
            h.write(head + json.dumps(t, separators=(",", ":")) + ");\n")
    with open(report, "w", encoding="utf8") as h:
        h.write("\n".join(log))
    print(dict(counts), "lontani", len(log))
    print("\n".join(log[:40]))


if __name__ == "__main__":
    main(*sys.argv[1:4])
