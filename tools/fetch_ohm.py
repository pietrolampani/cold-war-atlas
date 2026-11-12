"""Scarica relazioni da OpenHistoricalMap e ne ricuce gli anelli esterni.

Uso: python -I tools/fetch_ohm.py cartella id1 id2 ...
Scrive cartella/id.json con {"tags": ..., "rings": [[[lon, lat], ...], ...], "open": segmenti non chiusi}.
"""
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "ColdWarAtlas/1.0 (personal history map)", "Accept": "application/json"}


def stitch(lines):
    rings, loose = [], []
    lines = [l for l in lines if len(l) > 1]
    while lines:
        line = lines.pop()
        grown = True
        while grown and line[0] != line[-1]:
            grown = False
            for i, o in enumerate(lines):
                if o[0] == line[-1]:
                    line = line + o[1:]
                elif o[-1] == line[-1]:
                    line = line + o[::-1][1:]
                elif o[-1] == line[0]:
                    line = o + line[1:]
                elif o[0] == line[0]:
                    line = o[::-1] + line[1:]
                else:
                    continue
                lines.pop(i)
                grown = True
                break
        (rings if line[0] == line[-1] else loose).append(line)
    return rings, loose


def area_km2(r):
    lat0 = math.radians(sum(p[1] for p in r) / len(r))
    return abs(sum((p[0] - q[0]) * (p[1] + q[1]) / 2 for p, q in zip(r, r[1:]))) * math.cos(lat0) * 111.32 ** 2


def main(folder, ids):
    os.makedirs(folder, exist_ok=True)
    for rel in ids:
        body = urllib.parse.urlencode({"data": f"[out:json][timeout:90];relation({rel});out geom;"}).encode()
        req = urllib.request.Request("https://overpass-api.openhistoricalmap.org/api/interpreter", body, UA)
        head = json.loads(urllib.request.urlopen(req, timeout=120).read())["elements"][0]
        outer = [m for m in head["members"] if m["type"] == "way" and m.get("role") in ("outer", "") and m.get("geometry")]
        rings, loose = stitch([[[p["lon"], p["lat"]] for p in m["geometry"]] for m in outer])
        rings.sort(key=area_km2, reverse=True)
        with open(os.path.join(folder, f"{rel}.json"), "w", encoding="utf8") as h:
            json.dump({"tags": head["tags"], "rings": rings, "open": loose}, h, separators=(",", ":"), ensure_ascii=False)
        t = head["tags"]
        print(rel, t.get("name"), t.get("start_date"), t.get("end_date"), "anelli", len(rings), "aperti", len(loose), "km2", [round(area_km2(r)) for r in rings[:4]], "punti", sum(map(len, rings)), "licenza", t.get("license"), flush=True)
        time.sleep(1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
