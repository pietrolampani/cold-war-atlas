"""Coste precise (OpenStreetMap) per i punti chiave della Guerra Fredda. Scrive coasts.js.

Per ogni riquadro: scarica le coste, le cuce e costruisce la terra ritagliata sul riquadro.
OSM tiene la terra a sinistra del verso della costa: i capi aperti si chiudono seguendo il bordo.

Uso: python -I tools/build_coasts.py cartella_cache coasts.js
"""
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request

# nome, stato (codice), ovest, est, sud, nord
PATCHES = [
    ("Malta", 338, 14.1, 14.65, 35.75, 36.12),
    ("Hong Kong", 710, 113.8, 114.45, 22.15, 22.6),
    ("Singapore", 830, 103.55, 104.15, 1.15, 1.52),
    ("Aden", 681, 44.75, 45.25, 12.7, 12.95),
    ("Guantánamo", 40, -75.35, -74.95, 19.82, 20.08),
    ("Baia dei Porci", 40, -81.6, -80.85, 21.9, 22.5),
    ("Sebastopoli", 365, 33.3, 33.8, 44.4, 44.8),
    ("Kronštadt", 365, 29.5, 30.4, 59.8, 60.1),
    ("Murmansk", 365, 32.9, 33.9, 68.95, 69.5),
    ("Cam Ranh", 816, 109.0, 109.4, 11.75, 12.15),
    ("Da Nang", 816, 108.05, 108.4, 15.9, 16.25),
    ("Inchon", 732, 126.3, 126.8, 37.25, 37.65),
    ("Porto Said", 651, 32.15, 32.5, 31.1, 31.4),
    ("Suez", 651, 32.4, 32.7, 29.85, 30.05),
    ("Pearl Harbor", 4, -158.1, -157.8, 21.25, 21.45),
    ("Kuwait", 690, 47.8, 48.45, 29.0, 29.55),
]
MIRRORS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]


def fetch(cache, p):
    path = os.path.join(cache, f"coast_{p[0].encode('ascii', 'ignore').decode().replace(' ', '_')}.json")
    if os.path.exists(path):
        return json.load(open(path, encoding="utf8"))["elements"]
    q = f'[out:json][timeout:120];way["natural"="coastline"]({p[4]},{p[2]},{p[5]},{p[3]});out geom;'
    body = urllib.parse.urlencode({"data": q}).encode()
    for attempt in range(6):
        try:
            req = urllib.request.Request(MIRRORS[attempt % 2], body, {"User-Agent": "ColdWarAtlas/1.0 (personal history map)", "Accept": "*/*"})
            data = urllib.request.urlopen(req, timeout=170).read()
            with open(path, "wb") as h:
                h.write(data)
            time.sleep(3)
            return json.loads(data)["elements"]
        except Exception as e:
            print(p[0], e, flush=True)
            time.sleep(15)
    return []


def thin(pts, tol):
    out = [pts[0]]
    k = math.cos(math.radians(pts[0][1]))
    for q in pts[1:-1]:
        if math.hypot((q[0] - out[-1][0]) * k, q[1] - out[-1][1]) * 111320 >= tol:
            out.append(q)
    return out + [pts[-1]] if pts[-1] != out[-1] else out


def inside(p, b):
    return b[0] <= p[0] <= b[1] and b[2] <= p[1] <= b[3]


def crossing(a, b, box):
    """Punto in cui il segmento a->b (a dentro, b fuori) esce dal riquadro."""
    t = 1.0
    w, e, s, n = box
    dx, dy = b[0] - a[0], b[1] - a[1]
    if dx > 0:
        t = min(t, (e - a[0]) / dx)
    elif dx < 0:
        t = min(t, (w - a[0]) / dx)
    if dy > 0:
        t = min(t, (n - a[1]) / dy)
    elif dy < 0:
        t = min(t, (s - a[1]) / dy)
    return (a[0] + dx * t, a[1] + dy * t)


