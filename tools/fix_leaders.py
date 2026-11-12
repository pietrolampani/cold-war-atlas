"""Corregge i nomi dei leader in leaders.js e aggiunge a ogni riga il link alla voce di Wikipedia.

Ogni riga di leaders.js diventa [codice, inizio, fine, nome, foto, tipo, wiki] con wiki "it:Titolo" o "en:Titolo".
- capi di Stato ("h"): la foto è già l'identificativo Wikidata;
- capi di governo ("g"): l'identificativo viene da leaders_gov.json;
- leader di Archigos ("l"): il titolo inglese viene dal campo dbpediauri di Archigos, decodificato del tutto
  (prima restava codificato a metà, "%C3%89lie Lescot"); dove manca si riusa la persona di una riga "h"/"g" dello stesso
  Stato con lo stesso cognome, altrimenti si cerca su Wikipedia "cognome + Stato" e si accetta solo un titolo che contiene il cognome.
Poi Wikidata dà etichetta italiana (o inglese) e collegamenti: il nome mostrato diventa l'etichetta, il link la voce italiana se c'è.
Tutte le risposte stanno in una cache, così si può rilanciare.

Uso: python -I tools/fix_leaders.py archigos.dta leaders_gov.json leaders.js cache.json
"""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_archigos import read_dta, to_ym  # noqa: E402
from build_leaders import TITLES  # noqa: E402

