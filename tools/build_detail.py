"""Costruisce detail.js (planimetria di Berlino e checkpoint) e lines.js (linee precise).

Uso: python -I tools/build_detail.py cartella_osm countries-10m.json disputed.geojson .
"""
import json
import math
import os
import sys

E6 = 1000000
M_LAT = 111320.0


def m_lon(lat):
    return 111320.0 * math.cos(math.radians(lat))


def dp(pts, tol_m):
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    k = m_lon(pts[0][1])
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        dx, dy = (pts[b][0] - ax) * k, (pts[b][1] - ay) * M_LAT
        den = dx * dx + dy * dy
        best, bi = tol_m * tol_m, -1
        for i in range(a + 1, b):
            px, py = (pts[i][0] - ax) * k, (pts[i][1] - ay) * M_LAT
            d = px * px + py * py if den == 0 else (px * dy - py * dx) ** 2 / den
            if d > best:
                best, bi = d, i
        if bi >= 0:
            keep[bi] = True
            stack += [(a, bi), (bi, b)]
    return [p for p, f in zip(pts, keep) if f]


def enc(pts):
    """Interi in micro-gradi, a delta: una lista piatta [x0,y0,dx,dy,...]."""
    out, px, py = [], 0, 0
    for lon, lat in pts:
        x, y = round(lon * E6), round(lat * E6)
        out += [x - px, y - py]
        px, py = x, y
    return out


def geom(e):
    return [(p["lon"], p["lat"]) for p in e.get("geometry", []) if p]


def load(folder, name):
    return json.load(open(os.path.join(folder, name + ".json"), encoding="utf8"))["elements"]


def dist(a, b):
    return math.hypot((a[0] - b[0]) * m_lon(a[1]), (a[1] - b[1]) * M_LAT)


def stitch(segs):
    """Unisce i segmenti scegliendo ogni volta l'estremo più vicino. Restituisce l'anello e i salti in metri."""
    segs = [list(s) for s in segs if len(s) > 1]
    line = segs.pop(0)
    gaps = []
    while segs:
        best = None
        for i, s in enumerate(segs):
            for rev in (False, True):
                d = dist(line[-1], s[-1] if rev else s[0])
                if best is None or d < best[0]:
                    best = (d, i, rev)
        d, i, rev = best
        s = segs.pop(i)
        if rev:
            s.reverse()
        if d > 1:
            gaps.append(round(d))
        line += s if d > 0 else s[1:]
    gaps.append(round(dist(line[-1], line[0])))
    return line, gaps


def signed_area(r):
    return sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r))) / 2


def offset_outside(ring, metres):
    """La striscia della morte stava sul lato est, cioè fuori dall'anello di Berlino Ovest."""
    sign = 1 if signed_area(ring) > 0 else -1
    out = []
    n = len(ring)
    for i in range(n):
        a, b = ring[i - 1], ring[(i + 1) % n]
        k = m_lon(ring[i][1])
        dx, dy = (b[0] - a[0]) * k, (b[1] - a[1]) * M_LAT
        ln = math.hypot(dx, dy) or 1
        nx, ny = dy / ln * sign, -dx / ln * sign
        out.append((ring[i][0] + nx * metres / k, ring[i][1] + ny * metres / M_LAT))
    return out


