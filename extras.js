/* Aggiunte compilate a mano, da memoria e non verificate su fonti: fronti, battaglie, missili, depositi nucleari, eventi. */

/* Barriera del Sahara: tracciato a mano tra località note, a fasi come fu costruita. Sostituisce la versione precedente. */
window.LINES = window.LINES.filter(l => l.n !== "Barriera del Sahara Occidentale");
var SAHARA_SRC = "Ricostruzione a mano tra località note: dati aperti del tracciato non trovati";
window.LINES.push(
{n:"Barriera del Sahara: primo tratto",from:"1980-08",to:"1991-12",k:"line",src:SAHARA_SRC,d:"Il \"triangolo utile\": protegge Smara, Bou Craa e El Aaiun.",p:[[-8.67,27.66],[-9.2,27.25],[-9.9,26.95],[-10.7,26.6]]},
{n:"Barriera del Sahara: Guelta Zemmour",from:"1984-12",to:"1991-12",k:"line",src:SAHARA_SRC,d:"Estensione verso sud fino a Guelta Zemmour.",p:[[-10.7,26.6],[-11.15,26.2],[-11.6,25.8],[-12.1,25.3],[-12.6,24.6]]},
{n:"Barriera del Sahara: fino alla Mauritania",from:"1987-04",to:"1991-12",k:"line",src:SAHARA_SRC,d:"Ultimo tratto completato nel 1987, circa 2.700 km in totale.",p:[[-12.6,24.6],[-12.9,23.9],[-13.35,23.1],[-13.9,22.5],[-14.5,21.9],[-15.2,21.4],[-16.2,21.35],[-16.95,21.33]]},

/* Vietnam */
{n:"Vietnam: offensiva del Têt",from:"1968-01",to:"1968-03",k:"front",src:"Ricostruzione a mano",d:"Attacchi contemporanei: nessun fronte continuo. Linea degli scontri maggiori a Hue, Khe Sanh e sul 17° parallelo.",p:[[106.7,16.65],[107.1,16.7],[107.6,16.45]]},
{n:"Vietnam: offensiva di Pasqua",from:"1972-03",to:"1972-09",k:"front",src:"Ricostruzione a mano",d:"Il Nord occupa Quang Tri; il fronte si ferma a nord di Hue, a Kontum e An Loc.",p:[[107,16.4],[107.4,16.55],[107.6,16.65]]},
{n:"Vietnam: An Loc e Kontum",from:"1972-04",to:"1972-07",k:"front",src:"Ricostruzione a mano",d:"Assedi sugli altopiani e a nord di Saigon.",p:[[107.95,14.35],[107.55,13.3],[106.6,11.65]]},
{n:"Vietnam: confine dopo Parigi",from:"1973-02",to:"1974-12",k:"line",src:"Ricostruzione a mano",d:"Zone a macchia di leopardo dopo gli accordi di Parigi. Linea indicativa delle aree comuniste a ovest.",p:[[107.1,16.5],[107.6,15.5],[107.9,14.5],[107.8,13.5],[107.3,12.5],[106.8,11.5],[106,10.8]]},
{n:"Vietnam: offensiva finale",from:"1975-03",to:"1975-03",k:"front",src:"Ricostruzione a mano",d:"Ban Me Thuot cade il 10 marzo, gli altopiani crollano, Hue e Da Nang cadono entro il mese.",p:[[109.3,13.2],[108.3,12.9],[107.7,12.6],[106.9,11.6]]},
{n:"Vietnam: verso Saigon",from:"1975-04",to:"1975-04",k:"front",src:"Ricostruzione a mano",d:"Xuan Loc cade il 21 aprile, Saigon il 30.",p:[[107.25,10.65],[107.2,10.95],[106.7,11.1],[106.3,11]]},

/* Guerre arabo-israeliane */
{n:"Guerra del 1948: Israele",from:"1948-05",to:"1949-06",k:"front",src:"Ricostruzione a mano",d:"Fronti su Galilea, Gerusalemme e Negev. La Linea verde arriva con gli armistizi del 1949.",p:[[35.1,33.08],[35.6,33.2],[35.6,32.7],[35.5,32.4],[35.0,32.3],[35.0,31.8],[35.2,31.75],[34.9,31.35],[34.55,31.3]]},
{n:"Crisi di Suez: avanzata israeliana",from:"1956-10",to:"1957-03",k:"front",src:"Ricostruzione a mano",d:"Israele occupa il Sinai fino a pochi km dal Canale. Ritiro entro marzo 1957.",p:[[32.5,31.1],[32.6,30.5],[32.75,29.9],[33.2,29.3],[34.3,27.8]]},
{n:"Guerra dei Sei giorni: Sinai",from:"1967-06",to:"1967-06",k:"front",src:"OpenStreetMap, Canale di Suez",d:"Israele raggiunge il Canale in quattro giorni.",geo:"suez"},
{n:"Fiume Giordano e Wadi Araba",from:"1967-06",to:"1994-10",k:"line",src:"OpenStreetMap, confine della Giordania",d:"Linea del cessate il fuoco con la Giordania dopo la guerra dei Sei giorni: Yarmuk, fiume Giordano, Mar Morto e Wadi Araba fino ad Aqaba.",geo:"jordan"},
{n:"Guerra del Kippur: riva est",from:"1973-10",to:"1974-01",k:"front",src:"Ricostruzione a mano",d:"Gli egiziani tengono una fascia a est del Canale, Israele attraversa a ovest e circonda la Terza Armata.",p:[[32.5,31.2],[32.55,30.65],[32.5,30.4],[32.35,30.3],[32.3,30.1],[32.55,29.95]]},
{n:"Guerra del Kippur: Golan",from:"1973-10",to:"1974-05",k:"front",src:"Ricostruzione a mano",d:"Israele respinge i siriani e avanza verso Damasco, entro 40 km dalla città.",p:[[35.75,33.3],[35.95,33.35],[36.1,33.2],[36.1,33],[35.9,32.8]]},
{n:"Sinai: disimpegno e ritiro",from:"1974-01",to:"1982-04",k:"line",src:"Ricostruzione a mano",d:"Passi di Mitla e Gidi, poi ritiro israeliano completato il 25 aprile 1982.",p:[[33,31],[32.9,30.5],[33,29.9],[33.1,29.2]]},
{n:"Libano: invasione israeliana",from:"1982-06",to:"1982-09",k:"front",src:"Ricostruzione a mano",d:"Pace in Galilea: Israele arriva a Beirut, assedio estivo.",p:[[35.5,33.85],[35.7,33.8],[35.75,33.55],[35.85,33.45]]},
{n:"Libano: zona di sicurezza",from:"1985-06",to:"1991-12",k:"line",src:"Ricostruzione a mano",d:"Israele si ritira nella fascia sud fino al 2000.",p:[[35.2,33.3],[35.45,33.4],[35.65,33.4],[35.75,33.3]]},

/* Afghanistan: nessun fronte continuo */
{n:"Afghanistan: assi sovietici",from:"1979-12",to:"1989-02",k:"line",src:"Ricostruzione a mano. Non è un fronte",d:"L'URSS tiene città e strade principali: da Termez per il Salang a Kabul e dal Turkmenistan per Herat a Kandahar. Le campagne restano contese, non esiste una linea continua.",p:[[67.2,37.2],[68.0,36.7],[68.65,36.2],[69.1,35.3],[69.2,34.55],[68.4,33.55],[67.1,32.5],[65.7,31.6],[64.3,31.9],[62.2,33.2],[62.2,34.35],[61.9,35.3]]},
{n:"Afghanistan: valle del Panjshir",from:"1980-04",to:"1988-12",k:"front",src:"Ricostruzione a mano",d:"Nove offensive sovietiche contro Massoud nella valle.",p:[[69.3,35.15],[69.75,35.4],[70.3,35.75]]},
{n:"Afghanistan: Khost",from:"1987-11",to:"1988-01",k:"front",src:"Ricostruzione a mano",d:"Operazione Magistral per riaprire la strada di Khost.",p:[[69.35,33.6],[69.7,33.4],[69.95,33.35]]},
{n:"Afghanistan: Jalalabad",from:"1989-03",to:"1989-07",k:"front",src:"Ricostruzione a mano",d:"I mujaheddin falliscono l'assalto alla città dopo il ritiro sovietico.",p:[[70.3,34.55],[70.45,34.45],[70.6,34.45]]},

/* Guerra del Golfo */
{n:"Golfo: occupazione del Kuwait",from:"1990-08",to:"1991-01",k:"line",src:"Ricostruzione a mano, confine saudita",d:"Linea irachena sul confine saudita, con la Linea Saddam fortificata.",p:[[46.55,29.1],[47.45,29.0],[47.7,28.53],[48.42,28.54]]},
{n:"Golfo: Desert Storm",from:"1991-02",to:"1991-02",k:"front",src:"Ricostruzione a mano",d:"24-28 febbraio. Il VII Corpo gira a ovest nel deserto iracheno e chiude verso Bassora, la coalizione libera il Kuwait.",p:[[46.1,31],[46.9,30.8],[47.5,30.45],[47.9,30.1],[48.0,29.65],[48.15,29.35]]},
{n:"Golfo: linea del cessate il fuoco",from:"1991-03",to:"1991-04",k:"line",src:"Ricostruzione a mano",d:"Tregua di Safwan il 3 marzo.",p:[[46.1,31],[46.9,30.8],[47.5,30.45],[47.9,30.3]]},

/* Angola */
{n:"Angola: avanzata di Savannah",from:"1975-10",to:"1976-03",k:"front",src:"Ricostruzione a mano",d:"Il Sudafrica sale verso Luanda, fermato a Ebo e Quifangondo con i cubani. Ritiro nel marzo 1976.",p:[[13.5,-8.9],[14.5,-10.5],[15.5,-11.3],[15.2,-12.5],[14.5,-13.5]]},
{n:"Angola: Mavinga e Cuito Cuanavale",from:"1987-08",to:"1988-03",k:"front",src:"Ricostruzione a mano",d:"L'FAPLA avanza con i sovietici verso Mavinga, respinta dal Sudafrica sul Lomba; poi assedio di Cuito Cuanavale.",p:[[18.5,-15.2],[19.1,-15.15],[19.5,-15.3],[20,-15.5],[20.5,-15.8]]},
{n:"Angola: Cunene e Calueque",from:"1988-05",to:"1988-08",k:"front",src:"Ricostruzione a mano",d:"Cuba porta le truppe al confine namibiano, scontri a Calueque. Porta agli accordi di New York.",p:[[13.5,-17],[14.5,-16.7],[15.5,-16.5],[16.5,-16.5]]},
{n:"Angola: zona UNITA",from:"1984-01",to:"1991-05",k:"line",src:"Ricostruzione a mano",d:"Linea indicativa del sud-est sotto l'UNITA, con Jamba come base.",p:[[17,-17.5],[17.5,-16],[18.5,-14.5],[20,-13.5],[21.5,-13]]}
);

