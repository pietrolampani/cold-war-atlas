/* Linee. "geo" prende il tracciato da lines.js (Natural Earth o OpenStreetMap); "p" è disegnato a mano, [lon, lat].
   I confini odierni seguono le linee storiche solo dove la nota lo dice. */
var KOREA = "Fronte di Corea";
var PARALLEL38 = [];
for (var lon = 124.6; lon <= 128.7; lon += 0.1) PARALLEL38.push([+lon.toFixed(1), 38]);
window.LINES = [
{n:"38° parallelo",from:"1945-08",to:"1950-05",k:"line",src:"Parallelo geografico",d:"Linea di divisione tra zona USA e zona sovietica in Corea.",p:PARALLEL38},
{n:KOREA,from:"1950-06",to:"1950-06",k:"front",src:"Ricostruzione a mano",d:"Fine giugno: Seul è caduta, i nordcoreani arrivano al fiume Han.",p:[[126.55,37.65],[126.8,37.58],[127.0,37.52],[127.2,37.5],[127.5,37.6],[127.95,37.62],[128.3,37.68],[128.9,37.75]]},
{n:KOREA,from:"1950-07",to:"1950-07",k:"front",src:"Ricostruzione a mano",d:"Fine luglio: Taejon è caduta, ripiegamento verso il Naktong.",p:[[127.75,34.95],[128.1,35.2],[127.92,35.68],[128.1,36.1],[128.35,36.45],[128.7,36.55],[129.05,36.45],[129.4,36.42]]},
{n:KOREA,from:"1950-08",to:"1950-09",k:"front",src:"Ricostruzione a mano",d:"Perimetro di Pusan: Masan, fiume Naktong, Waegwan, Taegu, P'ohang. Lo sbarco di Inchon è del 15 settembre.",p:[[128.56,35.08],[128.46,35.2],[128.42,35.37],[128.44,35.55],[128.45,35.7],[128.38,35.85],[128.4,35.99],[128.5,36.08],[128.62,36.12],[128.85,36.13],[129.1,36.12],[129.38,36.1]]},
{n:KOREA,from:"1950-10",to:"1950-10",k:"front",src:"Ricostruzione a mano",d:"Fine ottobre: l'ONU supera Pyongyang e si avvicina allo Yalu, la Cina entra in guerra.",p:[[124.6,40],[125.2,40.2],[125.8,40.3],[126.3,40.4],[126.8,40.5],[127.25,40.3],[127.6,40.4],[128.1,40.75],[128.6,41.2],[129.2,41.35],[129.8,41.5]]},
{n:KOREA,from:"1950-11",to:"1950-11",k:"front",src:"Ricostruzione a mano",d:"Fine novembre: offensiva cinese, battaglie del Ch'ongch'on e del bacino di Chosin.",p:[[125.1,39.6],[125.6,39.65],[126.1,39.7],[126.6,39.9],[127,40.1],[127.4,40.25],[127.9,40.3],[128.4,40.6],[128.9,40.9],[129.7,41.1]]},
{n:KOREA,from:"1950-12",to:"1950-12",k:"front",src:"Ricostruzione a mano",d:"L'ONU ripiega al 38° parallelo. Evacuazione di Hungnam.",p:[[126.1,37.9],[126.6,37.92],[127,38],[127.5,38.02],[128,38],[128.3,38.1],[128.6,38.2]]},
/* Dal 1951 il tracciato è la situazione a fine mese, ricostruito a mano da descrizioni testuali e località note. */
{n:KOREA,from:"1951-01",to:"1951-01",k:"front",src:"Ricostruzione a mano: Osan, Yoju, Wonju, Samch'ok",d:"Fine gennaio: l'Ottava Armata è poco oltre la Linea D, sotto Osan e Wonju. Il 25 parte l'operazione Thunderbolt, che risale verso Suwon.",p:[[126.75,37.02],[127.03,37.17],[127.25,37.2],[127.45,37.24],[127.64,37.25],[127.95,37.28],[128.2,37.22],[128.5,37.22],[128.9,37.35],[129.25,37.47]]},
{n:KOREA,from:"1951-02",to:"1951-02",k:"front",src:"Ricostruzione a mano: fiume Han, Yangp'yong, Hoengsong, Kangnung",d:"Fine febbraio: Inch'on è ripresa, la resistenza a sud del fiume Han crolla, Chip'yong-ni ha tenuto. L'operazione Killer risale verso Hoengsong.",p:[[126.55,37.6],[126.75,37.58],[126.98,37.52],[127.2,37.52],[127.49,37.52],[127.65,37.5],[127.98,37.43],[128.2,37.45],[128.5,37.52],[128.9,37.74]]},
{n:KOREA,from:"1951-03",to:"1951-03",k:"front",src:"Ricostruzione a mano: Linea Idaho, Munsan, Yangyang",d:"31 marzo: l'Ottava Armata è sulla Linea Idaho, appena sotto il 38° parallelo. Seul è ripresa il 14-15 marzo, a est i sudcoreani sono già oltre, verso Yangyang.",p:[[126.65,37.75],[126.78,37.86],[127.06,37.95],[127.5,37.98],[127.75,37.97],[128.1,38],[128.4,38],[128.66,38.08]]},
{n:"Linea Kansas",from:"1951-04",to:"1951-04",k:"line",src:"Ricostruzione a mano dalla descrizione di Operation Rugged",d:"Raggiunta il 9 aprile da quasi tutta l'Ottava Armata: riva sud dell'Imjin, da 3 a 10 km sopra il 38° parallelo fino al bacino di Hwach'on, poi 16 km sopra il parallelo e giù verso Yangyang. Persa a fine aprile, ripresa a giugno.",p:[[126.65,37.76],[126.85,37.97],[127.03,38.03],[127.3,38.07],[127.6,38.1],[127.8,38.11],[128.1,38.15],[128.35,38.12],[128.62,38.08]]},
{n:KOREA,from:"1951-04",to:"1951-04",k:"front",src:"Ricostruzione a mano: Linea No Name",d:"30 aprile: l'offensiva cinese di primavera si ferma appena a nord di Seul, sulla Linea No Name fino a Taepo-ri sulla costa est.",p:[[126.7,37.75],[126.9,37.72],[127.05,37.72],[127.35,37.72],[127.55,37.7],[127.85,37.75],[128.1,37.85],[128.4,38],[128.6,38.17]]},
{n:KOREA,from:"1951-05",to:"1951-05",k:"front",src:"Ricostruzione a mano, appena sotto la Linea Kansas",d:"31 maggio: dopo l'offensiva fermata il 20 maggio, l'Ottava Armata è appena sotto la Linea Kansas. A est, sulla costa, già verso Kansong.",p:[[126.68,37.77],[126.84,37.93],[127.03,38],[127.3,38.04],[127.6,38.07],[127.8,38.08],[128.1,38.13],[128.3,38.2],[128.47,38.36]]},
{n:KOREA,from:"1951-06",to:"1951-08",k:"front",src:"Ricostruzione a mano: Linea Wyoming, Kansas, Kansong",d:"Linea Kansas più il rigonfiamento Wyoming verso il Triangolo di ferro, con Ch'orwon e Kumhwa. A ovest il fronte scende sotto il 38° parallelo, a nord di Seul. Da luglio i negoziati.",p:[[126.68,37.77],[126.82,37.92],[126.95,38],[127.1,38.15],[127.25,38.22],[127.42,38.27],[127.6,38.25],[127.85,38.22],[128.05,38.22],[128.2,38.25],[128.42,38.33],[128.5,38.4]]},
{n:KOREA,from:"1951-09",to:"1951-09",k:"front",src:"Ricostruzione a mano: Bloody Ridge, Punchbowl",d:"Attacco ONU da 8 a 11 km a nord della Kansas: Bloody Ridge cade il 5 settembre, Heartbreak Ridge è ancora contesa fino al 13 ottobre.",p:[[126.68,37.77],[126.82,37.92],[126.95,38],[127.1,38.15],[127.25,38.22],[127.42,38.3],[127.6,38.33],[127.8,38.33],[128.02,38.3],[128.15,38.35],[128.35,38.5],[128.45,38.55]]},
{n:KOREA,from:"1951-10",to:"1951-10",k:"front",src:"Ricostruzione a mano: Linea Jamestown da Operation Commando, Kumsong",d:"Linea Jamestown: dall'Imjin a Samich'on, Kyeho-dong, Chut'oso e Chungasan, a nord-est di Ch'orwon. Più a est il IX Corpo arriva al margine di Kumsong.",p:[[126.62,37.78],[126.7,37.9],[126.83,37.97],[126.88,38],[126.99,38.11],[127.15,38.28],[127.28,38.3],[127.47,38.31],[127.55,38.37],[127.62,38.41],[127.72,38.415],[127.8,38.41],[127.9,38.35],[128,38.29],[128.08,38.27],[128.2,38.33],[128.33,38.48],[128.38,38.6]]},
{n:KOREA,from:"1951-11",to:"1953-05",k:"front",src:"Linea di demarcazione da OpenStreetMap; saliente di Kumsong a mano",d:"Guerra di posizione. Il 27 novembre 1951 si concorda la linea di contatto come base dell'armistizio. Il fronte coincide quasi con la linea finale, tranne il saliente di Kumsong, che ancora sporge verso nord. Combattimenti per avamposti non mostrati: Old Baldy, Pork Chop, The Hook.",geo:"kor5111"},
{n:KOREA,from:"1953-06",to:"1953-06",k:"front",src:"Linea di demarcazione da OpenStreetMap; saliente a mano",d:"Le offensive cinesi del 10-18 giugno fanno arretrare i sudcoreani di circa 3 km su 13 km di fronte, tra la collina 973 e Capitol Hill.",geo:"kor5306"},
{n:KOREA,from:"1953-07",to:"1953-07",k:"front",src:"Linea di demarcazione da OpenStreetMap",d:"13-20 luglio: l'ultima offensiva cinese elimina il saliente di Kumsong con un arretramento di circa 10-13 km. Il fronte si ferma sul fiume Kumsong. Armistizio il 27 luglio.",geo:"dmz"},
{n:"Zona demilitarizzata coreana",from:"1953-08",to:"1991-12",k:"line",src:"Linea di demarcazione da OpenStreetMap",d:"Linea dell'armistizio del 27 luglio 1953, con la zona larga 4 km.",geo:"dmz"},
{n:"Fiume Ben Hai, 17° parallelo",from:"1954-07",to:"1975-04",k:"line",src:"OpenStreetMap, corso del fiume",d:"Linea di demarcazione fissata a Ginevra tra Nord e Sud Vietnam.",geo:"benhai"},
{n:"Sentiero di Ho Chi Minh",from:"1959-05",to:"1975-04",k:"front",src:"Ricostruzione a mano, molto semplificata",d:"Rete di rifornimento attraverso il passo di Mu Gia, il Laos e la Cambogia.",p:[[105.86,17.7],[105.78,17.45],[106.05,17.05],[106.25,16.6],[106.45,16.05],[106.6,15.5],[106.8,15.0],[107,14.5],[107.1,13.85],[107.15,13.2],[107.25,12.6],[107.3,12],[106.9,11.6],[106.5,11.3]]},
{n:"Linea di quarantena di Cuba",from:"1962-10",to:"1962-11",k:"front",src:"Arco calcolato: 500 miglia nautiche da Capo Maisí",d:"Il blocco navale USA durante la crisi dei missili.",geo:"quarantine"},
{n:"Linea verde",from:"1949-07",to:"1967-05",k:"line",src:"Natural Earth, confini di Cisgiordania e Gaza",d:"Linee dell'armistizio del 1949 tra Israele e Stati arabi.",geo:"green"},
{n:"Canale di Suez",from:"1967-06",to:"1973-10",k:"front",src:"OpenStreetMap, tracciato del canale",d:"Fronte tra Israele ed Egitto dopo la guerra dei Sei giorni, con la linea Bar-Lev sulla riva est.",geo:"suez"},
{n:"Alture del Golan",from:"1967-06",to:"1974-05",k:"front",src:"Natural Earth, linea di fatto",d:"Linea del cessate il fuoco tra Israele e Siria.",geo:"golan"},
{n:"Linea di controllo del Kashmir",from:"1949-01",to:"1991-12",k:"line",src:"Natural Earth, confine di fatto",d:"Linea del cessate il fuoco del 1949 tra India e Pakistan, ridefinita nel 1972.",geo:"kashmir"},
{n:"Linea di controllo sino-indiana",from:"1962-11",to:"1991-12",k:"line",src:"Natural Earth, confine di fatto attuale",d:"Linea di fatto dopo la guerra sino-indiana.",geo:"lac"},
{n:"Linea verde di Cipro",from:"1974-08",to:"1991-12",k:"line",src:"Natural Earth, zona cuscinetto ONU",d:"Divisione dopo l'intervento turco.",geo:"cyprus"},
{n:"Stretto di Taiwan",from:"1954-09",to:"1955-05",k:"front",src:"Ricostruzione a mano",d:"Prima crisi: bombardamenti cinesi su Quemoy e Matsu.",p:[[118.35,24.45],[118.5,24.5],[119.3,25.3],[119.95,26.15]]},
{n:"Stretto di Taiwan",from:"1958-08",to:"1958-12",k:"front",src:"Ricostruzione a mano",d:"Seconda crisi: nuovi bombardamenti su Quemoy e Matsu.",p:[[118.35,24.45],[118.5,24.5],[119.3,25.3],[119.95,26.15]]},
{n:"Fronte Iran-Iraq",from:"1980-09",to:"1988-08",k:"front",src:"Natural Earth, confine internazionale",d:"Il confine, attorno al quale il fronte si è mosso di decine di chilometri.",geo:"iraniraq"},
{n:"Barriera del Sahara Occidentale",from:"1982-08",to:"1991-12",k:"line",src:"Ricostruzione a mano, semplificata",d:"Muro marocchino contro il Fronte Polisario.",p:[[-8.67,27.67],[-9.8,27.3],[-11,26.7],[-12.0,26.3],[-12.9,26],[-13.1,24.7],[-13.2,23.5],[-14.5,22],[-16.0,21.5],[-16.9,21.3]]},
{n:"Frontiera Angola-Namibia",from:"1975-10",to:"1989-04",k:"front",src:"Natural Earth, confine internazionale",d:"Guerra di confine sudafricana contro SWAPO e forze angolane e cubane.",geo:"angola"},
];

