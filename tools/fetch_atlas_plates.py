"""Scarica lentamente le tavole dell'Atlas of the World Battle Fronts (Army Map Service, 1945, pubblico dominio) da Wikimedia Commons.

Uso: python -I tools/fetch_atlas_plates.py cartella data1Ger data2Jap ...   (es. 1945-01-15Ger)
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "ColdWarAtlas/1.0 (personal history map; low volume)"}


def main(folder, names):
    os.makedirs(folder, exist_ok=True)
    titles = "|".join(f"File:{n}WW2BattlefrontAtlas.jpg" for n in names)
    url = "https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url&titles=" + urllib.parse.quote(titles)
    pages = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read())["query"]["pages"].values()
    for p in pages:
        name = p["title"][5:].replace("WW2BattlefrontAtlas", "")
        dst = os.path.join(folder, name)
        if os.path.exists(dst) and os.path.getsize(dst) > 10000:
            continue
        for attempt in range(3):
            try:
                data = urllib.request.urlopen(urllib.request.Request(p["imageinfo"][0]["url"], headers=UA), timeout=120).read()
                open(dst, "wb").write(data)
                print(name, len(data), flush=True)
                break
            except Exception as ex:
                print(name, ex, flush=True)
                time.sleep(600)
        time.sleep(120)
    print("FATTO", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
