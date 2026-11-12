"""Zone in mano a Nord Vietnam, Viet Cong e Pathet Lao, 1959-1975, dal video "The Vietnam War: Every Fortnight" (EmperorTigerstar).

vietnam_video_frames.txt viene dal browser: per ogni secondo del video campionato, i contorni delle aree rosse su una griglia
dimezzata del fotogramma 1920x1080, in coppie di caratteri base 64 ("x y" a due cifre). Il Nord Vietnam è già tolto.
La carta del video è equirettangolare: georeferenziata adattandone la costa a Natural Earth (tools/fit_coast.py), errore medio 2,8 pixel.
Le date dei fotogrammi sono lette a vista; i fotogrammi con una didascalia al posto della data hanno un mese stimato.

Uso: python -I tools/build_vietnam.py vietnam_video_frames.txt atlas10.json territories.js vietnam.js
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_ww2_atlas import atlas_rings  # noqa: E402

A = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
FIT = (68.7393, -6709.7141, -65.1096, 1590.9641)  # x = a·lon + b, y = c·lat + d sul fotogramma intero
# Secondo del video -> mese del fotogramma (letto sulla data in basso a destra; * = didascalia, mese stimato)
DATES = {16: "1959-06", 19: "1959-09", 22: "1959-11", 25: "1960-02", 28: "1960-05", 31: "1960-08", 34: "1960-10", 37: "1961-01", 40: "1961-04",
         43: "1961-07", 46: "1961-09", 49: "1961-12", 52: "1962-03", 55: "1962-06", 58: "1962-09", 61: "1962-12", 64: "1963-02", 67: "1963-04",
         70: "1963-07", 73: "1963-10", 76: "1964-01", 79: "1964-03", 82: "1964-06", 85: "1964-09", 88: "1964-12", 91: "1965-03", 94: "1965-05",
         97: "1965-08", 100: "1965-11", 103: "1966-02", 106: "1966-04", 109: "1966-07", 112: "1966-10", 115: "1967-01", 118: "1967-03",
         121: "1967-06", 124: "1967-09", 127: "1967-12", 130: "1968-02", 133: "1968-03", 136: "1968-04", 139: "1968-05", 142: "1968-06",
         145: "1968-08", 148: "1968-09", 151: "1968-10", 154: "1969-01", 157: "1969-04", 160: "1969-07", 163: "1970-05", 166: "1970-08",
         169: "1971-01", 172: "1972-04", 175: "1972-07", 178: "1972-10", 181: "1973-01", 184: "1973-02", 187: "1974-12", 190: "1974-12",
         193: "1975-01", 196: "1975-04"}
GUESSED = {130, 133, 139, 142, 145, 148, 160, 169}
LAST = "1975-04"  # Il 30 aprile cade Saigon: da maggio vale lo stato di base


def decode(text):
    frames = {}
    for chunk in text.strip().split(";"):
        if ":" not in chunk:
            continue
        t, body = chunk.split(":", 1)
        rings = []
        for ring in body.split(","):
            pts = [(A.index(ring[i]) * 64 + A.index(ring[i + 1]), A.index(ring[i + 2]) * 64 + A.index(ring[i + 3])) for i in range(0, len(ring) - 3, 4)]
            if len(pts) >= 3:
                a, b, c, d = FIT
                rings.append([[round((2 * x - b) / a, 4), round((2 * y - d) / c, 4)] for x, y in pts])
        frames[int(t)] = rings
    return frames


def month_add(m, k):
    y, mo = map(int, m.split("-"))
    n = y * 12 + mo - 1 + k
    return f"{n // 12}-{n % 12 + 1:02d}"


def main(src, atlas, territories, dst):
    frames = decode(open(src, encoding="utf8").read())
    # Un fotogramma vale dal suo mese fino al mese prima del successivo; quelli assenti dal file ripetono il precedente
    keys = sorted(t for t in DATES if DATES[t] <= LAST)
    spans, current = [], None
    for t in keys:
        if t in frames:
            current = (t, frames[t])
        if current:
            spans.append((DATES[t], current))
    entries = []
    for i, (month, (t, rings)) in enumerate(spans):
        end = month_add(spans[i + 1][0], -1) if i + 1 < len(spans) else LAST
        if end < month:  # Due fotogrammi nello stesso mese: vale il più recente
            continue
        note = (f"Zone tenute da Nord Vietnam, Viet Cong e Pathet Lao secondo il video \"The Vietnam War: Every Fortnight\" (EmperorTigerstar), "
                f"fotogramma {'di mese stimato, ' if t in GUESSED else ''}del {month}. Nella guerriglia il controllo è indicativo.")
        entries.append({"n": "Controllo comunista", "from": month, "to": end, "look": "st-S t-fill", "rings": rings, "vn": 1, "clipKey": "indochina", "d": note})
    text = open(territories, encoding="utf8").read()
    terr = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("vn")]
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr + entries, separators=(",", ":"), ensure_ascii=False) + ";\n")
    clip = [r for r in atlas_rings(atlas, ["Vietnam", "Laos", "Cambodia"]) if len(r) >= 3]
    with open(dst, "w", encoding="utf8") as h:
        h.write("/* Ritaglio per le zone della guerra del Vietnam: solo Vietnam, Laos e Cambogia (il video colora di rosso anche la Cina). */\n"
                f"window.TERR_CLIPS = Object.assign(window.TERR_CLIPS || {{}}, {{ indochina: {json.dumps(clip, separators=(',', ':'))} }});\n")
    print(len(entries), "periodi da", entries[0]["from"], "a", entries[-1]["to"], "; punti", sum(len(r) for e in entries for r in e["rings"]))


if __name__ == "__main__":
    main(*sys.argv[1:5])
