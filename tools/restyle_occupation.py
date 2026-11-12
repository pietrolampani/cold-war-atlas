"""Zone e settori alleati con le tinte nazionali piene, e Vienna a piena risoluzione.

- Tinte: britannici viola (oc-uk), americani blu (oc-us), francesi arancione (oc-fr); i sovietici restano st-s.
  Valgono per le zone in Germania e Austria e per i settori di Berlino e Vienna.
- Germania: ogni zona occidentale resta della sua potenza fino alla nascita della RFT (maggio 1949). Bizona (1947) e Trizona
  (1948) erano fusioni economiche: i governi militari restarono distinti, quindi le zone tengono il loro colore e le due
  fusioni si citano nella descrizione invece di ricoprire tutto di blu.
- Vienna: settori dall'unione dei distretti OSM con tolleranza ~2 m (prima ~50 m), più i confini dei 23 distretti e i loro
  baricentri per i numeri romani.

Uso: python -I tools/restyle_occupation.py cartella_ohm territories.js occupation.js
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_occupation import VIENNA, VIENNA_NAMES, union  # noqa: E402

LOOK = {"emp-uk": "oc-uk", "emp-fr": "oc-fr", "st-U": "oc-us"}
KEY = {"americano": "us", "britannico": "uk", "francese": "fr", "sovietico": "su"}
BIZ = (" Dal gennaio 1947 la zona fu unita economicamente a quella americana nella Bizona, dall'agosto 1948 anche alla francese"
       " nella Trizona; il governo militare restò britannico fino alla RFT.")


def centroid(r):
    a = cx = cy = 0
    for (x1, y1), (x2, y2) in zip(r, r[1:] + r[:1]):
        c = x1 * y2 - x2 * y1
        a += c; cx += (x1 + x2) * c; cy += (y1 + y2) * c
    return [round(cx / (3 * a), 5), round(cy / (3 * a), 5)]


def main(folder, territories, occupation):
    text = open(territories, encoding="utf8").read()
    terr = json.loads(text.split("=", 1)[1].rstrip().rstrip(";"))
    terr = [x for x in terr if not (x.get("occ") and x["n"] in ("Bizona", "Trizona"))]
    terr = [x for x in terr if x["n"] != "Vienna, distretti"]
    wien = json.load(open(os.path.join(folder, "wien_bezirke.json"), encoding="utf8"))["elements"]
    num = lambda t: VIENNA_NAMES.get(t.get("name")) or (int(t["ref"]) if str(t.get("ref", "")).isdigit() else None)
    for x in terr:
        if not x.get("occ"):
            continue
        parts = x["look"].split()
        x["look"] = " ".join(LOOK.get(p, p) for p in parts)
        n = x["n"]
        # zone occidentali fino al maggio 1949
        if n == "Zona di occupazione britannica" and x["to"] == "1946-12":
            x["to"] = "1949-05"
            if not x.get("occbase"):
                x["d"] = x["d"].split(" Dal gennaio 1947")[0] + BIZ
        if n == "Zona di occupazione americana" and x["to"] == "1946-12":
            x["to"] = "1949-05"
            if not x.get("occbase"):
                x["d"] = x["d"].split(" Dal gennaio 1947")[0] + BIZ.replace("a quella americana", "a quella britannica").replace("britannico fino", "americano fino")
        if n == "Zona di occupazione francese" and x["to"] == "1948-07":
            x["to"] = "1949-05"
            x["d"] = x["d"].split(" Dall'agosto 1948")[0] + " Dall'agosto 1948 unita economicamente alla Bizona nella Trizona; il governo militare restò francese fino alla RFT."
        if n.startswith("Vienna, "):
            k = "int" if "Innere" in n else KEY[n.split()[-1]]
            x["rings"] = union(wien, lambda t, ds=set(VIENNA[k]): num(t) in ds, tol=0.00002)
            print(n, len(x["rings"]), "anelli", sum(map(len, x["rings"])), "punti")
    # un solo fondo per le zone occidentali (copre le fessure tra i poligoni OHM e il confine della Germania)
    terr = [x for x in terr if not (x.get("occbase") and x["n"] == "Zona di occupazione americana")]
    for x in terr:
        if x.get("occbase"):
            x["to"] = "1949-05"
    dist, labels = [], []
    for rel in wien:
        d = num(rel["tags"])
        if not d:
            continue
        rs = union([rel], lambda t: True, tol=0.00002)
        dist += rs
        big = max(rs, key=len)
        labels.append([d] + centroid(big[:-1] if big[0] == big[-1] else big))
    terr.append({"n": "Vienna, distretti", "from": "1945-09", "to": "1955-07", "look": "t-dist", "rings": dist, "z": 2.2, "occ": 1, "pass": 1})
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr, separators=(",", ":"), ensure_ascii=False) + ";\n")
    own = ("/* Distretti di Vienna", "window.VIENNA_DISTRICTS")
    occ = "\n".join(l for l in open(occupation, encoding="utf8").read().rstrip("\n").split("\n") if not l.startswith(own))
    occ += ("\n/* Distretti di Vienna: numero e baricentro (lon, lat) per le etichette in numeri romani. */\n"
            f"window.VIENNA_DISTRICTS = {json.dumps(sorted(labels), separators=(',', ':'))};\n")
    with open(occupation, "w", encoding="utf8") as h:
        h.write(occ)
    print("distretti", len(labels), "anelli", len(dist))


if __name__ == "__main__":
    main(*sys.argv[1:4])
