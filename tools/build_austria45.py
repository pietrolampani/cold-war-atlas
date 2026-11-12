"""Austria, maggio-luglio 1945: le occupazioni prima dell'assetto definitivo delle zone.

- Stiria: l'Armata Rossa tenne la Stiria (Graz compresa) fino al 24 luglio 1945, poi passò ai britannici. Nel frattempo i
  britannici, arrivati dalla Carinzia, tenevano il distretto di Murau e gli americani l'Ennstal (distretto di Liezen).
  I limiti interni sono approssimati con i distretti di oggi: la linea reale passava per il ponte sulla Mura a Judenburg.
- Tirolo: occupato dalla 7ª Armata americana a inizio maggio, consegnato ai francesi all'inizio di luglio 1945.
  Il Vorarlberg fu francese da subito.
- Mühlviertel: occupato dagli americani fino al 1° agosto 1945, poi sovietico. Urfahr, la parte di Linz a nord del Danubio,
  si ritaglia sulla zona sovietica.

A risoluzione mensile vale lo stato a metà mese: Tirolo americano a maggio-giugno, Stiria sovietica e Mühlviertel americano
fino a luglio. Confini da OpenStreetMap (polygons.openstreetmap.fr), ritagliati sulle zone definitive.

Uso: python -I tools/build_austria45.py cartella_poligoni territories.js occupation.js
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_occupation import ring_simplify  # noqa: E402
from fetch_ohm import area_km2  # noqa: E402

TAG = "at45"


def rings_of(folder, rel):
    g = json.load(open(os.path.join(folder, f"{rel}.geojson"), encoding="utf8"))
    out = []
    for x in g.get("geometries", [g]):
        for p in (x["coordinates"] if x["type"] == "MultiPolygon" else [x["coordinates"]]):
            out.append(p[0])  # solo anelli esterni
    return out


def union(folder, rels):
    """Unione di poligoni adiacenti annullando i lati in comune (vie OSM condivise, stessi vertici)."""
    count = defaultdict(int)
    for rel in rels:
        for r in rings_of(folder, rel):
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
            ring, cur = [start], first
            seen.add(e)
            while cur != start:
                ring.append(cur)
                cand = [q for q in nxt[cur] if ((cur, q) if cur < q else (q, cur)) not in seen]
                if not cand:
                    break
                seen.add((cur, cand[0]) if cur < cand[0] else (cand[0], cur))
                cur = cand[0]
            if cur == start and len(ring) > 3:
                rings.append([list(p) for p in ring] + [list(start)])
    return [ring_simplify(r, 0.0005) for r in rings if area_km2(r) > 1]


def main(folder, territories, occupation):
    text = open(territories, encoding="utf8").read()
    terr = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if x.get("tag") != TAG]
    zone = lambda n: next(x for x in terr if x["n"] == n)["rings"]
    clips = {"atUK": zone("Zona di occupazione britannica in Austria"), "atFR": zone("Zona di occupazione francese in Austria"),
             "atSU": zone("Zona di occupazione sovietica in Austria")}
    E = lambda n, a, b, look, rings, clip, z, d: terr.append({"n": n, "from": a, "to": b, "look": look, "rings": rings, "clipKey": clip, "z": z,
                                                              "occ": 1, "tag": TAG, "d": d + " Confini da OpenStreetMap."})
    E("Stiria sotto occupazione sovietica", "1945-05", "1945-07", "st-s", union(folder, [35183]), "atUK", 1.1,
      "L'Armata Rossa tenne la Stiria, Graz compresa, fino al 24 luglio 1945, quando la consegnò ai britannici. "
      "La linea con i britannici passava per il ponte sulla Mura a Judenburg: qui è approssimata con il distretto di Murau.")
    E("Distretto di Liezen sotto occupazione americana", "1945-05", "1945-07", "oc-us", union(folder, [50587]), "atUK", 1.2,
      "La 3ª Armata americana occupò l'Ennstal e si congiunse ai sovietici a Liezen; il distretto passò ai britannici con il resto della Stiria (luglio 1945).")
    E("Distretto di Murau sotto occupazione britannica", "1945-05", "1945-07", "oc-uk", union(folder, [50802]), "atUK", 1.2,
      "Le truppe britanniche venute dalla Carinzia occuparono la Stiria occidentale fino alla linea della Mura a Judenburg.")
    E("Tirolo sotto occupazione americana", "1945-05", "1945-06", "oc-us", union(folder, [52343]), "atFR", 1.1,
      "La 7ª Armata americana occupò il Tirolo settentrionale a inizio maggio 1945 e lo consegnò ai francesi all'inizio di luglio. "
      "Il Vorarlberg fu francese da subito; il Tirolo orientale, britannico.")
    E("Mühlviertel sotto occupazione americana", "1945-05", "1945-07", "oc-us", union(folder, [107941, 86257, 422468, 128117, 86708]), "atSU", 1.1,
      "Gli americani occuparono l'Alta Austria a nord del Danubio e la consegnarono all'Armata Rossa il 1° agosto 1945. "
      "Urfahr, la parte di Linz a nord del fiume, restò poi sovietica fino al 1955.")
    for x in terr[-5:]:
        print(x["n"], len(x["rings"]), "anelli", sum(map(len, x["rings"])), "punti")
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr, separators=(",", ":"), ensure_ascii=False) + ";\n")
    own = ("/* Zone austriache",) + tuple(f"window.TERR_CLIPS.{k} " for k in clips)
    occ = "\n".join(l for l in open(occupation, encoding="utf8").read().rstrip("\n").split("\n") if not l.startswith(own))
    occ += "\n/* Zone austriache definitive: ritaglio per le occupazioni di maggio-luglio 1945. */\n"
    for k, v in clips.items():
        occ += f"window.TERR_CLIPS.{k} = {json.dumps(v, separators=(',', ':'))};\n"
    with open(occupation, "w", encoding="utf8") as h:
        h.write(occ)


if __name__ == "__main__":
    main(*sys.argv[1:4])