/* Battaglie: nome, da, a, lat, lon, nota */
window.BATTLES = [
["Inchon","1950-09","1950-09",37.47,126.62,"Sbarco ONU di MacArthur alle spalle dei nordcoreani."],
["Bacino di Chosin","1950-11","1950-12",40.45,127.1,"Marines accerchiati dai cinesi, ritirata verso Hungnam."],
["Imjin","1951-04","1951-04",37.97,126.97,"I Gloucester resistono all'offensiva di primavera."],
["Kapyong","1951-04","1951-04",37.83,127.5,"Australiani e canadesi fermano i cinesi."],
["Bloody Ridge","1951-08","1951-09",38.25,128,"Tre colline contese per quasi un mese."],
["Heartbreak Ridge","1951-09","1951-10",38.31,128.03,"Oltre 3.000 perdite ONU."],
["Old Baldy","1952-06","1953-03",38.33,126.95,"Collina contesa per mesi nel fronte centrale."],
["Pork Chop Hill","1953-04","1953-07",38.3,126.95,"Ultimi combattimenti prima dell'armistizio."],
["Dien Bien Phu","1954-03","1954-05",21.39,103.02,"Sconfitta francese decisiva, porta agli accordi di Ginevra."],
["Algeri","1957-01","1957-10",36.77,3.06,"Paracadutisti francesi contro l'FLN nella Casbah."],
["Ap Bac","1963-01","1963-01",10.43,106.12,"Prima vittoria Viet Cong su forze sudvietnamite armate dagli USA."],
["Ia Drang","1965-11","1965-11",13.6,107.65,"Primo grande scontro USA-Nord Vietnam."],
["Khe Sanh","1968-01","1968-07",16.65,106.73,"Assedio della base dei Marines."],
["Hue","1968-01","1968-03",16.46,107.59,"Combattimenti casa per casa durante il Têt."],
["Hamburger Hill","1969-05","1969-05",16.25,107.2,"Assalto USA alla Collina 937 nella valle di A Shau."],
["Quang Tri","1972-03","1972-09",16.75,107.19,"Presa dal Nord e riconquistata dal Sud."],
["Xuan Loc","1975-04","1975-04",10.93,107.25,"Ultima grande resistenza sudvietnamita."],
["Suez, Port Said","1956-11","1956-11",31.26,32.3,"Sbarco anglo-francese."],
["Mitla","1956-10","1956-11",30,32.9,"Paracadutisti israeliani nel Sinai."],
["Gerusalemme","1967-06","1967-06",31.78,35.23,"Israele prende la città vecchia."],
["Valle delle Lacrime","1973-10","1973-10",33.15,35.8,"La difesa israeliana regge sul Golan."],
["Fattoria cinese","1973-10","1973-10",30.45,32.45,"Attraversamento israeliano del Canale."],
["Beirut","1982-06","1982-08",33.88,35.5,"Assedio dell'OLP, poi massacro di Sabra e Shatila."],
["Khorramshahr","1982-05","1982-05",30.43,48.18,"L'Iran riprende la città dagli iracheni."],
["Bassora, Kerbala 5","1987-01","1987-02",30.5,47.9,"Grande offensiva iraniana fallita."],
["Halabja","1988-03","1988-03",35.19,45.98,"Attacco chimico iracheno sui curdi."],
["Khafji","1991-01","1991-02",28.43,48.5,"Incursione irachena in Arabia Saudita."],
["73 Easting","1991-02","1991-02",29.8,46.9,"Grande scontro di carri nel deserto."],
["Lang Son","1979-02","1979-03",21.85,106.76,"Battaglia principale della guerra sino-vietnamita."],
["Isola di Damanskij","1969-03","1969-03",46.49,133.84,"Scontri sull'Ussuri tra URSS e Cina."],
["Baia dei Porci","1961-04","1961-04",22.1,-81.2,"Esuli cubani sconfitti in tre giorni."],
["Ebo","1975-11","1975-11",-11.1,14.7,"Sudafricani fermati in Angola."],
["Quifangondo","1975-11","1975-11",-8.75,13.45,"Salva Luanda per l'MPLA."],
["Cassinga","1978-05","1978-05",-15.1,16.1,"Raid aereo sudafricano sul campo SWAPO."],
["Cuito Cuanavale","1987-11","1988-03",-15.17,19.18,"Maggiore battaglia africana dal 1945."],
["Calueque","1988-06","1988-06",-17.27,14.53,"Scontro al confine namibiano."],
["Jijiga","1977-08","1978-03",9.35,42.8,"Offensiva somala e controffensiva etiope e cubana."],
["Goose Green","1982-05","1982-05",-51.82,-58.97,"Falkland: prima grande battaglia terrestre."],
["Mount Longdon","1982-06","1982-06",-51.67,-57.95,"Falkland: ultima notte prima della resa."],
["Budapest","1956-10","1956-11",47.5,19.05,"Rivolta soffocata dai carri sovietici."],
["Praga","1968-08","1968-08",50.08,14.42,"Invasione del Patto di Varsavia."],
["Massaua","1990-02","1990-02",15.6,39.45,"Offensiva eritrea, porto preso all'Etiopia."],
["Naktong","1950-08","1950-09",35.9,128.4,"Difesa del Perimetro di Pusan."],
["Seul","1950-09","1950-09",37.56,126.98,"L'ONU riprende la capitale."],
["Mukden","1948-09","1948-11",41.8,123.43,"Liao-Shen: svolta della guerra civile cinese."],
["Huai-Hai","1948-11","1949-01",34.2,117.2,"Vittoria decisiva comunista sui nazionalisti."],
["Grammos","1949-08","1949-08",40.38,20.83,"Fine della guerra civile greca."],
];

