"""Unisce Archigos 4.1 (leader effettivi, tutti gli Stati) ai capi di Stato di Wikidata in leaders.js.

Dove Wikidata ha un capo di Stato con date resta quello; negli altri Stati si usa Archigos, indicato come "leader".
Formato righe di leaders.js: [codice, inizio, fine, nome, id foto o "", tipo] con tipo "h" capo di Stato, "l" leader.

Uso: python -I tools/build_archigos.py Archigos.dta leaders_wikidata.json leaders.js
"""
import base64
import datetime
import json
import os
import re
import struct
import sys
import time
import urllib.parse
import urllib.request


def read_dta(path):
    b = open(path, "rb").read()
    assert b[:11] == b"<stata_dta>", "non è un file Stata recente"
    h = b.index(b"<release>") + 9
    release = int(b[h:h + 3])
    pos = b.index(b"<K>") + 3
    k = struct.unpack("<H", b[pos:pos + 2])[0]
    pos = b.index(b"<N>") + 3
    n = struct.unpack("<Q" if release >= 118 else "<I", b[pos:pos + (8 if release >= 118 else 4)])[0]
    pos = b.index(b"<variable_types>") + 16
    types = struct.unpack(f"<{k}H", b[pos:pos + 2 * k])
    pos = b.index(b"<varnames>") + 10
    width = 129 if release >= 118 else 33
    names = [b[pos + i * width:pos + (i + 1) * width].split(b"\0")[0].decode() for i in range(k)]
    strls = {}
    s0 = b.index(b"<strls>") + 7
    s1 = b.index(b"</strls>", s0)
    p = s0
    while p < s1 and b[p:p + 3] == b"GSO":
        v, o = struct.unpack("<IQ", b[p + 3:p + 15])
        t = b[p + 15]
        ln = struct.unpack("<I", b[p + 16:p + 20])[0]
        strls[(v, o)] = b[p + 20:p + 20 + ln].split(b"\0")[0].decode("utf8", "replace")
        p += 20 + ln
    p = b.index(b"<data>") + 6
    sizes = {65526: ("<d", 8), 65527: ("<f", 4), 65528: ("<i", 4), 65529: ("<h", 2), 65530: ("<b", 1)}
    rows = []
    for _ in range(n):
        r = {}
        for name, t in zip(names, types):
            if t in sizes:
                fmt, sz = sizes[t]
                r[name] = struct.unpack(fmt, b[p:p + sz])[0]
                p += sz
            elif t == 32768:
                v = struct.unpack("<H", b[p:p + 2])[0]
                o = int.from_bytes(b[p + 2:p + 8], "little")
                r[name] = strls.get((v, o), "")
                p += 8
            else:
                r[name] = b[p:p + t].split(b"\0")[0].decode("utf8", "replace")
                p += t
        rows.append(r)
    return rows


def to_ym(v):
    if isinstance(v, str):
        return v[:7] if len(v) >= 7 and v[4] == "-" else None
    if v is None or v != v or abs(v) > 1e7:
        return None
    return (datetime.date(1960, 1, 1) + datetime.timedelta(days=int(v))).strftime("%Y-%m")


