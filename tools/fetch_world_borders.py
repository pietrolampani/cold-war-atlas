"""Scarica da OpenStreetMap i confini di Stato terrestri di tutto il mondo, a riquadri, e scrive un unico file.

Si può rilanciare: i riquadri già scaricati restano nella cartella cache. I vertici a meno di 100 metri dal precedente
si tolgono subito, tenendo gli estremi delle vie, che servono per collegarle.

Uso: python -I tools/fetch_world_borders.py cartella_cache world_borders.json
"""
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request

MIRRORS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]
STEP = 30


def thin(g):
    out = [g[0]]
    for p in g[1:-1]:
        k = math.cos(math.radians(p["lat"]))
        if math.hypot((p["lon"] - out[-1]["lon"]) * k, p["lat"] - out[-1]["lat"]) * 111320 >= 100:
            out.append(p)
    out.append(g[-1])
    return out


def box(s, w, n, e, cache, depth=0):
    path = os.path.join(cache, f"{s}_{w}_{n}_{e}.json")
    if os.path.exists(path):
        return True
    q = f'[out:json][timeout:170];way["boundary"="administrative"]["admin_level"="2"]["maritime"!="yes"]["natural"!="coastline"]({s},{w},{n},{e});out geom tags;'
    body = urllib.parse.urlencode({"data": q}).encode()
    for attempt in range(4):
        try:
            req = urllib.request.Request(MIRRORS[attempt % 2], body, {"User-Agent": "ColdWarAtlas/1.0 (personal history map)", "Accept": "*/*"})
            reply = json.loads(urllib.request.urlopen(req, timeout=178).read())
            if reply.get("remark"):  # Timeout a metà query: risponde 200 con dati parziali o vuoti
                raise ValueError("risposta incompleta: " + reply["remark"])
            els = reply["elements"]
            rows = []
            for e_ in els:
                if e_.get("geometry") and len(e_["geometry"]) > 1:
                    rows.append({"type": "way", "id": e_["id"], "geometry": thin(e_["geometry"])})
            with open(path, "w") as h:
                json.dump(rows, h, separators=(",", ":"))
            print(s, w, n, e, len(rows), "vie", flush=True)
            time.sleep(4)
            return True
        except Exception as ex:
            print(s, w, n, e, ex, flush=True)
            time.sleep(20)
    if depth < 2:  # Troppo pesante: si divide in quattro
        ms, mw = (s + n) // 2, (w + e) // 2
        done = [box(*b, cache, depth + 1) for b in ((s, w, ms, mw), (s, mw, ms, e), (ms, w, n, mw), (ms, mw, n, e))]
        if all(done):  # Se un pezzo manca, il riquadro si riprova al prossimo avvio
            with open(path, "w") as h:
                json.dump([], h)
            return True
        return False
    print("NON SCARICATO", s, w, n, e, flush=True)
    return False


def main(cache, out):
    os.makedirs(cache, exist_ok=True)
    missing = 0
    for s in range(-60, 80, STEP):
        for w in range(-180, 180, STEP):
            if not box(s, w, s + STEP, w + STEP, cache):
                missing += 1
    if missing:
        print("INCOMPLETO", missing, "riquadri da riprovare: rilanciare", flush=True)
        return
    seen, rows = set(), []
    for f in os.listdir(cache):
        for r in json.load(open(os.path.join(cache, f))):
            if r["id"] not in seen:
                seen.add(r["id"])
                rows.append(r)
    with open(out, "w") as h:
        json.dump({"elements": rows}, h, separators=(",", ":"))
    print("FATTO", len(rows), "vie", sum(len(r["geometry"]) for r in rows), "punti", round(os.path.getsize(out) / 1e6, 1), "MB", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
