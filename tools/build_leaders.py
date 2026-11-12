"""Capi di Stato da Wikidata (P35, con date) e foto da Wikimedia Commons.

Uso: python -I tools/build_leaders.py cartella_cache leaders.js photos.js
Scrive leaders.js (nomi e date) e photos.js (miniature come data URI, caricato solo a richiesta).
"""
import base64
import json
import os
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "ColdWarAtlas/1.0 (personal history map; contact via Claude Code session)", "Accept": "*/*"}
START, END = "1945-09", "1991-12"
# Codice Gleditsch-Ward -> ISO3 per gli Stati che esistono ancora; HIST per quelli scomparsi
ISO = {2:"USA",20:"CAN",31:"BHS",40:"CUB",41:"HTI",42:"DOM",51:"JAM",52:"TTO",53:"BRB",70:"MEX",80:"BLZ",90:"GTM",91:"HND",92:"SLV",93:"NIC",94:"CRI",95:"PAN",100:"COL",101:"VEN",110:"GUY",115:"SUR",130:"ECU",135:"PER",140:"BRA",145:"BOL",150:"PRY",155:"CHL",160:"ARG",165:"URY",200:"GBR",205:"IRL",210:"NLD",211:"BEL",212:"LUX",220:"FRA",225:"CHE",230:"ESP",235:"PRT",260:"DEU",290:"POL",305:"AUT",310:"HUN",325:"ITA",338:"MLT",339:"ALB",343:"MKD",350:"GRC",352:"CYP",355:"BGR",359:"MDA",360:"ROU",365:"RUS",366:"EST",367:"LVA",368:"LTU",369:"UKR",370:"BLR",371:"ARM",372:"GEO",373:"AZE",375:"FIN",380:"SWE",385:"NOR",390:"DNK",395:"ISL",402:"CPV",404:"GNB",411:"GNQ",420:"GMB",432:"MLI",433:"SEN",434:"BEN",435:"MRT",436:"NER",437:"CIV",438:"GIN",439:"BFA",450:"LBR",451:"SLE",452:"GHA",461:"TGO",471:"CMR",475:"NGA",481:"GAB",482:"CAF",483:"TCD",484:"COG",490:"COD",500:"UGA",501:"KEN",510:"TZA",516:"BDI",517:"RWA",520:"SOM",522:"DJI",530:"ETH",540:"AGO",541:"MOZ",551:"ZMB",552:"ZWE",553:"MWI",560:"ZAF",565:"NAM",570:"LSO",571:"BWA",572:"SWZ",580:"MDG",581:"COM",590:"MUS",600:"MAR",615:"DZA",616:"TUN",620:"LBY",625:"SDN",630:"IRN",640:"TUR",645:"IRQ",651:"EGY",652:"SYR",660:"LBN",663:"JOR",666:"ISR",670:"SAU",678:"YEM",690:"KWT",692:"BHR",694:"QAT",696:"ARE",698:"OMN",700:"AFG",701:"TKM",702:"TJK",703:"KGZ",704:"UZB",705:"KAZ",710:"CHN",712:"MNG",713:"TWN",731:"PRK",732:"KOR",740:"JPN",750:"IND",760:"BTN",770:"PAK",771:"BGD",775:"MMR",780:"LKA",781:"MDV",790:"NPL",800:"THA",811:"KHM",812:"LAO",816:"VNM",820:"MYS",830:"SGP",835:"BRN",840:"PHL",850:"IDN",900:"AUS",910:"PNG",920:"NZL",940:"SLB",950:"FJI"}
HIST = {365:["Q15180"],260:["Q713750"],265:["Q16957"],315:["Q33946"],345:["Q36704","Q83286"],680:["Q199841"],678:["Q267584"],817:["Q180573"],816:["Q172640"],490:["Q974"],710:["Q148","Q865"]}