def build_detail(osm, out):
    d = {}
    wall = load(osm, "wall")[0]
    ring, gaps = stitch([geom(m) for m in wall["members"] if m["type"] == "way"])
    print("muro:", len(ring), "punti, salti in metri:", gaps, "area km2:",
          round(abs(signed_area(ring)) * m_lon(52.5) * M_LAT / 1e6))
    ring = dp(ring, .5)
    d["wall"] = enc(ring + [ring[0]])
    strip = offset_outside(ring, 45)
    d["strip"] = enc(dp(strip, 2) + [strip[0]])

    d["remains"] = []
    for e in load(osm, "hinter"):
        g = geom(e)
        t = e.get("tags", {})
        if len(g) > 1 and t.get("wall") != "brick" and t.get("historic") != "yes":
            d["remains"].append(enc(dp(g, .3)))

    polys, rivers = [], []
    for e in load(osm, "water"):
        if e["type"] == "relation":
            outer = [geom(m) for m in e.get("members", []) if m["type"] == "way" and m.get("role") == "outer"]
            rs = []
            for s in outer:  # gli outer spezzati vanno cuciti, quelli chiusi sono già anelli
                if s and s[0] == s[-1]:
                    polys.append(s)
                else:
                    rs.append(s)
            if rs:
                polys.append(stitch(rs)[0])
        else:
            g = geom(e)
            if len(g) < 2:
                continue
            if e.get("tags", {}).get("natural") == "water" and g[0] == g[-1]:
                polys.append(g)
            elif e.get("tags", {}).get("waterway") in ("river", "canal"):
                rivers.append(g)
    sized = [(abs(signed_area(p)) * m_lon(52.5) * M_LAT, p) for p in polys]
    d["water"] = [enc(dp(p, 2)) for a, p in sized if a > 8000]
    d["rivers"] = [enc(dp(g, 2)) for g in rivers]

    road = {"motorway": "a", "trunk": "a", "primary": "b", "secondary": "b", "tertiary": "c"}
    roads = {"a": [], "b": [], "c": []}
    for e in load(osm, "roads"):
        cl = road[e["tags"]["highway"]]
        roads[cl].append(enc(dp(geom(e), 3)))
    d["roads"] = roads
    d["rail"] = [enc(dp(geom(e), 4)) for e in load(osm, "rail")
                 if len(geom(e)) > 1 and e.get("tags", {}).get("service") is None and e.get("tags", {}).get("railway") in ("rail", "light_rail")]

    streets, seen = [], {}
    for e in load(osm, "streets") + [r for r in load(osm, "roads") if 13.37 < r["bounds"]["minlon"] < 13.41 and 52.495 < r["bounds"]["minlat"] < 52.52]:
        g = geom(e)
        if len(g) < 2:
            continue
        streets.append(enc(dp(g, 1)))
        n = e.get("tags", {}).get("name")
        if n and n not in seen:
            seen[n] = g[len(g) // 2]
    d["streets"] = streets
    d["streetNames"] = [[n, round(p[0], 6), round(p[1], 6)] for n, p in seen.items()]

    def buildings(items, keep):
        out_b = []
        for e in items:
            t = e.get("tags", {})
            g = geom(e)
            if e["type"] == "way" and "building" in t and len(g) > 2 and keep(e, g):
                out_b.append({"n": t.get("name", ""), "p": enc(g)})
        return out_b

    def highways(items, box):
        return [enc(dp(geom(e), 1)) for e in items if e["type"] == "way" and "highway" in e.get("tags", {})
                and box[0] < e["bounds"]["minlat"] and e["bounds"]["maxlat"] < box[2] and box[1] < e["bounds"]["minlon"] and e["bounds"]["maxlon"] < box[3]]

    alpha = load(osm, "alpha")
    skip = ("Esso", "Tank", "Lappwald")
    d["alpha"] = {
        "b": buildings(alpha, lambda e, g: 52.2115 < g[0][1] < 52.2170 and 11.0795 < g[0][0] < 11.0875 and not e["tags"].get("name", "").startswith(skip)
                       or e["tags"].get("name") in ("Grenz-Stahlturm", "Wachturm", "Zoll")),
        "r": highways(alpha, (52.205, 11.05, 52.225, 11.095)),
    }
    bravo = load(osm, "bravo")
    ids_new = {106050244, 186866535, 186866538}
    d["bravo"] = {
        "b": buildings(bravo, lambda e, g: e["id"] in ids_new),
        "r": highways(bravo, (52.392, 13.16, 52.42, 13.205)),
    }
    old = next((e for e in bravo if e["id"] == 9089128), None)
    d["bravoOld"] = [enc(geom(m)) for m in (old or {}).get("members", []) if m["type"] == "way" and len(geom(m)) > 1]

    # Strade e ferrovie di Berlino non servono alla mappa: restano fuori dal file
    for key in ("roads", "streets", "streetNames", "rail"):
        del d[key]
    text = "window.DETAIL=" + json.dumps(d, separators=(",", ":"), ensure_ascii=False) + ";\n"
    with open(os.path.join(out, "detail.js"), "w", encoding="utf8") as h:
        h.write(text)
    print("detail.js", round(len(text) / 1e6, 2), "MB; edifici alpha", len(d["alpha"]["b"]), "bravo", len(d["bravo"]["b"]), "strade charlie", len(streets))


def build_lines(osm, atlas_path, disputed_path, out):
    t = json.load(open(atlas_path, encoding="utf8"))
    sx, sy = t["transform"]["scale"]
    tx, ty = t["transform"]["translate"]
    arcs = []
    for arc in t["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((round(x * sx + tx, 4), round(y * sy + ty, 4)))
        arcs.append(pts)

    def arc_ids(a):
        return {i if i >= 0 else ~i for i in flatten(a)}

    def flatten(a):
        for v in a:
            if isinstance(v, list):
                yield from flatten(v)
            else:
                yield v

    by = {}
    for g in t["objects"]["countries"]["geometries"]:
        by[g["properties"]["name"]] = arc_ids(g["arcs"])

    def shared(a, b, keep=lambda p: True):
        res = []
        for i in by[a] & by[b]:
            run = []
            for p in arcs[i]:
                if keep(p):
                    run.append(p)
                elif run:
                    res.append(run)
                    run = []
            if len(run) > 1:
                res.append(run)
        return res

    lines = {
        "dmz": shared("North Korea", "South Korea"),
        "green": shared("Israel", "Palestine"),
        "kashmir": shared("India", "Pakistan", lambda p: p[1] > 32.45),
        "lac": shared("India", "China"),
        "cyprus": shared("N. Cyprus", "Cyprus U.N. Buffer Zone"),
        "iraniraq": shared("Iran", "Iraq"),
        "angola": shared("Angola", "Namibia"),
    }
    for f in json.load(open(disputed_path, encoding="utf8"))["features"]:
        p = f["properties"]
        g = f["geometry"]
        segs = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        if p.get("FEATURECLA") == "Elusive frontier" or p.get("NAME") == "Western Saharan claim":
            lines.setdefault("sahara", []).extend(segs)
        if p.get("NAME") == "Syrian claim":
            lines.setdefault("golan", []).extend(segs)

    # Basi sovrane britanniche a Cipro: anelli di Natural Earth, non linee
    lines["sba"] = {}
    for g in t["objects"]["countries"]["geometries"]:
        name = g["properties"]["name"]
        if name in ("Akrotiri", "Dhekelia"):
            polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
            rings = []
            for poly in polys:
                for ring in poly:
                    pts = []
                    for a in ring:
                        pts += arcs[a] if a >= 0 else arcs[~a][::-1]
                    rings.append(pts)
            lines["sba"][name] = rings

    lines["jordan"] = [dp(geom(e), 30) for e in load(osm, "jordan") if e.get("tags", {}).get("maritime") != "yes"]

    suez = [geom(e) for e in load(osm, "suez")]
    lines["suez"] = suez
    lines["benhai"] = [dp(geom(e), 50) for e in load(osm, "benhai")]

    # Linea di demarcazione coreana: confine tra le due Coree in OSM, cucito da ovest a est
    sys.path.insert(0, os.path.dirname(__file__))
    import build_borders
    mdl, gaps = build_borders.mdl_line(os.path.join(osm, "mdl.json")), []
    print("linea di demarcazione:", len(mdl), "punti, da", mdl[0], "a", mdl[-1], "salti", gaps)
    mdl = dp(mdl, 40)
    lines["dmz"] = [mdl]
    west = [p for p in mdl if p[0] < 127.47]
    east = [p for p in mdl if p[0] > 128.1]
    # Saliente di Kumsong prima del 1953, dalla descrizione di Battle of Kumsong:
    # 3 miglia a NE di Kumhwa, colline a sud di Kumsong, 10 miglia a est, 13 miglia a SE fino a Mundung-ni
    bulge = [(127.47, 38.31), (127.55, 38.37), (127.62, 38.41), (127.72, 38.415), (127.8, 38.41), (127.9, 38.35), (128.0, 38.29), (128.08, 38.27)]
    lines["kor5111"] = [west + bulge + east]
    # Giugno 1953: la ROK arretra di circa 3 km su 13 km di fronte attorno alla colline 973 e Capitol Hill
    bulge2 = [(127.47, 38.31), (127.55, 38.37), (127.62, 38.40), (127.72, 38.39), (127.8, 38.38), (127.9, 38.32), (128.0, 38.27), (128.08, 38.27)]
    lines["kor5306"] = [west + bulge2 + east]

    lat, lon = 20.25, -74.13  # Capo Maisí: raggio di 500 miglia nautiche
    r = 500 * 1852 / 6371000
    arc = []
    for deg in range(-20, 200, 4):  # bearing misurato da nord, verso il lato atlantico
        b = math.radians(deg)
        la = math.asin(math.sin(math.radians(lat)) * math.cos(r) + math.cos(math.radians(lat)) * math.sin(r) * math.cos(b))
        lo = math.radians(lon) + math.atan2(math.sin(b) * math.sin(r) * math.cos(math.radians(lat)), math.cos(r) - math.sin(math.radians(lat)) * math.sin(la))
        arc.append((round(math.degrees(lo), 3), round(math.degrees(la), 3)))
    lines["quarantine"] = [arc]
    text = "window.LINE_GEO=" + json.dumps(lines, separators=(",", ":")) + ";\n"
    with open(os.path.join(out, "lines.js"), "w", encoding="utf8") as h:
        h.write(text)
    print("lines.js", round(len(text) / 1e3), "KB")


if __name__ == "__main__":
    build_lines(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    build_detail(sys.argv[1], sys.argv[4])