CACHE_PATH = [""]
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = {"User-Agent": "ColdWarAtlas/1.0 (personal history map; Claude Code)", "Accept": "application/json"}
# Correzioni verificate a mano (titolo inglese di Wikipedia; None = nessun link): nomi di Archigos ambigui o storpiati.
# Chiave: nome di Archigos, oppure (Stato, inizio, nome) quando lo stesso nome indica persone diverse.
OVERRIDE = {
    "AL-Sallal": "Abdullah al-Sallal", "de los Santos": "Emilio de los Santos Salcié", "Berreras": "Antonio Imbert Barrera",
    "Galvez": "Juan Manuel Gálvez", "Hector Caraccioli": "Héctor Caraccioli", "Villeda Morales": "Ramón Villeda Morales",
    (92, "1949-01", "Osorio"): "Óscar Osorio", "Oscar Bolanos": "Óscar Bolaños", "Castillo": None, "Portillo": "Aníbal Portillo",
    "Magana Borjo": "Álvaro Magaña", "Shick Gutierrez": "René Schick", "Otilia Ulate": "Otilio Ulate Blanco", "Monge Alverez": "Luis Alberto Monge",
    "Jimenez": "Enrique Adolfo Jiménez", "Diaz Arosomena": "Domingo Díaz Arosemena", "Arosomena, A.": "Alcibíades Arosemena",
    "Remon Cantero": "José Antonio Remón Cantera", "Laureanco Gomez": "Laureano Gómez", "Csar Gaviria Trujillo": "César Gaviria",
    "Arosemana Tola": "Carlos Julio Arosemena Tola", "Ponce Enriquez": "Camilo Ponce Enríquez", "Oliveria Ramos": "Nereu Ramos",
    "Castello Branco": "Humberto de Alencar Castelo Branco", "Sarnay": "José Sarney", (145, "1946-08", "Gutierrez"): "Tomás Monje",
    "Herzog": "Enrique Hertzog", (145, "1952-04", "Hernán Siles Zuazo"): "Hernán Siles Zuazo", "Barrientos Ortuna": "René Barrientos",
    "Padilla Aranciba": "David Padilla", "Lidia Gueiler Tejada": "Lidia Gueiler Tejada", "Higinio Mornigo": "Higinio Morínigo", "Bielech": None,
    "Levingston": "Roberto M. Levingston", (165, "1955-03", "Batlle Berres"): "Luis Batlle Berres", "Fisher": "Carlos Fischer",
    (165, "1963-03", "Crespo"): "Daniel Fernández Crespo", "Demichelli": "Alberto Demicheli", "Alvarez Armalino": "Gregorio Conrado Álvarez",
    "Lacalle de Herrera": "Luis Alberto Lacalle", (211, "1946-03", "van Acker"): "Achille Van Acker", (225, "1947-01", "Etter"): "Philipp Etter",
    "Petipierre": "Max Petitpierre", "Chaudet": "Paul Chaudet", (225, "1961-01", "Friedrich"): "Friedrich Traugott Wahlen",
    "Hurlimann": "Hans Hürlimann", (225, "1990-01", "Koller"): "Arnold Koller", "Ludvík Svoboda": "Ludvík Svoboda", "Kolisevski": "Lazar Koliševski",
    "Spiljac": "Mika Špiljak", "Djuranovic": "Veselin Đuranović", "Dizarevic": "Raif Dizdarević", "G. Papandreou": "Georgios Papandreou",
    "Sophoulis": "Themistoklis Sofoulis", "K. Tsaldaris": "Konstantinos Tsaldaris", "Stephanopoulos": "Stefanos Stefanopoulos",
    (350, "1963-12", "Paraskevopoulos"): "Ioannis Paraskevopoulos", "Ionannides": "Dimitrios Ioannidis", "Filip Dimitrov": "Filip Dimitrov",
    "Jorgensen": "Anker Jørgensen", "Jonasson": "Hermann Jónasson", "Bjarni Benediktsson": "Bjarni Benediktsson (born 1908)",
    (404, "1974-09", "Cabral"): "Luís Cabral", "Seibou": "Ali Saibou", "Zerbo": "Saye Zerbo", "J. P. Ouedraogo": "Jean-Baptiste Ouédraogo",
    "Mba": "Léon M'ba", "Aubaume": "Jean-Hilaire Aubame", "Kasavubu": "Joseph Kasa-Vubu", "Banaisa": "Godfrey Binaisa", "Banti": "Tafari Benti",
    "Mengistu Marriam": "Mengistu Haile Mariam", "Donges": "Eben Dönges", "Subhuza II": "Sobhuza II", "Ntombe Thwala": "Ntfombi",
    "Boumedienne": "Houari Boumédiène", "Qaddafi": "Muammar Gaddafi", "Maghoub": "Muhammad Ahmad Mahgoub", "Osman": None,
    "Abdul Rahman Swaredahab": "Abdel Rahman Swar al-Dahab", "Karrim Kassem": "Abd al-Karim Qasim", "Rahmen Aref": "Abd al-Rahman Arif",
    "Kuwatli": "Shukri al-Quwatli", "Al-Zaim": "Husni al-Za'im", "Zahreddin": "Abd al-Karim Zahr al-Din", "Al-Khatib": "Ahmad al-Khatib",
    "Chebab": "Fuad Chehab", "Franjieh": "Suleiman Frangieh", "Elias Hrawi": "Elias Hrawi", "Ibn Abdullah-Hashim": "Talal of Jordan",
    "Saud": "Saud of Saudi Arabia", "Ibn Ahmed Alwazir": "Abdullah al-Wazir", "Ibn Yahya Hamid": "Ahmad bin Yahya", "Al-Iryani": "Abdul Rahman al-Iryani",
    "Al-Hamadi": "Ibrahim al-Hamdi", "Saleh al-Hashidi": "Ali Abdullah Saleh", "Ali Rubayyi": "Salim Rubaya Ali", "Ali Nassir Hassani": "Ali Nasir Muhammad",
    "Abdullah As-Sabah": "Abdullah Al-Salim Al-Sabah", "Sabah As-Sabah": "Sabah Al-Salim Al-Sabah", "Jabir As-Sabah": "Jaber Al-Ahmad Al-Sabah",
    "Isa Ibn Al-Khalifah": "Isa bin Salman Al Khalifa", "Ahmed Ath-Thani": "Ahmad bin Ali Al Thani", "Khalifah Ath-Thani": "Khalifa bin Hamad Al Thani",
    "An-Nahayan": "Zayed bin Sultan Al Nahyan", "Mahmud Khan Ghazi": "Shah Mahmud Khan", "Mohammad Yusuf": "Mohammad Yusuf (Afghan politician)",
    "Abdul Zahir": "Abdul Zahir (politician)", "Batmonh": "Jambyn Batmönkh", "Li Tsung-jen": "Li Zongren", "Choi Kuy Hay": "Choi Kyu-hah",
    "Douglas MacArthur": "Douglas MacArthur", (750, "1966-01", "Gulzarilal Nanda"): "Gulzarilal Nanda", "Moshtaque Ahmed": "Khondaker Mostaq Ahmad",
    "Saw Maung": "Saw Maung", "Krishna Prasad Bhatterai": "Krishna Prasad Bhattarai", "Kou Abhay Og Long": "Kou Abhay", "Kong Le": "Kong Le",
    "Kouprasith": "Kouprasith Abhay", "Phomivan": "Kaysone Phomvihane", "Pham Buu Loc": "Bửu Lộc", (817, "1975-04", "Minh"): "Dương Văn Minh",
    "Abdul Razak": "Abdul Razak Hussein", "Mike Moore": "Mike Moore (New Zealand politician)", "Juan Bosch": "Juan Bosch",
    "Executive council": None, "Military Junta": None, "Ponce Enriquez": "Q879056", "Hector Caraccioli": "Q1490067",
    "Juan Bosch": "Juan Bosch (politician)", "Luis Somoza Debayle": "Luis Somoza Debayle", "Echavarria": None, "de los Santos": "Emilio de los Santos",
}
# Nomi da mostrare dove non c'è una voce a cui collegarsi
NAMES = {"Echavarria": "Pedro Rodríguez Echavarría", "Oscar Bolanos": "Óscar Bolaños", "Castillo": "Miguel Ángel Castillo", "Executive council": "Consiglio esecutivo",
         "Military Junta": "Giunta militare",
}
EXTRA_TITLES = {260: "West Germany", 265: "East Germany", 315: "Czechoslovakia", 345: "Yugoslavia", 365: "Soviet Union", 680: "South Yemen",
                678: "North Yemen", 817: "South Vietnam", 816: "Vietnam", 710: "China", 490: "Zaire", 701: "Turkmenistan", 702: "Tajikistan",
                703: "Kyrgyzstan", 704: "Uzbekistan", 705: "Kazakhstan", 359: "Moldova", 366: "Estonia", 367: "Latvia", 368: "Lithuania",
                369: "Ukraine", 370: "Belarus", 371: "Armenia", 372: "Georgia", 373: "Azerbaijan", 343: "North Macedonia", 344: "Croatia",
                346: "Bosnia and Herzegovina", 349: "Slovenia", 731: "North Korea", 816.0: "Vietnam"}


