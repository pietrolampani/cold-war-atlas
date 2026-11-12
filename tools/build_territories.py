"""Territori sovrapposti alla mappa in un intervallo di date. Scrive territories.js.

Uso: python -I tools/build_territories.py countries-10m.json enclaves.json territories.js
"""
import json
import os
import sys


def atlas(path):
    t = json.load(open(path, encoding="utf8"))
    sx, sy = t["transform"]["scale"]
    tx, ty = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0
        p = []
        for dx, dy in a:
            x += dx
            y += dy
            p.append([round(x * sx + tx, 4), round(y * sy + ty, 4)])
        arcs.append(p)
    out = {}
    for g in t["objects"]["countries"]["geometries"]:
        polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
        rings = []
        for poly in polys:
            for ring in poly[:1]:
                r = []
                for a in ring:
                    r += arcs[a] if a >= 0 else arcs[~a][::-1]
                rings.append(r)
        out[g["properties"]["name"]] = rings
    return out


def stitch(members):
    segs = [[[round(p["lon"], 5), round(p["lat"], 5)] for p in m["geometry"]] for m in members if m["type"] == "way" and m.get("role") == "outer" and m.get("geometry")]
    ends = {}
    rings = []
    while segs:
        line = segs.pop()
        grown = True
        while grown and line[0] != line[-1]:
            grown = False
            for i, s in enumerate(segs):
                if s[0] == line[-1]:
                    line += s[1:]
                elif s[-1] == line[-1]:
                    line += s[::-1][1:]
                else:
                    continue
                segs.pop(i)
                grown = True
                break
        if line[0] == line[-1] and len(line) > 3:
            rings.append(line)
    return rings


def coast_rings(folder, name, min_pts=4):
    # Le coste delle isole grandi sono spezzate in più tratti: si cuciono per estremi
    rings, heads = [], {}
    for e in json.load(open(os.path.join(folder, name), encoding="utf8"))["elements"]:
        g = [[round(p["lon"], 5), round(p["lat"], 5)] for p in e["geometry"]]
        if g[0] == g[-1]:
            if len(g) >= min_pts:
                rings.append(g)
        else:
            heads[tuple(g[0])] = g
    used = set()
    for h in list(heads):
        if h in used:
            continue
        line, cur = [], h
        while cur in heads and cur not in used:
            used.add(cur)
            line += heads[cur] if not line else heads[cur][1:]
            cur = tuple(line[-1])
        if line[0] == line[-1] and len(line) >= min_pts:
            rings.append(line)
    return rings


