"""Stima il contorno del lago d'Aral dal 1960 al 1991 e scrive aral.js.

Punti reali: il contorno storico e i bacini residui di Natural Earth, e le superfici pubblicate.
I contorni intermedi NON sono osservati: sono isolinee di un campo che va dalla riva del 1960 (0)
ai bacini residui (1), scelte in modo che l'area coincida con la superficie dell'anno.

Uso: python -I tools/build_aral.py ne_10m_lakes_historic.json ne_10m_lakes.json aral.js
"""
import json
import math
import sys

STEP = 0.015
LON0, LAT0, NX, NY = 58.0, 43.2, 270, 250
# Superficie in km²: 1960, 1971, 1976, 1989, 1992 da tabella pubblicata; 1987 è un valore indicativo
AREAS = [(1960, 68000), (1971, 60200), (1976, 55700), (1987, 41000), (1989, 36900), (1992, 33600)]
EAST_SEED = (59.75, 45.05, 0.32, 0.45)  # il bacino est era ancora pieno nel 1991, ma nei dati residui manca
ISLANDS = [(59.25, 45.1, 0.15, 0.1), (59.92, 45.68, 0.15, 0.06)]  # Vozroždenie e Barsakelmes, posizione e forma indicative
SPLIT = ((59.2, 46.0), (60.3, 46.45))  # stretto di Berg e Kokaral: i bacini si separano a fine anni Ottanta


def point_in(rings, x, y):
    inside = False
    for r in rings:
        for (ax, ay), (bx, by) in zip(r, r[1:]):
            if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
                inside = not inside
    return inside


def chamfer(seed):
    """Distanza in km da ogni cella all'insieme seed, con due passate."""
    kx = STEP * 111.2 * math.cos(math.radians(45))
    ky = STEP * 111.2
    kd = math.hypot(kx, ky)
    d = [[0 if seed[j][i] else 1e9 for i in range(NX)] for j in range(NY)]
    for j in range(NY):
        for i in range(NX):
            v = d[j][i]
            if i:
                v = min(v, d[j][i - 1] + kx)
            if j:
                v = min(v, d[j - 1][i] + ky)
                if i:
                    v = min(v, d[j - 1][i - 1] + kd)
                if i < NX - 1:
                    v = min(v, d[j - 1][i + 1] + kd)
            d[j][i] = v
    for j in range(NY - 1, -1, -1):
        for i in range(NX - 1, -1, -1):
            v = d[j][i]
            if i < NX - 1:
                v = min(v, d[j][i + 1] + kx)
            if j < NY - 1:
                v = min(v, d[j + 1][i] + ky)
                if i:
                    v = min(v, d[j + 1][i - 1] + kd)
                if i < NX - 1:
                    v = min(v, d[j + 1][i + 1] + kd)
            d[j][i] = v
    return d


def contour(f, t):
    """Marching squares: anelli chiusi all'isolinea t, in lon/lat."""
    def edge(i, j, side):
        return (i, j, side)

    def pos(e):
        i, j, side = e
        if side == 0:  # orizzontale, da (i,j) a (i+1,j)
            a, b = f[j][i], f[j][i + 1]
            s = (t - a) / (b - a)
            return (LON0 + (i + s) * STEP, LAT0 + j * STEP)
        a, b = f[j][i], f[j + 1][i]
        s = (t - a) / (b - a)
        return (LON0 + i * STEP, LAT0 + (j + s) * STEP)

    links = {}

    def link(a, b):
        links.setdefault(a, []).append(b)
        links.setdefault(b, []).append(a)

    for j in range(NY - 1):
        for i in range(NX - 1):
            c = [f[j][i] > t, f[j][i + 1] > t, f[j + 1][i + 1] > t, f[j + 1][i] > t]
            es = []
            if c[0] != c[1]:
                es.append(edge(i, j, 0))
            if c[1] != c[2]:
                es.append(edge(i + 1, j, 1))
            if c[3] != c[2]:
                es.append(edge(i, j + 1, 0))
            if c[0] != c[3]:
                es.append(edge(i, j, 1))
            if len(es) == 2:
                link(es[0], es[1])
            elif len(es) == 4:
                link(es[0], es[1])
                link(es[2], es[3])
    rings, seen = [], set()
    for start in links:
        if start in seen:
            continue
        ring, cur, prev = [], start, None
        while True:
            seen.add(cur)
            ring.append(pos(cur))
            nxt = [n for n in links[cur] if n != prev and n not in seen]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
        ring.append(ring[0])
        rings.append(ring)
    return rings


