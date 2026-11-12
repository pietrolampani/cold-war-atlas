"""Confine tra le due Germanie (1949-1990) preciso, dai Länder orientali di OpenStreetMap.

La carta di base (CShapes) disegna la linea tra RFT e RDT con pochi vertici. Qui si riusa l'unione OSM dei Länder orientali
(la stessa della zona sovietica, costruita da build_soviet_zone.py): la RDT si disegna sopra con quei confini, la RFT sotto
come fondo che riempie tutta la Germania. Entrambe si ritagliano su tutta la Germania (Natural Earth), come le zone 1945-1949.
I colori vengono dal codice dello Stato, quindi seguono lo stato del mese (allineamento, leader, ecc.).

Uso: python -I tools/build_german_border.py territories.js
"""
import json
import sys


def main(territories):
    text = open(territories, encoding="utf8").read()
    terr = json.loads(text.split("=", 1)[1].rstrip().rstrip(";"))
    terr = [x for x in terr if x.get("tag") != "de2"]
    zone = next(x for x in terr if x["n"] == "Zona di occupazione sovietica")
    box = next(x for x in terr if x.get("occbase") and x["n"] == "Trizona")["rings"]
    terr.append({"n": "Repubblica Federale di Germania", "from": "1949-06", "to": "1990-09", "code": 260, "cls": "t-fill", "rings": box,
                 "clipKey": "germanyAll", "z": 0.9, "tag": "de2", "pass": 1})
    terr.append({"n": "Repubblica Democratica Tedesca", "from": "1949-10", "to": "1990-09", "code": 265, "rings": zone["rings"],
                 "clipKey": "germanyAll", "z": 1.5, "tag": "de2", "pass": 1,
                 "d": "Confine interno tedesco dai Länder orientali di OpenStreetMap, che ricalcano la linea di demarcazione del 1945."})
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr, separators=(",", ":"), ensure_ascii=False) + ";\n")
    print("ok", len(zone["rings"]), "anelli RDT")


if __name__ == "__main__":
    main(sys.argv[1])
