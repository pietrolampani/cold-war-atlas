"""Staaken Ovest fuori dal settore britannico di Berlino dal settembre 1945.

Con l'accordo del 30 agosto 1945 Staaken Ovest passò ai sovietici in cambio della parte di Seeburg con l'aeroporto di Gatow;
dal febbraio 1951 la amministrò la DDR. I quartieri OSM di oggi la contano in Spandau (tornò a Berlino nel 1990), quindi il
settore costruito da build_occupation.py la include. Qui il settore, dal settembre 1945, si ritaglia sul confine di Berlino Ovest
di OpenHistoricalMap (relazione 2692239), che la esclude.

Uso: python -I tools/build_west_staaken.py cartella_ohm territories.js occupation.js
"""
import json
import os
import sys

NAME = "Berlino, settore britannico"
EDGE = "Berlino, confine di Staaken Ovest"


def main(folder, territories, occupation):
    wb = json.load(open(os.path.join(folder, "2692239.json"), encoding="utf8"))["rings"]
    wb = [[[round(p[0], 6), round(p[1], 6)] for p in r] for r in wb]
    text = open(territories, encoding="utf8").read()
    terr = json.loads(text.split("=", 1)[1].rstrip().rstrip(";"))
    base = next(x for x in terr if x["n"] == NAME and "clipKey" not in x)
    terr = [x for x in terr if x["n"] not in (NAME, EDGE)]
    early = dict(base, to="1945-08")
    late = dict(base, **{"from": "1945-09", "to": "1990-09", "clipKey": "westBerlin",
                         "d": base["d"] + " Senza Staaken Ovest, passata ai sovietici il 30 agosto 1945 (confine di Berlino Ovest da OpenHistoricalMap)."})
    # Il ritaglio non ha bordo: la linea del taglio è l'anello di Berlino Ovest ritagliato sul settore
    edge = {"n": EDGE, "from": "1945-09", "to": "1990-09", "look": "t-edge", "rings": wb, "clipKey": "ukBerlin", "z": 2.1, "occ": 1, "pass": 1}
    terr += [early, late, edge]
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr, separators=(",", ":"), ensure_ascii=False) + ";\n")
    own = ("/* Berlino Ovest", "window.TERR_CLIPS.westBerlin", "window.TERR_CLIPS.ukBerlin")
    occ = "\n".join(l for l in open(occupation, encoding="utf8").read().rstrip("\n").split("\n") if not l.startswith(own))
    occ += ("\n/* Berlino Ovest (OpenHistoricalMap 2692239), senza Staaken Ovest: ritaglio del settore britannico dal settembre 1945. */\n"
            f"window.TERR_CLIPS.westBerlin = {json.dumps(wb, separators=(',', ':'))};\n"
            f"window.TERR_CLIPS.ukBerlin = {json.dumps(base['rings'], separators=(',', ':'))};\n")
    with open(occupation, "w", encoding="utf8") as h:
        h.write(occ)
    print("ok", len(wb), "anelli", sum(map(len, wb)), "punti")


if __name__ == "__main__":
    main(*sys.argv[1:4])
