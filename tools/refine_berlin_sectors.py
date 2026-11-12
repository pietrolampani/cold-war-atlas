"""Settori di Berlino a piena risoluzione OSM (per gli zoom altissimi del dettaglio).

build_occupation.py semplifica i settori a ~50 m: oltre 2500x i bordi tra settori si vedono a zigzag e lasciano fessure.
Qui si rifà l'unione dei quartieri (Ortsteile) con una tolleranza di ~2 m e si sostituiscono solo gli anelli dei quattro
settori, lasciando date, colori e ritagli (Staaken Ovest) come sono.

Uso: python -I tools/refine_berlin_sectors.py cartella_ohm territories.js
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_occupation import BERLIN, union  # noqa: E402

KEY = {"americano": "us", "britannico": "uk", "francese": "fr"}


def main(folder, territories):
    berlin = json.load(open(os.path.join(folder, "berlin_ortsteile.json"), encoding="utf8"))["elements"]
    west = {n for v in BERLIN.values() for n in v}
    rings = {k: union(berlin, lambda t, names=set(BERLIN[k]): t.get("name") in names, tol=0.00002) for k in BERLIN}
    rings["su"] = union(berlin, lambda t: t.get("name") not in west, tol=0.00002)
    text = open(territories, encoding="utf8").read()
    terr = json.loads(text.split("=", 1)[1].rstrip().rstrip(";"))
    for x in terr:
        if x["n"].startswith("Berlino, settore "):
            x["rings"] = rings[KEY.get(x["n"].split()[-1], "su")]
            print(x["n"], x["from"], len(x["rings"]), "anelli", sum(map(len, x["rings"])), "punti")
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr, separators=(",", ":"), ensure_ascii=False) + ";\n")


if __name__ == "__main__":
    main(*sys.argv[1:3])
