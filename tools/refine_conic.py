"""Affina la similitudine di una carta conica (fit_conic.py) con la costa: ICP sui punti di costa del mare aperto più i punti di controllo.

La proiezione (tipo, meridiano, paralleli) resta fissa; si ristimano scala, rotazione e traslazione abbinando ogni punto di costa
della carta al punto più vicino della costa di Natural Earth proiettata, scartando il 30% peggiore. I punti di controllo pesano 20 volte.

Uso: python -I tools/refine_conic.py atlas10.json costa_px.json controllo.json kind lon0 p1 p2 a b tx ty
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fit_coast import coast  # noqa: E402
from fit_conic import proj, similarity  # noqa: E402


def main(atlas, pts_path, ctrl_path, kind, lon0, p1, p2, a, b, tx, ty):
    P = proj(kind, float(lon0), float(p1), float(p2))
    sim = tuple(map(float, (a, b, tx, ty)))
    to_xy = lambda lon, lat: (lambda q: (q[0], -q[1]))(P(lon, lat))
    ref = [to_xy(*p) for p in coast(atlas, [70, 145, 5, 55])]
    px = json.load(open(pts_path))
    ctrl = json.load(open(ctrl_path))
    cxy = [to_xy(c[2], c[3]) for c in ctrl]
    for it in range(12):
        a, b, tx, ty = sim
        k = a * a + b * b
        inv = lambda u, v: ((a * (u - tx) + b * (v - ty)) / k, (-b * (u - tx) + a * (v - ty)) / k)
        cell = 0.004
        grid = {}
        for q in ref:
            grid.setdefault((int(q[0] / cell), int(q[1] / cell)), []).append(q)
        pairs = []
        for u, v in px:
            x, y = inv(u, v)
            gx, gy = int(x / cell), int(y / cell)
            best, bq = 1e9, None
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for q in grid.get((gx + dx, gy + dy), []):
                        d = (q[0] - x) ** 2 + (q[1] - y) ** 2
                        if d < best:
                            best, bq = d, q
            if bq:
                pairs.append((math.sqrt(best), bq, (u, v)))
        pairs.sort(key=lambda e: e[0])
        keep = pairs[:int(len(pairs) * 0.7)]
        src = [e[1] for e in keep] + cxy * 20
        dst = [e[2] for e in keep] + [(c[0], c[1]) for c in ctrl] * 20
        sim = similarity(src, dst)
        a, b, tx, ty = sim
        s = math.hypot(a, b)
        cres = [math.hypot(a * x - b * y + tx - c[0], b * x + a * y + ty - c[1]) for (x, y), c in zip(cxy, ctrl)]
        kres = [math.hypot(a * q[0] - b * q[1] + tx - p[0], b * q[0] + a * q[1] + ty - p[1]) for _, q, p in keep]
        print(f"iter {it}: costa {sum(kres) / len(kres):.2f} px, controllo {[round(r, 1) for r in cres]} px ({s:.0f} px/rad)")
    print(json.dumps(list(sim)))


if __name__ == "__main__":
    main(*sys.argv[1:12])
