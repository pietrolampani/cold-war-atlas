"""Zone controllate dagli insorti e territori occupati nei conflitti della Guerra Fredda senza un video di riferimento.

Ricostruzione a mano, semplificata, dalle zone note nella storiografia (zone liberate, aree di base, occupazioni): contorni
indicativi, dell'ordine di decine di chilometri. Ogni zona si ritaglia sullo Stato del mese (clip per codice) e ha il contorno
rosso tratteggiato del fronte. Colori: rosa per i movimenti vicini a Mosca, azzurro per quelli sostenuti dall'Occidente,
il colore dello Stato occupante per le occupazioni.

Uso: python -I tools/build_coldwar_zones.py territories.js
"""
import json
import sys

S, U = "st-s t-fill t-occ", "st-u t-fill t-occ"
NOTE = " Ricostruzione approssimativa delle zone note, non un rilievo: i contorni sono indicativi."

# (nome, da, a, look o codice occupante, clip, anelli, descrizione)
VIET_BAC = [[104.8, 22.9], [105.5, 22.6], [106.2, 22.4], [106.6, 21.9], [106.2, 21.6], [105.8, 21.6], [105.3, 21.8], [104.9, 22.2], [104.6, 22.6]]
NORTH = [[103.9, 22.7], [104.4, 22.85], [105.3, 23.15], [106.0, 22.95], [106.7, 22.85], [107.3, 22.0], [107.0, 21.6], [106.4, 21.45], [105.9, 21.45],
         [105.45, 21.45], [105.1, 21.55], [104.6, 21.75], [104.1, 22.1]]
