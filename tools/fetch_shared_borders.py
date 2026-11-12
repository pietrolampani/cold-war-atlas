"""Recupera i confini le cui vie OSM non hanno l'etichetta di confine di Stato: l'etichetta sta solo nella relazione dello Stato.

Una via senza etichetta è confine terrestre se appartiene alle relazioni di due Stati: le coste e le linee in mare stanno in una sola.
Unisce il risultato a quanto già scaricato con fetch_world_borders.py e fetch_world_borders_api.py.

Uso: python -I tools/fetch_shared_borders.py cache_condivisi cache_api cache_overpass world_borders.json
"""
import json
import math
import os
import sys
import time
import urllib.request
from collections import Counter

UA = {"User-Agent": "ColdWarAtlas/1.0 (personal history map)", "Accept": "application/json"}
SECONDS_PER_MB = 5
RELS = {"AF": 303427, "AM": 364066, "AZ": 364110, "BT": 184629, "BY": 59065, "CA": 1428125, "CD": 192795, "CF": 192790, "CG": 192794, "CM": 192830, "CN": 270056,
        "CO": 120027, "CY": 307787, "DE": 51477, "DZ": 192756, "EE": 79510, "EG": 1473947, "EH": 2559126, "FI": 54224, "GA": 192793, "GE": 28699, "GH": 192781,
        "GY": 287083, "HU": 21335, "ID": 304751, "IL": 1473946, "IN": 304716, "JO": 184818, "KG": 178009, "KZ": 214665, "LB": 184843, "LT": 72596, "LV": 72594,
        "LY": 192758, "MA": 3630439, "MD": 58974, "MN": 161033, "MR": 192763, "MX": 114686, "MY": 2108121, "NO": 2978650, "NP": 184633, "N_CYPRUS": 2514541, "OM": 305138,
        "PK": 307573, "PL": 49715, "PS": 1703814, "RO": 90689, "RU": 60189, "SA": 307584, "SD": 192789, "SI": 218657, "SO": 192799, "SOMALILAND": 0, "SY": 184840,
        "TG": 192782, "TJ": 214626, "UA": 60199, "AE": 307763, "US": 148838, "VE": 272644}
RELS["SOMALILAND"] = 3536160


def thin(g):
    out = [g[0]]
    for p in g[1:-1]:
        k = math.cos(math.radians(p["lat"]))
        if math.hypot((p["lon"] - out[-1]["lon"]) * k, p["lat"] - out[-1]["lat"]) * 111320 >= 100:
            out.append(p)
    out.append(g[-1])
    return out


def country(rel):
    req = urllib.request.Request(f"https://api.openstreetmap.org/api/0.6/relation/{rel}/full.json", headers=UA)
    raw = urllib.request.urlopen(req, timeout=170).read()
    time.sleep(len(raw) / 1e6 * SECONDS_PER_MB)  # L'API limita la banda: si rallenta in proporzione a quanto si è scaricato
    els = json.loads(raw)["elements"]
    head = next(e for e in els if e["type"] == "relation" and e["id"] == rel)
    print(" ", head["tags"].get("name:en") or head["tags"].get("name"), "livello", head["tags"].get("admin_level"), round(len(raw) / 1e6, 1), "MB", flush=True)
    nodes = {e["id"]: {"lat": e["lat"], "lon": e["lon"]} for e in els if e["type"] == "node"}
    rows = []
    for e in els:
        t = e.get("tags", {})
        if e["type"] == "way" and t.get("maritime") != "yes" and t.get("natural") != "coastline":
            rows.append({"type": "way", "id": e["id"], "geometry": thin([nodes[n] for n in e["nodes"]])})
    return rows


def rows_in(folder):
    for f in os.listdir(folder):
        yield from json.load(open(os.path.join(folder, f)))


def main(shared, api, boxes, out):
    os.makedirs(shared, exist_ok=True)
    failed = []
    for iso, rel in sorted(RELS.items()):
        path = os.path.join(shared, iso + ".json")
        if os.path.exists(path):
            continue
        for attempt in range(6):
            try:
                rows = country(rel)
                with open(path, "w") as h:
                    json.dump(rows, h, separators=(",", ":"))
                print(iso, rel, len(rows), "vie", flush=True)
                break
            except Exception as ex:
                wait = int((getattr(ex, "headers", None) or {}).get("Retry-After") or 0) or 120 * 2 ** attempt
                print(iso, rel, ex, "attendo", wait, "s", flush=True)
                time.sleep(wait)
        else:
            failed.append(iso)
    if failed:
        print("INCOMPLETO", " ".join(failed), flush=True)
        return
    seen, rows = set(), []
    for folder in (api, boxes):
        for r in rows_in(folder):
            if r["id"] not in seen:
                seen.add(r["id"])
                rows.append(r)
    tagged = len(rows)
    count, geom = Counter(), {}
    for r in rows_in(shared):
        count[r["id"]] += 1
        geom[r["id"]] = r
    for i, n in count.items():
        if n >= 2 and i not in seen:
            seen.add(i)
            rows.append(geom[i])
    with open(out, "w") as h:
        json.dump({"elements": rows}, h, separators=(",", ":"))
    print("FATTO", tagged, "vie etichettate,", len(rows) - tagged, "vie condivise senza etichetta,", sum(len(r["geometry"]) for r in rows), "punti", round(os.path.getsize(out) / 1e6, 1), "MB", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:5])
