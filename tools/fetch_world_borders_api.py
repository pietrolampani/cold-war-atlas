"""Scarica i confini di Stato terrestri Stato per Stato dall'API principale di OpenStreetMap, molto più rapida di Overpass.

Le relazioni OSM degli Stati vengono da Wikidata (P297 codice ISO, P402 relazione OSM), più gli Stati senza codice ISO in EXTRA.
Tiene le vie con gli stessi filtri di fetch_world_borders.py. Si può rilanciare: gli Stati già scaricati restano nella cache.
Unisce il risultato ai riquadri Overpass già scaricati e riporta quante vie di quei riquadri l'API non ha trovato.

Uso: python -I tools/fetch_world_borders_api.py cache_api cache_overpass world_borders.json
"""
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "ColdWarAtlas/1.0 (personal history map)", "Accept": "application/json"}
API = "https://www.wikidata.org/w/api.php"
SEARCH = "haswbstatement:P297 haswbstatement:P402"
EXTRA = {"XK": "Q1246", "SOMALILAND": "Q34754", "N_CYPRUS": "Q23681"}
SECONDS_PER_MB = 5
# Solo gli Stati con confini terrestri nei riquadri che Overpass non ha completato (a nord di 30°N); il resto viene da quei riquadri
NEED = set("""AD AF AL AM AT AZ BA BE BG BY CA CH CN CY CZ DE DK EE EG ES FI FR GB GE GR HR HU IE IL IN IQ IR IT JO KG KP KR KZ LB LI LT LU LV LY
MC MD ME MK MN NL NO NP PK PL PS RO RS RU SA SE SI SK SM SY TJ TM TN TR UA US UZ VA XK N_CYPRUS""".split())


def get(url, timeout=170):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read())


def thin(g):
    out = [g[0]]
    for p in g[1:-1]:
        k = math.cos(math.radians(p["lat"]))
        if math.hypot((p["lon"] - out[-1]["lon"]) * k, p["lat"] - out[-1]["lat"]) * 111320 >= 100:
            out.append(p)
    out.append(g[-1])
    return out


def relations():
    rels, ids, off = {}, [], 0
    while off is not None:  # La ricerca di Wikidata, perché il suo SPARQL limita a una richiesta al minuto
        reply = get(API + "?action=query&list=search&format=json&srlimit=500&srnamespace=0&srsearch=" + urllib.parse.quote(SEARCH) + f"&sroffset={off}")
        ids += [r["title"] for r in reply["query"]["search"]]
        off = reply.get("continue", {}).get("sroffset")
    for i in range(0, len(ids), 50):
        for ent in get(API + "?action=wbgetentities&props=claims&format=json&ids=" + "|".join(ids[i:i + 50]))["entities"].values():
            claims = ent["claims"]
            iso, rel = [[c["mainsnak"]["datavalue"]["value"] for c in claims.get(p, []) if "datavalue" in c["mainsnak"]] for p in ("P297", "P402")]
            if iso and rel and "P576" not in claims:  # Niente Stati scomparsi
                rels.setdefault(iso[0], rel[0])
        time.sleep(1)
    ents = get(API + "?action=wbgetentities&props=claims&format=json&ids=" + "|".join(EXTRA.values()))["entities"]
    for name, q in EXTRA.items():
        claims = ents[q]["claims"].get("P402")
        if claims:
            rels[name] = claims[0]["mainsnak"]["datavalue"]["value"]
        else:
            print("SENZA RELAZIONE", name, flush=True)
    return rels


def country(rel):
    req = urllib.request.Request(f"https://api.openstreetmap.org/api/0.6/relation/{rel}/full.json", headers=UA)
    raw = urllib.request.urlopen(req, timeout=170).read()
    time.sleep(len(raw) / 1e6 * SECONDS_PER_MB)  # L'API limita la banda: si rallenta in proporzione a quanto si è scaricato
    els = json.loads(raw)["elements"]
    nodes = {e["id"]: {"lat": e["lat"], "lon": e["lon"]} for e in els if e["type"] == "node"}
    rows = []
    for e in els:
        t = e.get("tags", {})
        if e["type"] != "way" or t.get("boundary") != "administrative" or t.get("admin_level") != "2":
            continue
        if t.get("maritime") == "yes" or t.get("natural") == "coastline":
            continue
        rows.append({"type": "way", "id": e["id"], "geometry": thin([nodes[n] for n in e["nodes"]])})
    return rows


def main(cache, boxes, out):
    os.makedirs(cache, exist_ok=True)
    rels = relations()
    print(len(rels), "Stati", flush=True)
    failed = []
    print("mancano da Wikidata:", " ".join(sorted(NEED - set(rels))), flush=True)
    for iso, rel in sorted(rels.items()):
        path = os.path.join(cache, iso + ".json")
        if iso not in NEED or os.path.exists(path):
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
        time.sleep(1)
    if failed:
        print("INCOMPLETO", " ".join(failed), flush=True)
        return
    seen, rows = set(), []
    for f in os.listdir(cache):
        for r in json.load(open(os.path.join(cache, f))):
            if r["id"] not in seen:
                seen.add(r["id"])
                rows.append(r)
    api, only_box = len(rows), 0
    for f in os.listdir(boxes):
        for r in json.load(open(os.path.join(boxes, f))):
            if r["id"] not in seen:
                seen.add(r["id"])
                rows.append(r)
                only_box += 1
    with open(out, "w") as h:
        json.dump({"elements": rows}, h, separators=(",", ":"))
    print("FATTO", api, "vie API,", only_box, "vie solo nei riquadri Overpass,", sum(len(r["geometry"]) for r in rows), "punti", round(os.path.getsize(out) / 1e6, 1), "MB", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
