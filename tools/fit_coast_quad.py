"""Affina la georeferenziazione di una carta con un polinomio quadratico (pixel -> lon, lat), alla maniera ICP:
parte dal modello di Mercatore di fit_coast.py, abbina ogni punto di costa della carta al punto più vicino della costa
di Natural Earth, scarta il 25% peggiore e rifà i minimi quadrati, finché converge.

Uso: python -I tools/fit_coast_quad.py atlas10.json punti_costa_px.json lon0 lon1 lat0 lat1 a b c d
(a b c d: modello di Mercatore x = a·lon + b, y = c·merc(lat) + d). Stampa i 12 coefficienti e l'errore in km.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fit_coast import coast  # noqa: E402


def terms(x, y):
    x = (x - 960) / 1000; y = (y - 540) / 1000
    return [1, x, y, x * x, x * y, y * y]


def apply(cf, x, y):
    return sum(c * t for c, t in zip(cf, terms(x, y)))


def lstsq(rows, vals):
    n = len(rows[0])
    M = [[sum(r[i] * r[j] for r in rows) for j in range(n)] + [sum(r[i] * v for r, v in zip(rows, vals))] for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda k: abs(M[k][i])); M[i], M[p] = M[p], M[i]
        for k in range(n):
            if k != i:
                f = M[k][i] / M[i][i]
                M[k] = [a - f * b for a, b in zip(M[k], M[i])]
    return [M[i][n] / M[i][i] for i in range(n)]


def main(atlas, pts_path, lon0, lon1, lat0, lat1, a, b, c, d, ctrl_path=None):
    box = [float(lon0), float(lon1), float(lat0), float(lat1)]
    a, b, c, d = map(float, (a, b, c, d))
    ref = coast(atlas, box)
    px = json.load(open(pts_path))
    rows = [terms(x, y) for x, y in px]
    lon = [(x - b) / a for x, y in px]
    lat = [math.degrees(2 * math.atan(math.exp(math.radians((y - d) / c))) - math.pi / 2) for x, y in px]
    ctrl = json.load(open(ctrl_path)) if ctrl_path else []
    crow = [terms(p[0], p[1]) for p in ctrl] * 15
    clon = [p[2] for p in ctrl] * 15; clat = [p[3] for p in ctrl] * 15
    if ctrl:
        cl = lstsq(crow, clon); ct = lstsq(crow, clat)
        print("solo punti di controllo:", [round(math.hypot((apply(cl, p[0], p[1]) - p[2]) * math.cos(math.radians(p[3])), apply(ct, p[0], p[1]) - p[3]) * 111) for p in ctrl], "km")
    else:
        cl = lstsq(rows, lon); ct = lstsq(rows, lat)
    cell = 0.5
    grid = {}
    for u, v in ref:
        grid.setdefault((int(u // cell), int(v // cell)), []).append((u, v))
    for it in range(20):
        res = []
        for (x, y), r in zip(px, rows):
            u = sum(p * q for p, q in zip(cl, r)); v = sum(p * q for p, q in zip(ct, r))
            gx, gy = int(u // cell), int(v // cell)
            best, bq = 1e9, None
            k = math.cos(math.radians(v))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for q in grid.get((gx + dx, gy + dy), []):
                        dd = ((q[0] - u) * k) ** 2 + (q[1] - v) ** 2
                        if dd < best:
                            best, bq = dd, q
            res.append((math.sqrt(best), r, bq))
        ds = sorted(e[0] for e in res)
        lim = ds[int(len(ds) * 0.75)]
        keep = [e for e in res if e[0] <= lim and e[2]]
        cl = lstsq([e[1] for e in keep] + crow, [e[2][0] for e in keep] + clon)
        ct = lstsq([e[1] for e in keep] + crow, [e[2][1] for e in keep] + clat)
        km = [e[0] * 111 for e in keep]
        print(f"iter {it}: media {sum(km) / len(km):.1f} km (75% migliori), mediana di tutti {ds[len(ds) // 2] * 111:.1f} km")
    print("controllo:", [round(math.hypot((apply(cl, p[0], p[1]) - p[2]) * math.cos(math.radians(p[3])), apply(ct, p[0], p[1]) - p[3]) * 111) for p in ctrl], "km")
    print("LON", [round(v, 6) for v in cl])
    print("LAT", [round(v, 6) for v in ct])


if __name__ == "__main__":
    main(*sys.argv[1:12])
