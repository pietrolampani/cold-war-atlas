"""Manciukuò dai confini OpenStreetMap della Manciuria interna attuale.

Heilongjiang, Jilin, Liaoning (con il Kwantung), e nella Mongolia Interna Hulunbuir, Hinggan, Tongliao e Chifeng, più Chengde
(il Rehe, annesso nel 1933). Si scaricano le relazioni da Overpass, si tengono le vie usate una sola volta (il bordo esterno
dell'unione: quelle condivise tra due province si annullano), si ricuciono gli anelli e si semplificano a circa 300 m.
Il risultato sostituisce gli anelli delle voci "Manciukuò", "Manciukuò, costa" e "Armata Rossa in Manciuria" in territories.js.

Uso: python -I tools/build_manchukuo.py cartella_cache territories.js
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_ohm import area_km2, stitch  # noqa: E402

RELS = [199073, 198590, 912942, 161769, 2753442, 2753408, 2753364, 2989561]
UA = {"User-Agent": "ColdWarAtlas/1.0 (personal history map; Claude Code)"}


def simplify(pts, tol):
    if len(pts) < 4:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x0, y0), (x1, y1) = pts[a], pts[b]
        L = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** .5 or 1e-12
        best, bd = -1, 0
        for i in range(a + 1, b):
            x, y = pts[i]
            d = abs((x1 - x0) * (y0 - y) - (x0 - x) * (y1 - y0)) / L
            if d > bd:
                best, bd = i, d
        if bd > tol:
            keep[best] = True
            stack += [(a, best), (best, b)]
    return [p for p, k in zip(pts, keep) if k]


def main(cache, territories):
    os.makedirs(cache, exist_ok=True)
    path = os.path.join(cache, "manchukuo_rels.json")
    if not os.path.exists(path):
        q = f"[out:json][timeout:300];relation(id:{','.join(map(str, RELS))});out geom;"
        req = urllib.request.Request("https://overpass-api.de/api/interpreter", urllib.parse.urlencode({"data": q}).encode(), UA)
        for attempt in range(4):
            try:
                data = json.loads(urllib.request.urlopen(req, timeout=320).read())
                break
            except Exception as e:
                print("overpass", e, flush=True)
                time.sleep(60)
        json.dump(data, open(path, "w", encoding="utf8"))
    data = json.load(open(path, encoding="utf8"))
    uses, geom = Counter(), {}
    for rel in data["elements"]:
        for m in rel["members"]:
            if m["type"] == "way" and m.get("role") in ("outer", "") and m.get("geometry"):
                uses[m["ref"]] += 1
                geom[m["ref"]] = [[round(p["lon"], 6), round(p["lat"], 6)] for p in m["geometry"]]
    edge = [geom[w] for w, n in uses.items() if n == 1]
    rings, loose = stitch(edge)
    rings.sort(key=area_km2, reverse=True)
    def ring_simplify(r, tol):  # anello chiuso: si spezza nel punto più lontano dal primo
        k = max(range(len(r)), key=lambda i: (r[i][0] - r[0][0]) ** 2 + (r[i][1] - r[0][1]) ** 2)
        return simplify(r[:k + 1], tol) + simplify(r[k:], tol)[1:]
    rings = [ring_simplify(r, 0.003) for r in rings if area_km2(r) > 2]
    print(len(data["elements"]), "relazioni;", len(edge), "vie esterne;", len(rings), "anelli; aperti", len(loose),
          "; km2", [round(area_km2(r)) for r in rings[:3]], "; punti", sum(map(len, rings)))
    text = open(territories, encoding="utf8").read()
    terr = json.loads(text.split("=", 1)[1].rstrip().rstrip(";"))
    for x in terr:
        if x["n"] in ("Manciukuò", "Manciukuò, costa", "Armata Rossa in Manciuria") and x["from"] >= "1945-01" and x["to"] <= "1945-08":
            x["rings"] = rings
            x.pop("_d", None)
            if x["n"] == "Manciukuò":
                x["d"] = ("Stato fantoccio giapponese dal 1932, compreso il Rehe (annesso nel 1933). Confini: le province attuali della Manciuria "
                          "(Heilongjiang, Jilin, Liaoning) e della Mongolia Interna orientale (Hulunbuir, Hinggan, Tongliao, Chifeng) più Chengde, da OpenStreetMap. "
                          "Invaso dai sovietici il 9 agosto 1945.")
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr, separators=(",", ":"), ensure_ascii=False) + ";\n")


if __name__ == "__main__":
    main(*sys.argv[1:3])
