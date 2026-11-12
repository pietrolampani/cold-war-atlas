"""Trova dove le strade note di Gorizia incrociano il confine: geometria da Nominatim, confine da world_borders.json.

Uso: python -I tools/find_gorizia_crossings.py world_borders.json
"""
import json
import math
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "ColdWarAtlas/1.0 (personal history map)"}
QUERIES = ["Erjavčeva ulica, Nova Gorica", "Via Giuseppe Brass, Gorizia", "Via Salcano, Gorizia", "Via del Santo, Gorizia", "Vrtojbenska cesta, Šempeter pri Gorici", "Via Sant'Anna, Gorizia",
           "Goriška cesta, Solkan", "Via Vittorio Veneto, Gorizia", "Via Trieste, Gorizia", "Prvomajska ulica, Nova Gorica", "Kolodvorska pot, Nova Gorica", "Šempeter pri Gorici", "Solkan", "Pristava, Nova Gorica", "Piedimonte, Gorizia", "valico confine Gorizia", "mejni prehod Nova Gorica", "dogana Gorizia", "border_control Gorizia"]


def border(world):
    out = []
    for r in json.load(open(world))["elements"]:
        g = [(p["lon"], p["lat"]) for p in r["geometry"]]
        if any(13.55 < x < 13.72 and 45.88 < y < 46.02 for x, y in g):
            out += list(zip(g, g[1:]))
    return out


def cross(a, b, c, d):
    den = (b[0] - a[0]) * (d[1] - c[1]) - (b[1] - a[1]) * (d[0] - c[0])
    if not den:
        return None
    t = ((c[0] - a[0]) * (d[1] - c[1]) - (c[1] - a[1]) * (d[0] - c[0])) / den
    u = ((c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])) / den
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])) if 0 <= t <= 1 and 0 <= u <= 1 else None


def lines(geo):
    t, c = geo["type"], geo["coordinates"]
    return [c] if t == "LineString" else c if t == "MultiLineString" else []


def near(p, segs):
    k = math.cos(math.radians(p[1]))
    return min(math.hypot((p[0] - s[0][0]) * k, p[1] - s[0][1]) for s in segs) * 111.32


def main(world):
    segs = border(world)
    print("tratti di confine", len(segs))
    for q in QUERIES:
        url = "https://nominatim.openstreetmap.org/search?format=jsonv2&polygon_geojson=1&limit=6&countrycodes=it,si&viewbox=13.55,46.02,13.72,45.88&bounded=1&q=" + urllib.parse.quote(q)
        try:
            rows = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read())
        except Exception as ex:
            print(q, "ERRORE", ex)
            time.sleep(2)
            continue
        hits, info = set(), []
        for r in rows:
            p = (float(r["lon"]), float(r["lat"]))
            name = (r.get("display_name") or "")[:45]
            info.append(f'{r.get("category")}/{r.get("type")} {p[1]:.5f},{p[0]:.5f} a {near(p, segs):.2f} km {name}')
            for ln in lines(r.get("geojson", {"type": "x", "coordinates": []})):
                for a, b in zip(ln, ln[1:]):
                    for c, d in segs:
                        x = cross(tuple(a[:2]), tuple(b[:2]), c, d)
                        if x:
                            hits.add((round(x[1], 5), round(x[0], 5)))
        print(q, "| incroci", sorted(hits), "|", "; ".join(info[:3]), flush=True)
        time.sleep(1.5)


if __name__ == "__main__":
    main(sys.argv[1])
