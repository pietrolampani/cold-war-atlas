"""Aggiunge a territories.js i confini italiani 1945-1954, che CShapes non ha: tiene un solo contorno dell'Italia dal 1919.

Geometrie da OpenHistoricalMap (CC0). Linea Morgan, linea dell'Isonzo e Pola sono tracciate a mano, schematiche.
Si può rilanciare: le voci precedenti, segnate con "it", vengono sostituite.

Uso: python -I tools/build_italy.py cartella_ohm territories.js
"""
import json
import math
import os
import sys

# Da nord a sud, a mano: Zona A con Caporetto, Tolmino, Gorizia, Trieste e Muggia; Idria, Aidussina, Sesana e Capodistria alla Zona B
MORGAN = [(13.65, 46.44), (13.79, 46.33), (13.87, 46.20), (13.80, 46.10), (13.72, 46.03), (13.73, 45.95), (13.72, 45.86), (13.70, 45.79), (13.80, 45.73), (13.88, 45.65), (13.86, 45.60), (13.79, 45.58), (13.75, 45.56)]
ISONZO = [(13.57, 46.42), (13.54, 46.33), (13.58, 46.25), (13.73, 46.17), (13.67, 46.02), (13.63, 45.94), (13.56, 45.87), (13.53, 45.77), (13.54, 45.71)]
POLA = [[13.78, 44.83], [13.95, 44.83], [13.95, 44.97], [13.78, 44.97], [13.78, 44.83]]


def thin(r, metres=60):
    out = [r[0]]
    for p in r[1:-1]:
        k = math.cos(math.radians(p[1]))
        if math.hypot((p[0] - out[-1][0]) * k, p[1] - out[-1][1]) * 111320 >= metres:
            out.append(p)
    out.append(r[-1])
    return [[round(x, 5), round(y, 5)] for x, y in out]


def nearest(ring, p):
    k = math.cos(math.radians(p[1]))
    return min(range(len(ring) - 1), key=lambda i: ((ring[i][0] - p[0]) * k) ** 2 + (ring[i][1] - p[1]) ** 2)


def east_of(ring, line):
    """Parte dell'anello a est della linea: dall'inizio della linea all'ultimo punto, passando per Fiume."""
    body = ring[:-1]
    a, b = nearest(ring, line[0]), nearest(ring, line[-1])
    via = nearest(ring, (14.40, 45.32))
    arc = []
    i = a
    while i != b:
        arc.append(body[i])
        i = (i + 1) % len(body)
    if via not in {(a + n) % len(body) for n in range(len(arc))}:
        arc = []
        i = a
        while i != b:
            arc.append(body[i])
            i = (i - 1) % len(body)
    arc.append(body[b])
    closed = arc + [list(p) for p in line[::-1]]
    return closed + [closed[0]]