NORTHWEST = [[102.6, 22.4], [103.9, 22.7], [104.1, 22.1], [104.6, 21.75], [105.1, 21.55], [104.9, 21.2], [104.4, 21.0], [103.8, 20.9], [103.4, 21.1], [103.0, 21.6], [102.7, 22.0]]
INTERZONE4 = [[104.6, 20.3], [105.6, 20.1], [105.85, 19.9], [105.95, 19.4], [105.75, 18.9], [106.4, 18.1], [106.5, 17.8], [105.6, 18.3], [105.0, 18.8], [104.5, 19.5]]
INTERZONE5 = [[108.3, 15.4], [108.9, 15.2], [109.2, 14.4], [109.3, 13.3], [108.9, 13.2], [108.5, 13.9], [108.0, 14.6], [107.9, 15.2]]
SOUTH = [[[105.6, 10.95], [106.2, 10.95], [106.3, 10.55], [105.8, 10.45], [105.5, 10.6]], [[104.8, 9.6], [105.3, 9.6], [105.4, 9.0], [105.0, 8.8], [104.8, 9.1]]]
VM = "Zone tenute dal Viet Minh nella prima guerra d'Indocina"
ZONES = [
    ("Viet Minh", "1950-06", "1950-09", S, 815, [VIET_BAC, INTERZONE4, INTERZONE5] + SOUTH, VM + ": il Viet Bac, la Zona interregionale IV (Thanh Hoa, Nghe An, Ha Tinh), la V (Quang Ngai, Binh Dinh) e le basi del sud."),
    ("Viet Minh", "1950-10", "1952-09", S, 815, [NORTH, INTERZONE4, INTERZONE5] + SOUTH, VM + ": dopo la campagna della frontiera (ottobre 1950, la RC4 e Cao Bang) tutto il confine con la Cina; i francesi tengono il delta del Fiume Rosso dietro la linea De Lattre."),
    ("Viet Minh", "1952-10", "1954-07", S, 815, [NORTH, NORTHWEST, INTERZONE4, INTERZONE5] + SOUTH, VM + ": da ottobre 1952 (Nghia Lo) anche il Nord-Ovest; Lai Chau è abbandonata a dicembre 1953 e Dien Bien Phu cade il 7 maggio 1954. Accordi di Ginevra il 21 luglio."),
    ("Viet Minh e Pathet Lao", "1953-04", "1954-07", S, 812, [[[103.7, 20.9], [104.6, 20.7], [104.9, 20.1], [104.4, 19.9], [103.8, 20.1], [103.5, 20.5]],
                                                          [[101.6, 22.4], [102.3, 22.4], [102.6, 21.7], [102.1, 21.4], [101.7, 21.6]]],
     "Sam Neua e Phongsaly, prese dal Viet Minh e dal Pathet Lao con l'invasione del Laos dell'aprile 1953."),
    # Congo
    ("Stato del Katanga", "1960-07", "1963-01", U, 490, [[[22.0, -6.9], [23.0, -6.5], [24.5, -5.8], [26.0, -5.0], [27.3, -5.0], [29.3, -6.0], [29.8, -7.5], [30.6, -8.3], [28.9, -8.5], [28.4, -9.3],
                                                          [28.9, -10.5], [28.6, -11.8], [29.0, -12.4], [29.8, -12.2], [29.8, -13.4], [28.4, -12.9], [27.6, -12.3], [27.2, -11.6], [26.0, -11.9],
                                                          [25.3, -11.2], [24.4, -11.1], [23.9, -10.9], [22.3, -11.0], [22.0, -9.8], [21.8, -8.0]]],
     "Secessione del Katanga di Ciombe (11 luglio 1960), sostenuta dal Belgio e dalle compagnie minerarie; finisce con l'operazione Grandslam dell'ONU (gennaio 1963)."),
    ("Stato minerario del Sud Kasai", "1960-08", "1962-10", U, 490, [[[22.6, -5.5], [23.6, -5.5], [24.4, -6.0], [24.5, -6.8], [23.8, -7.4], [22.9, -7.2], [22.5, -6.5]]],
     "Secessione del Sud Kasai di Kalonji (agosto 1960 - ottobre 1962)."),
    ("Governo lumumbista di Stanleyville", "1960-12", "1962-01", S, 490, [[[23.5, 4.3], [27.5, 5.2], [30.5, 3.6], [31.2, 2.2], [30.0, 0.0], [28.8, -1.0], [26.0, -1.0], [24.0, 0.0], [23.0, 1.5], [23.0, 3.5]]],
     "Il governo di Gizenga a Stanleyville, riconosciuto dal blocco sovietico, tiene la Provincia Orientale e il Kivu."),
    ("Ribellione dei Simba", "1964-08", "1964-11", S, 490, [[[23.5, 4.3], [27.5, 5.2], [30.5, 3.6], [31.2, 2.2], [30.0, 0.0], [29.0, -1.5], [29.2, -5.0], [27.0, -5.0], [25.5, -3.0], [24.0, 0.0], [23.0, 1.5], [23.0, 3.5]]],
     "I Simba prendono Stanleyville il 5 agosto 1964 e tengono il nord-est fino all'operazione Dragon Rouge del 24 novembre."),
    # Guerre coloniali portoghesi
    ("Zone liberate del PAIGC", "1964-01", "1974-09", S, 404, [[[-15.2, 11.4], [-14.6, 11.65], [-14.0, 11.7], [-13.75, 11.6], [-13.75, 11.0], [-14.6, 10.95], [-15.1, 11.0]],
                                                             [[-15.6, 12.6], [-15.0, 12.65], [-14.6, 12.45], [-14.9, 12.2], [-15.5, 12.25]]],
     "Guinea portoghese: zone liberate del PAIGC nel sud (Quitafine, Tombali) e nel nord (Oio); il PAIGC proclama l'indipendenza nel 1973, riconosciuta a settembre 1974."),
    ("Zone liberate del PAIGC (Boé)", "1968-01", "1974-09", S, 404, [[[-14.3, 11.95], [-13.7, 12.0], [-13.7, 11.6], [-14.2, 11.6]]], "Il Boé, nell'est, dove il PAIGC proclama l'indipendenza il 24 settembre 1973."),
    ("Insurrezione dell'UPA", "1961-03", "1961-09", U, 540, [[[14.0, -6.8], [15.7, -6.5], [16.2, -7.4], [15.5, -8.3], [14.3, -8.4], [13.9, -7.7]]],
     "Angola: rivolta dell'UPA di Holden Roberto nel nord (Uíge, Dembos) dal 15 marzo 1961, poi respinta dall'esercito portoghese."),
    ("FNLA nei Dembos", "1961-10", "1974-04", U, 540, [[[14.2, -7.6], [14.9, -7.5], [15.1, -8.2], [14.4, -8.3]]], "Angola: sacche della guerriglia del FNLA nella foresta dei Dembos."),
    ("Fronte orientale dell'MPLA", "1966-05", "1974-04", S, 540, [[[20.0, -11.5], [22.0, -11.3], [24.0, -11.5], [24.0, -13.0], [22.0, -13.0], [22.0, -16.0], [21.0, -16.5], [20.0, -14.0]]],
     "Angola: il fronte orientale dell'MPLA nel Moxico e nel Cuando Cubango, dalle basi in Zambia."),
    ("Zone liberate del FRELIMO", "1964-09", "1975-06", S, 541, [[[39.0, -10.5], [40.2, -10.5], [40.2, -11.6], [39.3, -12.2], [38.6, -11.8]]],
     "Mozambico: il FRELIMO apre la guerra il 25 settembre 1964 a Cabo Delgado (altopiano dei Makonde, Mueda)."),
    ("Zone liberate del FRELIMO (Niassa)", "1965-01", "1975-06", S, 541, [[[34.7, -11.6], [36.0, -11.5], [36.3, -12.5], [35.3, -13.3], [34.8, -12.6]]], "Mozambico: zone del FRELIMO nel Niassa, sul lago."),
    ("Zone del FRELIMO (Tete)", "1968-03", "1975-06", S, 541, [[[31.5, -15.3], [33.0, -14.9], [33.8, -15.6], [33.0, -16.5], [31.8, -16.2]]], "Mozambico: il fronte di Tete, aperto nel marzo 1968 attorno alla diga di Cahora Bassa."),
    # Angola e Mozambico indipendenti
    ("UNITA", "1976-04", "1991-05", U, 540, [[[19.0, -14.5], [21.0, -14.5], [22.0, -16.0], [23.0, -17.4], [21.0, -18.0], [19.5, -17.8], [18.5, -16.0]]],
     "Angola: l'UNITA di Savimbi tiene il sud-est (Cuando Cubango, capitale Jamba), sostenuta da Sudafrica e USA, fino agli accordi di Bicesse (maggio 1991)."),
    ("Occupazione sudafricana del Cunene", "1981-08", "1988-08", 560, 540, [[[14.3, -17.45], [14.8, -16.5], [15.9, -16.3], [16.8, -16.6], [17.5, -17.4]]],
     "Angola: l'operazione Protea (agosto 1981) porta l'esercito sudafricano nel sud del Cunene, dove resta fino agli accordi dell'agosto 1988."),
    ("RENAMO", "1977-05", "1981-12", U, 541, [[[34.0, -18.4], [34.6, -18.3], [34.7, -19.0], [34.1, -19.1]]], "Mozambico: la RENAMO, creata dai servizi rhodesiani, ha la base nella Gorongosa."),
    ("RENAMO", "1982-01", "1991-12", U, 541, [[[33.2, -17.5], [35.2, -17.0], [36.5, -17.5], [36.8, -16.5], [37.5, -16.0], [37.0, -15.0], [35.6, -15.5], [34.5, -16.5], [33.2, -16.8]],
                                               [[33.8, -18.3], [35.0, -18.2], [35.2, -19.5], [34.4, -20.7], [33.5, -20.0]]],
     "Mozambico: dagli anni Ottanta la RENAMO, sostenuta dal Sudafrica, controlla larga parte delle province centrali (Zambézia, Sofala, Manica)."),
    # Asia e America Latina
    ("Occupazione cinese", "1979-02", "1979-03", 710, 816, [[[103.75, 22.6], [104.1, 22.8], [104.3, 22.5], [104.0, 22.3]], [[105.8, 22.85], [106.7, 22.85], [106.7, 22.5], [106.0, 22.5]],
                                                        [[106.6, 21.95], [107.0, 22.15], [107.0, 21.75], [106.7, 21.75]], [[104.8, 23.0], [105.2, 23.1], [105.2, 22.85], [104.85, 22.8]]],
     "Guerra sino-vietnamita: dal 17 febbraio 1979 l'Esercito popolare di liberazione occupa Lao Cai, Cao Bang, Lang Son e Ha Giang; il ritiro finisce il 16 marzo."),
    ("Zone del FMLN", "1981-01", "1991-12", S, 92, [[[-89.2, 14.35], [-88.7, 14.35], [-88.7, 14.05], [-89.1, 14.05]], [[-88.25, 14.0], [-87.95, 13.95], [-87.95, 13.7], [-88.25, 13.75]],
                                                  [[-89.2, 13.95], [-89.05, 13.95], [-89.05, 13.85], [-89.2, 13.85]], [[-88.9, 13.65], [-88.55, 13.7], [-88.5, 13.45], [-88.8, 13.4]]],
     "El Salvador: zone di controllo del FMLN dall'offensiva del gennaio 1981 agli accordi di Chapultepec (gennaio 1992): Chalatenango, Morazán, il vulcano di Guazapa, San Vicente e Usulután."),
    ("Zona d'operazione dei Contras", "1982-03", "1990-02", U, 93, [[[-86.6, 13.8], [-85.0, 14.1], [-84.4, 14.0], [-84.8, 13.4], [-85.6, 13.2], [-86.3, 13.3]]],
     "Nicaragua: i Contras, armati dagli USA dalle basi in Honduras, operano nel nord (Nueva Segovia, Jinotega) senza tenere stabilmente il territorio; disarmo dopo le elezioni del 1990."),
]


def main(territories):
    text = open(territories, encoding="utf8").read()
    terr = [x for x in json.loads(text.split("=", 1)[1].rstrip().rstrip(";")) if not x.get("cwz")]
    add = []
    for n, a, b, look, clip, rings, d in ZONES:
        e = {"n": n, "from": a, "to": b, "rings": [r + r[:1] for r in rings], "clip": clip, "z": 1, "cwz": 1, "d": d + NOTE}
        if isinstance(look, int):
            e["code"], e["cls"] = look, "t-fill t-occ"
        else:
            e["look"] = look
        add.append(e)
    with open(territories, "w", encoding="utf8") as h:
        h.write("window.TERRITORIES=" + json.dumps(terr + add, separators=(",", ":"), ensure_ascii=False) + ";\n")
    print(len(add), "zone")


if __name__ == "__main__":
    main(sys.argv[1])