TITLES = {2:"United States",20:"Canada",31:"The Bahamas",40:"Cuba",41:"Haiti",42:"Dominican Republic",51:"Jamaica",52:"Trinidad and Tobago",53:"Barbados",70:"Mexico",80:"Belize",90:"Guatemala",91:"Honduras",92:"El Salvador",93:"Nicaragua",94:"Costa Rica",95:"Panama",100:"Colombia",101:"Venezuela",110:"Guyana",115:"Suriname",130:"Ecuador",135:"Peru",140:"Brazil",145:"Bolivia",150:"Paraguay",155:"Chile",160:"Argentina",165:"Uruguay",200:"United Kingdom",205:"Republic of Ireland",210:"Netherlands",211:"Belgium",212:"Luxembourg",220:"France",225:"Switzerland",230:"Spain",235:"Portugal",290:"Poland",305:"Austria",310:"Hungary",325:"Italy",338:"Malta",339:"Albania",350:"Greece",352:"Cyprus",355:"Bulgaria",360:"Romania",375:"Finland",380:"Sweden",385:"Norway",390:"Denmark",395:"Iceland",402:"Cape Verde",404:"Guinea-Bissau",411:"Equatorial Guinea",420:"The Gambia",432:"Mali",433:"Senegal",434:"Benin",435:"Mauritania",436:"Niger",437:"Ivory Coast",438:"Guinea",439:"Burkina Faso",450:"Liberia",451:"Sierra Leone",452:"Ghana",461:"Togo",471:"Cameroon",475:"Nigeria",481:"Gabon",482:"Central African Republic",483:"Chad",484:"Republic of the Congo",500:"Uganda",501:"Kenya",510:"Tanzania",516:"Burundi",517:"Rwanda",520:"Somalia",522:"Djibouti",530:"Ethiopia",540:"Angola",541:"Mozambique",551:"Zambia",552:"Zimbabwe",553:"Malawi",560:"South Africa",565:"Namibia",570:"Lesotho",571:"Botswana",572:"Eswatini",580:"Madagascar",581:"Comoros",590:"Mauritius",600:"Morocco",615:"Algeria",616:"Tunisia",620:"Libya",625:"Sudan",630:"Iran",640:"Turkey",645:"Iraq",651:"Egypt",652:"Syria",660:"Lebanon",663:"Jordan",666:"Israel",670:"Saudi Arabia",690:"Kuwait",692:"Bahrain",694:"Qatar",696:"United Arab Emirates",698:"Oman",700:"Afghanistan",712:"Mongolia",713:"Taiwan",731:"North Korea",732:"South Korea",740:"Japan",750:"India",760:"Bhutan",770:"Pakistan",771:"Bangladesh",775:"Myanmar",780:"Sri Lanka",781:"Maldives",790:"Nepal",800:"Thailand",811:"Cambodia",812:"Laos",820:"Malaysia",830:"Singapore",835:"Brunei",840:"Philippines",850:"Indonesia",900:"Australia",910:"Papua New Guinea",920:"New Zealand",940:"Solomon Islands",950:"Fiji"}


def sparql(q):
    url = "https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q)
    # Il servizio accetta al momento una richiesta al minuto
    for attempt in range(8):
        time.sleep(70)
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=170))["results"]["bindings"]
        except Exception as e:
            print("wikidata", e, flush=True)
    raise SystemExit("Wikidata non risponde")


def ym(s):
    return s[:7] if s else None


def api(**params):
    url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({"format": "json", **params})
    for attempt in range(5):
        try:
            data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
            time.sleep(2)
            return data
        except Exception as e:
            print("api", e, flush=True)
            time.sleep(45)
    return {}


def time_of(snak):
    if snak.get("snaktype") != "value":
        return None
    t = snak["datavalue"]["value"]["time"].lstrip("+")
    return t[:7] if len(t) >= 7 and t[5:7] != "00" else t[:4] + "-01"


