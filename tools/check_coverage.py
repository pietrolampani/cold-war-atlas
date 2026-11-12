"""Cerca la terra OSM non coperta dagli Stati: griglia da 0.02 gradi, solo nelle zone indicate dai tasselli.

Per ogni tassello rasterizza terra e Stati del mese scelto, allarga gli Stati di MARGIN gradi (l'alone) e riporta i pezzi scoperti.

Uso: python -I tools/check_coverage.py borders-hi.js cartella_land anno report.txt
"""
import json
import math
import os
import sys
from collections import defaultdict

CELL = 0.02
MARGIN = 0.0  # calcolato sopra: l'alone si aggiunge a parte
SCALE = 1e4


def fill(rings, grid):
    """Pari-dispari su righe, una riga di griglia alla volta."""
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
    for iy, xs in rows.items():
        xs.sort()
        s = grid.setdefault(iy, [])
        for i in range(0, len(xs) - 1, 2):
            s.append((math.ceil(xs[i] / CELL - .5), math.ceil(xs[i + 1] / CELL - .5)))


def states(path, year):
    t = json.loads(open(path, encoding="utf8").read().split("=", 1)[1].rstrip().rstrip(";"))
    sx, sy = t["transform"]["scale"]; tx, ty = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0; pts = []
        for dx, dy in a:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    m = year * 12 + 5
    out = []
    for g in t["objects"]["states"]["geometries"]:
        p = g["properties"]
        if p["s"] <= m <= p["e"]:
            polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
            rings = []
            for poly in polys:
                for ring in poly:
                    r = []
                    for i in ring:
                        r += arcs[i] if i >= 0 else arcs[~i][::-1]
                    rings.append(r)
            out.append(rings)
    return out


def decode(a):
    x = y = 0; pts = []
    for i in range(0, len(a), 2):
        x += a[i]; y += a[i + 1]
        pts.append((x / SCALE, y / SCALE))
    return pts


def main(borders, folder, year, report):
    covered = defaultdict(list)
    for rings in states(borders, int(year)):
        grid = {}
        fill(rings, grid)
        for iy, spans in grid.items():
            covered[iy] += spans
    merged = {}
    for iy, spans in covered.items():
        spans.sort()
        m = []
        for a, b in spans:
            if m and a <= m[-1][1]:
                m[-1][1] = max(m[-1][1], b)
            else:
                m.append([a, b])
        merged[iy] = m
    pieces = []
    for f in sorted(os.listdir(folder)):
        text = open(os.path.join(folder, f), encoding="utf8").read()
        t = json.loads(text[text.index("{"): text.rindex("}") + 1])
        for a in t["land"]:
            r = decode(a)
            grid = {}
            fill([r], grid)
            total = out = 0
            sumx = sumy = 0
            for iy, spans in grid.items():
                cov = merged.get(iy, [])
                for s, e in spans:
                    total += e - s
                    for c0, c1 in cov:
                        if c1 <= s or c0 >= e:
                            continue
                        total += 0
                    un = e - s
                    for c0, c1 in cov:
                        un -= max(0, min(e, c1) - max(s, c0))
                    if un > 0:
                        out += un
                        sumx += un * (s + e) / 2 * CELL
                        sumy += un * (iy + .5) * CELL
            if out:
                k = math.cos(math.radians(sumy / out))
                pieces.append((round(out * (CELL * 111.32) ** 2 * k), round(total * (CELL * 111.32) ** 2 * k), round(sumy / out, 2), round(sumx / out, 2), f[:-3], a))
    pieces.sort(key=lambda p: -p[0])
    with open(report, "w", encoding="utf8") as h:
        h.write("km2 scoperti\tkm2 totali\tlat\tlon\ttassello\n")
        for p in pieces:
            h.write("\t".join(map(str, p[:5])) + "\n")
    print("pezzi con terra scoperta", len(pieces), "km2 scoperti", sum(p[0] for p in pieces))
    whole = [p for p in pieces if p[0] >= .5 * max(p[1], 1)]
    print("pezzi scoperti per più di metà", len(whole), "km2", sum(p[0] for p in whole))
    for p in whole[:25]:
        print(p[:5])


if __name__ == "__main__":
    main(*sys.argv[1:5])
