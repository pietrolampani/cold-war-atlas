"""Controlla tutte le isole coreane con nome in OSM contro borders-hi.js e scrive tools/korea_check.txt.

Per ogni isola: è presente? È dello Stato giusto? L'atteso viene dai confini OSM e dalle cinque isole del nord-ovest.

Uso: python -I tools/check_korea.py borders-hi.js korea_rel.json korea_islands.json
"""
import json
import sys


def main(borders, rel, islands):
    t = json.loads(open(borders, encoding="utf8").read().split("=", 1)[1].rstrip().rstrip(";"))
    sx, sy = t["transform"]["scale"]
    tx, ty = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in a:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def rings(g):
        out = []
        for poly in g["arcs"]:
            r = []
            for i in poly[0]:
                r += arcs[i] if i >= 0 else arcs[~i][::-1]
            out.append(r)
        return out

    state = {}
    for g in t["objects"]["states"]["geometries"]:
        p = g["properties"]
        if p["c"] in (731, 732) and p["s"] > 1953 * 12:
            state[p["c"]] = rings(g)
    print("anelli: Nord", len(state[731]), "Sud", len(state[732]))

    def hit(r, x, y):
        inside = False
        for (ax, ay), (bx, by) in zip(r, r[1:]):
            if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
                inside = not inside
        return inside

    def where(x, y):
        for c, rs in state.items():
            if any(hit(r, x, y) for r in rs):
                return {731: "KP", 732: "KR"}[c]
        # Isolotti a mezzaluna: il baricentro cade in acqua, vale un vertice dell'isola entro 300 metri
        for c, rs in state.items():
            for r in rs:
                if any(abs(a - x) < 0.0033 and abs(b - y) < 0.0027 for a, b in r):
                    return {731: "KP", 732: "KR"}[c]
        return None

    segs = {}
    for e in json.load(open(rel, encoding="utf8"))["elements"]:
        s = []
        for m in e["members"]:
            g = m.get("geometry") or []
            s += [((a["lon"], a["lat"]), (b["lon"], b["lat"])) for a, b in zip(g, g[1:])]
        segs[e["tags"]["ISO3166-1"]] = s

    def expect(x, y):
        res = []
        for iso, s in segs.items():
            inside = False
            for (ax, ay), (bx, by) in s:
                if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
                    inside = not inside
            if inside:
                res.append(iso)
        return res[0] if len(res) == 1 else "?"

    rows, tot = [], {"ok": 0, "sbagliata": 0, "assente": 0, "dubbia": 0}
    seen = set()
    for e in json.load(open(islands, encoding="utf8"))["elements"]:
        tags = e.get("tags", {})
        if not tags.get("place") or not tags.get("name"):
            continue
        if e.get("geometry"):
            g = e["geometry"]
            x, y = sum(p["lon"] for p in g) / len(g), sum(p["lat"] for p in g) / len(g)
        elif "lat" in e:
            x, y = e["lon"], e["lat"]
        else:
            continue
        key = (round(x, 3), round(y, 3))
        if key in seen:
            continue
        seen.add(key)
        want, got = expect(x, y), where(x, y)
        if want == "?":
            verdict = "dubbia"
        elif got is None:
            verdict = "assente"
        else:
            verdict = "ok" if got == want else "sbagliata"
        tot[verdict] += 1
        rows.append((verdict, tags.get("name:en") or tags["name"], tags["place"], e["type"], round(y, 4), round(x, 4), want, got))
    rows.sort()
    with open("tools/korea_check.txt", "w", encoding="utf8") as h:
        h.write("esito\tnome\ttipo\telemento\tlat\tlon\tatteso\ttrovato\n")
        for r in rows:
            h.write("\t".join(str(v) for v in r) + "\n")
    print(tot)
    for r in rows:
        if r[0] != "ok":
            print(ascii(r))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
