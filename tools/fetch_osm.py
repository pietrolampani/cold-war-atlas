"""Scarica da OpenStreetMap (Overpass) i dati grezzi della planimetria di Berlino.

Uso: python -I tools/fetch_osm.py cartella_di_destinazione
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

MIRRORS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter", "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]
BER = "52.33,13.05,52.68,13.78"
CHARLIE = "52.495,13.37,52.52,13.41"
ALPHA = "52.19,11.0,52.23,11.1"
BRAVO = "52.39,13.15,52.42,13.21"

QUERIES = {
    "wall": 'relation(6651797);out geom;',
    "hinter": f'(way["historic"="wall"]({BER});way["barrier"="wall"]["wall"="historic"]({BER});way["historic"="citywalls"]({BER});'
              f'way["barrier"="wall"]["historic"="memorial"]({BER}););out geom tags;',
    "water": f'(way["natural"="water"]({BER});relation["natural"="water"]({BER});way["waterway"~"^(river|canal|riverbank)$"]({BER}););out geom tags;',
    "roads": f'way["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"]({BER});out geom tags;',
    "streets": f'way["highway"~"^(residential|unclassified|living_street|pedestrian)$"]({CHARLIE});out geom tags;',
    "rail": f'way["railway"~"^(rail|light_rail)$"]({BER});out geom tags;',
    "towers": f'(nwr["name"~"Wachturm|Grenzturm|Führungsstelle|Fuehrungsstelle|Kommandantenturm|Grenzwachturm"]({BER});'
              f'nwr["man_made"="watchtower"]({BER});nwr["man_made"="tower"]["historic"]({BER}););out center tags;',
    "alpha": f'(way["building"]({ALPHA});way["highway"~"^(motorway|trunk|motorway_link|primary|secondary|tertiary|service|unclassified)$"]({ALPHA});'
             f'nwr["name"~"Marienborn|Deutsche Teilung|Grenzübergang|Checkpoint"]({ALPHA}););out geom tags;',
    "bravo": f'(way["building"]({BRAVO});way["highway"~"^(motorway|trunk|motorway_link|primary|secondary|tertiary|service)$"]({BRAVO});'
             f'relation(9089128);way(r);nwr["name"~"Checkpoint|Kontrollpunkt|Grenz|Zollamt"]({BRAVO}););out geom tags;',
    "suez": 'way["name"~"Suez Canal|قناة السويس"]["waterway"](29.8,32.2,31.4,32.7);out geom tags;',
    "benhai": 'way["waterway"="river"]["name"~"Bến Hải|Ben Hai"](16.7,106.4,17.2,107.2);out geom tags;',
}


def main(out):
    os.makedirs(out, exist_ok=True)
    for name, q in QUERIES.items():
        path = os.path.join(out, name + ".json")
        if os.path.exists(path):
            continue
        body = urllib.parse.urlencode({"data": f"[out:json][timeout:170];{q}"}).encode()
        data = None
        for attempt in range(8):
            host = MIRRORS[attempt % len(MIRRORS)]
            req = urllib.request.Request(host, body, {"User-Agent": "ColdWarAtlas/1.0 (personal history map)", "Accept": "*/*"})
            try:
                data = urllib.request.urlopen(req, timeout=180).read()
                break
            except Exception as e:
                print(name, host, e, flush=True)
                time.sleep(15)
        if data is None:
            print(name, "NON SCARICATO", flush=True)
            continue
        with open(path, "wb") as h:
            h.write(data)
        print(name, round(len(data) / 1e6, 2), "MB", len(json.loads(data)["elements"]), "elementi", flush=True)
        time.sleep(3)


if __name__ == "__main__":
    main(sys.argv[1])