/* Missili balistici a raggio intermedio: nome, lat, lon, proprietario, modello, da, a */
window.IRBM = [
["Thor: Hemswell",53.4,-0.56,"uk","Thor","1959-06","1963-05"],["Thor: Driffield",53.98,-0.49,"uk","Thor","1959-06","1963-05"],["Thor: North Luffenham",52.63,-0.6,"uk","Thor","1959-10","1963-05"],["Thor: Feltwell",52.48,0.52,"uk","Thor","1958-09","1963-08"],
["Jupiter: Gioia del Colle",40.77,16.93,"us","Jupiter","1961-07","1963-04"],["Jupiter: Altamura",40.83,16.55,"us","Jupiter","1961-07","1963-04"],["Jupiter: Çiğli",38.51,27.01,"us","Jupiter","1961-11","1963-04"],
["Pershing II: Mutlangen",48.82,9.87,"us","Pershing II","1983-12","1989-12"],["Pershing II: Neu-Ulm",48.4,10,"us","Pershing II","1984-06","1989-12"],["Pershing II: Heilbronn",49.14,9.21,"us","Pershing II","1984-06","1989-12"],
["GLCM: Greenham Common",51.38,-1.28,"us","GLCM","1983-11","1991-03"],["GLCM: Molesworth",52.38,-0.42,"us","GLCM","1986-12","1988-09"],["GLCM: Comiso",36.99,14.61,"us","GLCM","1984-03","1991-05"],["GLCM: Florennes",50.24,4.65,"us","GLCM","1985-03","1989-05"],["GLCM: Woensdrecht",51.45,4.34,"us","GLCM","1987-04","1988-12"],["GLCM: Wüschheim",49.99,7.4,"us","GLCM","1986-12","1990-12"],
["S-3: Plateau d'Albion",44,5.5,"fr","SSBS S-2/S-3","1971-08","1991-12"],
["DF-3: Datong",40.09,113.3,"cn","DF-3","1971-01","1991-12"],["DF-4: Lingbao",34.52,110.89,"cn","DF-4","1980-01","1991-12"],
["R-12: San Cristóbal",22.72,-83.05,"su","R-12 (SS-4)","1962-09","1962-11"],["R-12: Sagua la Grande",22.8,-80.07,"su","R-12 (SS-4)","1962-09","1962-11"],["R-14: Guanajay",22.93,-82.69,"su","R-14 (SS-5, mai completati)","1962-09","1962-11"],
["R-5: Vogelsang",53.1,13.17,"su","R-5 (SS-3), in DDR per pochi mesi","1959-05","1959-08"],
["SS-4/5: Baltico, Ventspils",57.4,21.56,"su","R-12 (SS-4)","1959-06","1989-05"],["SS-4/5: Ussurijsk",43.8,131.95,"su","R-14 (SS-5)","1962-01","1985-01"],["SS-4/5: Carpazi, Kolomyja",48.53,25.04,"su","R-12 (SS-4)","1959-06","1988-05"],
["SS-20: Postavy",55.11,26.83,"su","RSD-10 (SS-20)","1978-01","1989-12"],["SS-20: Lida",53.9,25.3,"su","RSD-10 (SS-20)","1979-01","1989-12"],["SS-20: Slonim",53.09,25.3,"su","RSD-10 (SS-20)","1978-01","1989-12"],["SS-20: Mozyr",52.05,29.25,"su","RSD-10 (SS-20)","1978-01","1989-12"],["SS-20: Petrikov",52.13,28.5,"su","RSD-10 (SS-20)","1978-01","1989-12"],["SS-20: Polonnoje",50.11,27.51,"su","RSD-10 (SS-20)","1980-01","1989-12"],["SS-20: Vetrino",55.4,28.47,"su","RSD-10 (SS-20)","1982-01","1989-12"],
["SS-20: Kansk",56.2,95.7,"su","RSD-10 (SS-20)","1982-01","1989-12"],["SS-20: Barnaul",53.36,83.76,"su","RSD-10 (SS-20)","1982-01","1989-12"],["SS-20: Novosibirsk",55.04,82.93,"su","RSD-10 (SS-20)","1981-01","1989-12"],["SS-20: Drovjanaja",51.48,113.05,"su","RSD-10 (SS-20)","1983-01","1989-12"],["SS-20: Kapustin Jar",48.57,45.75,"su","RSD-10 (SS-20)","1976-03","1989-12"],
];

