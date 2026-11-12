"""Occupazioni della guerra di Corea, giugno 1950 - luglio 1953.

Per ogni mese una linea del fronte da costa a costa (lon, lat), tracciata a mano sulle tappe note della guerra
(carte dello US Army Center of Military History: linea del Kum, perimetro di Pusan, Chongchon e Chosin, linea Kansas,
linea dell'armistizio). La situazione è quella di metà mese, tranne giugno 1950 (fine mese: la guerra inizia il 25).
Dalla linea si ricavano due poligoni: a nord il territorio comunista, a sud quello ONU. Si ritagliano sullo Stato
dell'altro campo in quel mese (clip per codice), così compare solo la parte occupata: il Sud tenuto da nordcoreani
e cinesi, il Nord tenuto dall'ONU. Precisione dell'ordine di 10-20 km: è una ricostruzione, non un rilievo.

Uso: python -I tools/build_korea.py territories.js
"""
import json
import sys

# start: "w" = la linea parte dalla costa occidentale, "s" = dalla costa meridionale (perimetro di Pusan)
FRONTS = [
    ("1950-06", "1950-06", "w", "30 giugno: Seul è caduta il 28, i nordcoreani passano lo Han.",
     [[126.45, 37.45], [126.85, 37.45], [127.2, 37.45], [127.6, 37.55], [128.0, 37.65], [128.5, 37.7], [128.9, 37.72], [129.05, 37.68]]),
    ("1950-07", "1950-07", "w", "Metà luglio: linea del fiume Kum, Taejon cade il 20.",
     [[126.55, 36.55], [127.0, 36.45], [127.3, 36.5], [127.7, 36.75], [128.2, 36.8], [128.6, 36.7], [129.1, 36.6], [129.42, 36.5]]),
    ("1950-08", "1950-08", "s", "Perimetro di Pusan lungo il Naktong, da Masan a Pohang.",
     [[128.42, 34.95], [128.4, 35.35], [128.45, 35.65], [128.38, 35.95], [128.6, 36.15], [128.9, 36.15], [129.2, 36.1], [129.42, 36.05]]),
    ("1950-09", "1950-09", "s", "Metà settembre: ancora il perimetro di Pusan; il 15 lo sbarco di Inchon, il 28 l'ONU riprende Seul.",
     [[128.45, 34.95], [128.35, 35.35], [128.42, 35.7], [128.4, 36.0], [128.65, 36.1], [128.95, 36.05], [129.25, 36.0], [129.4, 35.98]]),
    ("1950-10", "1950-10", "w", "Metà ottobre: l'ONU passa il 38° parallelo, Pyongyang cade il 19, i sudcoreani prendono Wonsan e Hamhung.",
     [[125.1, 38.55], [125.8, 38.7], [126.5, 38.8], [126.9, 39.0], [127.2, 39.35], [127.5, 39.6], [127.7, 39.78]]),
    ("1950-11", "1950-11", "w", "Metà novembre: l'ONU sul Chongchon e al bacino di Chosin; a fine mese arriva l'offensiva cinese.",
     [[125.35, 39.6], [125.8, 39.85], [126.3, 39.95], [126.8, 40.05], [127.2, 40.45], [127.6, 40.7], [128.1, 41.0], [128.6, 41.2], [129.0, 41.0], [129.3, 40.75]]),
    ("1950-12", "1950-12", "w", "Metà dicembre: l'ONU ripiega sull'Imjin; la testa di ponte di Hungnam è evacuata entro il 24.",
     [[126.4, 37.75], [126.8, 37.95], [127.1, 38.0], [127.6, 38.1], [128.1, 38.2], [128.45, 38.4], [128.55, 38.45]]),
    ("1951-01", "1951-01", "w", "Metà gennaio: terza offensiva cinese, Seul cade il 4; linea da Pyeongtaek a Wonju e Samcheok.",
     [[126.8, 36.95], [127.1, 37.0], [127.5, 37.1], [127.95, 37.25], [128.4, 37.2], [128.9, 37.35], [129.15, 37.45]]),
    ("1951-02", "1951-02", "w", "Metà febbraio: l'ONU torna sullo Han; battaglia di Chipyong-ni.",
     [[126.6, 37.42], [126.85, 37.5], [127.15, 37.45], [127.55, 37.45], [127.95, 37.4], [128.4, 37.35], [128.9, 37.55], [129.0, 37.68]]),
    ("1951-03", "1951-03", "w", "Metà marzo: operazione Ripper, Seul ripresa il 15.",
     [[126.55, 37.62], [126.95, 37.65], [127.4, 37.7], [127.85, 37.75], [128.3, 37.85], [128.75, 37.98], [128.85, 38.02]]),
    ("1951-04", "1951-04", "w", "Metà aprile: linea Kansas, poco a nord del 38° parallelo; il 22 inizia l'offensiva di primavera cinese.",
     [[126.65, 37.75], [126.9, 37.95], [127.1, 38.15], [127.5, 38.2], [127.75, 38.15], [128.2, 38.2], [128.5, 38.25], [128.62, 38.12]]),
    ("1951-05", "1951-05", "w", "Metà maggio: seconda fase dell'offensiva di primavera, l'ONU tiene la linea a nord di Seul.",
     [[126.65, 37.7], [126.95, 37.75], [127.3, 37.75], [127.7, 37.75], [128.1, 37.72], [128.45, 37.78], [128.82, 37.95]]),
    ("1951-06", "1953-07", "w", "Dal giugno 1951 il fronte si ferma vicino alla linea dell'armistizio del 27 luglio 1953: Kaesong resta al Nord, "
     "il Triangolo di ferro e il Punchbowl all'ONU.",
     [[126.65, 37.75], [126.68, 37.95], [126.95, 38.0], [127.2, 38.25], [127.45, 38.3], [127.75, 38.3], [128.05, 38.3], [128.3, 38.45], [128.37, 38.6]]),
]
HUNGNAM = [[127.4, 39.75], [127.75, 39.75], [127.75, 40.1], [127.4, 40.1], [127.4, 39.75]]  # testa di ponte di dicembre 1950


