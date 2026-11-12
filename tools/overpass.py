"""Interrogazioni Overpass con cache su disco e più server: si prova il primo, e se risponde male (502, 504, 429, timeout)
si passa al successivo, con attese crescenti. Una risposta già in cache non si riscarica.

Uso come modulo: from overpass import query; data = query(ql, cache_path)
Uso da riga di comando: python -I tools/overpass.py "query QL" file_cache.json
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

SERVERS = ["https://overpass.private.coffee/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
           "https://maps.mail.ru/osm/tools/overpass/api/interpreter", "https://overpass-api.de/api/interpreter"]
UA = {"User-Agent": "ColdWarAtlas/1.0 (personal history map; Claude Code)"}


def query(ql, cache, timeout=300):
    if os.path.exists(cache):
        return json.load(open(cache, encoding="utf8"))
    body = urllib.parse.urlencode({"data": ql}).encode()
    wait = 10
    for rnd in range(3):
        for url in SERVERS:
            try:
                raw = urllib.request.urlopen(urllib.request.Request(url, body, UA), timeout=timeout + 30).read()
                data = json.loads(raw)
                if data.get("remark") and "runtime error" in data["remark"]:
                    raise RuntimeError(data["remark"][:200])
                os.makedirs(os.path.dirname(os.path.abspath(cache)), exist_ok=True)
                with open(cache, "wb") as h:
                    h.write(raw)
                print("overpass:", url.split("/")[2], round(len(raw) / 1e6, 1), "MB", flush=True)
                return data
            except Exception as e:
                print("overpass:", url.split("/")[2], "->", str(e)[:120], flush=True)
        time.sleep(wait)
        wait *= 3
    raise SystemExit("nessun server Overpass ha risposto")


if __name__ == "__main__":
    d = query(sys.argv[1], sys.argv[2])
    print(len(d.get("elements", [])), "elementi")
