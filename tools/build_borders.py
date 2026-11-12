"""Converte CShapes 2.0 (GeoJSON) in borders.js: una TopoJSON con archi condivisi e semplificati.

Uso: python -I tools/build_borders.py CShapes-2.0.geojson borders.js [tolleranza_gradi] [countries-50m.json]
"""
import heapq
import json
import math
import sys

START = 1945 * 12  # 1945-01
END = 1991 * 12 + 11  # 1991-12
Q = 100  # griglia di 0.01 gradi
MIN_AREA = 0.02 * Q * Q  # isole sotto ~0.02 gradi quadrati spariscono
VAR = "BORDERS"
EXTRA_LINES = []
EXTRAS = {"Greenland":3901,"Falkland Is.":3902,"Grenada":3903,"Saint Lucia":3904,"St. Vin. and Gren.":3905,"Dominica":3906,"Antigua and Barb.":3907,"St. Kitts and Nevis":3908,"Seychelles":3909,"S\u00e3o Tom\u00e9 and Principe":3910,"Samoa":3911,"Tonga":3912,"Vanuatu":3913,"Kiribati":3914,"Tuvalu":3915,"Nauru":3916,"Marshall Is.":3917,"Micronesia":3918,"Palau":3919,"Monaco":3920,"Liechtenstein":3921,"San Marino":3922,"Andorra":3923,"Macao":3924,"Hong Kong":3925,"Bermuda":3926,"Cayman Is.":3927,"Turks and Caicos Is.":3928,"British Virgin Is.":3929,"U.S. Virgin Is.":3930,"Guam":3931,"American Samoa":3932,"N. Mariana Is.":3933,"Cook Is.":3934,"Niue":3935,"Saint Helena":3936,"Anguilla":3937,"Montserrat":3938,"Aruba":3939,"Cura\u00e7ao":3939,"Faeroe Is.":3940}  # nome in Natural Earth -> codice locale in data.js


def ring_area(r):
    a = 0
    for i in range(len(r) - 1):
        a += r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1]
    return a / 2


def clean_ring(ring):
    out = []
    for lon, lat in ring:
        p = (round((lon + 180) * Q), round((lat + 90) * Q))
        if not out or out[-1] != p:
            out.append(p)
    if out[0] != out[-1]:
        out.append(out[0])
    return out


def douglas_peucker(pts, tol):
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    t2 = tol * tol
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        dx, dy = pts[b][0] - ax, pts[b][1] - ay
        den = dx * dx + dy * dy
        best, bi = t2, -1
        for i in range(a + 1, b):
            px, py = pts[i][0] - ax, pts[i][1] - ay
            if den == 0:
                d = px * px + py * py
            else:
                c = px * dy - py * dx
                d = c * c / den
            if d > best:
                best, bi = d, i
        if bi >= 0:
            keep[bi] = True
            stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]


def simplify_closed(pts, tol):
    # Un anello senza giunzioni va spezzato in due, altrimenti il primo punto resterebbe fisso da solo
    if len(pts) < 8:
        return pts
    mid = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)
    return douglas_peucker(pts[: mid + 1], tol)[:-1] + douglas_peucker(pts[mid:], tol)