/* Berlino e i tre checkpoint alleati. Le coordinate degli edifici arrivano da OpenStreetMap (detail.js);
   Charlie è un mio schema in metri, dx verso est e dy verso nord dall'incrocio Friedrichstraße / Zimmerstraße. */
window.PLACES = [
{n:"Lago d'Aral",lat:45.1,lon:59.9,min:18,c:"title",d:"Dal 1960 si ritira per la deviazione dei fiumi verso il cotone sovietico."},
{n:"Berlino Ovest",from:"1948-12",to:"1990-09",lat:52.49,lon:13.27,min:60,max:1500,c:"title",d:"Settori americano, britannico e francese. Il confine è il perimetro del Muro."},
{n:"Berlino Est",from:"1948-12",to:"1990-09",lat:52.53,lon:13.47,min:60,max:1500,c:"title",d:"Settore sovietico, capitale della DDR."},
{n:"Porta di Brandeburgo",lat:52.5163,lon:13.3777,min:1500,from:"1945-09",d:"Chiusa dal 1961 al dicembre 1989, dentro la zona di confine."},
{n:"Reichstag",lat:52.5186,lon:13.3762,min:1500,d:"A Berlino Ovest, a ridosso del Muro."},
{n:"East Side Gallery",lat:52.5052,lon:13.4397,min:2000,from:"1990-02",d:"Tratto di Hinterlandmauer dipinto nel 1990."},
{n:"Bernauer Straße",lat:52.5352,lon:13.3895,min:2000,d:"Le facciate delle case erano il confine: famose fughe dalle finestre nel 1961."},
{n:"Bornholmer Straße",lat:52.5547,lon:13.3982,min:800,c:"gate",from:"1961-08",to:"1990-06",d:"Valico. Qui il 9 novembre 1989 si aprì per primo il Muro."},
{n:"Chausseestraße",lat:52.5327,lon:13.3826,min:800,c:"gate",from:"1961-08",to:"1990-06",d:"Valico per i berlinesi ovest."},
{n:"Invalidenstraße",lat:52.5310,lon:13.3727,min:800,c:"gate",from:"1961-08",to:"1990-06",d:"Valico per i berlinesi ovest."},
{n:"Bahnhof Friedrichstraße",lat:52.5203,lon:13.3869,min:800,c:"gate",from:"1961-08",to:"1990-07",d:"Valico ferroviario: il \"Palazzo delle lacrime\"."},
{n:"Heinrich-Heine-Straße",lat:52.5070,lon:13.4113,min:800,c:"gate",from:"1961-08",to:"1990-06",d:"Valico per i tedeschi occidentali."},
{n:"Oberbaumbrücke",lat:52.5019,lon:13.4457,min:800,c:"gate",from:"1963-12",to:"1990-06",d:"Valico pedonale sulla Sprea."},
{n:"Sonnenallee",lat:52.4640,lon:13.4740,min:800,c:"gate",from:"1961-08",to:"1990-06",d:"Valico per i berlinesi ovest."},
{n:"Glienicker Brücke",lat:52.4133,lon:13.0903,min:800,c:"gate",from:"1952-05",to:"1989-11",d:"Il ponte delle spie: scambi di agenti nel 1962, 1964 e 1985."},
{n:"Staaken",lat:52.5354,lon:13.1236,min:800,c:"gate",from:"1951-09",to:"1990-06",d:"Valico sulla strada di Amburgo."},
{n:"Heiligensee",lat:52.6198,lon:13.2492,min:800,c:"gate",from:"1982-01",to:"1990-06",d:"Valico autostradale verso Amburgo, aperto nel 1982 (data indicativa)."},
{n:"Torre di guardia, Erna-Berger-Straße",lat:52.5085,lon:13.3797,min:2500,c:"tower",from:"1966-01",d:"Torre BT-6 conservata."},
{n:"Torre di guardia, Schlesischer Busch",lat:52.4957,lon:13.4507,min:2500,c:"tower",from:"1966-01",d:"Torre di comando conservata."},
{n:"Torre di guardia BT-9, Puschkinallee",lat:52.5392,lon:13.4012,min:2500,c:"tower",from:"1970-01",d:"Posizione da OpenStreetMap."},
{n:"Torre di Nieder Neuendorf",lat:52.6051,lon:13.1997,min:2500,c:"tower",from:"1966-01",d:"Torre di comando conservata."},
];

