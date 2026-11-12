"""Territori e fronti del Pacifico nel 1945 dalle tavole dell'Atlas of the World Battle Fronts (Army Map Service, pubblico dominio).

Come build_ww2_atlas.py per l'Europa, con due differenze: sulle tavole del Pacifico il rosa alleato copre anche il mare,
quindi i fronti si tengono solo sulla terra e ad almeno COAST_KM dalla costa; il colore alleato serve solo sul Giappone (Iwo Jima, Okinawa).
Voci "ww2p" in territories.js, fronti in ww2pacific.js.

Uso: python -I tools/build_pacific_atlas.py cartella_tavole territories.js ww2pacific.js atlas10.json
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_ww2_atlas import atlas_rings, fronts, inside, km  # noqa: E402

COAST_KM = 15
JAPAN_HELD = ["China", "North Korea", "South Korea", "Japan", "Taiwan", "Vietnam", "Laos", "Cambodia", "Thailand", "Myanmar", "Malaysia", "Singapore", "Brunei",
              "Indonesia", "Timor-Leste", "Philippines", "Papua New Guinea", "Solomon Is.", "Hong Kong", "Palau", "Micronesia", "Marshall Is.", "N. Mariana Is.",
              "Guam", "Nauru", "Kiribati"]
# Impero giapponese e alleati in tinta uniforme; tutto il resto è occupato, a righe
JAPAN_CORE = ["Japan", "North Korea", "South Korea", "Taiwan", "Thailand"]
REPLACED = ["Birmania", "Fronte cinese", "Luzon", "Okinawa"]
SRC = "Atlas of the World Battle Fronts in Semimonthly Phases, Army Map Service 1945 (pubblico dominio); tavola del 15 del mese, georeferenziata"


def main(folder, territories, dst, atlas):
    land = atlas_rings(atlas, JAPAN_HELD)
    japan = atlas_rings(atlas, ["Japan"])
    coast = {}
    for r in land:  # Punti della costa ogni 2 km circa, in una griglia da 0,2 gradi
        for a, b in zip(r, r[1:] + r[:1]):
            n = max(1, int(km(a, b) / 2))
            for i in range(n + 1):
                p = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
                coast.setdefault((int(p[0] * 5), int(p[1] * 5)), []).append(p)

    def inland(p):
        cx, cy = int(p[0] * 5), int(p[1] * 5)
        if any(km(p, q) < COAST_KM for gx in range(cx - 1, cx + 2) for gy in range(cy - 1, cy + 2) for q in coast.get((gx, gy), ())):
            return False
        return inside(p, land)

    text = open(territories, encoding="utf8").read()
    terr = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("ww2p")]
    add, lines, months = [], [], []
    for f in sorted(os.listdir(folder)):
        if not f.endswith("Jap.json"):
            continue
        t = json.load(open(os.path.join(folder, f), encoding="utf8"))
        month = t["name"][:7]
        months.append(month)
        note = f"Situazione al {int(t['name'][8:10])} del mese secondo la tavola dell'Army Map Service del 1945. Georeferenziata su {t['n']} città, errore medio circa {t['rms'] * 8:.0f} km."
        add.append({"n": "Tenuto dal Giappone", "from": month, "to": month, "look": "st-X t-fill", "rings": t["axis"], "ww2p": 1, "clipKey": "japanCore", "d": note})
        add.append({"n": "Occupato dal Giappone", "from": month, "to": month, "look": "st-O t-fill", "rings": t["axis"], "ww2p": 1, "clipKey": "japanOccupied", "d": note})
        # Le aree alleate delle tavole non si usano: le tavole non coprono il Giappone (che risultava "alleato") e in agosto
        # l'avanzata sovietica esce a chiazze. Iwo Jima, Okinawa e l'Armata Rossa di agosto sono voci scritte a parte (z alto).
        count = 0
        for l in fronts(t["axis"], t["allied"]):
            run = []
            for p in l + [None]:
                if p is not None and inland(p):
                    run.append(p)
                    continue
                if len(run) >= 3 and sum(km(a, b) for a, b in zip(run, run[1:])) > 30:
                    lines.append({"n": "Fronte del Pacifico", "from": month, "to": month, "k": "front", "src": SRC, "d": note, "p": run})
                    count += 1
                run = []
        print(month, "Giappone", len(t["axis"]), "anelli; fronti", count, "; città", t["n"], "rms px", round(t["rms"], 1))
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr + add, separators=(",", ":"), ensure_ascii=False) + ";\n")
    core = atlas_rings(atlas, JAPAN_CORE)
    occupied = atlas_rings(atlas, [n for n in JAPAN_HELD if n not in JAPAN_CORE])
    clips = {"japanHeld": [r for r in land if len(r) >= 3], "japanHome": [r for r in japan if len(r) >= 3],
             "japanCore": [r for r in core if len(r) >= 3], "japanOccupied": [r for r in occupied if len(r) >= 3]}
    js = ("/* Il fronte è il bordo dei riempimenti (le linee ricavate dalle tavole erano rumorose e sono state tolte). Tavole dell'Army Map Service: sostituiscono quelli a mano nei mesi coperti. */\n"
          f"window.TERR_CLIPS = Object.assign(window.TERR_CLIPS || {{}}, {json.dumps(clips, separators=(',', ':'))});\n"
          f"(function () {{ var M = {json.dumps(months)}, R = {json.dumps(REPLACED, ensure_ascii=False)};\n"
          "  window.LINES = window.LINES.filter(function (l) { return !(R.indexOf(l.n) >= 0 && M.indexOf(l.from) >= 0); });\n"
          "})();\n")
    with open(dst, "w", encoding="utf8") as h:
        h.write(js)
    print(round(os.path.getsize(dst) / 1e6, 2), "MB")


if __name__ == "__main__":
    main(*sys.argv[1:5])
