"""Capi di governo da Wikidata (P6, con date), con lo stesso metodo di build_leaders.py. Scrive leaders_gov.json.

Uso: python -I tools/fetch_gov.py leaders_gov.json
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import build_leaders as b


def main(out):
    codes = {}
    titles = {v: k for k, v in b.TITLES.items()}
    names = sorted(titles)
    for i in range(0, len(names), 50):
        res = b.api(action="wbgetentities", sites="enwiki", titles="|".join(names[i: i + 50]), props="sitelinks", sitefilter="enwiki")
        for q, ent in res.get("entities", {}).items():
            t = ent.get("sitelinks", {}).get("enwiki", {}).get("title")
            if t in titles:
                codes.setdefault(titles[t], []).append(q)
    for code, ids in b.HIST.items():
        codes.setdefault(code, []).extend(ids)
    back = {}
    for code, v in codes.items():
        for q in v:
            back.setdefault(q, set()).add(code)
    rows, people = [], set()
    ids = sorted(back)
    for i in range(0, len(ids), 40):
        res = b.api(action="wbgetentities", ids="|".join(ids[i: i + 40]), props="claims")
        for q, ent in res.get("entities", {}).items():
            for st in ent.get("claims", {}).get("P6", []):
                ms = st["mainsnak"]
                if ms.get("snaktype") != "value":
                    continue
                ql = st.get("qualifiers", {})
                s = b.time_of(ql["P580"][0]) if "P580" in ql else None
                e = b.time_of(ql["P582"][0]) if "P582" in ql else None
                if not s or s > "1991-12" or (e and e < "1945-01"):
                    continue
                h = ms["datavalue"]["value"]["id"]
                people.add(h)
                for code in back[q]:
                    rows.append({"c": code, "h": h, "s": s, "e": e})
    people = sorted(people)
    info = {}
    for i in range(0, len(people), 50):
        res = b.api(action="wbgetentities", ids="|".join(people[i: i + 50]), props="labels", languages="it|en")
        for q, ent in res.get("entities", {}).items():
            lab = ent.get("labels", {})
            info[q] = (lab.get("it") or lab.get("en") or {}).get("value", q)
    for r in rows:
        r["n"] = info.get(r["h"], r["h"])
    with open(out, "w", encoding="utf8") as h:
        json.dump(rows, h, ensure_ascii=False)
    print(len(rows), "mandati", len({r["c"] for r in rows}), "Stati")


if __name__ == "__main__":
    main(sys.argv[1])
