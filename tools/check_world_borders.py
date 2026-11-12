"""Controlla quanta parte di ogni confine terrestre di Natural Earth ha una via OSM entro MAX_KM.

Uso: python -I tools/check_world_borders.py atlas10.json world_borders.json report.txt
"""
import json
import math
import sys
from collections import defaultdict

MAX_KM = 15
CELL = 0.25


def arcs_of(topo):
    tr = topo["transform"]
    out = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * tr["scale"][0] + tr["translate"][0], y * tr["scale"][1] + tr["translate"][1]))
        out.append(pts)
    return out


def flat(a):
    for v in a:
        if isinstance(v, list):
            yield from flat(v)
        else:
            yield v


def main(atlas, world, report):
    topo = json.load(open(atlas, encoding="utf8"))
    arcs = arcs_of(topo)
    owners = defaultdict(set)
    for g in topo["objects"]["countries"]["geometries"]:
        for i in flat(g.get("arcs", [])):
            owners[i if i >= 0 else ~i].add(g["properties"]["name"])
    grid = defaultdict(list)
    for r in json.load(open(world))["elements"]:
        g = r["geometry"]
        for a, b in zip(g, g[1:]):
            n = max(1, int(max(abs(a["lon"] - b["lon"]), abs(a["lat"] - b["lat"])) / 0.05))
            for t in range(n + 1):
                lon, lat = a["lon"] + (b["lon"] - a["lon"]) * t / n, a["lat"] + (b["lat"] - a["lat"]) * t / n
                grid[int(lon // CELL), int(lat // CELL)].append((lon, lat))
    pairs = defaultdict(lambda: [0, 0])
    for i, own in owners.items():
        if len(own) != 2:
            continue
        key = " / ".join(sorted(own))
        for lon, lat in arcs[i][::2] or arcs[i]:
            k = math.cos(math.radians(lat))
            cx, cy = int(lon // CELL), int(lat // CELL)
            ok = False
            reach = int(MAX_KM / 111 / max(k, 0.2) / CELL) + 1
            for gx in range(cx - reach, cx + reach + 1):
                for gy in range(cy - 1, cy + 2):
                    for x, y in grid.get((gx, gy), ()):
                        if math.hypot((x - lon) * k, y - lat) * 111.32 <= MAX_KM:
                            ok = True
                            break
                    if ok:
                        break
                if ok:
                    break
            pairs[key][0] += 1
            pairs[key][1] += ok
    bad = sorted(((v[1] / v[0], k, v[0]) for k, v in pairs.items() if v[1] / v[0] < 0.95))
    with open(report, "w", encoding="utf8") as h:
        for share, k, n in bad:
            h.write(f"{share * 100:5.1f}%  {k}  ({n} punti)\n")
    total = sum(v[0] for v in pairs.values())
    covered = sum(v[1] for v in pairs.values())
    print(len(pairs), "confini,", round(covered / total * 100, 1), "% dei punti coperti,", len(bad), "confini sotto il 95%")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