def extra(a, folder):
    def near(rings, spots, r=0.12):
        keep = []
        for g in rings:
            cx, cy = sum(p[0] for p in g) / len(g), sum(p[1] for p in g) / len(g)
            if any(abs(cx - x) < r and abs(cy - y) < r for x, y in spots):
                keep.append(g)
        return keep

    penghu = coast_rings(folder, "penghu.json")
    # Solo le isole davvero tenute da Taiwan: i riquadri comprendono anche isolotti cinesi
    kinmen = near(coast_rings(folder, "kinmen.json"), [(118.36, 24.45), (118.24, 24.43)], 0.08)
    matsu = near(coast_rings(folder, "matsu.json"), [(119.94, 26.16), (120.0, 26.22), (119.97, 25.97), (120.49, 26.37)], 0.05)
    macau_pen = [[113.5315, 22.2155], [113.5495, 22.2165], [113.5595, 22.2], [113.5555, 22.1885], [113.545, 22.1855], [113.533, 22.1945], [113.5315, 22.2155]]
    # Hengqin, subito a ovest, è cinese: restano Taipa e Coloane
    macau = [g for g in coast_rings(folder, "macau.json") if sum(p[0] for p in g) / len(g) > 113.548 and sum(p[1] for p in g) / len(g) < 22.178]
    # Zone di occupazione in Iran: confini del 1941, approssimati e ritagliati sullo Stato
    sov = [[[43.5, 40], [49, 39.9], [49.5, 37.3], [54, 37.3], [56, 38.3], [61.5, 36.7], [61, 35.7], [57.7, 36.1], [55, 36.2], [53.4, 35.45], [51.4, 35.75], [50, 36.1], [48.5, 36.5], [47, 36.9], [45.1, 37], [43.5, 37.2], [43.5, 40]]]
    gb = [[[45, 35.2], [46.5, 35], [48.3, 34.3], [50, 34.5], [51, 33], [52.5, 31.5], [54, 30], [57, 28], [58, 25], [53, 25], [47, 29], [45, 33], [45, 35.2]]]
    azer = [[[44.3, 38.5], [46, 39.8], [48.5, 39.6], [48.7, 37.3], [47.4, 36.5], [46.2, 36.8], [45.3, 37.2], [44.3, 38.5]]]
    mahabad = [[[45, 37.1], [46.2, 36.9], [46.2, 36.2], [45.2, 36.1], [45, 37.1]]]
    manchukuo = [[[119.5, 41.6], [118, 40.3], [119.6, 39.9], [121.5, 40.7], [122.2, 40.5], [121, 38.7], [125, 39.5], [128.5, 41.5], [131, 42.7], [131.5, 45.2], [135.2, 48.5], [130.5, 49.2], [127, 50.2], [125.5, 53.7], [120.2, 53.4], [116.3, 49.9], [116.8, 47.8], [119.2, 46.8], [120.5, 45], [119.6, 43.2], [119.5, 41.6]]]
    return [
        {"n": "Kuwait", "from": "1945-01", "to": "1961-05", "look": "emp-uk", "rings": a["Kuwait"], "d": "Protettorato britannico fino al giugno 1961. Contorno di oggi."},
        {"n": "Bahrein", "from": "1945-01", "to": "1971-07", "look": "emp-uk", "rings": a["Bahrain"], "d": "Protettorato britannico fino all'agosto 1971. Contorno di oggi."},
        {"n": "Isole Falkland occupate", "from": "1982-04", "to": "1982-06", "look": "t-arg", "rings": a["Falkland Is."], "d": "Occupate dall'Argentina dal 2 aprile al 14 giugno 1982."},
        {"n": "Macao", "from": "1945-01", "to": "1991-12", "look": "emp-pt", "rings": [macau_pen] + macau, "d": "Colonia portoghese fino al 1999. Penisola tracciata a mano; Taipa e Coloane da OpenStreetMap, nella forma di oggi, con terra di bonifica."},
        {"n": "Penghu", "from": "1945-01", "to": "1945-07", "look": "emp-jp", "rings": penghu, "d": "Isole dei Pescatori: Impero giapponese fino al 1945."},
        {"n": "Penghu", "from": "1945-08", "to": "1949-11", "code": 710, "rings": penghu, "d": "Isole dei Pescatori, alla Cina dei nazionalisti dal 1945."},
        {"n": "Penghu", "from": "1949-12", "to": "1991-12", "code": 713, "rings": penghu, "d": "Isole dei Pescatori, sotto Taiwan."},
        {"n": "Quemoy", "from": "1949-10", "to": "1991-12", "code": 713, "rings": kinmen, "d": "Sotto Taiwan a pochi km dalla costa cinese: al centro delle crisi del 1954 e del 1958."},
        {"n": "Matsu", "from": "1949-10", "to": "1991-12", "code": 713, "rings": matsu, "d": "Sotto Taiwan, davanti al Fujian. Bombardata nelle crisi del 1954 e del 1958."},
        {"n": "Manciukuò", "from": "1945-01", "to": "1945-08", "look": "st-X", "clip": 710, "rings": manchukuo, "d": "Stato fantoccio giapponese dal 1932, compreso il Rehe. Invaso dai sovietici il 9 agosto 1945. Confine meridionale e occidentale tracciato a mano."},
        {"n": "Occupazione sovietica dell'Iran", "from": "1945-01", "to": "1946-05", "look": "t-sov", "clip": 630, "rings": sov, "d": "Zona sovietica dal 1941. Il ritiro, previsto per marzo 1946, finisce a maggio dopo la crisi all'ONU. Confine approssimato."},
        {"n": "Occupazione britannica dell'Iran", "from": "1945-01", "to": "1946-03", "look": "t-uk", "clip": 630, "rings": gb, "d": "Zona britannica dal 1941, fino al ritiro di marzo 1946. Confine approssimato."},
        {"n": "Azerbaigian iraniano", "from": "1945-12", "to": "1946-12", "look": "t-sov", "clip": 630, "rings": azer, "d": "Governo popolare sostenuto da Mosca, abbattuto da Teheran a dicembre 1946. Confine approssimato."},
        {"n": "Repubblica di Mahabad", "from": "1946-01", "to": "1946-12", "look": "t-sov", "clip": 630, "rings": mahabad, "d": "Repubblica curda sostenuta da Mosca. Confine approssimato."},
    ]


