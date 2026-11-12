"""Guerra di Corea dal video "The Korean War: Every Day" (EmperorTigerstar), giugno 1950 - luglio 1953.

korea_video_frames.txt viene dal browser: per un fotogramma a metà di ogni mese (fine mese per giugno 1950), "mese:rossi|blu",
contorni a risoluzione piena del fotogramma 1440x1080 (carta nei primi 800 pixel), con i buchi delle scritte chiusi (2 px).
Rossi = Corea del Nord e Cina, blu = Corea del Sud e ONU, in tutte e tre le tonalità. Si ritagliano sullo Stato dell'altro campo:
i rossi sulla Corea del Sud (occupazione nordcoreana e cinese), i blu sulla Corea del Nord (occupazione ONU).
Date: 5 giorni al secondo dal 29 giugno 1950 (secondo 5) al 9 giugno 1951 (secondo 74); poi il video dichiara il fronte fermo
dal 14 giugno 1951 al 26 luglio 1953 e mostra un solo fotogramma, usato per tutto quel periodo.
Georeferenziato adattando la costa del mare aperto (tools/fit_coast.py).

Uso: python -I tools/build_korea_video.py korea_video_frames.txt territories.js a b c d [merc]
"""
import json
import math
import sys

A = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
SRC = " Dal video \"The Korean War: Every Day\" (EmperorTigerstar), fotogramma di {day}; contorni semplificati, errore di qualche chilometro."


def main(src, territories, a, b, c, d, model="lin"):
    a, b, c, d = map(float, (a, b, c, d))
    if model == "merc":
        to_ll = lambda x, y: [round((x - b) / a, 4), round(math.degrees(2 * math.atan(math.exp(math.radians((y - d) / c))) - math.pi / 2), 4)]
    else:
        to_ll = lambda x, y: [round((x - b) / a, 4), round((y - d) / c, 4)]
    chunks = open(src, encoding="utf8").read().strip().split(";")
    months = [ch.split(":", 1)[0] for ch in chunks]
    entries = []
    for i, ch in enumerate(chunks):
        m, body = ch.split(":", 1)
        red, blue = body.split("|")
        if m == "1951-07":
            end, day = "1953-07", "fronte fermo dal 14 giugno 1951 all'armistizio del 27 luglio 1953"
        else:
            nxt = months[i + 1]
            y, mo = map(int, nxt.split("-"))
            n = y * 12 + mo - 2
            end = f"{n // 12}-{n % 12 + 1:02d}"
            day = "30 giugno 1950" if m == "1950-06" else f"metà {m}"
        rings = lambda body: [[to_ll(int(A.index(r[i]) * 64 + A.index(r[i + 1])), int(A.index(r[i + 2]) * 64 + A.index(r[i + 3]))) for i in range(0, len(r) - 3, 4)] for r in body.split(",") if len(r) >= 12]
        comm = "Occupazione nordcoreana" if m < "1950-11" else "Occupazione nordcoreana e cinese"
        entries.append({"n": comm, "from": m, "to": end, "code": 731, "cls": "t-occ", "clip": 732, "rings": rings(red), "kor": 1,
                        "d": "Territorio sudcoreano tenuto dal Nord" + (" e dai volontari cinesi" if m >= "1950-11" else "") + "." + SRC.format(day=day)})
        entries.append({"n": "Occupazione ONU", "from": m, "to": end, "code": 732, "cls": "t-occ", "clip": 731, "rings": rings(blue), "kor": 1,
                        "d": "Territorio nordcoreano tenuto da ONU e Corea del Sud." + SRC.format(day=day)})
    text = open(territories, encoding="utf8").read()
    terr = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("kor")]
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr + entries, separators=(",", ":"), ensure_ascii=False) + ";\n")
    print(len(entries), "voci;", sum(len(r) for e in entries for r in e["rings"]), "punti")


if __name__ == "__main__":
    main(*sys.argv[1:8])