class Conflator:
    """Sostituisce un arco storico con il tracciato Natural Earth, solo se i due corrono vicini.
    Un confine scomparso (Germania Est, Yugoslavia) non ha corrispondenza e resta CShapes."""

    BORDER_KM = 8
    COAST_KM = 20

    def __init__(self, path):
        t = json.load(open(path, encoding="utf8"))
        sx, sy = t["transform"]["scale"]
        tx, ty = t["transform"]["translate"]
        self.arcs = []
        for arc in t["arcs"]:
            x = y = 0
            pts = []
            for dx, dy in arc:
                x += dx
                y += dy
                pts.append((x * sx + tx, y * sy + ty))
            self.arcs.append(pts)
        natural_earth = len(self.arcs)
        # In Indocina si aggiungono i confini di OpenStreetMap e il fiume Ben Hai, molto più fitti di Natural Earth
        for extra in EXTRA_LINES:
            for e in json.load(open(extra, encoding="utf8"))["elements"]:
                if e["type"] == "way" and e.get("geometry") and e.get("tags", {}).get("maritime") != "yes":
                    self.arcs.append([(p["lon"], p["lat"]) for p in e["geometry"]])
        self.grid = {}
        self.graph = {}
        self.lengths = []
        for a, pts in enumerate(self.arcs):
            for i, p in enumerate(pts):
                self.grid.setdefault((int(p[0] * 4), int(p[1] * 4)), []).append((a, i))
            ln = sum(km(p, q) for p, q in zip(pts, pts[1:]))
            self.lengths.append(ln)
            s, e = pts[0], pts[-1]
            self.graph.setdefault(s, []).append((e, ln, a, False))
            self.graph.setdefault(e, []).append((s, ln, a, True))
        self.stats = {"costa": 0, "confine": 0, "tenuto": 0, "osm": 0}
        # Rete a parte delle sole linee OSM: nella rete mista il percorso più corto preferisce gli archi grossolani di Natural Earth
        self.osm_grid = {}
        self.osm_graph = {}
        for a, pts in enumerate(self.arcs[natural_earth:], natural_earth):
            for i, p in enumerate(pts):
                self.osm_grid.setdefault((int(p[0] * 4), int(p[1] * 4)), []).append((a, i))
            s, e = pts[0], pts[-1]
            self.osm_graph.setdefault(s, []).append((e, self.lengths[a], a, False))
            self.osm_graph.setdefault(e, []).append((s, self.lengths[a], a, True))

    def nearest(self, p, grid=None):
        cx, cy = int(p[0] * 4), int(p[1] * 4)
        best, bd = None, 1e9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for a, i in (self.grid if grid is None else grid).get((cx + dx, cy + dy), ()):
                    d = km(p, self.arcs[a][i])
                    if d < bd:
                        best, bd = (a, i), d
        return best, bd

    def route(self, u, v, limit, graph=None):
        """Percorso più corto sugli archi, da vertice a vertice."""
        graph = self.graph if graph is None else graph
        (a, i), (b, j) = u, v
        A, B = self.arcs[a], self.arcs[b]
        if a == b:
            return A[i: j + 1] if i <= j else A[j: i + 1][::-1]
        heap = [(sum(km(p, q) for p, q in zip(A[i:], A[i + 1:])), A[-1], A[i:]),
                (sum(km(p, q) for p, q in zip(A[:i], A[1: i + 1])), A[0], A[: i + 1][::-1])]
        heapq.heapify(heap)
        ends = {B[0]: B[: j + 1], B[-1]: B[j:][::-1]}
        seen = set()
        while heap:
            cost, node, path = heapq.heappop(heap)
            if cost > limit:
                return None
            if node in seen:
                continue
            seen.add(node)
            if node in ends:
                return path + ends[node][1:]
            for nxt, ln, arc, rev in graph.get(node, ()):
                if nxt not in seen and arc != a and arc != b:
                    seg = self.arcs[arc][::-1] if rev else self.arcs[arc]
                    heapq.heappush(heap, (cost + ln, nxt, path + seg[1:]))
        return None

    def split(self, pts, depth):
        """Divide il tratto a metà, agganciando il punto di mezzo alla linea OSM più vicina, e riprova sulle due parti."""
        m = len(pts) // 2
        mid = pts[m]
        lon, lat = mid[0] / Q - 180, mid[1] / Q - 90
        near, d = self.nearest((lon, lat), self.osm_grid)
        if near and d <= self.BORDER_KM:
            q = self.arcs[near[0]][near[1]]
            mid = (round((q[0] + 180) * Q), round((q[1] + 90) * Q))
        left = self.on_osm(pts[:m] + [mid], depth + 1)
        right = self.on_osm([mid] + pts[m + 1:], depth + 1)
        return left + right[1:]

    def on_osm(self, pts, depth=0):
        """Tracciato sulle sole linee OSM. Dove non regge si divide; i pezzi più piccoli ricadono su Natural Earth o CShapes."""
        deg = [(x / Q - 180, y / Q - 90) for x, y in pts]
        closed = pts[0] == pts[-1]
        if not closed:
            mx, my = deg[len(deg) // 2]
            tol = 30 if 100 < mx < 110 and 8 < my < 24 else self.BORDER_KM
            length = sum(km(p, q) for p, q in zip(deg, deg[1:]))
            u, du = self.nearest(deg[0], self.osm_grid)
            v, dv = self.nearest(deg[-1], self.osm_grid)
            if u and v and du <= tol and dv <= tol:
                path = self.route(u, v, length * 5 + 20, self.osm_graph)
                if path and len(path) > 1:
                    plen = sum(km(p, q) for p, q in zip(path, path[1:]))
                    if 0.6 * length - 5 <= plen <= 5 * length + 10 and not hausdorff_over(deg, path, tol) and not hausdorff_over(path, deg, tol):
                        self.stats["osm"] += 1
                        out = [pts[0]]
                        for lon, lat in path[1:-1]:
                            q = (round((lon + 180) * Q), round((lat + 90) * Q))
                            if q != out[-1]:
                                out.append(q)
                        if out[-1] != pts[-1]:
                            out.append(pts[-1])
                        return out
        if len(pts) >= 6 and depth < 7:
            return self.split(pts, depth)
        return self.apply_natural_earth(pts, closed, False)

    def apply(self, pts, closed, coast):
        """pts è in interi della griglia; restituisce il tracciato da usare, con gli stessi estremi."""
        if not coast and self.osm_graph:
            return self.on_osm(list(pts))
        return self.apply_natural_earth(pts, closed, coast)

    def apply_natural_earth(self, pts, closed, coast):
        deg = [(x / Q - 180, y / Q - 90) for x, y in pts]
        tol = self.COAST_KM if coast else self.BORDER_KM
        # In Indocina i confini coloniali di CShapes sono grossolani: si accetta una distanza maggiore
        mx, my = deg[len(deg) // 2]
        if 100 < mx < 110 and 8 < my < 24:
            tol = max(tol, 30)
        u, du = self.nearest(deg[0])
        v, dv = self.nearest(deg[-1])
        if u is None or v is None or du > tol or dv > tol:
            self.stats["tenuto"] += 1
            return pts
        length = sum(km(p, q) for p, q in zip(deg, deg[1:]))
        if closed:
            if u[0] != self.nearest(deg[len(deg) // 2])[0][0] if self.nearest(deg[len(deg) // 2])[0] else True:
                self.stats["tenuto"] += 1
                return pts
            arc = self.arcs[u[0]]
            if arc[0] != arc[-1]:
                self.stats["tenuto"] += 1
                return pts
            path = arc[u[1]: -1] + arc[: u[1] + 1]
        else:
            path = self.route(u, v, length * (6 if tol == 30 else 3) + 60)
        if not path or len(path) < 2:
            self.stats["tenuto"] += 1
            return pts
        plen = sum(km(p, q) for p, q in zip(path, path[1:]))
        if not (0.6 * length - 5 <= plen <= (6 if tol == 30 else 4 if coast else 3.5) * length + 10):
            self.stats["tenuto"] += 1
            return pts
        if hausdorff_over(deg, path, tol) or hausdorff_over(path, deg, tol):
            if tol == 30:
                print("Indocina, troppo distante:", deg[0], deg[-1], round(length), round(plen))
            self.stats["tenuto"] += 1
            return pts
        self.stats["costa" if coast else "confine"] += 1
        out = [pts[0]]
        for lon, lat in path[1:-1]:
            q = (round((lon + 180) * Q), round((lat + 90) * Q))
            if q != out[-1]:
                out.append(q)
        if out[-1] != pts[-1]:
            out.append(pts[-1])
        return out


def km(a, b):
    return math.hypot((a[0] - b[0]) * math.cos(math.radians((a[1] + b[1]) / 2)), a[1] - b[1]) * 111.2


def sample(pts, n):
    step = max(1, len(pts) // n)
    return pts[::step] + [pts[-1]]


def hausdorff_over(a, b, tol):
    """Vero se un punto di a dista da b più della tolleranza."""
    other = sample(b, 300)
    for p in sample(a, 50):
        k = math.cos(math.radians(p[1]))
        best = 1e18
        for s, e in zip(other, other[1:]):
            dx, dy = (e[0] - s[0]) * k, e[1] - s[1]
            px, py = (p[0] - s[0]) * k, p[1] - s[1]
            den = dx * dx + dy * dy
            t = 0 if den == 0 else max(0, min(1, (px * dx + py * dy) / den))
            d = (px - t * dx) ** 2 + (py - t * dy) ** 2
            if d < best:
                best = d
        if math.sqrt(best) * 111.2 > tol:
            return True
    return False


def split_at_latitude(polys, lat):
    """Taglia anelli in senso orario lungo un parallelo. Restituisce (nord, sud), ogni parte è una lista di anelli chiusi."""
    y0 = round((lat + 90) * Q)
    north, south = [], []
    for poly in polys:
        ring = poly[0]
        ys = [p[1] for p in ring]
        if min(ys) >= y0:
            north.append([ring])
            continue
        if max(ys) <= y0:
            south.append([ring])
            continue
        pts = ring[:-1]
        k = next(i for i, p in enumerate(pts) if p[1] != y0)
        pts = pts[k:] + pts[:k]
        chains, cur, side = {True: [], False: []}, [], pts[0][1] > y0
        for a, b in zip(pts, pts[1:] + pts[:1]):
            cur.append(a)
            if b[1] == y0 or (b[1] > y0) == side:
                continue
            x = round(a[0] + (y0 - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
            cur.append((x, y0))
            chains[side].append(cur)
            cur, side = [(x, y0)], not side
        # L'ultimo tratto continua nel primo, perché l'anello parte a metà di una catena
        chains[side][0] = cur + chains[side][0]
        for is_north, out, step in ((True, north, -1), (False, south, 1)):
            todo = chains[is_north]
            while todo:
                r = list(todo.pop(0))
                while todo:
                    ahead = [c for c in todo if (c[0][0] - r[-1][0]) * step > 0]
                    if (r[0][0] - r[-1][0]) * step > 0 and (not ahead or (r[0][0] - r[-1][0]) * step <= min((c[0][0] - r[-1][0]) * step for c in ahead)):
                        break
                    if not ahead:
                        break
                    nxt = min(ahead, key=lambda c: (c[0][0] - r[-1][0]) * step)
                    todo.remove(nxt)
                    r += nxt
                out.append([r + [r[0]]])
    return north, south


def korea_on_parallel(feats):
    """Fino all'armistizio il confine coreano è il 38° parallelo: CShapes usa la linea del 1953 fin dal 1945."""
    armistice = 1953 * 12 + 7
    whole = next(f for f in feats if f["c"] == 730)
    korean_islands(whole)
    north, south = split_at_latitude(whole["polys"], 38)
    extra = []
    for f in feats:
        if f["c"] in (731, 732) and f["s"] <= armistice:
            part = north if f["c"] == 731 else south
            if f["e"] > armistice:
                extra.append({"c": f["c"], "s": armistice + 1, "e": f["e"], "polys": f["polys"]})
                f["e"] = armistice
            f["polys"] = part
    path = next((p for p in EXTRA_LINES if "mdl" in p), None)
    if path:
        north2, south2 = korea_on_armistice(whole["polys"], path)
        for f in extra:
            f["polys"] = north2 if f["c"] == 731 else south2
    feats.extend(extra)


def mdl_line(path):
    """La linea di demarcazione di terra: niente tratti marittimi, solo vie contigue, tagliata alle due coste."""
    ways = [[(p["lon"], p["lat"]) for p in e["geometry"]] for e in json.load(open(path, encoding="utf8"))["elements"]
            if e.get("geometry") and e.get("tags", {}).get("maritime") != "yes"]
    ways = [g for g in ways if all(37.7 < p[1] < 38.7 and 126.6 < p[0] < 128.45 for p in g)]
    start = min(ways, key=lambda g: min(g[0][0], g[-1][0]))
    ways.remove(start)
    line = start if start[0][0] < start[-1][0] else start[::-1]
    while ways:
        nxt = min(ways, key=lambda g: min(km(line[-1], g[0]), km(line[-1], g[-1])))
        if min(km(line[-1], nxt[0]), km(line[-1], nxt[-1])) > 1:
            break
        ways.remove(nxt)
        if km(line[-1], nxt[0]) > km(line[-1], nxt[-1]):
            nxt = nxt[::-1]
        line = line + nxt[1:]
    return [p for p in line if p[0] >= 126.655]


def korea_on_armistice(polys, path):
    """Dal 1953 il confine è la linea di demarcazione di OpenStreetMap, non quella grossolana di CShapes."""
    line = mdl_line(path)
    mdl = [(round((x + 180) * Q), round((y + 90) * Q)) for x, y in line]
    mdl = [p for i, p in enumerate(mdl) if i == 0 or p != mdl[i - 1]]
    main = max(polys, key=lambda p: abs(ring_area(p[0])))
    ring = main[0][:-1]
    near = lambda q: min(range(len(ring)), key=lambda i: (ring[i][0] - q[0]) ** 2 + (ring[i][1] - q[1]) ** 2)
    iw, ie = near(mdl[0]), near(mdl[-1])
    # L'anello è in senso orario: da ovest a est passa per il nord
    north_coast = ring[iw:ie + 1] if iw <= ie else ring[iw:] + ring[:ie + 1]
    south_coast = ring[ie:iw + 1] if ie <= iw else ring[ie:] + ring[:iw + 1]
    north_ring = north_coast + mdl[::-1] + [north_coast[0]]
    south_ring = south_coast + mdl + [south_coast[0]]
    north, south = [[north_ring]], [[south_ring]]
    for p in polys:
        if p is main:
            continue
        (south if island_owner(p[0]) == "KR" else north).append(p)
    return north, south


KOREA_BOUNDS = {}


def load_korea_bounds():
    """Segmenti dei confini di Stato OSM, acque comprese, per decidere di chi è ogni isola."""
    path = next((p for p in EXTRA_LINES if "korea_rel" in p), None)
    if not path or KOREA_BOUNDS:
        return
    for e in json.load(open(path, encoding="utf8"))["elements"]:
        iso = e["tags"]["ISO3166-1"]
        segs = []
        for m in e["members"]:
            g = m.get("geometry") or []
            segs += [((a["lon"], a["lat"]), (b["lon"], b["lat"])) for a, b in zip(g, g[1:])]
        KOREA_BOUNDS[iso] = segs


def inside_bound(iso, lon, lat):
    hit = False
    for (ax, ay), (bx, by) in KOREA_BOUNDS.get(iso, ()):
        if (ay > lat) != (by > lat) and lon < ax + (lat - ay) * (bx - ax) / (by - ay):
            hit = not hit
    return hit


# Le cinque isole del nord-ovest restano al Sud per l'armistizio: se OSM fosse ambiguo vale questa lista
NW_ISLANDS = [("Baengnyeong", 124.62, 124.75, 37.9, 38.0), ("Daecheong", 124.66, 124.76, 37.8, 37.87), ("Socheong", 124.7, 124.82, 37.74, 37.79),
              ("Yeonpyeong", 125.66, 125.75, 37.62, 37.69), ("U-do", 125.95, 126.0, 37.59, 37.63)]
ISLAND_LOG = []


def island_owner(ring, name=""):
    xs = [q[0] for q in ring]
    ys = [q[1] for q in ring]
    lon, lat = sum(xs) / len(xs) / Q - 180, sum(ys) / len(ys) / Q - 90
    load_korea_bounds()
    kr, kp = inside_bound("KR", lon, lat), inside_bound("KP", lon, lat)
    fixed = next((n for n, w, e, s, nn in NW_ISLANDS if w < lon < e and s < lat < nn), None)
    if fixed:
        owner, why = "KR", "armistizio: " + fixed
    elif kr != kp:
        owner, why = ("KR", "confine OSM") if kr else ("KP", "confine OSM")
    else:
        # Né nell'uno né nell'altro, o in entrambi: si guarda il lato della linea e si segnala
        owner, why = ("KP", "DUBBIO") if lat >= 37.75 and lon < 126.2 else ("KR", "DUBBIO")
    if KOREA_BOUNDS:
        ISLAND_LOG.append((why, round(lat, 3), round(lon, 3), round(abs(ring_area(ring)) / Q / Q * 111.2 ** 2 * math.cos(math.radians(lat)), 2), owner, name))
    return owner


def korean_islands(whole):
    """Aggiunge gli isolotti di OSM che i dati generali non hanno, solo nella versione fine."""
    paths = [p for p in EXTRA_LINES if "korea_islands" in p]
    if not paths:
        return
    load_korea_bounds()
    # Tutte le isole vengono da OSM: quelle di CShapes sono masse grossolane che inglobano gli isolotti vicini
    whole["polys"] = [max(whole["polys"], key=lambda p: abs(ring_area(p[0])))]
    known = []

    def covered(lon, lat):
        for r in known:
            hit = False
            for (ax, ay), (bx, by) in zip(r, r[1:]):
                if (ay > lat) != (by > lat) and lon < ax + (lat - ay) * (bx - ax) / (by - ay):
                    hit = not hit
            if hit:
                return True
        return False

    seen = set()
    elements = [e for p in paths for e in json.load(open(p, encoding="utf8"))["elements"]]
    # Le coste delle isole grandi (Baengnyeong) sono spezzate in più tratti: vanno cucite prima
    closed, open_ways = [], {}
    for e in elements:
        g = e.get("geometry")
        if e["type"] != "way" or not g or len(g) < 2 or e["id"] in seen:
            continue
        seen.add(e["id"])
        pts = [(p["lon"], p["lat"]) for p in g]
        if pts[0] == pts[-1]:
            closed.append((pts, e.get("tags", {})))
        elif e.get("tags", {}).get("natural") == "coastline":
            open_ways[pts[0]] = pts
    used = set()
    for head in list(open_ways):
        if head in used:
            continue
        line, cur = [], head
        while cur in open_ways and cur not in used:
            used.add(cur)
            line += open_ways[cur] if not line else open_ways[cur][1:]
            cur = line[-1]
        if line[0] == line[-1]:
            closed.append((line, {}))
    for pts, tags in closed:
        r = clean_ring(pts)
        if len(r) < 4 or abs(ring_area(r)) == 0:
            continue
        lon = sum(q[0] for q in r) / len(r) / Q - 180
        lat = sum(q[1] for q in r) / len(r) / Q - 90
        # Fuori dai confini coreani (Tsushima, isole cinesi) o già presente: non si aggiunge
        if covered(lon, lat) or not (inside_bound("KR", lon, lat) or inside_bound("KP", lon, lat)):
            continue
        if ring_area(r) > 0:
            r.reverse()
        whole["polys"].append([r])
        ISLAND_PTS.update(r)
        known.append([(x / Q - 180, y / Q - 90) for x, y in r])
        ISLAND_NAMES[tuple(r[0])] = tags.get("name:en") or tags.get("name") or ""


ISLAND_NAMES = {}
ISLAND_PTS = set()


def cyprus_rings(path):
    """L'isola intera da Natural Earth: CShapes taglia la penisola di Akrotiri, che finirebbe in mare.
    Natural Earth divide Cipro in cinque pezzi: il contorno sono gli archi usati da un pezzo solo."""
    t = json.load(open(path, encoding="utf8"))
    sx, sy = t["transform"]["scale"]
    tx, ty = t["transform"]["translate"]
    decoded = []
    for arc in t["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        decoded.append(pts)
    names = {"Cyprus", "N. Cyprus", "Cyprus U.N. Buffer Zone", "Akrotiri", "Dhekelia"}
    uses = {}
    for g in t["objects"]["countries"]["geometries"]:
        if g["properties"]["name"] in names:
            polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
            for poly in polys:
                for ring in poly:
                    for a in ring:
                        uses[a if a >= 0 else ~a] = uses.get(a if a >= 0 else ~a, 0) + 1
    segs = [decoded[a] for a, n in uses.items() if n == 1]
    rings = []
    while segs:  # i tratti contigui si uniscono; gli isolotti restano anelli a sé
        line = list(segs.pop())
        grown = True
        while grown and line[0] != line[-1]:
            grown = False
            for i, s in enumerate(segs):
                if s[0] == line[-1]:
                    line += s[1:]
                elif s[-1] == line[-1]:
                    line += s[::-1][1:]
                else:
                    continue
                segs.pop(i)
                grown = True
                break
        rings.append(line)
    out = []
    for r in rings:
        c = clean_ring(r)
        if len(c) >= 4:
            if ring_area(c) > 0:
                c.reverse()
            out.append([c])
    return out


def atlas_extras(path):
    """CShapes non copre Groenlandia e Falkland: le prende da world-atlas (Natural Earth)."""
    t = json.load(open(path, encoding="utf8"))
    sx, sy = t["transform"]["scale"]
    tx, ty = t["transform"]["translate"]
    arcs = []
    for arc in t["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append([x * sx + tx, y * sy + ty])
        arcs.append(pts)

    def ring(ids):
        out = []
        for a in ids:
            seg = arcs[a] if a >= 0 else arcs[~a][::-1]
            out += seg if not out else seg[1:]
        return out

    out = []
    for g in t["objects"]["countries"]["geometries"]:
        code = EXTRAS.get(g["properties"]["name"])
        if not code:
            continue
        polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
        rings = []
        for poly in polys:
            r = clean_ring(ring(poly[0]))
            if len(r) >= 4:
                if ring_area(r) > 0:
                    r.reverse()
                rings.append([r])
        if not rings:  # Troppo piccolo per la griglia: un quadratino, così il territorio esiste anche a bassa scala
            x, y = clean_ring(ring(polys[0][0]))[0]
            rings = [[[(x - 1, y - 1), (x - 1, y + 1), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y - 1)]]]
        out.append({"c": code, "s": START, "e": END, "polys": rings})
    return out


def main(src, dst, tol_deg, atlas=None):
    feats = []
    for f in json.load(open(src, encoding="utf8"))["features"]:
        p = f["properties"]
        s = p["gwsyear"] * 12 + p["gwsmonth"] - 1
        e = p["gweyear"] * 12 + p["gwemonth"] - 1
        if e < START or s > END:
            continue
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        rings = []
        for poly in polys:
            out = []
            for i, ring in enumerate(poly):
                r = clean_ring(ring)
                if len(r) < 4:
                    continue
                # d3-geo vuole l'esterno in senso orario e i buchi in senso antiorario
                if (ring_area(r) > 0) == (i == 0):
                    r.reverse()
                out.append(r)
            if out:
                rings.append(out)
        feats.append({"c": p["gwcode"], "s": s, "e": e, "polys": rings})

    feats += atlas_extras(atlas) if atlas else []
    korea_on_parallel(feats)
    if atlas and VAR == "BORDERS_HI":
        island = cyprus_rings(atlas)
        print("Cipro:", len(island), "anelli,", sum(len(p[0]) for p in island), "punti")
        for f in feats:
            if f["c"] == 352:
                f["polys"] = island

    # Giunzioni: un punto con vicini diversi tra le sue occorrenze separa due archi
    neigh, junction = {}, set()
    codes = {}  # punto -> codice che lo usa, o 0 se ne usano più d'uno: un punto con un solo codice è costa
    for f in feats:
        for poly in f["polys"]:
            for r in poly:
                n = len(r) - 1
                for i in range(n):
                    was = codes.get(r[i])
                    codes[r[i]] = f["c"] if was is None or was == f["c"] else 0
                    pair = frozenset((r[i - 1] if i else r[n - 1], r[i + 1]))
                    seen = neigh.get(r[i])
                    if seen is None:
                        neigh[r[i]] = pair
                    elif seen != pair:
                        junction.add(r[i])
    del neigh

    tol = tol_deg * Q
    arcs, index = [], {}
    conflator = Conflator(atlas) if atlas and VAR == "BORDERS_HI" else None

    def add_arc(pts, closed):
        key = tuple(pts)
        if key in index:
            return index[key]
        rkey = key[::-1]
        if rkey in index:
            return ~index[rkey]
        # Le isole coreane vengono già da OSM: Natural Earth ne taglierebbe pezzi interi
        if conflator and pts[0] not in ISLAND_PTS:
            mid = pts[len(pts) // 2]
            pts = conflator.apply(pts, closed, codes.get(mid, 0) != 0)
        # Gli isolotti hanno bisogno di una tolleranza più fine, o diventano triangoli
        arc_tol = tol / 4 if pts[0] in ISLAND_PTS else tol
        simple = simplify_closed(pts, arc_tol) if closed else douglas_peucker(pts, arc_tol)
        arcs.append(simple)
        index[key] = len(arcs) - 1
        return index[key]

    def canonical_closed(r):
        pts = r[:-1]
        i = pts.index(min(pts))
        rot = pts[i:] + pts[:i]
        rev = [rot[0]] + rot[1:][::-1]
        if rev[1] < rot[1]:
            return rev + [rev[0]], True
        return rot + [rot[0]], False

    def ring_arcs(r):
        cuts = [i for i in range(len(r) - 1) if r[i] in junction]
        if not cuts:
            pts, flipped = canonical_closed(r)
            a = add_arc(pts, True)
            return [~a if flipped else a]
        pts = r[cuts[0]:-1] + r[: cuts[0] + 1]
        out, start = [], 0
        for i in range(1, len(pts)):
            if pts[i] in junction:
                out.append(add_arc(pts[start: i + 1], False))
                start = i
        return out

    def decoded(ids):
        pts = []
        for a in ids:
            seg = arcs[a] if a >= 0 else arcs[~a][::-1]
            pts += seg if not pts else seg[1:]
        return pts

    geoms = []
    for f in feats:
        kept = []
        for poly in f["polys"]:
            ids = [ring_arcs(r) for r in poly]
            # Il tracciato sostituito può avere verso opposto: un anello invertito riempirebbe tutto il globo
            for i, ring_ids in enumerate(ids):
                a = ring_area(decoded(ring_ids))
                if (a > 0) == (i == 0):
                    ids[i] = [~x for x in reversed(ring_ids)]
            kept.append((ids, abs(ring_area(decoded(ids[0]))) if ids else 0))
        biggest = max((a for _, a in kept), default=0)
        coords = []
        for ids, area in kept:
            # Un anello collassato dalla semplificazione ha area zero e per d3 riempirebbe tutto il globo
            if area >= MIN_AREA or area == biggest or (f["c"] in (730, 731, 732) and KOREA_BOUNDS and area >= 4) or (f["c"] >= 3900 and area >= 4):
                coords.append([ids[0]] + [h for h in ids[1:] if abs(ring_area(decoded(h))) >= MIN_AREA * 4])
        geoms.append({"type": "MultiPolygon", "arcs": coords, "c": f["c"], "s": f["s"], "e": f["e"]})

    # Rimuove gli archi non referenziati e li codifica in delta
    used = {}

    def remap(x):
        if isinstance(x, list):
            return [remap(v) for v in x]
        a = x if x >= 0 else ~x
        if a not in used:
            used[a] = len(used)
        return used[a] if x >= 0 else ~used[a]

    for g in geoms:
        g["arcs"] = remap(g["arcs"])
    out_arcs = [None] * len(used)
    for old, new in used.items():
        pts = arcs[old]
        d = [list(pts[0])]
        for a, b in zip(pts, pts[1:]):
            d.append([b[0] - a[0], b[1] - a[1]])
        out_arcs[new] = d

    topo = {
        "type": "Topology",
        "transform": {"scale": [1 / Q, 1 / Q], "translate": [-180, -90]},
        "objects": {"states": {"type": "GeometryCollection", "geometries": [
            {"type": "MultiPolygon", "arcs": g["arcs"], "properties": {"c": g["c"], "s": g["s"], "e": g["e"]}} for g in geoms
        ]}},
        "arcs": out_arcs,
    }
    text = f"window.{VAR}=" + json.dumps(topo, separators=(",", ":")) + ";\n"
    with open(dst, "w", encoding="utf8") as h:
        h.write(text)
    if ISLAND_LOG and VAR == "BORDERS_HI":
        with open("tools/korea_islands_report.txt", "w", encoding="utf8") as h:
            h.write("motivo\tlat\tlon\tkm2\tstato\n")
            for row in sorted(set(ISLAND_LOG), key=lambda r: (r[0], r[1])):
                h.write("\t".join(str(v) for v in row[:5]) + "\n")
        res = {}
        for row in set(ISLAND_LOG):
            res[row[0].split(":")[0]] = res.get(row[0].split(":")[0], 0) + 1
        print("isole coreane:", res)
    if conflator:
        print("archi da Natural Earth e rimasti CShapes:", conflator.stats)
    print(len(geoms), "feature,", len(out_arcs), "archi,", sum(map(len, out_arcs)), "punti,", round(len(text) / 1e6, 2), "MB")


if __name__ == "__main__":
    # Parametri facoltativi per la versione ad alta risoluzione: griglia per grado, area minima in gradi quadrati, nome della variabile
    if len(sys.argv) > 5:
        Q = int(sys.argv[5])
        MIN_AREA = float(sys.argv[6]) * Q * Q
        VAR = sys.argv[7]
        EXTRA_LINES = sys.argv[8:]
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.015, sys.argv[4] if len(sys.argv) > 4 else None)
