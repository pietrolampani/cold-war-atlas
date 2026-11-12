"""Scarica i grandi fiumi da OpenStreetMap: relazioni da Wikidata (P402 dalla voce inglese), vie dall'API principale.

Si tengono il corso principale e le vie senza ruolo, non gli affluenti. Si può rilanciare: i fiumi scaricati restano nella cache.
Rallenta in proporzione ai dati scaricati, perché l'API limita la banda.

Uso: python -I tools/fetch_rivers.py cartella_cache
"""
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "ColdWarAtlas/1.0 (personal history map)", "Accept": "application/json"}
SECONDS_PER_MB = 5
SKIP_ROLES = {"side_stream", "tributary", "spring", "source", "mouth", "outflow", "inflow", "anabranch"}
RIVERS = """Nile|White Nile|Blue Nile|Congo River|Ubangi River|Kasai River|Niger River|Benue River|Zambezi|Orange River|Limpopo River|Senegal River|Volta River|Okavango River|Juba River|Shebelle River|Kunene River|Cuanza River|Amazon River|Madeira River|Tocantins River|Paraná River|Paraguay River|Uruguay River|Orinoco|São Francisco River|Magdalena River|Mississippi River|Missouri River|Ohio River|Rio Grande|Colorado River|Columbia River|Yukon River|Mackenzie River|Saint Lawrence River|Nelson River|Arkansas River|Hudson River|Danube|Rhine|Elbe|Oder|Vistula|Seine|Loire|Rhône|Garonne|Po (river)|Tagus|Ebro|Douro|Guadalquivir|River Thames|Tiber|Adige|Isonzo|Dnieper|Dniester|Don (river)|Volga|Kama (river)|Northern Dvina|Pechora River|Ural (river)|Neva|Daugava|Neman|Sava|Drava|Tisza|Vardar|Maritsa|Tigris|Euphrates|Jordan River|Kura (Caspian Sea)|Aras (river)|Indus River|Ganges|Brahmaputra River|Godavari River|Irrawaddy River|Salween|Mekong|Red River (Asia)|Chao Phraya River|Yangtze|Yellow River|Xi River|Amur|Songhua|Yalu River|Imjin River|Han River (Korea)|Ob River|Irtysh|Yenisey|Angara|Lena River|Kolyma River|Helmand River|Kabul River|Karun|Murray River|Darling River|Amu Darya|Syr Darya|Juba River (Africa)|Cunene River|St. Lawrence River|Soča|Pechora (river)|Kura (river)|Aras (river)|Aras River|Salween River|Songhua River|Ob (river)|Yenisei|Kolyma (river)|Kolyma""".split("|")


def get(url, timeout=170):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read())


def thin(g):
    out = [g[0]]
    for p in g[1:-1]:
        k = math.cos(math.radians(p[1]))
        if math.hypot((p[0] - out[-1][0]) * k, p[1] - out[-1][1]) * 111320 >= 100:
            out.append(p)
    out.append(g[-1])
    return [[round(x, 4), round(y, 4)] for x, y in out]


def relations():
    out = {}
    for i in range(0, len(RIVERS), 40):
        batch = RIVERS[i:i + 40]
        reply = get("https://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&props=claims|sitelinks&format=json&titles=" + urllib.parse.quote("|".join(batch)))
        for ent in reply["entities"].values():
            if "missing" in ent:
                continue
            title = ent["sitelinks"]["enwiki"]["title"]
            vals = [c["mainsnak"]["datavalue"]["value"] for c in ent["claims"].get("P402", []) if "datavalue" in c["mainsnak"]]
            if vals:
                out[title] = vals[0]
        time.sleep(1)
    return out


def fetch(rel, seen, depth=0):
    req = urllib.request.Request(f"https://api.openstreetmap.org/api/0.6/relation/{rel}/full.json", headers=UA)
    raw = urllib.request.urlopen(req, timeout=170).read()
    time.sleep(len(raw) / 1e6 * SECONDS_PER_MB + 1)
    els = json.loads(raw)["elements"]
    nodes = {e["id"]: [e["lon"], e["lat"]] for e in els if e["type"] == "node"}
    ways = {e["id"]: e for e in els if e["type"] == "way"}
    head = next(e for e in els if e["type"] == "relation" and e["id"] == int(rel))
    lines = []
    for m in head["members"]:
        if m.get("role") in SKIP_ROLES:
            continue
        if m["type"] == "way" and m["ref"] in ways:
            lines.append(thin([nodes[n] for n in ways[m["ref"]]["nodes"]]))
        elif m["type"] == "relation" and depth < 3 and m["ref"] not in seen:
            seen.add(m["ref"])
            lines += fetch(m["ref"], seen, depth + 1)[0]
    return lines, head["tags"]


def main(cache):
    os.makedirs(cache, exist_ok=True)
    rels = relations()
    print(len(rels), "relazioni su", len(RIVERS), "; senza:", [r for r in RIVERS if r not in rels and r.replace("_", " ") not in rels], flush=True)
    failed = []
    for name, rel in sorted(rels.items()):
        path = os.path.join(cache, name.replace(" ", "_").replace("(", "").replace(")", "") + ".json")
        if os.path.exists(path):
            continue
        for attempt in range(6):
            try:
                lines, tags = fetch(rel, {int(rel)})
                with open(path, "w", encoding="utf8") as h:
                    json.dump({"n": name, "rel": rel, "name": tags.get("name:en") or tags.get("name"), "type": tags.get("type"), "lines": lines}, h, separators=(",", ":"), ensure_ascii=False)
                km = sum(math.hypot((a[0] - b[0]) * math.cos(math.radians(a[1])), a[1] - b[1]) * 111.32 for l in lines for a, b in zip(l, l[1:]))
                print(name, rel, tags.get("name:en") or tags.get("name"), tags.get("type"), "vie", len(lines), "km", round(km), flush=True)
                break
            except Exception as ex:
                wait = int((getattr(ex, "headers", None) or {}).get("Retry-After") or 0) or 120 * 2 ** attempt
                print(name, rel, ex, "attendo", wait, "s", flush=True)
                time.sleep(wait)
        else:
            failed.append(name)
    print("INCOMPLETO " + " | ".join(failed) if failed else "FATTO", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
