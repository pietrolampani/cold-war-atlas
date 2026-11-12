"""Scrive tests.js (test nucleari SIPRI/Tidy Tuesday) ed elections.js (ParlGov).

Uso: python -I tools/build_records.py nuclear_explosions.csv view_election.csv .
"""
import csv
import json
import os
import sys

# ParlGov -> codice Gleditsch-Ward
PARLGOV = {"AUS":900,"AUT":305,"BEL":211,"BGR":355,"CAN":20,"CHE":225,"CYP":352,"CZE":315,"DEU":260,"DNK":390,"ESP":230,"EST":366,"FIN":375,"FRA":220,"GBR":200,"GRC":350,"HRV":None,"HUN":310,"IRL":205,"ISL":395,"ISR":666,"ITA":325,"JPN":740,"LTU":368,"LUX":212,"LVA":367,"MLT":338,"NLD":210,"NOR":385,"NZL":920,"POL":290,"PRT":235,"ROU":360,"SVK":None,"SVN":None,"SWE":380,"TUR":640}
TOP = 7


def num(s):
    try:
        return float(s)
    except ValueError:
        return 0.0


def tests(path, out):
    rows = []
    for r in csv.DictReader(open(path, encoding="utf8")):
        d = r["date_long"]
        y, m = int(d[:4]), int(d[4:6])
        if (y, m) < (1945, 1) or y > 1991:
            continue
        rows.append([f"{y}-{m:02d}", d[6:8], r["country"], (r["name"] if r["name"] not in ("", "NA") else r["region"]).strip(), r["region"].strip(),
                     float(r["latitude"]), float(r["longitude"]), num(r["yield_lower"]), num(r["yield_upper"]),
                     r["type"].strip(), r["purpose"].strip()])
    with open(out, "w", encoding="utf8") as h:
        h.write("window.TESTS=" + json.dumps(rows, separators=(",", ":"), ensure_ascii=False) + ";\n")
    print("test", len(rows), "dal", rows[0][0], "al", rows[-1][0], round(sum(r[8] for r in rows) / 1000), "Mt massimi")


def elections(path, out):
    groups = {}
    for r in csv.DictReader(open(path, encoding="utf8")):
        if r["election_type"] != "parliament" or r["election_date"][:4] < "1945" or r["election_date"][:7] > "1991-12":
            continue
        code = PARLGOV.get(r["country_name_short"])
        if not code:
            continue
        key = (code, r["election_date"])
        g = groups.setdefault(key, {"t": r["seats_total"], "p": []})
        try:
            v = float(r["vote_share"]) if r["vote_share"] else None
            s = int(float(r["seats"])) if r["seats"] else None
        except ValueError:
            continue
        name = r["party_name_short"] or r["party_name_english"]
        if name in ("one", "other", "none"):
            continue
        g["p"].append([name, r["party_name_english"], v, s])
    rows = []
    for (code, date), g in sorted(groups.items()):
        parties = sorted(g["p"], key=lambda p: (p[3] or 0, p[2] or 0), reverse=True)[:TOP]
        total = int(float(g["t"])) if g["t"] else None
        rows.append([code, date, total, parties])
    with open(out, "w", encoding="utf8") as h:
        h.write("window.ELECTIONS=" + json.dumps(rows, separators=(",", ":"), ensure_ascii=False) + ";\n")
    print("elezioni", len(rows), "Stati", len({r[0] for r in rows}), round(os.path.getsize(out) / 1000), "KB")


if __name__ == "__main__":
    tests(sys.argv[1], os.path.join(sys.argv[3], "tests.js"))
    elections(sys.argv[2], os.path.join(sys.argv[3], "elections.js"))
