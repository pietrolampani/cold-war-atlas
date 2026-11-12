"""Zone della guerra in Afghanistan 1978-1991 dal video "War in Afghanistan (1978-present): Every Two Weeks".

afghanistan_video_frames.txt viene dal browser: per un fotogramma ogni 4-8 secondi, "secondo:governo|sciiti", con i contorni
del governo comunista (con i sovietici) e dei mujaheddin sciiti dell'Hazarajat su una griglia dimezzata, già ritagliati
sull'Afghanistan; il resto del Paese è dei mujaheddin sunniti. Coppie di caratteri base 64 per x e y.
Georeferenziato con 13 città lette sul fotogramma; il video avanza a ritmo costante, circa 1,38 mesi per secondo, da aprile 1978.

Colori: governo e sovietici con lo stato dell'Afghanistan in quel mese, sunniti come "vicino agli USA" (sostenuti da USA e Pakistan),
sciiti come non allineati (sostenuti dall'Iran).

Uso: python -I tools/build_afghanistan.py afghanistan_video_frames.txt atlas10.json territories.js afghanistan.js
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_ww2_atlas import atlas_rings  # noqa: E402

A = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
X0, Y0 = 300, 60
# Città: pixel sul fotogramma 1920x1080, lon, lat
CONTROL = [(721, 236, 65.75, 36.67), (890, 231, 67.11, 36.71), (743, 284, 65.93, 36.22), (594, 311, 64.78, 35.92), (1110, 229, 68.86, 36.73),
           (1194, 227, 69.53, 36.74), (1003, 279, 68.02, 36.26), (1093, 316, 68.71, 35.94), (1195, 382, 69.52, 35.31), (1367, 372, 70.92, 35.42),
           (657, 478, 65.25, 34.52), (980, 439, 67.83, 34.82), (766, 556, 66.14, 33.72)]
LAST = "1991-12"


def fit():
    """Due rette ai minimi quadrati: x da lon, y da lat."""
    def line(us, vs):
        n = len(us); mu = sum(us) / n; mv = sum(vs) / n
        a = sum((u - mu) * (v - mv) for u, v in zip(us, vs)) / sum((u - mu) ** 2 for u in us)
        return a, mv - a * mu
    ax, bx = line([c[2] for c in CONTROL], [c[0] for c in CONTROL])
    ay, by = line([c[3] for c in CONTROL], [c[1] for c in CONTROL])
    res = [((c[2] * ax + bx - c[0]) ** 2 + (c[3] * ay + by - c[1]) ** 2) ** .5 for c in CONTROL]
    print("georeferenziazione: errore medio", round(sum(res) / len(res), 1), "px, massimo", round(max(res), 1))
    return lambda x, y: [round((x - bx) / ax, 4), round((y - by) / ay, 4)]


def rings_of(body, to_ll):
    out = []
    for ring in body.split(","):
        pts = [(A.index(ring[i]) * 64 + A.index(ring[i + 1]), A.index(ring[i + 2]) * 64 + A.index(ring[i + 3])) for i in range(0, len(ring) - 3, 4)]
        if len(pts) >= 3:
            out.append([to_ll(X0 + 2 * x, Y0 + 2 * y) for x, y in pts])
    return out


def month_of(t):
    n = 1978 * 12 + 3 + int((t - 20) * 1.375)
    return f"{n // 12}-{n % 12 + 1:02d}"


def month_add(m, k):
    y, mo = map(int, m.split("-"))
    n = y * 12 + mo - 1 + k
    return f"{n // 12}-{n % 12 + 1:02d}"


def main(src, atlas, territories, dst):
    to_ll = fit()
    frames = []
    for chunk in open(src, encoding="utf8").read().strip().split(";"):
        t, body = chunk.split(":", 1)
        gov, shia = body.split("|")
        if not gov and not shia:  # Aprile 1978: prima della guerriglia
            continue
        frames.append((int(t), rings_of(gov, to_ll) if gov else [], rings_of(shia, to_ll) if shia else []))
    afg = [r for r in atlas_rings(atlas, ["Afghanistan"]) if len(r) >= 3]
    entries = []
    for i, (t, gov, shia) in enumerate(frames):
        start = month_of(t)
        end = month_add(month_of(frames[i + 1][0]), -1) if i + 1 < len(frames) else LAST
        note = f"Secondo il video \"War in Afghanistan (1978-present): Every Two Weeks\", fotogramma di {start}. Situazione indicativa: i contorni sono semplificati."
        entries.append({"n": "Mujaheddin sunniti", "from": start, "to": end, "look": "st-u t-fill", "rings": afg, "afg": 1, "clipKey": "afghanistan",
                        "d": "Territorio fuori dal controllo del governo comunista, tenuto dai gruppi sunniti sostenuti da Pakistan e USA. " + note})
        if gov:
            entries.append({"n": "Governo comunista" + (" e sovietici" if start >= "1979-12" and start < "1989-02" else ""), "from": start, "to": end, "code": 700,
                            "rings": gov, "afg": 1, "clipKey": "afghanistan", "d": "Città, valli e strade tenute dal governo di Kabul. " + note})
        if shia:
            entries.append({"n": "Mujaheddin sciiti", "from": start, "to": end, "look": "st-N t-fill", "rings": shia, "afg": 1, "clipKey": "afghanistan",
                            "d": "Hazarajat, gruppi sciiti sostenuti dall'Iran. " + note})
    text = open(territories, encoding="utf8").read()
    terr = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("afg")]
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr + entries, separators=(",", ":"), ensure_ascii=False) + ";\n")
    with open(dst, "w", encoding="utf8") as h:
        h.write("/* Ritaglio per le zone della guerra in Afghanistan. */\n"
                f"window.TERR_CLIPS = Object.assign(window.TERR_CLIPS || {{}}, {{ afghanistan: {json.dumps(afg, separators=(',', ':'))} }});\n")
    print(len(frames), "fotogrammi da", month_of(frames[0][0]), "a", LAST, ";", len(entries), "voci")


if __name__ == "__main__":
    main(*sys.argv[1:5])