/* Nuove basi: nome, lat, lon, proprietario, tipo, da, a, nota, nucleare, sovrana */
window.EXTRA_BASES = [
["Büchel",50.17,7.06,"us","air","1958-01","","Bombe USA per i Tornado tedeschi",1,0],["Nörvenich",50.83,6.66,"us","air","1962-01","","Bombe USA, caccia tedeschi",1,0],["Memmingen",47.99,10.24,"us","air","1962-01","","Bombe USA, caccia tedeschi",1,0],["Landsberg",48.08,10.9,"us","air","1962-01","","Bombe USA",1,0],["Volkel",51.65,5.71,"us","air","1962-01","","Bombe USA, caccia olandesi",1,0],["Kleine Brogel",51.17,5.47,"us","air","1963-01","","Bombe USA, caccia belgi",1,0],["Ghedi",45.43,10.27,"us","air","1963-01","","Bombe USA, caccia italiani",1,0],["Rimini",44.02,12.61,"us","air","1964-01","1993-01","Bombe USA",1,0],["Araxos",38.15,21.43,"us","air","1962-01","","Bombe USA, caccia greci",1,0],["Murted, Akıncı",40.08,32.57,"us","air","1964-01","","Bombe USA in Turchia",1,0],["Balıkesir",39.62,27.93,"us","air","1964-01","","Bombe USA in Turchia",1,0],["Eskişehir",39.78,30.58,"us","air","1964-01","","Bombe USA in Turchia",1,0],["Erhaç",38.43,38.08,"us","air","1964-01","","Bombe USA in Turchia",1,0],["Tainan",22.95,120.21,"us","air","1958-01","1974-07","Armi USA a Taiwan",1,0],["Chinatown, Henoko",26.53,128.04,"us","naval","1954-12","1972-05","Maggior deposito USA nel Pacifico, Okinawa",1,0],["Harmon, Terranova",48.54,-58.55,"us","air","1956-01","1966-01","Bombardieri USA in Canada",1,0],["Bejucal",22.93,-82.4,"su","missile","1962-10","1962-11","Deposito di testate sovietiche a Cuba",1,0],["Mannheim",49.49,8.47,"us","army","1955-01","1991-12","Artiglieria nucleare USA, esempio di molti depositi in Germania",1,0],
["Himmelpfort",53.12,13.2,"su","army","1959-05","1991-06","Deposito sovietico in DDR",1,0],["Stolzenhain",51.61,13.48,"su","army","1967-01","1991-06","Deposito sovietico in DDR",1,0],["Bílá Voda",50.43,16.92,"su","army","1969-01","1991-06","Deposito sovietico in Cecoslovacchia",1,0],["Míšov",49.6,13.73,"su","army","1969-01","1991-06","Deposito sovietico in Cecoslovacchia",1,0],["Podborsko",53.97,16.05,"su","army","1969-01","1990-12","Deposito sovietico in Polonia",1,0],["Brzeźnica-Kolonia",53.58,16.63,"su","army","1969-01","1990-12","Deposito sovietico in Polonia",1,0],["Tököl",47.32,18.97,"su","army","1969-01","1991-06","Deposito sovietico in Ungheria (indicativo)",1,0],
["Honington",52.34,0.77,"uk","air","1959-01","","Bombe WE.177",1,0],["Tengah, Singapore",1.39,103.71,"uk","air","1962-01","1970-12","Bombe Red Beard",1,0],["Istres",43.52,4.92,"fr","air","1964-10","","Forza di dissuasione, Mirage IV",1,0],["Mont-de-Marsan",43.91,-0.5,"fr","air","1964-02","","Primo squadrone Mirage IV",1,0],["Luxeuil",47.79,6.36,"fr","air","1966-01","","Mirage IV",1,0],
["Zona del Canale di Panama",9.08,-79.68,"us","army","1945-09","1979-10","Territorio USA fino ai trattati Torrijos-Carter",0,1],["Okinawa, amministrazione USA",26.3,127.8,"us","army","1945-09","1972-05","Governata dagli USA fino al 1972",0,1],["Territorio britannico dell'Oceano Indiano",-6.3,71.8,"uk","naval","1965-11","","Chagos, creato nel 1965",0,1],
];
/* Basi già presenti con armi nucleari note da fonti aperte, o sovrane o in affitto a lungo termine */
window.BASE_FLAGS = {"Ramstein":[1],"Hahn":[1],"Lakenheath":[1],"Upper Heyford":[1],"Greenham Common":[1],"Holy Loch":[1],"Aviano":[1],"Rota":[1],"Torrejón":[1],"Morón":[1],"Saragozza":[1],"Incirlik":[1],"Kadena":[1],"Osan":[1],"Kunsan":[1],"Clark":[1],"Subic Bay":[1],"Andersen, Guam":[1],"Thule":[1],"Nouasseur":[1],"Sidi Slimane":[1],"Goose Bay":[1],"Baia di Suda":[1],"Faslane":[1],"Île Longue":[1],"Plateau d'Albion":[1],"Akrotiri":[1,1],"Dhekelia":[0,1],"Guantánamo":[0,1],"Diego Garcia":[1,1],"Gibilterra":[0,1],"Wideawake, Ascensione":[0,1],"Roosevelt Roads":[0,1],"Pearl Harbor":[0,1],"Kindley, Bermuda":[0,1],"Hong Kong":[0,1],"Port Arthur":[0,1],"Porkkala":[0,1]};

