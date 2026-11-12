"""Stima la proiezione conica di una carta da punti di controllo (pixel e lon/lat noti).

Prova conica equidistante, conforme di Lambert e equivalente di Albers: per ogni coppia di paralleli standard
proietta i punti e trova la trasformazione di similitudine (scala, rotazione, traslazione) ai pixel ai minimi quadrati.
Opzionalmente affina con i punti di costa (ICP) come fit_coast_quad.py.

Uso: python -I tools/fit_conic.py controllo.json [atlas10.json punti_costa_px.json lon0 lon1 lat0 lat1]
Stampa il modello migliore: tipo, meridiano centrale, paralleli standard, similitudine, errore in pixel e km.
"""
import json
import math
import os
import sys


def proj(kind, lon0, p1, p2):
    f1, f2 = math.radians(p1), math.radians(p2)
    if kind == "eqd":
        n = (math.cos(f1) - math.cos(f2)) / (f2 - f1) if p1 != p2 else math.sin(f1)
        G = math.cos(f1) / n + f1
        return lambda lon, lat: _xy(n, G - math.radians(lat), lon, lon0)
    if kind == "lcc":
        t = lambda f: math.tan(math.pi / 4 + f / 2)
        n = math.log(math.cos(f1) / math.cos(f2)) / math.log(t(f2) / t(f1)) if p1 != p2 else math.sin(f1)
        F = math.cos(f1) * t(f1) ** n / n
        return lambda lon, lat: _xy(n, F / t(math.radians(lat)) ** n, lon, lon0)
    n = (math.sin(f1) + math.sin(f2)) / 2
    C = math.cos(f1) ** 2 + 2 * n * math.sin(f1)
    return lambda lon, lat: _xy(n, math.sqrt(max(C - 2 * n * math.sin(math.radians(lat)), 0)) / n, lon, lon0)


def _xy(n, rho, lon, lon0):
    th = n * math.radians(lon - lon0)
    return rho * math.sin(th), -rho * math.cos(th)


def similarity(src, dst):
    """dst ≈ s·R·src + t: minimi quadrati con u = a·X − b·Y + tx, v = b·X + a·Y + ty."""
    n = len(src)
    mx = sum(p[0] for p in src) / n; my = sum(p[1] for p in src) / n
    ux = sum(p[0] for p in dst) / n; uy = sum(p[1] for p in dst) / n
    sxx = sum((p[0] - mx) ** 2 + (p[1] - my) ** 2 for p in src)
    a = sum((p[0] - mx) * (q[0] - ux) + (p[1] - my) * (q[1] - uy) for p, q in zip(src, dst)) / sxx
    b = sum((p[0] - mx) * (q[1] - uy) - (p[1] - my) * (q[0] - ux) for p, q in zip(src, dst)) / sxx
    return a, b, ux - a * mx + b * my, uy - b * mx - a * my


def evaluate(ctrl, kind, lon0, p1, p2, yflip=True):
    P = proj(kind, lon0, p1, p2)
    src = [P(c[2], c[3]) for c in ctrl]
    src = [(x, -y) for x, y in src] if yflip else src  # i pixel crescono verso il basso
    dst = [(c[0], c[1]) for c in ctrl]
    a, b, tx, ty = similarity(src, dst)
    res = [math.hypot(a * x - b * y + tx - u, b * x + a * y + ty - v) for (x, y), (u, v) in zip(src, dst)]
    return sum(r * r for r in res) / len(res), (a, b, tx, ty), res


def main(ctrl_path):
    ctrl = json.load(open(ctrl_path))
    best = None
    for kind in ("eqd", "lcc", "alb"):
        for lon0 in range(95, 121):
            for p1 in range(15, 50, 2):
                for p2 in range(p1, 60, 2):
                    e, sim, res = evaluate(ctrl, kind, lon0, p1, p2)
                    if best is None or e < best[0]:
                        best = (e, kind, lon0, p1, p2, sim, res)
    e, kind, lon0, p1, p2, sim, res = best
    scale = math.hypot(sim[0], sim[1])  # pixel per radiante
    print("modello", kind, "lon0", lon0, "paralleli", p1, p2, "similitudine", [round(v, 4) for v in sim])
    print("residui px", [round(r, 1) for r in res], "-> km", [round(r / scale * 6371) for r in res])
    print(json.dumps({"kind": kind, "lon0": lon0, "p1": p1, "p2": p2, "sim": sim}))


if __name__ == "__main__":
    main(sys.argv[1])