def fetch_rows():
    """Usa l'API di Wikidata, non il servizio SPARQL che accetta una richiesta al minuto."""
    codes = {}
    # Una richiesta sola per 50 Paesi, tramite i titoli di Wikipedia in inglese
    titles = {v: k for k, v in TITLES.items()}
    names = sorted(titles)
    for i in range(0, len(names), 50):
        res = api(action="wbgetentities", sites="enwiki", titles="|".join(names[i: i + 50]), props="sitelinks", sitefilter="enwiki")
        for q, ent in res.get("entities", {}).items():
            title = ent.get("sitelinks", {}).get("enwiki", {}).get("title")
            if title in titles:
                codes.setdefault(titles[title], []).append(q)
    print(len(codes), "Paesi trovati su", len(names), "; mancano", [n for n in names if titles[n] not in codes], flush=True)
    for code, ids in HIST.items():
        codes.setdefault(code, []).extend(ids)
    back = {}
    for code, v in codes.items():
        for q in v:
            back.setdefault(q, set()).add(code)
    print(len(back), "Paesi", flush=True)
    rows, people = [], set()
    ids = sorted(back)
    for i in range(0, len(ids), 40):
        res = api(action="wbgetentities", ids="|".join(ids[i: i + 40]), props="claims")
        for q, ent in res.get("entities", {}).items():
            for st in ent.get("claims", {}).get("P35", []):
                ms = st["mainsnak"]
                if ms.get("snaktype") != "value":
                    continue
                h = ms["datavalue"]["value"]["id"]
                ql = st.get("qualifiers", {})
                s = time_of(ql["P580"][0]) if "P580" in ql else None
                e = time_of(ql["P582"][0]) if "P582" in ql else None
                people.add(h)
                for code in back[q]:
                    rows.append({"c": code, "h": h, "s": s, "e": e})
    info = {}
    people = sorted(people)
    for i in range(0, len(people), 50):
        res = api(action="wbgetentities", ids="|".join(people[i: i + 50]), props="labels|claims", languages="it|en")
        for q, ent in res.get("entities", {}).items():
            lab = ent.get("labels", {})
            name = (lab.get("it") or lab.get("en") or {}).get("value", q)
            img = None
            p18 = ent.get("claims", {}).get("P18", [])
            if p18 and p18[0]["mainsnak"].get("snaktype") == "value":
                img = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(p18[0]["mainsnak"]["datavalue"]["value"].replace(" ", "_"))
            info[q] = (name, img)
        print("persone", i, flush=True)
    for r in rows:
        r["n"], r["img"] = info.get(r["h"], (r["h"], None))
    return rows


def main(cache, leaders_out, photos_out):
    os.makedirs(cache, exist_ok=True)
    rows_path = os.path.join(cache, "rows.json")
    if os.path.exists(rows_path):
        rows = json.load(open(rows_path, encoding="utf8"))
    else:
        rows = fetch_rows()
        json.dump(rows, open(rows_path, "w", encoding="utf8"), ensure_ascii=False)
    seen, out, imgs = set(), [], {}
    for r in rows:
        if not r["s"] or r["n"].startswith("Q"):
            continue
        end = r["e"] or "9999-12"
        if end < START or r["s"] > END:
            continue
        key = (r["c"], r["h"], r["s"])
        if key in seen:
            continue
        seen.add(key)
        out.append([r["c"], r["s"], r["e"], r["n"], r["h"]])
        if r.get("img"):
            imgs[r["h"]] = r["img"]
    out.sort(key=lambda x: (x[0], x[1]))
    by = {}
    for r in out:
        by.setdefault(r[0], []).append(r)
    print(len(out), "mandati;", len(by), "Stati;", len(imgs), "foto")
    print("Stati senza dati:", [c for c in list(ISO) + list(HIST) if c not in by])
    with open(leaders_out, "w", encoding="utf8") as h:
        h.write("window.LEADERS=" + json.dumps(out, separators=(",", ":"), ensure_ascii=False) + ";\n")
    photo_dir = os.path.join(cache, "photos")
    os.makedirs(photo_dir, exist_ok=True)
    done = 0
    for hid, url in imgs.items():
        path = os.path.join(photo_dir, hid + ".jpg")
        if not os.path.exists(path):
            thumb = url.replace("http://", "https://") + "?width=72"
            try:
                data = urllib.request.urlopen(urllib.request.Request(thumb, headers=UA), timeout=60).read()
                with open(path, "wb") as f:
                    f.write(data)
                time.sleep(3)
            except Exception as e:
                print("foto", hid, e, flush=True)
                time.sleep(30)
        done += 1
        if done % 100 == 0:
            print("foto", done, flush=True)
    photos = {}
    for hid in imgs:
        path = os.path.join(photo_dir, hid + ".jpg")
        if os.path.exists(path) and os.path.getsize(path) < 40000:
            raw = open(path, "rb").read()
            kind = "png" if raw[:4] == b"\x89PNG" else "jpeg"
            photos[hid] = f"data:image/{kind};base64," + base64.b64encode(raw).decode()
    with open(photos_out, "w", encoding="utf8") as h:
        h.write("window.PHOTOS=" + json.dumps(photos, separators=(",", ":")) + ";\n")
    print("photos.js", round(os.path.getsize(photos_out) / 1e6, 2), "MB,", len(photos), "foto")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