def get(url, cache, key):
    if key in cache:
        return cache[key]
    for attempt in range(6):
        try:
            data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
            cache[key] = data
            if len(cache) % 20 == 0:
                json.dump(cache, open(CACHE_PATH[0], "w", encoding="utf8"), ensure_ascii=False)
            time.sleep(4.5)
            return data
        except urllib.error.HTTPError as e:
            wait = int(e.headers.get("Retry-After") or 30)
            print("HTTP", e.code, "attendo", wait, flush=True)
            time.sleep(wait)
        except Exception as e:
            print("errore", e, flush=True)
            time.sleep(20)
    raise SystemExit("Wikimedia non risponde")


def full_unquote(s):
    for _ in range(4):
        u = urllib.parse.unquote(s)
        if u == s:
            break
        s = u
    return s


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()


def archigos_titles(dta):
    out = {}
    for r in read_dta(dta):
        s = to_ym(r["startdate"])
        if not s:
            continue
        uri = r.get("dbpediauri", "") or ""
        m = re.search(r"dbpedia\.org_resource_([^&]+)", uri)
        if not m:
            continue
        t = re.sub(r"-([0-9A-F]{2})", r"%\1", m.group(1)).replace("_", "%2F")
        t = full_unquote(urllib.parse.unquote(t).rsplit("/", 1)[-1])
        t = full_unquote(t).replace("_", " ")
        if "�" in t or "ï¿½" in t:
            continue
        out.setdefault((int(r["ccode"]), s), []).append((r["leader"], t))
    return out


def arch_title(arch, code, s, name):
    """Più leader possono iniziare nello stesso mese: si sceglie quello col nome che corrisponde."""
    cands = arch.get((code, s), [])
    n = fold(full_unquote(name))
    for leader, t in cands:
        if fold(t) == n or fold(t).split(" (")[0] == n:
            return t
    for leader, t in cands:
        last = fold(leader.replace(",", " ").split()[0] if "," in leader else leader.split()[-1]) if leader else ""
        if last and (last in n or n.split()[-1] in fold(t)):
            return t
    return cands[0][1] if len(cands) == 1 else None