def simplify(pts, tol):
    if len(pts) < 4:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[len(pts) // 2] = keep[-1] = True
    stack = [(0, len(pts) // 2), (len(pts) // 2, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        dx, dy = pts[b][0] - ax, pts[b][1] - ay
        den = dx * dx + dy * dy or 1e-12
        best, bi = tol * tol, -1
        for i in range(a + 1, b):
            c = (pts[i][0] - ax) * dy - (pts[i][1] - ay) * dx
            d = c * c / den
            if d > best:
                best, bi = d, i
        if bi >= 0:
            keep[bi] = True
            stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]


def ring_km2(r):
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(r, r[1:])) / 2) * 111.2 ** 2 * math.cos(math.radians(45))


def area_at(y):
    for (y0, a0), (y1, a1) in zip(AREAS, AREAS[1:]):
        if y <= y1:
            return a0 + (a1 - a0) * max(0, y - y0) / (y1 - y0)
    return AREAS[-1][1]


def main(hist, modern, out):
    hf = next(f for f in json.load(open(hist, encoding="utf8"))["features"] if f["properties"].get("name") == "Aral Sea")
    rings = hf["geometry"]["coordinates"]
    cores = [f["geometry"]["coordinates"] for f in json.load(open(modern, encoding="utf8"))["features"]
             if f["properties"].get("name") in ("North Aral Sea", "South Aral Sea")]
    water = [[False] * NX for _ in range(NY)]
    core = [[False] * NX for _ in range(NY)]
    land = [[False] * NX for _ in range(NY)]
    ex, ey, ea, eb = EAST_SEED
    for j in range(NY):
        y = LAT0 + j * STEP
        for i in range(NX):
            x = LON0 + i * STEP
            w = point_in(rings, x, y) and not any(((x - a) / b) ** 2 + ((y - c) / e) ** 2 < 1 for a, c, b, e in ISLANDS)
            water[j][i] = w
            land[j][i] = not w
            if w and (any(point_in(c, x, y) for c in cores) or ((x - ex) / ea) ** 2 + ((y - ey) / eb) ** 2 < 1):
                core[j][i] = True
    ds, dc = chamfer(land), chamfer(core)
    (sx0, sy0), (sx1, sy1) = SPLIT
    f = [[-0.05] * NX for _ in range(NY)]
    for j in range(NY):
        y = LAT0 + j * STEP
        for i in range(NX):
            if water[j][i]:
                v = 1.0 if core[j][i] else ds[j][i] / (ds[j][i] + dc[j][i])
                x = LON0 + i * STEP
                if not core[j][i] and sx0 < x < sx1 and sy0 < y < sy1:
                    v *= 0.40  # bassofondo: si prosciuga prima e separa i due bacini
                f[j][i] = v
    cell = (STEP * 111.2) ** 2 * math.cos(math.radians(45))
    total = sum(map(sum, water)) * cell
    values = sorted(v for row in f for v in row if v > 0)
    print("area poligono 1960:", round(total), "km2, celle", len(values))
    frames = []
    months = [(y, m) for y in range(1960, 1992) for m in (0, 6)]
    for y, m in months:
        yy = y + m / 12
        target = area_at(yy) / 68000 * total
        drop = max(0, len(values) - int(target / cell))
        t = values[drop] if drop else 1e-4
        rs = [simplify(r, 0.006) for r in contour(f, t)]
        rs = [r for r in rs if ring_km2(r) > 3]
        big = sum(1 for r in rs if ring_km2(r) > 1500)
        frames.append({"m": f"{y}-{m + 1:02d}", "a": round(area_at(yy)),
                       "r": [[[round(p[0], 3), round(p[1], 3)] for p in r] for r in rs]})
        if m == 0:
            print(y, round(area_at(yy)), "t", round(t, 3), "anelli", len(rs), "grandi", big)
    data = {"full": [[[round(p[0], 3), round(p[1], 3)] for p in r] for r in rings], "frames": frames,
            "areas": AREAS}
    text = "window.ARAL=" + json.dumps(data, separators=(",", ":")) + ";\n"
    with open(out, "w", encoding="utf8") as h:
        h.write(text)
    print("aral.js", round(len(text) / 1000), "KB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
