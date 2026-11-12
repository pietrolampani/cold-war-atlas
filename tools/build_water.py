"""Laghi e fiumi da Natural Earth 10m. Scrive water.js, caricato allo zoom.

I bacini artificiali compaiono solo dalla data in RESERVOIRS; quelli non elencati restano fuori, perché non si sa se esistevano.
Le date dei bacini sono a memoria. Accanto ai fiumi mondiali ci sono i supplementi per Europa e Nord America, tutti senza sfoltire i vertici.

Amu Darya e Syr Darya si tagliano sulla riva del 1960 dell'Aral: il tratto sul fondale, allungato verso il centro, va in aral.js
e la pagina lo disegna fino alla riva del mese, così il fiume avanza con il ritiro del lago.

Uso: python -I tools/build_water.py ne_10m_lakes.json water.js aral.js fiumi1.json fiumi2.json ...
     oppure, con i soli fiumi OpenStreetMap di fetch_rivers.py: ... aral.js cartella_osm
"""
import json
import sys

RESERVOIRS = {"Lake Nasser": "1970-07", "Lake Kariba": "1959-06", "Lake Volta": "1965-08", "Kuybyshev Reservoir": "1957-01", "Rybinsk Reservoir": "1945-01",
              "Volgograd Reservoir": "1958-01", "Bratsk Reservoir": "1967-01", "Krasnoyarsk Reservoir": "1970-01", "Lake Cahora Bassa": "1975-01",
              "Tsimlyansk Reservoir": "1952-01", "Kakhovka Reservoir": "1956-01", "Lake Mead": "1945-01", "Lake Powell": "1966-01", "Lake Sakakawea": "1956-01", "Oahe Reservoir": "1962-01"}
# Tratti a mano dalla fine del fiume in Natural Earth verso il centro del lago: oltre la riva non si vedono
ARAL_TAIL = {(59.54, 44.15): [[59.72, 44.42], [59.95, 44.8], [60.15, 45.2]], (58.32, 44.43): [[58.42, 44.75], [58.6, 45.1]], (60.88, 46.14): [[60.78, 46.3], [60.72, 46.5]]}


def rnd(r, step=2, digits=3):
    out = []
    for i, (x, y) in enumerate(p[:2] for p in r):
        if i % step == 0 or i == len(r) - 1:
            q = [round(x, digits), round(y, digits)]
            if not out or out[-1] != q:
                out.append(q)
    return out


def inside(p, ring):
    x, y = p
    c = False
    for (a, b), (e, f) in zip(ring, ring[1:]):
        if (b > y) != (f > y) and x < (e - a) * (y - b) / (f - b) + a:
            c = not c
    return c


def osm_rivers(folder, ring):
    """Solo fiumi OSM. Il grado dipende dalla lunghezza: i più lunghi si vedono già da lontano."""
    import math
    import os
    buckets, channels, seen = {}, [], set()
    for f in sorted(os.listdir(folder)):
        r = json.load(open(os.path.join(folder, f), encoding="utf8"))
        if r["rel"] in seen:
            continue
        seen.add(r["rel"])
        km = sum(math.hypot((a[0] - b[0]) * math.cos(math.radians(a[1])), a[1] - b[1]) * 111.32 for l in r["lines"] for a, b in zip(l, l[1:]))
        rank = "1" if km > 2500 else "3" if km > 1200 else "5"
        for line in r["lines"]:
            if len(line) < 2:
                continue
            if r["n"] in ("Amu Darya", "Syr Darya") and any(inside(p, ring) for p in line):
                channels.append({"n": r["n"], "p": line})
            else:
                buckets.setdefault(rank, []).append(line)
    return buckets, channels


def main(lakes, dst, aral, rivers):
    aral_data = json.loads(open(aral, encoding="utf8").read().split("=", 1)[1].rstrip().rstrip(";"))
    ring = aral_data["full"][0]
    data = {"lakes": [], "rivers": {}}
    for f in json.load(open(lakes, encoding="utf8"))["features"]:
        p, g = f["properties"], f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        x, y = polys[0][0][0][:2]
        if 57 < x < 63 and 42 < y < 48:  # Il lago d'Aral ha il suo livello
            continue
        name = p.get("name") or ""
        start = "1945-01"
        if p.get("featurecla") == "Reservoir":
            if name not in RESERVOIRS:
                continue
            start = RESERVOIRS[name]
        rings = [rnd(r, 1) for poly in polys for r in poly]
        data["lakes"].append({"n": name, "s": start, "r": int(p.get("scalerank") or 9), "p": rings})
    channels, seen = [], set()
    if len(rivers) == 1 and rivers[0].endswith("osm"):
        data["rivers"], channels = osm_rivers(rivers[0], ring)
        rivers = []
    for path in rivers:
        for f in json.load(open(path, encoding="utf8"))["features"]:
            p, g = f["properties"], f["geometry"]
            if not g:
                continue
            rank = str(int(p.get("scalerank") or 9))
            name = (p.get("name") or "").replace("  ", " ")
            segs = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
            bucket = data["rivers"].setdefault(rank, [])
            for s in segs:
                s = rnd(s, 1, 4)
                key = (s[0][0], s[0][1], s[-1][0], s[-1][1], len(s))
                if key in seen or len(s) < 2:  # Lo stesso tratto compare in più file
                    continue
                seen.add(key)
                if name in ("Amu Darya", "Syr Darya"):
                    cut = next((i for i, q in enumerate(s) if inside(q, ring)), None)
                    tail = next((v for k, v in ARAL_TAIL.items() if abs(s[-1][0] - k[0]) < .02 and abs(s[-1][1] - k[1]) < .02), None)
                    if cut is not None:
                        channels.append({"n": name, "p": s[max(cut - 1, 0):] + (tail or [])})
                        s = s[:cut]
                    elif tail:
                        channels.append({"n": name, "p": s + tail})
                        s = []
                    if len(s) < 2:
                        continue
                bucket.append(s)
    text = "window.WATER=" + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n"
    with open(dst, "w", encoding="utf8") as h:
        h.write(text)
    aral_data["rivers"] = channels
    with open(aral, "w", encoding="utf8") as h:
        h.write("window.ARAL=" + json.dumps(aral_data, separators=(",", ":"), ensure_ascii=False) + ";\n")
    print(len(data["lakes"]), "laghi", {k: len(v) for k, v in sorted(data["rivers"].items(), key=lambda kv: int(kv[0]))}, round(len(text) / 1e6, 2), "MB")
    print("canali Aral:", [(c["n"], len(c["p"]), c["p"][0], c["p"][-1]) for c in channels])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