def main(dta, gov_path, leaders_path, cache_path):
    CACHE_PATH[0] = cache_path
    cache = json.load(open(cache_path, encoding="utf8")) if os.path.exists(cache_path) else {}
    text = open(leaders_path, encoding="utf8").read()
    rows = json.loads(text.split("=", 1)[1].rstrip().rstrip(";"))
    gov = {(g["c"], g["s"], g["n"]): g["h"] for g in json.load(open(gov_path, encoding="utf8"))}
    arch = archigos_titles(dta)
    country = {**TITLES, **EXTRA_TITLES}
    # 1. Un riferimento per riga: ("q", QID) oppure ("t", titolo inglese)
    ref = []
    for r in rows:
        code, s, e, name, photo, kind = r[:6]
        if kind == "h" and re.fullmatch(r"Q\d+", photo or ""):
            ref.append(("q", photo))
        elif kind == "g" and gov.get((code, s, name)):
            ref.append(("q", gov[(code, s, name)]))
        elif kind == "l" and (code, s, full_unquote(name)) in OVERRIDE:
            v = OVERRIDE[(code, s, full_unquote(name))]
            ref.append((("q" if re.fullmatch(r"Q\d+", v) else "t"), v) if v else ("x", ""))
        elif kind == "l" and full_unquote(name) in OVERRIDE:
            v = OVERRIDE[full_unquote(name)]
            ref.append((("q" if re.fullmatch(r"Q\d+", v) else "t"), v) if v else ("x", ""))
        elif kind == "l" and arch_title(arch, code, s, name):
            ref.append(("t", arch_title(arch, code, s, name)))
        else:
            ref.append(None)
    # 2. Titoli inglesi -> QID
    titles = sorted({x[1] for x in ref if x and x[0] == "t"})
    t2q = {}
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        q = urllib.parse.urlencode({"action": "query", "format": "json", "redirects": 1, "prop": "pageprops", "ppprop": "wikibase_item", "titles": "|".join(chunk)})
        data = get("https://en.wikipedia.org/w/api.php?" + q, cache, "en:" + "|".join(chunk))
        back = {}
        for m in data["query"].get("normalized", []) + data["query"].get("redirects", []):
            back[m["to"]] = back.get(m["from"], m["from"])
        for p in data["query"]["pages"].values():
            qid = p.get("pageprops", {}).get("wikibase_item")
            if qid:
                t2q[back.get(p["title"], p["title"])] = qid
                t2q[p["title"]] = qid
    print("titoli Archigos:", len(titles), "risolti:", sum(1 for t in titles if t in t2q), flush=True)
    qref = [("q", x[1]) if x and x[0] == "q" else ("q", t2q[x[1]]) if x and x[1] in t2q else None for x in ref]
    # 3. Righe senza riferimento: stessa persona in un'altra riga dello Stato (cognome uguale e date che si toccano)
    for i, r in enumerate(rows):
        if qref[i] or (ref[i] and ref[i][0] == "x"):
            continue
        last = fold(r[3].replace(",", " ").split()[0] if "," in r[3] else r[3].split()[-1])
        for j, o in enumerate(rows):
            if j != i and qref[j] and o[0] == r[0] and last in fold(o[3]) and o[1] <= (r[2] or "9999") and r[1] <= (o[2] or "9999"):
                qref[i] = qref[j]
                break
    # 4. Ancora mancanti: ricerca su Wikipedia
    for i, r in enumerate(rows):
        if qref[i] or (ref[i] and ref[i][0] == "x"):
            continue
        name = r[3]
        if "," in name:  # "Arias, A." / "Gemayel, Amin"
            a, b = [x.strip() for x in name.split(",", 1)]
            name = (b + " " + a) if len(b) > 2 and "." not in b else a
        if name in ("Executive council", "Military Junta"):
            continue
        keys = [fold(w) for w in re.split(r"[\s-]+", name) if len(w) >= 4] or [fold(name.split()[-1])]
        query = f"{name} {country.get(r[0], '')} {r[1][:4]}"
        ok = lambda t: any(k in fold(t) for k in keys) and not re.search(r"election|cabinet|government|list|coup|history", t.lower())
        if "s:" + query in cache:  # ricerche già fatte col metodo vecchio (due richieste)
            data = cache["s:" + query]
            hit = next((h["title"] for h in data["query"]["search"] if ok(h["title"])), None)
        else:  # una sola richiesta: la ricerca restituisce già l'identificativo Wikidata
            q = urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search", "gsrlimit": 5, "gsrsearch": query,
                                        "prop": "pageprops", "ppprop": "wikibase_item"})
            data = get("https://en.wikipedia.org/w/api.php?" + q, cache, "g:" + query)
            pages = sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
            page = next((p for p in pages if ok(p["title"])), None)
            hit = page["title"] if page else None
            if page and page.get("pageprops", {}).get("wikibase_item"):
                qref[i] = ("q", page["pageprops"]["wikibase_item"])
            hit = None if qref[i] else hit
            print("cerco", r[3], "->", page["title"] if page else None, flush=True)
            if not hit:
                continue
        if hit:
            q = urllib.parse.urlencode({"action": "query", "format": "json", "redirects": 1, "prop": "pageprops", "ppprop": "wikibase_item", "titles": hit})
            data = get("https://en.wikipedia.org/w/api.php?" + q, cache, "en:" + hit)
            for p in data["query"]["pages"].values():
                if p.get("pageprops", {}).get("wikibase_item"):
                    qref[i] = ("q", p["pageprops"]["wikibase_item"])
        print("cerco", r[3], "->", hit, flush=True)
    # 5. QID -> etichetta e collegamenti
    qids = sorted({x[1] for x in qref if x})
    info = {}
    for i in range(0, len(qids), 50):
        chunk = qids[i:i + 50]
        q = urllib.parse.urlencode({"action": "wbgetentities", "format": "json", "ids": "|".join(chunk), "props": "labels|sitelinks|claims", "languages": "it|en", "sitefilter": "itwiki|enwiki"})
        data = get("https://www.wikidata.org/w/api.php?" + q, cache, "wd:" + "|".join(chunk))
        for qid, ent in data.get("entities", {}).items():
            human = any(c["mainsnak"].get("datavalue", {}).get("value", {}).get("id") == "Q5" for c in ent.get("claims", {}).get("P31", []))
            lab = ent.get("labels", {})
            sl = ent.get("sitelinks", {})
            info[qid] = {"human": human, "it": lab.get("it", {}).get("value"), "en": lab.get("en", {}).get("value"),
                         "itwiki": sl.get("itwiki", {}).get("title"), "enwiki": sl.get("enwiki", {}).get("title")}
    json.dump(cache, open(cache_path, "w", encoding="utf8"), ensure_ascii=False)
    # 6. Riscrive le righe
    changed, linked, report = 0, 0, []
    for r, x in zip(rows, qref):
        r[:] = r[:6]
        old = r[3]
        if not x or x[1] not in info or not info[x[1]]["human"]:
            fixed = NAMES.get(full_unquote(old), full_unquote(old))
            if fixed != old:
                r[3] = fixed
                changed += 1
            r.append("")
            if x and x[1] in info:
                report.append(f"non persona: {old} -> {x[1]}")
            continue
        d = info[x[1]]
        label = ((d["itwiki"] or d["enwiki"] or "").split(" (")[0]) or d["it"] or d["en"] or full_unquote(old)
        if label != old:
            changed += 1
            report.append(f"{old} -> {label}")
        r[3] = label
        r.append(("it:" + d["itwiki"]) if d["itwiki"] else ("en:" + d["enwiki"]) if d["enwiki"] else "")
        linked += bool(r[6])
    with open(leaders_path, "w", encoding="utf8") as h:
        h.write("window.LEADERS=" + json.dumps(rows, separators=(",", ":"), ensure_ascii=False) + ";\n")
    with open(os.path.splitext(cache_path)[0] + "_report.txt", "w", encoding="utf8") as h:
        h.write("\n".join(sorted(set(report))) + "\n")
        h.write("\nSENZA LINK:\n" + "\n".join(sorted({r[3] for r in rows if not r[6]})) + "\n")
    print(len(rows), "righe;", changed, "nomi cambiati;", linked, "con link;", len(rows) - linked, "senza", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:5])