/* Eventi rilevanti */
window.EVENT_LOG = [
["1945-09","Il Giappone firma la resa. Ho Chi Minh proclama l'indipendenza del Vietnam."],["1945-10","Nascono le Nazioni Unite."],["1945-11","Si apre il processo di Norimberga."],
["1946-03","Churchill parla di cortina di ferro a Fulton."],["1946-05","L'URSS lascia l'Iran dopo la crisi."],["1946-06","Referendum: l'Italia diventa repubblica."],["1946-07","Test Crossroads a Bikini."],["1946-12","Inizia la guerra d'Indocina."],
["1947-03","Dottrina Truman."],["1947-06","Annuncio del Piano Marshall."],["1947-07","National Security Act: nasce la CIA."],["1947-08","Indipendenza e partizione di India e Pakistan."],["1947-10","Nasce il Cominform."],
["1948-02","Colpo di Praga."],["1948-04","Elezioni italiane: vince la DC."],["1948-05","Nasce Israele, prima guerra arabo-israeliana."],["1948-06","Espulsione di Tito dal Cominform. Inizia il blocco di Berlino."],["1948-08","Nascono le due Coree."],
["1949-01","Nasce il Comecon."],["1949-04","Trattato Nord Atlantico: nasce la NATO."],["1949-05","Fine del blocco di Berlino, nasce la Germania Ovest."],["1949-08","Primo test atomico sovietico."],["1949-10","Mao proclama la Repubblica popolare. Nasce la Germania Est."],
["1950-02","Trattato sino-sovietico."],["1950-06","La Corea del Nord invade il Sud."],["1950-09","Sbarco di Inchon."],["1950-10","La Cina entra in guerra in Corea."],["1950-11","La Cina occupa il Tibet, entrata da ottobre."],
["1951-04","Truman rimuove MacArthur."],["1951-07","Iniziano i negoziati in Corea."],["1951-09","Trattato di San Francisco e ANZUS."],["1952-02","Grecia e Turchia nella NATO."],["1952-07","Rivoluzione degli Ufficiali liberi in Egitto."],["1952-10","Primo test atomico britannico."],["1952-11","Ivy Mike: prima bomba H."],
["1953-03","Muore Stalin."],["1953-06","Rivolta di Berlino Est."],["1953-07","Armistizio in Corea."],["1953-08","Colpo di stato in Iran. Test sovietico termonucleare."],["1954-03","Castle Bravo: 15 megatoni, il più grande test USA."],["1954-05","Caduta di Dien Bien Phu."],["1954-06","Colpo di stato in Guatemala."],["1954-07","Accordi di Ginevra sull'Indocina."],["1954-09","Nasce la SEATO."],["1954-11","Inizia la guerra d'Algeria."],
["1955-04","Conferenza di Bandung."],["1955-05","La Germania Ovest nella NATO, nasce il Patto di Varsavia. Trattato di Stato austriaco."],["1955-11","Test sovietico della RDS-37, prima H lanciata da aereo."],["1956-02","Krusciov denuncia Stalin."],["1956-06","Rivolta di Poznań."],["1956-07","Nasser nazionalizza il Canale di Suez."],["1956-10","Rivolta ungherese, crisi di Suez."],["1956-11","Carri sovietici a Budapest."],
["1957-03","Trattati di Roma."],["1957-10","Sputnik."],["1958-07","Rivoluzione irachena. Marines in Libano."],["1958-08","Seconda crisi di Quemoy."],["1958-10","De Gaulle fonda la Quinta Repubblica."],["1959-01","Castro prende il potere."],["1959-09","Krusciov negli USA."],
["1960-02","Primo test atomico francese."],["1960-05","Abbattuto l'U-2 di Powers."],["1960-06","Congo indipendente, inizia la crisi."],["1960-07","Rottura sino-sovietica: tecnici ritirati."],["1960-12","Il Vietcong si organizza nel Fronte di liberazione."],
["1961-01","Assassinato Lumumba."],["1961-04","Gagarin. Baia dei Porci."],["1961-08","Sorge il Muro di Berlino."],["1961-09","Nascono i Non allineati a Belgrado."],["1961-10","Stallo al Checkpoint Charlie. Bomba Zar: 50 megatoni."],["1962-03","Accordi di Evian sull'Algeria."],["1962-10","Crisi dei missili di Cuba. Guerra sino-indiana."],
["1963-06","Kennedy a Berlino: Ich bin ein Berliner."],["1963-08","Trattato di bando parziale dei test."],["1963-11","Assassinato Kennedy. Colpo di stato a Saigon."],["1964-08","Golfo del Tonchino."],["1964-10","Krusciov destituito. Primo test atomico cinese."],
["1965-03","Marines a Da Nang, Rolling Thunder."],["1965-04","Intervento USA a Santo Domingo."],["1965-09","Guerra indo-pakistana. Massacri in Indonesia."],["1966-03","La Francia lascia il comando NATO."],["1966-05","Rivoluzione culturale in Cina."],["1967-04","Colpo dei colonnelli in Grecia."],["1967-06","Guerra dei Sei giorni. Primo H cinese."],["1967-10","Morte di Che Guevara."],
["1968-01","Offensiva del Têt."],["1968-07","Trattato di non proliferazione."],["1968-08","Invasione della Cecoslovacchia."],["1969-03","Scontri sull'Ussuri."],["1969-07","Luna: Apollo 11."],["1969-09","Gheddafi al potere."],["1969-10","Brandt inizia la Ostpolitik."],
["1970-03","Colpo di stato in Cambogia."],["1970-09","Settembre nero in Giordania. Allende eletto."],["1971-02","Patto sui fondali marini."],["1971-10","La Cina Popolare entra all'ONU."],["1971-12","Nasce il Bangladesh."],["1972-02","Nixon a Pechino."],["1972-05","SALT I e trattato ABM."],["1972-12","Bombardamenti di Natale. Trattato tra le due Germanie."],
["1973-01","Accordi di Parigi."],["1973-09","Colpo di stato in Cile."],["1973-10","Guerra del Kippur. Shock petrolifero."],["1974-04","Rivoluzione dei garofani."],["1974-05","Primo test indiano."],["1974-07","Crisi di Cipro."],["1974-08","Dimissioni di Nixon."],["1975-04","Cade Saigon. I Khmer rossi a Phnom Penh."],["1975-08","Atti di Helsinki."],["1975-11","Angola indipendente, intervento cubano."],
["1976-07","Riunificazione del Vietnam."],["1976-09","Muore Mao."],["1977-07","Guerra dell'Ogaden."],["1977-11","Sadat a Gerusalemme."],["1978-04","Colpo in Afghanistan."],["1978-09","Accordi di Camp David."],["1978-12","Il Vietnam invade la Cambogia."],
["1979-01","Lo scià lascia l'Iran."],["1979-02","Guerra sino-vietnamita."],["1979-06","SALT II."],["1979-07","Sandinisti al potere."],["1979-11","Ostaggi all'ambasciata USA di Teheran."],["1979-12","Doppia decisione NATO. L'URSS invade l'Afghanistan."],
["1980-08","Solidarność in Polonia."],["1980-09","Guerra Iran-Iraq."],["1981-01","Reagan presidente."],["1981-06","Israele bombarda Osirak."],["1981-12","Legge marziale in Polonia."],["1982-04","Guerra delle Falkland."],["1982-06","Israele in Libano."],["1982-11","Muore Brežnev."],
["1983-03","Reagan annuncia le Guerre stellari."],["1983-09","Abbattuto il volo KAL 007. Allarme di Petrov."],["1983-10","Grenada."],["1983-11","Able Archer. Arrivano i Pershing II."],["1985-03","Gorbačëv al potere."],["1985-11","Ginevra: Reagan e Gorbačëv."],
["1986-04","Černobyl'."],["1986-10","Reykjavík."],["1987-12","Trattato INF."],["1988-05","L'URSS inizia il ritiro dall'Afghanistan."],["1988-08","Tregua Iran-Iraq."],["1988-12","Accordi di New York su Angola e Namibia."],
["1989-02","Ultimi sovietici fuori dall'Afghanistan."],["1989-06","Tienanmen. Elezioni in Polonia."],["1989-08","Catena baltica."],["1989-11","Cade il Muro di Berlino."],["1989-12","Cade Ceaușescu. Il 20 gli USA invadono Panama: operazione Just Cause."],["1990-01","Noriega si arrende agli americani il 3 gennaio."],
["1990-03","La Lituania si dichiara indipendente. Namibia indipendente."],["1990-05","Riunificazione dello Yemen."],["1990-08","L'Iraq invade il Kuwait."],["1990-10","Riunificazione tedesca."],["1991-01","Desert Storm."],["1991-02","Battaglia di terra nel Golfo."],["1991-07","Sciolto il Patto di Varsavia. START I."],["1991-08","Golpe di agosto a Mosca."],["1991-12","Dissoluzione dell'URSS."],
];