def main(atlas_path, enclaves, out):
    a = atlas(atlas_path)
    rel = {e["id"]: e for e in json.load(open(enclaves, encoding="utf8"))["elements"]}
    osm = lambda i: stitch(rel[i]["members"])
    # Fascia di 8 km per lato lungo il canale, calcolata sulla mezzeria
    canal = [(-79.92, 9.38), (-79.92, 9.27), (-79.82, 9.2), (-79.69, 9.12), (-79.62, 9.03), (-79.56, 8.95)]
    left, right = [], []
    for i, p in enumerate(canal):
        a0, b0 = canal[max(i - 1, 0)], canal[min(i + 1, len(canal) - 1)]
        dx, dy = (b0[0] - a0[0]) * 0.987, b0[1] - a0[1]
        ln = (dx * dx + dy * dy) ** 0.5
        ox, oy = -dy / ln * 8 / (111.32 * 0.987), dx / ln * 8 / 111.32
        left.append([round(p[0] + ox, 4), round(p[1] + oy, 4)])
        right.append([round(p[0] - ox, 4), round(p[1] - oy, 4)])
    # Colón e Panamá, sul lato est delle due entrate, restavano a Panama: lì la fascia si stringe sul canale
    east = left if left[0][0] > right[0][0] else right
    for i in (0, len(canal) - 1):
        east[i] = [round(canal[i][0] + (east[i][0] - canal[i][0]) * 0.2, 4), round(canal[i][1] + (east[i][1] - canal[i][1]) * 0.2, 4)]
    ring = left + right[::-1]
    panama = [ring + [ring[0]]]
    t = [
        {"n": "Slovenia", "from": "1991-06", "to": "1991-12", "look": "t-conf", "rings": a["Slovenia"], "d": "Indipendenza proclamata il 25 giugno 1991, riconosciuta dagli altri Stati solo nel gennaio 1992. Contorno moderno."},
        {"n": "Croazia", "from": "1991-06", "to": "1991-12", "look": "t-conf", "rings": a["Croatia"], "d": "Indipendenza proclamata il 25 giugno 1991, guerra con la Jugoslavia, riconoscimento nel gennaio 1992. Contorno moderno."},
        {"n": "Zona del Canale di Panama", "from": "1945-01", "to": "1979-09", "look": "st-U", "rings": panama, "d": "Sotto giurisdizione USA, larga circa 16 km. Cessa il 1° ottobre 1979 con i trattati Torrijos-Carter. Fascia calcolata attorno al canale, schematica: ristretta presso Colón e Panamá, che ne erano escluse."},
        {"n": "Goa", "from": "1945-01", "to": "1961-12", "look": "emp-pt", "rings": osm(11251493), "d": "India portoghese, annessa dall'India nel dicembre 1961. Contorno dello Stato di oggi."},
        {"n": "Daman", "from": "1945-01", "to": "1961-12", "look": "emp-pt", "rings": osm(1953042), "d": "India portoghese fino al dicembre 1961. Contorno di oggi."},
        {"n": "Diu", "from": "1945-01", "to": "1961-12", "look": "emp-pt", "rings": osm(9576276), "d": "India portoghese fino al dicembre 1961. Contorno di oggi."},
        {"n": "Pondicherry", "from": "1945-01", "to": "1954-10", "look": "emp-fr", "rings": osm(107001), "d": "India francese con Karaikal, Yanam e Mahé. Passata di fatto all'India il 1° novembre 1954. Contorni di oggi."},
    ]
    t += extra(a, os.path.dirname(enclaves))
    for x in t:
        print(x["n"], len(x["rings"]), "anelli", sum(map(len, x["rings"])), "punti")
    with open(out, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(t, separators=(",", ":"), ensure_ascii=False) + ";\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
