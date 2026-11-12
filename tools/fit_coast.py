"""Georeferenzia una carta senza città adattando i punti della sua costa alla costa di Natural Earth.

Modello: x = a·lon + b, y = c·g(lat) + d, con g lineare o di Mercatore; minimizza la media troncata delle distanze
(si scarta il 20% peggiore: laghi, cornici, isole mancanti). Ricerca a griglia e poi Nelder-Mead.

Uso: python -I tools/fit_coast.py atlas10.json punti_costa_px.json lon0 lon1 lat0 lat1 a b c d
Stampa i parametri migliori per i due modelli e l'errore in pixel.
"""
import json
import math
import sys


def coast(path, box):
    t = json.load(open(path, encoding="utf8"))
    sx, sy = t["transform"]["scale"]; tx, ty = t["transform"]["translate"]
    out = []
    for a in t["arcs"]:
        x = y = 0
        prev = None
        for dx, dy in a:
            x += dx; y += dy
            p = (x * sx + tx, y * sy + ty)
            if box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3]:
                if prev:
                    n = max(1, int(math.hypot(p[0] - prev[0], p[1] - prev[1]) / .03))
                    for i in range(1, n + 1):
                        out.append((prev[0] + (p[0] - prev[0]) * i / n, prev[1] + (p[1] - prev[1]) * i / n))
                else:
                    out.append(p)
                prev = p
            else:
                prev = None
    return out


def merc(lat):
    return math.degrees(math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))


def score(params, pts, ref, g):
    a, b, c, d = params
    proj = [(a * lon + b, c * g(lat) + d) for lon, lat in ref]
    grid = {}
    for p in proj:
        grid.setdefault((int(p[0] // 20), int(p[1] // 20)), []).append(p)
    ds = []
    for x, y in pts:
        best = 60
        for gx in range(int(x // 20) - 2, int(x // 20) + 3):
            for gy in range(int(y // 20) - 2, int(y // 20) + 3):
                for q in grid.get((gx, gy), ()):
                    best = min(best, math.hypot(q[0] - x, q[1] - y))
        ds.append(best)
    ds.sort()
    keep = ds[: int(len(ds) * .8)]
    return sum(keep) / len(keep)


def nelder(f, x0, steps, iters=400):
    pts = [list(x0)] + [[v + (steps[i] if i == j else 0) for j, v in enumerate(x0)] for i in range(len(x0))]
    vals = [f(p) for p in pts]
    for _ in range(iters):
        order = sorted(range(len(pts)), key=lambda i: vals[i])
        pts = [pts[i] for i in order]; vals = [vals[i] for i in order]
        cen = [sum(p[k] for p in pts[:-1]) / (len(pts) - 1) for k in range(len(x0))]
        refl = [cen[k] + (cen[k] - pts[-1][k]) for k in range(len(x0))]
        fr = f(refl)
        if fr < vals[0]:
            exp = [cen[k] + 2 * (cen[k] - pts[-1][k]) for k in range(len(x0))]
            fe = f(exp)
            pts[-1], vals[-1] = (exp, fe) if fe < fr else (refl, fr)
        elif fr < vals[-2]:
            pts[-1], vals[-1] = refl, fr
        else:
            con = [cen[k] + .5 * (pts[-1][k] - cen[k]) for k in range(len(x0))]
            fc = f(con)
            if fc < vals[-1]:
                pts[-1], vals[-1] = con, fc
            else:
                pts = [pts[0]] + [[pts[0][k] + .5 * (p[k] - pts[0][k]) for k in range(len(x0))] for p in pts[1:]]
                vals = [vals[0]] + [f(p) for p in pts[1:]]
    i = min(range(len(pts)), key=lambda i: vals[i])
    return pts[i], vals[i]


def main(atlas, pts_path, lon0, lon1, lat0, lat1, a, b, c, d):
    pts = [p for p in json.load(open(pts_path)) if p[0] > 12]
    ref = coast(atlas, (float(lon0), float(lon1), float(lat0), float(lat1)))
    print(len(pts), "punti della carta,", len(ref), "punti di costa")
    for name, g in (("lineare", lambda v: v), ("Mercatore", merc)):
        x0 = [float(a), float(b), float(c), float(d)]
        if name == "Mercatore":  # Stesso intervallo verticale tra 8,6 e 21,5 gradi
            k = (21.53 - 8.6) / (merc(21.53) - merc(8.6))
            x0 = [x0[0], x0[1], x0[2] * k, x0[3] + x0[2] * (8.6 - k * merc(8.6))]
        best, val = nelder(lambda p: score(p, pts, ref, g), x0, [4, 400, 4, 60])
        best, val = nelder(lambda p: score(p, pts, ref, g), best, [1, 100, 1, 15])
        print(name, [round(v, 4) for v in best], "errore medio", round(val, 2), "px")


if __name__ == "__main__":
    main(*sys.argv[1:11])
