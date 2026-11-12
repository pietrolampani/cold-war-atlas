"""Zone di occupazione di Germania e Austria e settori di Berlino e Vienna, 1945-1955.

Germania (OpenHistoricalMap): zone britannica, americana e francese dal maggio 1945; dal gennaio 1947 Bizona e zona francese;
dall'agosto 1948 Trizona, fino alla nascita della Repubblica federale (maggio 1949). La zona sovietica è la Germania orientale della carta.
Austria (OpenHistoricalMap): zone americana, britannica e francese dal 1945 al trattato di Stato (luglio 1955); il resto è la zona sovietica.
Berlino: i settori dai quartieri OSM (Ortsteile), raggruppati per i distretti del 1945. Vienna: i distretti OSM per settore,
con l'Innere Stadt amministrata a turno dalle quattro potenze.

Uso: python -I tools/build_occupation.py cartella_ohm atlas10.json territories.js
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_manchukuo import simplify  # noqa: E402
from build_ww2_atlas import atlas_rings  # noqa: E402
from fetch_ohm import area_km2, stitch  # noqa: E402


def ring_simplify(r, tol=0.002):
    k = max(range(len(r)), key=lambda i: (r[i][0] - r[0][0]) ** 2 + (r[i][1] - r[0][1]) ** 2)
    return simplify(r[:k + 1], tol) + simplify(r[k:], tol)[1:]


def ohm(folder, rel, tol=0.003):
    return [ring_simplify(r, tol) for r in json.load(open(os.path.join(folder, f"{rel}.json"), encoding="utf8"))["rings"] if area_km2(r) > 0.5]


def union(elements, keep, tol=0.0005):
    """Unione di relazioni OSM adiacenti: si tengono le vie usate una volta sola e si ricuciono."""
    uses, geom = Counter(), {}
    for rel in elements:
        if not keep(rel["tags"]):
            continue
        for m in rel["members"]:
            if m["type"] == "way" and m.get("role") in ("outer", "") and m.get("geometry"):
                uses[m["ref"]] += 1
                geom[m["ref"]] = [[round(p["lon"], 6), round(p["lat"], 6)] for p in m["geometry"]]
    rings, loose = stitch([geom[w] for w, n in uses.items() if n == 1])
    return [ring_simplify(r, tol) for r in rings if area_km2(r) > 0.05]


# Distretti di Berlino del 1945 -> settore, attraverso i quartieri di oggi
BERLIN = {
    "us": ["Kreuzberg", "Neukölln", "Britz", "Buckow", "Rudow", "Gropiusstadt", "Tempelhof", "Mariendorf", "Marienfelde", "Lichtenrade", "Schöneberg", "Friedenau",
           "Steglitz", "Lichterfelde", "Lankwitz", "Zehlendorf", "Dahlem", "Nikolassee", "Wannsee", "Schlachtensee"],
    "uk": ["Moabit", "Hansaviertel", "Tiergarten", "Charlottenburg", "Westend", "Charlottenburg-Nord", "Wilmersdorf", "Schmargendorf", "Grunewald", "Halensee",
           "Spandau", "Haselhorst", "Siemensstadt", "Staaken", "Gatow", "Kladow", "Hakenfelde", "Falkenhagener Feld", "Wilhelmstadt"],
    "fr": ["Wedding", "Gesundbrunnen", "Reinickendorf", "Tegel", "Konradshöhe", "Heiligensee", "Frohnau", "Hermsdorf", "Waidmannslust", "Lübars", "Wittenau",
           "Märkisches Viertel", "Borsigwalde"],
}
VIENNA = {"us": [7, 8, 9, 17, 18, 19], "uk": [3, 5, 11, 12, 13], "fr": [6, 14, 15, 16], "su": [2, 4, 10, 20, 21, 22, 23], "int": [1]}
VIENNA_NAMES = {"Innere Stadt": 1, "Leopoldstadt": 2, "Landstraße": 3, "Wieden": 4, "Margareten": 5, "Mariahilf": 6, "Neubau": 7, "Josefstadt": 8, "Alsergrund": 9,
                "Favoriten": 10, "Simmering": 11, "Meidling": 12, "Hietzing": 13, "Penzing": 14, "Rudolfsheim-Fünfhaus": 15, "Ottakring": 16, "Hernals": 17,
                "Währing": 18, "Döbling": 19, "Brigittenau": 20, "Floridsdorf": 21, "Donaustadt": 22, "Liesing": 23}
LOOK = {"us": "st-U", "uk": "emp-uk", "fr": "emp-fr", "su": "st-s", "int": "st-N"}
NAME = {"us": "americano", "uk": "britannico", "fr": "francese", "su": "sovietico", "int": "interalleato"}


def main(folder, atlas, territories):
    E = []
    zone = lambda n, a, b, look, rings, clip, d: E.append({"n": n, "from": a, "to": b, "look": look, "rings": rings, "clip": clip, "z": 1, "occ": 1, "d": d})
    D = " Confini da OpenHistoricalMap."
    zone("Zona di occupazione britannica", "1945-05", "1945-07", "emp-uk", ohm(folder, 2856522), 260, "Germania nord-occidentale sotto il governo militare britannico." + D)
    zone("Zona di occupazione britannica", "1945-08", "1945-10", "emp-uk", ohm(folder, 2852444), 260, "Germania nord-occidentale sotto il governo militare britannico." + D)
    zone("Zona di occupazione britannica", "1945-11", "1946-12", "emp-uk", ohm(folder, 2856524), 260, "Germania nord-occidentale sotto il governo militare britannico." + D)
    zone("Zona di occupazione americana", "1945-05", "1945-08", "st-U", ohm(folder, 2855433), 260, "Baviera, Assia, Württemberg-Baden settentrionale e l'enclave di Brema." + D)
    zone("Zona di occupazione americana", "1945-09", "1946-12", "st-U", ohm(folder, 2852492), 260, "Baviera, Assia, Württemberg-Baden settentrionale e l'enclave di Brema." + D)
    zone("Zona di occupazione francese", "1945-07", "1947-11", "emp-fr", ohm(folder, 2900078), 260, "Renania-Palatinato, Baden meridionale, Württemberg-Hohenzollern; la Saar diventa un protettorato a parte nel 1947." + D)
    zone("Zona di occupazione francese", "1947-12", "1948-07", "emp-fr", ohm(folder, 2900083), 260, "Zona francese." + D)
    zone("Bizona", "1947-01", "1948-07", "st-U", ohm(folder, 2961812), 260, "Dal 1° gennaio 1947 le zone americana e britannica sono unite economicamente." + D)
    zone("Trizona", "1948-08", "1949-05", "st-U", ohm(folder, 2961811), 260, "Dall'agosto 1948 anche la zona francese si unisce: è il territorio da cui nasce la Repubblica federale il 23 maggio 1949." + D)
    # Austria
    A = "Austria occupata dalle quattro potenze fino al trattato di Stato (15 maggio 1955, ultimi soldati via a ottobre)."
    zone("Zona di occupazione sovietica in Austria", "1945-05", "1955-07", "st-s", [r for r in atlas_rings(atlas, ["Austria"]) if len(r) >= 3], 305, A + " Bassa Austria, Burgenland e Mühlviertel.")
    for rel, k in ((2746442, "us"), (2746443, "uk"), (2746444, "fr")):
        zone({"us": "Zona di occupazione americana in Austria", "uk": "Zona di occupazione britannica in Austria", "fr": "Zona di occupazione francese in Austria"}[k],
             "1945-05", "1955-07", LOOK[k], ohm(folder, rel), 305, A + D)
    # Berlino
    berlin = json.load(open(os.path.join(folder, "berlin_ortsteile.json"), encoding="utf8"))["elements"]
    west = {n for v in BERLIN.values() for n in v}
    for k in ("us", "uk", "fr"):
        names = set(BERLIN[k])
        E.append({"n": f"Berlino, settore {NAME[k]}", "from": "1945-07", "to": "1990-09", "look": LOOK[k], "rings": union(berlin, lambda t: t.get("name") in names), "z": 2, "occ": 1,
                  "d": f"Settore {NAME[k]} di Berlino, dal luglio 1945 alla riunificazione (3 ottobre 1990). Quartieri OSM raggruppati per i distretti del 1945."})
    E.append({"n": "Berlino, settore sovietico", "from": "1945-07", "to": "1990-09", "look": "st-s", "rings": union(berlin, lambda t: t.get("name") not in west), "z": 2, "occ": 1,
              "d": "Settore sovietico di Berlino (Berlino Est), capitale della DDR dal 1949. Quartieri OSM raggruppati per i distretti del 1945."})
    # Vienna
    wien = json.load(open(os.path.join(folder, "wien_bezirke.json"), encoding="utf8"))["elements"]
    num = lambda t: VIENNA_NAMES.get(t.get("name")) or (int(t["ref"]) if str(t.get("ref", "")).isdigit() else None)
    for k, ds in VIENNA.items():
        n = "Vienna, Innere Stadt interalleata" if k == "int" else f"Vienna, settore {NAME[k]}"
        E.append({"n": n, "from": "1945-09", "to": "1955-07", "look": LOOK[k], "rings": union(wien, lambda t, ds=ds: num(t) in ds), "z": 2, "occ": 1,
                  "d": ("Il I distretto, amministrato a turno dalle quattro potenze (i 'quattro in jeep')." if k == "int" else f"Settore {NAME[k]} di Vienna, distretti {', '.join(map(str, ds))}.")
                  + " Dal settembre 1945 al 1955."})
    text = open(territories, encoding="utf8").read()
    terr = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("occ")]
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr + E, separators=(",", ":"), ensure_ascii=False) + ";\n")
    for e in E:
        print(e["n"], e["from"], e["to"], len(e["rings"]), "anelli", sum(map(len, e["rings"])), "punti")


if __name__ == "__main__":
    main(*sys.argv[1:4])
