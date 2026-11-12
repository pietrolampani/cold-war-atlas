"""Da OpenStreetMap: contorno di Gibilterra, confine con la Spagna e costa spagnola vicina. Scrive gibraltar.js.

Uso: python -I tools/build_gibraltar.py gibraltar.json gibraltar.js
"""
import json
import math
import sys

BORDER_WAY = 345004358
WEST_LON, EAST_LON, SOUTH_LAT, NORTH_LAT = -5.46, -5.30, 36.077, 36.25


def thin(pts, tol_m=1.5):
    """Toglie i punti a meno di tol_m metri dal precedente, tenendo gli estremi."""
    out = [pts[0]]
    k = 111320 * math.cos(math.radians(36.1))
    for p in pts[1:-1]:
        if math.hypot((p[0] - out[-1][0]) * k, (p[1] - out[-1][1]) * 111320) >= tol_m:
            out.append(p)
    return out + [pts[-1]]


def main(src, dst):
    els = json.load(open(src, encoding="utf8"))["elements"]
    coast, closed = {}, []
    border = None
    for e in els:
        if e["type"] != "way":
            continue
        g = [(p["lon"], p["lat"]) for p in e["geometry"]]
        if e["id"] == BORDER_WAY:
            border = g
        elif e.get("tags", {}).get("natural") == "coastline":
            if g[0] == g[-1]:
                closed.append(g)
            else:
                coast[g[0]] = g
    west, east = max(border, key=lambda p: -p[0]), max(border, key=lambda p: p[0])
    if border[0] != east:
        border = border[::-1]  # da est verso ovest

    # L'acqua sta a destra del verso di OSM: da ovest a sud attorno alla Rocca, poi su fino al punto est
    rock, cur = [], west
    while cur != east:
        way = coast[cur]
        rock += way if not rock else way[1:]
        cur = way[-1]
    rock_ring = rock + border[1:]

    # Costa spagnola a est del confine, verso nord
    north, cur = [], east
    while cur in coast and coast[cur][-1][1] <= NORTH_LAT:
        way = coast[cur]
        north += way if not north else way[1:]
        cur = way[-1]
    # Costa spagnola nella baia, a ritroso dal punto ovest
    ends = {g[-1]: g for g in coast.values()}
    bay, cur = [], west
    while cur in ends and ends[cur][0][1] >= SOUTH_LAT - 0.001 and ends[cur][0][0] >= WEST_LON:
        way = ends[cur]
        bay = way[:-1] + bay
        cur = way[0]
    bay = bay + [west]
    corners = [(WEST_LON, bay[0][1]), (WEST_LON, NORTH_LAT), (north[-1][0], NORTH_LAT)]
    spain = corners + thin(north)[::-1] + border[1:-1] + thin(bay)[::-1]
    print("Rocca", len(rock_ring), "punti; Spagna", len(spain), "punti; da", bay[0], "a", north[-1])

    islets = [g for g in closed if WEST_LON < g[0][0] < EAST_LON and 36.1 < g[0][1] < 36.16]
    rnd = lambda r: [[round(x, 6), round(y, 6)] for x, y in r]
    data = {"rock": [rnd(thin(rock_ring))] + [rnd(g) for g in islets], "spain": [rnd(spain)], "border": rnd(border),
            "sea": [rnd([(WEST_LON, SOUTH_LAT), (EAST_LON, SOUTH_LAT), (EAST_LON, NORTH_LAT), (WEST_LON, NORTH_LAT)])]}
    with open(dst, "w", encoding="utf8") as h:
        h.write("window.GIBRALTAR=" + json.dumps(data, separators=(",", ":")) + ";\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