window.CHECKPOINTS = {
  charlie: {
    n:"Checkpoint Charlie",lat:52.50754,lon:13.39034,km:.32,from:"1961-08",to:"1990-06",
    d:"Friedrichstraße, unico varco per diplomatici, militari alleati e stranieri. Ottobre 1961: carri armati USA e sovietici si fronteggiano a 100 metri. Il posto di guardia alleato fu rimosso il 22 giugno 1990.",
    note:"Schema ricostruito da me su descrizioni generali: posizioni e misure del lato DDR sono indicative. Muro da OpenStreetMap.",
    origin:[13.39038,52.50764],rot:5,
    parts:[
      {n:"Posto di guardia alleato",k:"us",rect:[-2.5,-16,2.5,-13],lab:[4,-15]},
      {n:"Cartello del settore americano",k:"sign",rect:[-10,-10,-8.5,-9],lab:[-11,-9.5,"end"]},
      {n:"Linea di settore",k:"line",line:[[-8,0],[8,0]],lab:[10,-1.5]},
      {n:"Sbarra DDR",k:"gate",line:[[-8,6],[8,6]],lab:[-10,6,"end"]},
      {n:"Barriere a zigzag",k:"barrier",rect:[-8,10,2,11.5],lab:[10,26]},{n:"",k:"barrier",rect:[-2,20,8,21.5]},{n:"",k:"barrier",rect:[-8,30,2,31.5]},{n:"",k:"barrier",rect:[-2,40,8,41.5]},
      {n:"Torre di osservazione DDR",k:"gdr",rect:[20,12,26,18],lab:[27,15]},
      {n:"Tettoie veicoli",k:"gdr",rect:[-30,50,-10,95],lab:[-31,72,"end"]},
      {n:"Passaporti e dogana",k:"gdr",rect:[10,50,30,95],lab:[31,72]},
      {n:"Corsie di controllo",k:"lane",line:[[-6,45],[-6,105]],lab:[0,108,"middle"]},{n:"",k:"lane",line:[[0,45],[0,105]]},{n:"",k:"lane",line:[[6,45],[6,105]]},
      {n:"Muro lungo la Zimmerstraße",k:"wall",line:[[-60,3],[-9,3]],lab:[-58,7]},{n:"",k:"wall",line:[[9,3],[60,3]]},
      {n:"Recinto del valico",k:"fence",line:[[-35,3],[-35,115],[-9,115]],lab:[-36,110,"end"]},{n:"",k:"fence",line:[[9,115],[35,115],[35,3]]},
    ],
  },
  alpha: {
    n:"Checkpoint Alpha",lat:52.2145,lon:11.0835,km:.9,from:"1945-07",to:"1990-06",
    d:"Helmstedt, inizio del corridoio autostradale di 170 km verso Berlino. Il posto alleato era sul lato ovest; sul lato est il valico DDR di Marienborn.",
    note:"La planimetria mostra il valico DDR di Marienborn, con edifici e nomi da OpenStreetMap: è del 1972-74 e compare da gennaio 1974. Il posto alleato, senza planimetria, è il rombo rosso circa 1,5 km a ovest.",
    marker:[11.062,52.2181],
  },
  bravo: {
    n:"Checkpoint Bravo",lat:52.4118,lon:13.1945,km:2.2,from:"1945-07",to:"1990-06",
    d:"Dreilinden, arrivo del corridoio a Berlino Ovest. Di fronte il valico DDR di Drewitz, di cui resta la torre di comando.",
    note:"Tracciati da OpenStreetMap. Fino al 1969 l'autostrada passava sul ponte del Teltowkanal e il valico era più a ovest: il vecchio sito compare fino a novembre 1969.",
    marker:[13.1972,52.4161],
  },
};
