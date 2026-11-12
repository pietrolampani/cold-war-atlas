"""Centrali nucleari da GeoNuclearData (ODbL, IAEA/WNA) e zona di esclusione di Černobyl. Scrive nuclear.js e aggiorna territories.js.

Ogni centrale compare dall'inizio della costruzione del primo reattore e sparisce alla chiusura dell'ultimo. Il cerchio di 30 km è quello del 1986.

Uso: python -I tools/build_nuclear.py 4-nuclear_power_plants.json 2-status.json 1-countries.json nuclear.js territories.js
"""
import json
import math
import re
import sys
from collections import defaultdict

LAST = "1991-12"
ZONE = (30.099, 51.389, 30)  # Lon e lat del reattore 4, raggio in km


def month(s):
    return s[:7] if s else None


def main(plants, statuses, countries, dst, territories):
    rows = json.load(open(plants, encoding="utf8"))
    status = {s["Id"]: s["Type"] for s in json.load(open(statuses, encoding="utf8"))}
    names = {c["Code"]: c["Name"] for c in json.load(open(countries, encoding="utf8"))}
    groups = defaultdict(list)
    for r in rows:
        if r.get("Latitude") is None or r.get("Longitude") is None:
            continue
        base = re.sub(r"^G-\d \(Marcoule\)$", "Marcoule", r["Name"])
        base = re.sub(r"-\d+\s*\(.*\)$", "", base)
        base = re.sub(r"[\s-]*\d+[A-Z]?$", "", base).strip()
        base = re.sub(r"-[A-Z]\d*$", "", base).strip()
        groups[base, r["CountryCode"]].append(r)
    out, skipped = [], 0
    for (name, cc), rs in sorted(groups.items()):
        starts = [month(r["ConstructionStartAt"]) or month(r["OperationalFrom"]) for r in rs]
        starts = [s for s in starts if s]
        if not starts or min(starts) > LAST:
            skipped += 1
            continue
        ends = [month(r["OperationalTo"]) for r in rs]
        end = max(e for e in ends) if all(ends) else None
        lines = []
        for r in sorted(rs, key=lambda x: x["Name"]):
            s = month(r["ConstructionStartAt"]) or month(r["OperationalFrom"])
            if not s or s > LAST:
                continue
            bits = [r["Name"]]
            if r.get("Capacity"):
                bits.append(f'{r["Capacity"]} MW')
            if r.get("ConstructionStartAt"):
                bits.append(f'cantiere {month(r["ConstructionStartAt"])}')
            if r.get("OperationalFrom"):
                bits.append(f'in rete {month(r["OperationalFrom"])}')
            if r.get("OperationalTo"):
                bits.append(f'chiuso {month(r["OperationalTo"])}')
            lines.append(", ".join(bits))
        item = {"n": name, "from": max(min(starts), "1945-01"), "lat": round(sum(r["Latitude"] for r in rs) / len(rs), 4), "lon": round(sum(r["Longitude"] for r in rs) / len(rs), 4), "min": 5, "c": "nuke",
                "d": f'{names.get(cc, cc)}. ' + "; ".join(lines) + ". Fonte: GeoNuclearData."}
        if end:
            item["to"] = end
        out.append(item)
    with open(dst, "w", encoding="utf8") as h:
        h.write("/* Centrali nucleari. Fonte: GeoNuclearData di Cristian Stoica, ODbL, da IAEA e WNA. */\nwindow.PLACES.push(..." + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ");\n")
    print("centrali", len(out), "reattori", sum(len(groups[k]) for k in groups), "escluse perché successive", skipped)
    lon, lat, km = ZONE
    circle = [[round(lon + km / (111.32 * math.cos(math.radians(lat))) * math.cos(a * math.pi / 48), 4), round(lat + km / 111.32 * math.sin(a * math.pi / 48), 4)] for a in range(97)]
    text = open(territories, encoding="utf8").read()
    old = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("nuke")]
    old.append({"n": "Zona di esclusione di Černobyl", "from": "1986-05", "to": "1991-12", "look": "t-conf", "rings": [circle], "nuke": 1,
                "d": "Cerchio di 30 km attorno al reattore 4, evacuato dopo l'incidente del 26 aprile 1986. Contorno schematico: i limiti effettivi furono poi ridisegnati, e dal 1988 c'è la riserva bielorussa."})
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(old, separators=(",", ":"), ensure_ascii=False) + ";\n")


if __name__ == "__main__":
    main(*sys.argv[1:6])