def polys(start, line):
    x0, y0 = line[0]
    ex, ey = line[-1]
    if start == "w":
        north = line + [[131, ey], [131, 44], [122, 44], [122, y0]]
        south = line + [[131, ey], [131, 33], [122, 33], [122, y0]]
    else:
        north = line + [[131, ey], [131, 44], [122, 44], [122, 33], [x0, 33]]
        south = line + [[131, ey], [131, 33], [x0, 33]]
    return [north + [line[0]]], [south + [line[0]]]


def main(territories):
    entries = []
    for a, b, start, note, line in FRONTS:
        north, south = polys(start, line)
        if b == "1950-12" or a == "1950-12":
            south.append(HUNGNAM)
        comm = "Occupazione nordcoreana" if a < "1950-11" else "Occupazione nordcoreana e cinese"
        src = " Ricostruzione dalle linee del fronte note (US Army Center of Military History), tracciato semplificato."
        entries.append({"n": comm, "from": a, "to": b, "code": 731, "cls": "t-occ", "clip": 732, "rings": north, "kor": 1,
                        "d": "Territorio sudcoreano tenuto dal Nord" + (" e dai volontari cinesi" if a >= "1950-11" else "") + ". " + note + src})
        entries.append({"n": "Occupazione ONU", "from": a, "to": b, "code": 732, "cls": "t-occ", "clip": 731, "rings": south, "kor": 1,
                        "d": "Territorio nordcoreano tenuto da ONU e Corea del Sud. " + note + src})
    text = open(territories, encoding="utf8").read()
    terr = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("kor")]
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr + entries, separators=(",", ":"), ensure_ascii=False) + ";\n")
    print(len(entries), "voci")


if __name__ == "__main__":
    main(sys.argv[1])