def fetch_photos(res, photo_dir, photos_out, limit):
    """Miniature da Wikipedia per i leader Archigos, dai mandati più lunghi. Si può rilanciare: riparte da dove era."""
    UA = {"User-Agent": "ColdWarAtlas/1.0 (personal history map)", "Accept": "*/*"}
    span = {}
    for r in res:
        if r[4].startswith("A"):
            y0, y1 = int(r[1][:4]), int((r[2] or "1991")[:4])
            span[r[4]] = span.get(r[4], 0) + min(y1, 1991) - max(y0, 1945)
    order = sorted(span, key=lambda k: -span[k])
    todo = [k for k in order if not os.path.exists(os.path.join(photo_dir, safe(k) + ".jpg"))][:limit]
    urls = {}
    for i in range(0, len(todo), 50):
        titles = [urllib.parse.unquote(k[1:]).replace("_", " ") for k in todo[i: i + 50]]
        q = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "pageimages", "pithumbsize": 72, "redirects": 1, "pilimit": 50, "titles": "|".join(titles)})
        try:
            data = json.load(urllib.request.urlopen(urllib.request.Request("https://en.wikipedia.org/w/api.php?" + q, headers=UA), timeout=60))
        except Exception as e:
            print("wikipedia", e, flush=True)
            time.sleep(30)
            continue
        back = {}
        for m in data["query"].get("normalized", []) + data["query"].get("redirects", []):
            back[m["to"]] = back.get(m["from"], m["from"])
        for page in data["query"]["pages"].values():
            if "thumbnail" in page:
                t = back.get(page["title"], page["title"])
                urls["A" + urllib.parse.quote(t.replace(" ", "_"), safe="_(),.'-")] = page["thumbnail"]["source"]
                urls["A" + t.replace(" ", "_")] = page["thumbnail"]["source"]
        time.sleep(2)
    done = 0
    for k in todo:
        url = urls.get(k) or urls.get("A" + urllib.parse.unquote(k[1:]))
        if not url:
            continue
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            with open(os.path.join(photo_dir, safe(k) + ".jpg"), "wb") as f:
                f.write(raw)
            done += 1
            time.sleep(2)
        except Exception as e:
            print("foto", e, flush=True)
            time.sleep(30)
    print("foto scaricate", done, "su", len(todo), flush=True)
    photos = {}
    for name in os.listdir(photo_dir):
        path = os.path.join(photo_dir, name)
        if os.path.getsize(path) < 40000:
            raw = open(path, "rb").read()
            kind = "png" if raw[:4] == b"\x89PNG" else "jpeg"
            photos[name[:-4]] = f"data:image/{kind};base64," + base64.b64encode(raw).decode()
    for r in res:
        if r[4] and safe(r[4]) != r[4]:
            r[4] = safe(r[4])
    with open(photos_out, "w", encoding="utf8") as h:
        h.write("window.PHOTOS=" + json.dumps(photos, separators=(",", ":")) + ";\n")
    print("photos.js", round(os.path.getsize(photos_out) / 1e6, 2), "MB,", len(photos), "foto")


def safe(k):
    return re.sub(r"[^A-Za-z0-9_]", "_", k)


def main(dta, wiki, out):
    rows = read_dta(dta)
    print(sorted(rows[0]), {k: rows[0][k] for k in ("ccode", "leader", "startdate", "enddate") if k in rows[0]})
    with open(wiki, encoding="utf8") as h:
        wd = json.loads(h.read().split("=", 1)[1].rstrip().rstrip(";"))
    has = {r[0] for r in wd}
    res = [[r[0], r[1], r[2], r[3], r[4], "h"] for r in wd]
    used = 0
    for r in rows:
        code = int(r["ccode"])
        s, e = to_ym(r["startdate"]), to_ym(r["enddate"])
        if not s or s > "1991-12" or (e and e < "1945-01"):
            continue
        uri = r.get("dbpediauri", "") or ""
        # I link passano da un filtro di posta: resource_Harry-5FS.-5FTruman, con -5F al posto di _
        found = re.search(r"dbpedia\.org_resource_([^&]+)", uri)
        title = found.group(1) if found else ""
        title = urllib.parse.unquote(re.sub(r"-([0-9A-F]{2})", r"%\1", title).replace("_", "%2F")).rsplit("/", 1)[-1]
        name = title.replace("_", " ").split(" (")[0] if title else r["leader"]
        if "�" in name:  # accenti rovinati dal filtro: resta il cognome di Archigos
            name = r["leader"].replace("�", "")
        res.append([code, s, e, name, ("A" + title) if title else "", "l"])
        used += 1
    # Capi di governo da Wikidata; la foto si prende dal leader Archigos con lo stesso cognome
    gov = os.path.join(os.path.dirname(wiki), "leaders_gov.json")
    if os.path.exists(gov):
        seen = set()
        arch = [r for r in res if r[5] == "l"]
        for g in json.load(open(gov, encoding="utf8")):
            key = (g["c"], g["h"], g["s"])
            if key in seen or g["n"].startswith("Q"):
                continue
            seen.add(key)
            last = g["n"].split()[-1].lower()
            match = next((a[4] for a in arch if a[0] == g["c"] and a[3].lower().endswith(last)), "")
            res.append([g["c"], g["s"], g["e"], g["n"], match, "g"])
    res.sort(key=lambda x: (x[0], x[1]))
    if len(sys.argv) > 4:
        fetch_photos(res, sys.argv[4], sys.argv[5], int(sys.argv[6]))
    with open(out, "w", encoding="utf8") as h:
        h.write("window.LEADERS=" + json.dumps(res, separators=(",", ":"), ensure_ascii=False) + ";\n")
    print(len(res), "righe,", used, "da Archigos,", len({r[0] for r in res}), "Stati")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
