"""Guerra delle Sabbie (Marocco-Algeria), ottobre 1963 - febbraio 1964, dal video "The Sand War: Every Day".

sands_video_frames.txt viene dal browser: "secondo:contorni" dell'area rosso acceso (Algeria occupata dal Marocco)
sul fotogramma 1920x1080 intero; coppie di caratteri base 64 per x e y. Il video avanza di un giorno al secondo
(25 settembre 1963 al secondo 15, 2 novembre al 55). Si scartano gli anelli a est di x = 1000: sono la rivolta del FFS in Cabilia,
arancione nel video, che non è un'occupazione straniera.
Georeferenziato adattando la costa (tools/fit_coast.py, modello lineare, errore medio 4 pixel; le città del video sono disegnate a occhio e non servono).

Mesi: ottobre 1963 dal fotogramma del 15 ottobre; da novembre 1963 a febbraio 1964 dal fotogramma del 2 novembre:
il cessate il fuoco di Bamako (2-5 novembre) congela le posizioni fino all'accordo del 20 febbraio 1964 sulla zona smilitarizzata.

Uso: python -I tools/build_sands.py sands_video_frames.txt atlas10.json territories.js sands.js
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_ww2_atlas import atlas_rings  # noqa: E402

A = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
FIT = (70.6391, 1033.7467, -59.8796, 2272.5254)  # x = a·lon + b, y = c·lat + d (errore medio 4,2 px sulla costa)
SPANS = {"35": ("1963-10", "1963-10", "15 ottobre 1963"), "55": ("1963-11", "1964-02", "2 novembre 1963")}


def to_ll(x, y):
    a, b, c, d = FIT
    return [round((x - b) / a, 4), round((y - d) / c, 4)]


def main(src, atlas, territories, dst):
    entries = []
    for chunk in open(src, encoding="utf8").read().strip().split(";"):
        t, body = chunk.split(":", 1)
        rings = []
        for ring in body.split(","):
            pts = [(A.index(ring[i]) * 64 + A.index(ring[i + 1]), A.index(ring[i + 2]) * 64 + A.index(ring[i + 3])) for i in range(0, len(ring) - 3, 4)]
            if len(pts) >= 3 and sum(p[0] for p in pts) / len(pts) < 1000:
                rings.append([to_ll(x, y) for x, y in pts])
        start, end, day = SPANS[t]
        extra = (" Dal cessate il fuoco di Bamako (2-5 novembre) le posizioni restano congelate fino all'accordo del 20 febbraio 1964 "
                 "sulla zona smilitarizzata; poi le truppe tornano sulle linee di partenza.") if start != end else ""
        entries.append({"n": "Occupazione marocchina", "from": start, "to": end, "code": 600, "cls": "t-occ", "rings": rings, "sand": 1, "clipKey": "sands",
                        "d": "Territorio algerino tenuto dalle forze marocchine (Hassi Beida, Tinjoub e la zona a sud di Tagounit), "
                             f"secondo il video \"The Sand War: Every Day\", fotogramma del {day}. Contorni indicativi." + extra})
    text = open(territories, encoding="utf8").read()
    terr = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("sand")]
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr + entries, separators=(",", ":"), ensure_ascii=False) + ";\n")
    clip = [r for r in atlas_rings(atlas, ["Algeria"]) if len(r) >= 3]
    with open(dst, "w", encoding="utf8") as h:
        h.write("/* Ritaglio per l'occupazione marocchina nella Guerra delle Sabbie: solo l'Algeria. */\n"
                f"window.TERR_CLIPS = Object.assign(window.TERR_CLIPS || {{}}, {{ sands: {json.dumps(clip, separators=(',', ':'))} }});\n")
    print(len(entries), "voci;", [len(e["rings"]) for e in entries], "anelli;", [[r[0] for r in e["rings"]] for e in entries])


if __name__ == "__main__":
    main(*sys.argv[1:5])
