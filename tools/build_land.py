"""Coste mondiali OpenStreetMap a tasselli, dai simplified land polygons di osmdata.openstreetmap.de.

Scrive land/x_y.js, uno per tassello da 15 gradi: la terra e le isole minori raggruppate per Stato più vicino.

Uso: python -I tools/build_land.py simplified-land-polygons-complete-3857.zip borders-hi.js cartella_land [metri_minimi]
"""
import json
import math
import os
import struct
import sys
import zipfile

SIZE = 15
SCALE = 1e4  # 11 metri
R = 6378137.0
YEAR = 1975 * 12  # le isole prendono lo Stato più vicino a questa data
ISLET_KM2 = 800


def lonlat(x, y):
    return math.degrees(x / R), math.degrees(2 * math.atan(math.exp(y / R)) - math.pi / 2)


def read_shp(data):
    p = 100
    n = len(data)
    while p < n:
        length = struct.unpack(">i", data[p + 4:p + 8])[0] * 2
        rec = p + 8
        if struct.unpack("<i", data[rec:rec + 4])[0] == 5:
            nparts, npts = struct.unpack("<2i", data[rec + 36:rec + 44])
            parts = list(struct.unpack(f"<{nparts}i", data[rec + 44:rec + 44 + 4 * nparts])) + [npts]
            base = rec + 44 + 4 * nparts
            for a, b in zip(parts, parts[1:]):
                yield struct.unpack(f"<{(b - a) * 2}d", data[base + a * 16:base + b * 16])
        p = rec + length


def thin(flat, tol):
    """Toglie i vertici a meno di tol metri dal precedente, tenendo la chiusura."""
    pts = [lonlat(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)]
    out = [pts[0]]
    k = math.cos(math.radians(pts[0][1]))
    for q in pts[1:-1]:
        if math.hypot((q[0] - out[-1][0]) * k, q[1] - out[-1][1]) * 111320 >= tol:
            out.append(q)
    out.append(pts[-1])
    return out


def area_km2(r):
    s = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(r, r[1:]))
    return abs(s) / 2 * 111.2 ** 2 * math.cos(math.radians(r[0][1]))


def clip_side(r, axis, value, keep_low):
    """Sutherland-Hodgman su un solo lato. r è chiuso, e lo è anche il risultato."""
    out = []
    inside = (lambda p: p[axis] <= value) if keep_low else (lambda p: p[axis] >= value)
    for a, b in zip(r, r[1:]):
        ia, ib = inside(a), inside(b)
        if ia:
            out.append(a)
        if ia != ib:
            t = (value - a[axis]) / (b[axis] - a[axis])
            q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            out.append(q)
    if out and out[0] != out[-1]:
        out.append(out[0])
    return out


def split_ring(r):
    """Taglia un anello sui bordi dei tasselli, prima per colonne e poi per righe."""
    xs = [p[0] for p in r]
    ys = [p[1] for p in r]
    x0, x1 = int((min(xs) + 180) // SIZE), int((max(xs) + 180) // SIZE)
    y0, y1 = int((min(ys) + 90) // SIZE), int((max(ys) + 90) // SIZE)
    if x0 == x1 and y0 == y1:
        return [((x0, y0), r)]
    out = []

    def by_rows(col, piece):
        rest = piece
        for gy in range(y0, y1 + 1):
            if len(rest) < 4:
                break
            top = (gy + 1) * SIZE - 90
            cell = clip_side(rest, 1, top, True) if gy < y1 else rest
            rest = clip_side(rest, 1, top, False) if gy < y1 else []
            if len(cell) >= 4:
                out.append(((col, gy), cell))

    rest = r
    for gx in range(x0, x1 + 1):
        if len(rest) < 4:
            break
        right = (gx + 1) * SIZE - 180
        col = clip_side(rest, 0, right, True) if gx < x1 else rest
        rest = clip_side(rest, 0, right, False) if gx < x1 else []
        if len(col) >= 4:
            by_rows(gx, col)
    return out


def enc(r):
    out, px, py = [], 0, 0
    for lon, lat in r:
        x, y = round(lon * SCALE), round(lat * SCALE)
        if x != px or y != py or not out:
            out += [x - px, y - py]
            px, py = x, y
    return out


def nearest_index(path):
    t = json.loads(open(path, encoding="utf8").read().split("=", 1)[1].rstrip().rstrip(";"))
    sx, sy = t["transform"]["scale"]
    tx, ty = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0
        p = []
        for dx, dy in a:
            x += dx
            y += dy
            p.append((x * sx + tx, y * sy + ty))
        arcs.append(p)
    grid = {}

    def flat(a):
        for v in a:
            if isinstance(v, list):
                yield from flat(v)
            else:
                yield v

    for g in t["objects"]["states"]["geometries"]:
        pr = g["properties"]
        if pr["s"] <= YEAR <= pr["e"]:
            for i in set(flat(g["arcs"])):
                for x, y in arcs[i if i >= 0 else ~i][::3]:
                    grid.setdefault((int(x), int(y)), []).append((x, y, pr["c"]))

    def nearest(lon, lat):
        best, code = 1e18, None
        k = math.cos(math.radians(lat))
        for rad in (1, 3, 6):
            for gx in range(int(lon) - rad, int(lon) + rad + 1):
                for gy in range(int(lat) - rad, int(lat) + rad + 1):
                    for x, y, c in grid.get((gx, gy), ()):
                        d = ((x - lon) * k) ** 2 + (y - lat) ** 2
                        if d < best:
                            best, code = d, c
            if code is not None:
                return code
        return None

    return nearest


def main(src, borders, out, tol):
    os.makedirs(out, exist_ok=True)
    z = zipfile.ZipFile(src)
    name = next(n for n in z.namelist() if n.endswith(".shp"))
    print(name, flush=True)
    nearest = nearest_index(borders)
    tiles = {}
    total = rings = 0
    for flat in read_shp(z.read(name)):
        r = thin(flat, tol)
        if len(r) < 4:
            continue
        cx = sum(p[0] for p in r) / len(r)
        cy = sum(p[1] for p in r) / len(r)
        if cy < -60 and max(p[1] for p in r) < -60:
            continue
        a = area_km2(r)
        code = nearest(cx, cy) if a < ISLET_KM2 else None
        # I continenti sono un anello unico: vanno tagliati sulla griglia, o finirebbero in un tassello solo
        for key, piece in split_ring(r):
            t = tiles.setdefault(key, {"land": [], "isl": {}})
            if code is not None:
                t["isl"].setdefault(str(code), []).append(enc(piece))
            else:
                t["land"].append(enc(piece))
            rings += 1
            total += len(piece)
    size = 0
    for (x, y), t in tiles.items():
        text = f"window.LAND_TILE({x},{y}," + json.dumps(t, separators=(",", ":")) + ");\n"
        with open(os.path.join(out, f"{x}_{y}.js"), "w", encoding="utf8") as h:
            h.write(text)
        size += len(text)
    print(len(tiles), "tasselli,", rings, "anelli,", total, "punti,", round(size / 1e6, 1), "MB; il più grande", round(max(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out)) / 1e6, 2), "MB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 60)