def main(folder, dst):
    load = lambda r: json.load(open(os.path.join(folder, f"{r}.json"), encoding="utf8"))["rings"]
    italy = load(2851104)
    main_ring = thin(italy[0])
    others = [thin(r) for r in italy[1:]]
    small_east = [r for r in others if r[0][0] > 15 and 42.3 < r[0][1] < 46]  # Zara e Pelagosa: le altre isole a est restano italiane
    rest = [r for r in others if r not in small_east]
    print("isole a est:", [(r[0][0], r[0][1], len(r)) for r in small_east])
    aegean = [thin(r) for r in load(2920371)]
    entries = [
        {"n": "Italia, confini del 1945", "from": "1945-01", "to": "1947-08", "code": 325, "rings": [main_ring] + rest,
         "d": "Confine legale fino all'entrata in vigore del trattato di pace, il 15 settembre 1947: Istria, Fiume, Zara e parte della Slovenia di oggi erano italiane, così come Briga e Tenda. Fonte: OpenHistoricalMap."},
        {"n": "Italia sotto occupazione tedesca", "from": "1945-01", "to": "1945-03", "look": "st-O", "rings": [thin(r) for r in load(2961564)], "d": "Dal settembre 1943 alla resa dell'aprile-maggio 1945 il nord è sotto controllo tedesco, comprese le zone annesse di fatto. Fonte: OpenHistoricalMap, contorno fisso per il periodo."},
        {"n": "Repubblica Sociale Italiana", "from": "1945-01", "to": "1945-03", "look": "st-X", "rings": [thin(r) for r in load(2794957)], "d": "Stato fantoccio della Germania, fino al 25-29 aprile 1945. Il fronte della Linea Gotica ne segna il limite sud. Fonte: OpenHistoricalMap, contorno fisso per il periodo."},
        {"n": "Zara e Pelagosa", "from": "1945-01", "to": "1945-04", "code": 325, "rings": small_east, "d": "Italiane per legge. Zara è occupata dagli jugoslavi dall'ottobre 1944. Fonte: OpenHistoricalMap."},
        {"n": "Venezia Giulia, occupazione jugoslava", "from": "1945-05", "to": "1945-05", "look": "t-conf", "rings": [east_of(main_ring, ISONZO)] + small_east,
         "d": "Quaranta giorni: dal 1° maggio al 12 giugno 1945 gli jugoslavi tengono la regione fino all'Isonzo, Trieste compresa. Sovranità ancora italiana. Linea dell'Isonzo schematica."},
        {"n": "Zona B, amministrazione jugoslava", "from": "1945-06", "to": "1947-08", "look": "t-conf", "rings": [east_of(main_ring, MORGAN)] + small_east,
         "d": "A est della Linea Morgan, dal 12 giugno 1945: amministrazione militare jugoslava, sovranità ancora italiana fino al 15 settembre 1947. Linea Morgan tracciata a mano, schematica: non ho trovato un dato geografico aperto."},
        {"n": "Pola, Zona A", "from": "1945-06", "to": "1947-08", "code": 325, "rings": [POLA], "d": "Enclave sotto governo militare alleato. Esodo della popolazione italiana all'inizio del 1947. Contorno schematico."},
        {"n": "Territorio Libero di Trieste", "from": "1947-09", "to": "1954-09", "look": "t-conf", "rings": load(2742910), "d": "Istituito dal trattato di pace il 15 settembre 1947, mai realmente costituito. Diviso di fatto nel 1954 dal Memorandum di Londra del 5 ottobre. Fonte: OpenHistoricalMap."},
        {"n": "TLT, Zona A", "from": "1947-09", "to": "1954-09", "look": "st-U", "rings": load(2800540), "d": "Trieste e Muggia, governo militare angloamericano. All'Italia nell'ottobre 1954. Fonte: OpenHistoricalMap."},
        {"n": "TLT, Zona B", "from": "1947-09", "to": "1954-09", "code": 345, "rings": load(2800539), "d": "Capodistria e Buie, amministrazione militare jugoslava. Alla Jugoslavia nell'ottobre 1954. Fonte: OpenHistoricalMap."},
        {"n": "Dodecaneso, occupazione tedesca", "from": "1945-01", "to": "1945-04", "look": "st-O", "rings": aegean, "d": "Isole italiane dal 1912, occupate dai tedeschi dal settembre 1943 all'8 maggio 1945. Fonte: OpenHistoricalMap."},
        {"n": "Dodecaneso, amministrazione britannica", "from": "1945-05", "to": "1947-03", "look": "emp-uk", "rings": aegean, "d": "Sovranità italiana, amministrazione militare britannica fino al 31 marzo 1947, poi greca. Ceduto alla Grecia dal trattato di pace. Fonte: OpenHistoricalMap."},
    ]
    for x in entries:
        x["it"] = 1
    text = open(dst, encoding="utf8").read()
    old = json.loads(text.split("=", 1)[1].rstrip().rstrip(";"))
    old = [x for x in old if not x.get("it")]
    with open(dst, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(old + entries, separators=(",", ":"), ensure_ascii=False) + ";\n")
    for x in entries:
        print(x["n"], len(x["rings"]), "anelli", sum(map(len, x["rings"])), "punti")
    print(round(os.path.getsize(dst) / 1e6, 2), "MB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
