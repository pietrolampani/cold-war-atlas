"""Guerra civile cinese, settembre 1945 - maggio 1950, dal video "The Chinese Civil War (1945 and Beyond): Every Day".

china_video_frames.txt viene dal browser: per un fotogramma a metà di ogni mese, "mese:rossi|blu|magenta" con i contorni
su una griglia dimezzata che parte dal pixel (240, 0) del fotogramma 1920x1080; coppie di caratteri base 64 per x e y.
- rossi: zone comuniste (solo fino a settembre 1949, poi la base della carta è già la Repubblica popolare);
- blu: zone nazionaliste (solo da ottobre 1949: le ultime sacche del Guomindang);
- magenta: occupazione sovietica della Manciuria (fino al ritiro, maggio 1946).
Date: il video avanza di un giorno al fotogramma, circa 6,95 giorni al secondo (24 agosto 1945 al secondo 15,
2 luglio 1946 al 60, 1 marzo 1949 al 200, 12 aprile 1950 al 258); dopo maggio 1950 salta a mesi e anni.
La carta del video è una conica equivalente di Albers (meridiano 101° E, paralleli 25° e 43°), stimata con tools/fit_conic.py
su otto laghi (Balkhash, Issyk-Kul, Alakol, Zaysan, Uvs, Khövsgöl, Qinghai, Khanka) e affinata sulla costa: errore medio 1,85 pixel (circa 7 km).

Uso: python -I tools/build_china.py china_video_frames.txt atlas10.json territories.js chinawar.js
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_ww2_atlas import atlas_rings  # noqa: E402

A = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
X0, Y0 = 240, 0
LON0, P1, P2 = 101, 25, 43
SIM = (1696.2747374319545, 149.57056204154273, 1066.0181030210802, -1924.171173440291)  # affinata sulla costa (tools/refine_conic.py): 1,85 px
SRC = "secondo il video \"The Chinese Civil War (1945 and Beyond): Every Day\", fotogramma di metà {m}. Contorni semplificati e indicativi."


def inverse():
    f1, f2 = math.radians(P1), math.radians(P2)
    n = (math.sin(f1) + math.sin(f2)) / 2
    C = math.cos(f1) ** 2 + 2 * n * math.sin(f1)
    a, b, tx, ty = SIM
    k = a * a + b * b

    def to_ll(u, v):
        X = (a * (u - tx) + b * (v - ty)) / k
        Y = (-b * (u - tx) + a * (v - ty)) / k
        x, y = X, -Y  # la proiezione ha y verso nord
        rho = math.hypot(x, y)
        th = math.atan2(x, -y)
        lon = LON0 + math.degrees(th / n)
        lat = math.degrees(math.asin(max(-1, min(1, (C - (rho * n) ** 2) / (2 * n)))))
        return [round(lon, 4), round(lat, 4)]
    return to_ll


def rings_of(body, to_ll, step=2):
    out = []
    for ring in body.split(","):
        pts = [(A.index(ring[i]) * 64 + A.index(ring[i + 1]), A.index(ring[i + 2]) * 64 + A.index(ring[i + 3])) for i in range(0, len(ring) - 3, 4)]
        if len(pts) >= 3:
            out.append([to_ll(X0 + step * x, Y0 + step * y) for x, y in pts])
    return out


def main(src, atlas, territories, dst):
    to_ll = inverse()
    entries = []
    text = open(src, encoding="utf8").read().strip()
    step = 2
    if text.startswith("full;"):  # estrazione a risoluzione piena, con i buchi delle scritte chiusi (chiusura morfologica di 2 px)
        step, text = 1, text[5:]
    for chunk in text.split(";"):
        m, body = chunk.split(":", 1)
        red, blue, sov = body.split("|")
        note = SRC.format(m=m)
        if red:
            entries.append({"n": "Controllo comunista", "from": m, "to": m, "look": "st-s t-fill t-occ", "rings": rings_of(red, to_ll, step), "cn": 1, "clipKey": "china",
                            "d": "Zone tenute dal Partito comunista cinese e dall'Esercito popolare di liberazione, " + note})
        if blue:
            entries.append({"n": "Ultime zone nazionaliste", "from": m, "to": m, "look": "st-u t-fill t-occ", "rings": rings_of(blue, to_ll, step), "cn": 1, "clipKey": "china",
                            "d": "Sacche ancora in mano al Guomindang o alla guerriglia nazionalista dopo la proclamazione della Repubblica popolare, " + note})
        if sov:
            entries.append({"n": "Occupazione sovietica", "from": m, "to": m, "look": "st-s t-fill t-occ", "rings": rings_of(sov, to_ll, step), "cn": 1, "clipKey": "china",
                            "d": "Manciuria occupata dall'Armata Rossa dopo la resa giapponese; i sovietici se ne vanno nella primavera 1946 "
                                 "lasciando armi e città ai comunisti. " + note[0].upper() + note[1:]})
    text = open(territories, encoding="utf8").read()
    terr = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("cn")]
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr + entries, separators=(",", ":"), ensure_ascii=False) + ";\n")
    clip = [r for r in atlas_rings(atlas, ["China"]) if len(r) >= 3]
    with open(dst, "w", encoding="utf8") as h:
        h.write("/* Ritaglio per le zone della guerra civile cinese: la Cina continentale con Hainan (senza Taiwan, Hong Kong e Macao). */\n"
                f"window.TERR_CLIPS = Object.assign(window.TERR_CLIPS || {{}}, {{ china: {json.dumps(clip, separators=(',', ':'))} }});\n")
    print(len(entries), "voci;", sum(len(r) for e in entries for r in e["rings"]), "punti; ritaglio", len(clip), "anelli")
    ll = to_ll(1371, 842)
    print("controllo: punta nord di Taiwan ->", ll, "(atteso 121.58, 25.30)")


if __name__ == "__main__":
    main(*sys.argv[1:5])