def perim(p, box):
    """Posizione lungo il bordo in senso antiorario, partendo da sud-ovest."""
    w, e, s, n = box
    W, H = e - w, n - s
    if abs(p[1] - s) < 1e-9:
        return p[0] - w
    if abs(p[0] - e) < 1e-9:
        return W + p[1] - s
    if abs(p[1] - n) < 1e-9:
        return W + H + e - p[0]
    return 2 * W + H + n - p[1]


def build(elements, box):
    ways = [[(n["lon"], n["lat"]) for n in e["geometry"]] for e in elements if e.get("geometry")]
    starts = {w[0]: w for w in ways if w[0] != w[-1]}
    rings = [w for w in ways if w[0] == w[-1]]
    used, chains = set(), []
    ends = {w[-1] for w in starts.values()}
    heads = [k for k in starts if k not in ends] or list(starts)[:0]
    for head in heads + list(starts):
        if head in used or head not in starts:
            continue
        line, cur = [], head
        while cur in starts and cur not in used:
            used.add(cur)
            w = starts[cur]
            line += w if not line else w[1:]
            cur = w[-1]
        (rings if line[0] == line[-1] else chains).append(line)
    # Ritaglio: ogni tratto dentro il riquadro diventa un arco da bordo a bordo
    arcs, closed = [], []
    for ln in chains + rings:
        cur = []
        whole = all(inside(p, box) for p in ln)
        if whole and ln[0] == ln[-1]:
            closed.append(ln)
            continue
        for a, b in zip(ln, ln[1:]):
            ia, ib = inside(a, box), inside(b, box)
            if ia:
                cur.append(a)
            if ia and not ib:
                cur.append(crossing(a, b, box))
                arcs.append(cur)
                cur = []
            elif ib and not ia:
                cur = [crossing(b, a, box)]
        if cur and inside(ln[-1], box):
            cur.append(ln[-1])
            arcs.append(cur)
    land = list(closed)
    pending = [a for a in arcs if len(a) >= 2]
    corners = [(box[1], box[2]), (box[1], box[3]), (box[0], box[3]), (box[0], box[2])]
    corner_pos = [(perim(c, box), c) for c in corners]
    total = 2 * (box[1] - box[0] + box[3] - box[2])
    while pending:
        ring = list(pending.pop())
        for _ in range(len(pending) + 2):
            end = perim(ring[-1], box)
            # La terra è a sinistra: dal punto d'uscita si segue il bordo in senso antiorario
            best, dist = None, total + 1
            for i, a in enumerate(pending + [ring]):
                d = (perim(a[0], box) - end) % total
                if d < dist and (a is not ring or len(ring) > 2):
                    best, dist = i, d
            for pos, c in sorted(corner_pos, key=lambda x: (x[0] - end) % total):
                if (pos - end) % total < dist and (pos - end) % total > 0:
                    ring.append(c)
            if best == len(pending):
                break
            ring += pending.pop(best)
        land.append(ring + [ring[0]])
    return land


def main(cache, dst):
    os.makedirs(cache, exist_ok=True)
    out = []
    for p in PATCHES:
        els = fetch(cache, p)
        if not els:
            print(p[0], "nessun dato")
            continue
        box = (p[2], p[3], p[4], p[5])
        land = build(els, box)
        rings = [[[round(x, 5), round(y, 5)] for x, y in thin(r, 40)] for r in land if len(r) > 8]
        out.append({"n": p[0], "c": p[1], "box": list(box), "land": rings})
        print(p[0], len(els), "tratti,", len(rings), "anelli,", sum(map(len, rings)), "punti", flush=True)
    with open(dst, "w", encoding="utf8") as h:
        h.write("window.COASTS=" + json.dumps(out, separators=(",", ":"), ensure_ascii=False) + ";\n")
    print("coasts.js", round(os.path.getsize(dst) / 1000), "KB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
