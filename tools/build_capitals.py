"""Estrae da CShapes le capitali 1945-1991 con le loro date e scrive capitals.js.

Uso: python -I tools/build_capitals.py CShapes-2.0.geojson capitals.js
Stampa i nomi senza traduzione, da aggiungere a NOMI se serve.
"""
import json
import sys

START = 1945 * 12
END = 1991 * 12 + 11
NOMI = {}
if len(sys.argv) > 3:
    NOMI = json.load(open(sys.argv[3], encoding="utf8"))


def main(src, dst):
    rows = {}
    for f in json.load(open(src, encoding="utf8"))["features"]:
        p = f["properties"]
        s = p["gwsyear"] * 12 + p["gwsmonth"] - 1
        e = p["gweyear"] * 12 + p["gwemonth"] - 1
        if e < START or s > END or not p.get("capname"):
            continue
        rows.setdefault(p["gwcode"], []).append((s, e, p["capname"], round(p["caplat"], 3), round(p["caplong"], 3)))
    out, names = [], set()
    for code, items in rows.items():
        items.sort()
        cur = None
        for s, e, name, lat, lon in items:
            if cur and cur[3] == name:
                cur[2] = max(cur[2], e)
            else:
                cur = [code, s, e, name, lat, lon]
                out.append(cur)
            names.add(name)
    for r in out:
        # In CShapes alcuni accenti sono illeggibili
        r[3] = "Kinshasa" if r[3].startswith("Kinshasa") else "Nouméa" if r[3].startswith("Noum") else NOMI.get(r[3], r[3])
    print(len(out), "periodi,", len(names), "nomi")
    print(sorted(names))
    with open(dst, "w", encoding="utf8") as h:
        h.write("window.CAPITALS=" + json.dumps(out, separators=(",", ":"), ensure_ascii=False) + ";\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
