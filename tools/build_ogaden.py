"""Etiopia occupata dalla Somalia nella guerra dell'Ogaden, luglio 1977 - marzo 1978, dal video "The Ogaden War: Every Week".

ogaden_video_frames.txt viene dal browser: per un fotogramma a metà di ogni mese, "secondo:contorni" dell'area rosso acceso
(territorio etiope preso dalla Somalia) su una griglia dimezzata che parte dal pixel (360, 0) del fotogramma 1920x1080;
coppie di caratteri base 64 per x e y. Georeferenziato adattando la costa del Corno d'Africa (tools/fit_coast.py), errore medio 2 pixel.
Date lette sul fotogramma: 20 luglio 1977 al secondo 13, 14 dicembre al 29, 15 febbraio 1978 al 36 (circa 9,2 giorni al secondo).

Uso: python -I tools/build_ogaden.py ogaden_video_frames.txt atlas10.json territories.js ogaden.js
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_ww2_atlas import atlas_rings  # noqa: E402

A = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
X0, Y0 = 360, 0
FIT = (52.0304, -1511.7922, -52.7457, 791.141)  # x = a·lon + b, y = c·lat + d
MONTH = {"13": ("1977-07", "20 luglio"), "16": ("1977-08", "metà agosto"), "19": ("1977-09", "metà settembre"),
         "22.5": ("1977-10", "metà ottobre"), "26": ("1977-11", "metà novembre"), "29": ("1977-12", "14 dicembre"),
         "32.5": ("1978-01", "metà gennaio"), "36": ("1978-02", "15 febbraio"), "38": ("1978-03", "inizio marzo")}


def main(src, atlas, territories, dst):
    a, b, c, d = FIT
    entries = []
    for chunk in open(src, encoding="utf8").read().strip().split(";"):
        t, body = chunk.split(":", 1)
        rings = []
        for ring in body.split(","):
            pts = [(A.index(ring[i]) * 64 + A.index(ring[i + 1]), A.index(ring[i + 2]) * 64 + A.index(ring[i + 3])) for i in range(0, len(ring) - 3, 4)]
            if len(pts) >= 3:
                rings.append([[round((X0 + 2 * x - b) / a, 4), round((Y0 + 2 * y - d) / c, 4)] for x, y in pts])
        month, day = MONTH[t]
        extra = " Il 9 marzo Siad Barre ordina il ritiro; il 15 la guerra è finita." if month == "1978-03" else ""
        entries.append({"n": "Occupazione somala", "from": month, "to": month, "code": 520, "cls": "t-occ", "rings": rings, "og": 1, "clipKey": "ogaden",
                        "d": "Territorio etiope tenuto dall'esercito somalo e dal Fronte di liberazione della Somalia occidentale, "
                             f"secondo il video \"The Ogaden War: Every Week\", fotogramma del {day}. Contorni semplificati e indicativi." + extra})
    text = open(territories, encoding="utf8").read()
    terr = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("og")]
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr + entries, separators=(",", ":"), ensure_ascii=False) + ";\n")
    clip = [r for r in atlas_rings(atlas, ["Ethiopia"]) if len(r) >= 3]
    with open(dst, "w", encoding="utf8") as h:
        h.write("/* Ritaglio per l'occupazione somala dell'Ogaden: solo l'Etiopia. */\n"
                f"window.TERR_CLIPS = Object.assign(window.TERR_CLIPS || {{}}, {{ ogaden: {json.dumps(clip, separators=(',', ':'))} }});\n")
    print(len(entries), "mesi;", sum(len(r) for e in entries for r in e["rings"]), "punti; ritaglio", len(clip), "anelli")


if __name__ == "__main__":
    main(*sys.argv[1:5])
