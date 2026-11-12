"""Zona di occupazione sovietica in Germania (1945-1949) dai confini OSM dei Länder orientali.

Mecklenburg-Vorpommern, Brandenburg, Sachsen-Anhalt, Thüringen, Sachsen e Berlin (relazioni OSM 28322, 62504, 62607, 62366,
62467, 62422), scaricati da polygons.openstreetmap.fr senza semplificazione. L'unione si fa annullando i lati in comune
(i confini tra Länder sono le stesse vie OSM, quindi gli stessi vertici), poi si ricuciono gli anelli e si semplificano a circa 100 m.
Il confine tra le zone coincide con quello odierno tra Länder orientali e occidentali, con le piccole differenze del 1945
(lo scambio di Barber-Ljaščenko del novembre 1945, il Wanfrieder Abkommen del 1945) trascurate.

Le zone occidentali si ritagliano su tutta la Germania (Natural Earth): la zona sovietica, sopra, dà il confine esatto.

Uso: python -I tools/build_soviet_zone.py cartella_poligoni atlas10.json territories.js occupation.js
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_manchukuo import simplify  # noqa: E402
from build_ww2_atlas import atlas_rings  # noqa: E402
from fetch_ohm import area_km2  # noqa: E402

IDS = [28322, 62504, 62607, 62366, 62467, 62422]


def rings_of(geo):
    g = geo.get("geometries", [geo]) if geo.get("type") == "GeometryCollection" else [geo]
    out = []
    for x in g:
        polys = x["coordinates"] if x["type"] == "MultiPolygon" else [x["coordinates"]] if x["type"] == "Polygon" else []
        for p in polys:
            out += p  # anelli esterni e buchi: i buchi tra Länder non ci sono, quelli interni restano
    return out


def main(folder, atlas, territories, dst):
    count = defaultdict(int)
    for i in IDS:
        for r in rings_of(json.load(open(os.path.join(folder, f"{i}.geojson"), encoding="utf8"))):
            pts = [(round(p[0], 7), round(p[1], 7)) for p in r]
            for a, b in zip(pts, pts[1:]):
                if a != b:
                    count[(a, b) if a < b else (b, a)] += 1
    nxt = defaultdict(list)
    for (a, b), n in count.items():
        if n == 1:
            nxt[a].append(b); nxt[b].append(a)
    rings, seen = [], set()
    for start in list(nxt):
        for first in nxt[start]:
            e = (start, first) if start < first else (first, start)
            if e in seen:
                continue
            ring, prev, cur = [start], start, first
            seen.add(e)
            while cur != start:
                ring.append(cur)
                cand = [q for q in nxt[cur] if ((cur, q) if cur < q else (q, cur)) not in seen]
                if not cand:
                    break
                q = cand[0]
                seen.add((cur, q) if cur < q else (q, cur))
                prev, cur = cur, q
            if cur == start and len(ring) > 3:
                rings.append([list(p) for p in ring] + [list(start)])
    rings.sort(key=area_km2, reverse=True)

    def rs(r, tol=0.001):
        k = max(range(len(r)), key=lambda i: (r[i][0] - r[0][0]) ** 2 + (r[i][1] - r[0][1]) ** 2)
        return simplify(r[:k + 1], tol) + simplify(r[k:], tol)[1:]
    zone = [rs(r) for r in rings if area_km2(r) > 1]
    print("anelli", len(zone), "km2", [round(area_km2(r)) for r in zone[:4]], "punti", sum(map(len, zone)))
    text = open(territories, encoding="utf8").read()
    terr = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if x["n"] != "Zona di occupazione sovietica"]
    for x in terr:  # le zone occidentali e i loro fondi si ritagliano su tutta la Germania
        if x.get("occ") and x.get("clip") == 260:
            x.pop("clip"); x["clipKey"] = "germanyAll"
    terr.append({"n": "Zona di occupazione sovietica", "from": "1945-05", "to": "1949-09", "look": "st-s", "rings": zone, "clipKey": "germanyAll", "z": 1.5, "occ": 1,
                 "d": "Germania orientale sotto l'amministrazione militare sovietica (SMAD) fino alla nascita della DDR, il 7 ottobre 1949. "
                      "Confine dai Länder orientali di OpenStreetMap, che ricalcano la linea di demarcazione del 1945."})
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr, separators=(",", ":"), ensure_ascii=False) + ";\n")
    de = [r for r in atlas_rings(atlas, ["Germany"]) if len(r) >= 3]
    with open(dst, "w", encoding="utf8") as h:
        h.write("/* Ritaglio per le zone di occupazione in Germania: tutta la Germania (Natural Earth). */\n"
                f"window.TERR_CLIPS = Object.assign(window.TERR_CLIPS || {{}}, {{ germanyAll: {json.dumps(de, separators=(',', ':'))} }});\n")


if __name__ == "__main__":
    main(*sys.argv[1:5])
