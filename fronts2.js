/* Altri fronti, tracciati a mano da memoria tra città note: non verificati su fonti e non ricalcati da carte. */
var F2 = "Ricostruzione a mano da memoria tra località note";
window.LINES = window.LINES.filter(function (l) {
  return ["Guerra del 1948: Israele", "Crisi di Suez: avanzata israeliana", "Guerra dei Sei giorni: Sinai", "Guerra del Kippur: riva est", "Guerra del Kippur: Golan", "Sinai: disimpegno e ritiro", "Libano: invasione israeliana", "Canale di Suez", "Alture del Golan"].indexOf(l.n) < 0;
});
window.LINES.push(
/* Guerra civile cinese */
{n:"Cina: Manciuria, fiume Sungari",from:"1946-06",to:"1947-12",k:"front",src:F2,d:"Tregua di Marshall a giugno 1946: i comunisti tengono il nord del Sungari, i nazionalisti Changchun e Shenyang.",p:[[122.5,46.3],[124.8,45.2],[126.5,44.9],[127.6,45.3],[129.6,44.6],[130.9,43.9]]},
{n:"Cina: fronte del nord",from:"1946-06",to:"1948-08",k:"line",src:F2,d:"I comunisti controllano le campagne dello Shanxi, dello Hebei e dello Shandong, i nazionalisti ferrovie e città. Non è un fronte continuo.",p:[[118.9,39.2],[116.4,39.6],[114.5,38],[114.5,36.6],[115.5,35.4],[117.1,35.5],[118.6,36.4],[120.3,36.1]]},
{n:"Cina: Liaoshen",from:"1948-09",to:"1948-11",k:"front",src:F2,d:"Lin Biao prende Jinzhou, Changchun e Shenyang: la Manciuria è perduta per i nazionalisti.",p:[[119.8,40.3],[121.1,41.1],[122.2,41.2],[123.4,41.8],[124.6,43.3],[125.3,43.9]]},
{n:"Cina: Huai-Hai",from:"1948-11",to:"1949-01",k:"front",src:F2,d:"La battaglia decisiva, attorno a Xuzhou. Pechino cade a fine gennaio.",p:[[120.1,33.8],[118.3,33.7],[117.2,33.9],[116,33.6],[114.3,33.5],[112.5,32.9]]},
{n:"Cina: linea dello Yangtze",from:"1949-02",to:"1949-04",k:"front",src:F2,d:"I comunisti si fermano sul fiume durante i negoziati, che falliscono. Il 21 aprile lo attraversano, Nanchino cade il 23.",p:[[121.9,31.7],[120.5,32],[119.2,32.2],[118.1,31.4],[117,30.6],[115.9,29.8],[114.3,30.6],[112.5,30.3],[111.3,30.7],[109.5,30.9],[107.5,31.5]]},
{n:"Cina: avanzata al sud",from:"1949-05",to:"1949-08",k:"front",src:F2,d:"Shanghai cade il 27 maggio, Hunan e Fujian in estate.",p:[[121.4,28.6],[119.3,27.3],[117.5,27.5],[115.5,27],[113.8,27.4],[111.7,28.5],[109.8,29.8],[108.3,31],[106,32.8],[104.5,34.5],[102.5,36]]},
{n:"Cina: ultimi mesi",from:"1949-09",to:"1949-11",k:"front",src:F2,d:"Canton cade a ottobre, il 1° ottobre Mao proclama la Repubblica. Chongqing cade a fine novembre.",p:[[118.1,24.5],[116.7,23.4],[114.2,22.5],[112,22.5],[110.3,22.7],[108.5,24],[107,25.5],[105.5,28],[104.5,30.5],[103.3,32.4],[101,34],[97,36]]},
{n:"Cina: Hainan",from:"1949-12",to:"1950-05",k:"front",src:F2,d:"Ultimo fronte continentale: Chengdu cade a dicembre, Hainan è presa ad aprile-maggio 1950.",p:[[109.7,20.3],[110.4,20.15],[111,20]]},
/* Algeria */
{n:"Linea Morice",from:"1957-09",to:"1962-03",k:"line",src:F2,d:"Barriera francese elettrificata sul confine tunisino, da Bona a Negrine, per fermare i rifornimenti dell'FLN.",p:[[7.77,36.9],[7.8,36.5],[7.95,36.28],[8,35.8],[8.12,35.4],[7.9,35],[7.5,34.5]]},
{n:"Linea Challe",from:"1959-04",to:"1962-03",k:"line",src:F2,d:"Seconda barriera, più vicina al confine tunisino.",p:[[8.42,36.95],[8.3,36.4],[8.3,35.7],[8.3,35.2],[8,34.7]]},
{n:"Linea Pédron",from:"1957-06",to:"1962-03",k:"line",src:F2,d:"Barriera sul confine marocchino.",p:[[-2.15,35.1],[-1.9,34.65],[-1.75,34],[-1.7,33.3],[-1.9,32.7]]},
{n:"Battaglia di Algeri",from:"1957-01",to:"1957-10",k:"front",src:F2,d:"Non c'è un fronte: l'FLN combatte nelle città e nei massicci, Aurès e Cabilia.",p:[[3.3,36.55],[4.5,36.6],[5.7,36.5],[6.5,35.5],[6.9,35]]},
/* Ogaden */
{n:"Ogaden: invasione somala",from:"1977-07",to:"1977-08",k:"front",src:F2,d:"La Somalia di Siad Barre entra in Etiopia il 13 luglio e prende gran parte dell'Ogaden.",p:[[47.9,8],[45.2,6.5],[43.5,5],[42.4,4.5],[41.3,5.6],[41.5,7],[42,8.2],[43,9.1]]},
{n:"Ogaden: massima avanzata",from:"1977-09",to:"1978-01",k:"front",src:F2,d:"Jijiga cade a settembre; la Somalia si ferma davanti a Harar e Dire Dawa, tenute con armi sovietiche e truppe cubane.",p:[[40.8,8],[41.5,9],[41.9,9.5],[42.2,9.2],[42.5,9.5],[43.2,9.9],[43.6,10.3]]},
{n:"Ogaden: controffensiva",from:"1978-02",to:"1978-03",k:"front",src:F2,d:"Etiopi e cubani riprendono Jijiga il 5 marzo, ritiro somalo annunciato il 9.",p:[[42,7.5],[42.9,8.4],[43.5,9],[44,9.2],[45.2,8.5],[47.5,7.9]]},
/* Guerra del 1948 */
{n:"Israele: maggio-giugno 1948",from:"1948-05",to:"1948-06",k:"front",src:F2,d:"Invasione araba del 15 maggio. Gli egiziani arrivano a Isdud, siriani e iracheni a nord, la Legione araba a Latrun e nella Gerusalemme vecchia.",p:[[35.1,33.08],[35.35,33.03],[35.6,32.85],[35.5,32.6],[35.3,32.45],[35,32.45],[34.97,32.15],[34.98,31.85],[35.2,31.78],[34.85,31.72],[34.65,31.8]]},
{n:"Israele: luglio-ottobre 1948",from:"1948-07",to:"1948-10",k:"front",src:F2,d:"Le tregue dell'ONU e i Dieci giorni: Israele prende Lydda, Ramle e Nazareth. Il corridoio del Negev è ancora tagliato.",p:[[35.1,33.08],[35.55,33.2],[35.6,32.75],[35.3,32.45],[35.05,32.35],[34.97,32],[35,31.8],[35.2,31.78],[34.9,31.65],[34.65,31.75],[34.75,31.3],[34.5,31.3]]},
{n:"Israele: Negev",from:"1948-11",to:"1949-03",k:"front",src:F2,d:"Operazioni Yoav, Horev e Uvda: Israele prende Beersheba e arriva a Umm Rashrash, poi Eilat, il 10 marzo 1949. Gaza resta all'Egitto.",p:[[34.5,31.55],[34.25,31.3],[34.3,30.95],[34.5,30.5],[34.9,29.55],[35.2,30.3],[35.4,31],[35.1,31.35]]},
/* Suez */
{n:"Suez: avanzata israeliana",from:"1956-10",to:"1956-11",k:"front",src:F2,d:"Israele occupa il Sinai fino a 16 km dal Canale; paracadutisti al passo di Mitla, poi Sharm el-Sheikh. Anglo-francesi a Port Said.",p:[[32.55,31.2],[32.7,30.75],[32.75,30.3],[32.85,29.95],[33.2,29.4],[33.9,28.1],[34.3,27.8]]},
{n:"Suez: ritiro israeliano",from:"1956-12",to:"1957-03",k:"line",src:F2,d:"Ritiro a tappe, l'ONU schiera l'UNEF. Completato a marzo 1957.",p:[[33.8,31.1],[33.75,30.5],[33.7,29.9],[34.1,29]]},
/* Sei giorni e logoramento */
{n:"Canale di Suez",from:"1967-06",to:"1973-09",k:"line",src:"OpenStreetMap, tracciato del canale",d:"Fronte tra Israele ed Egitto dopo la guerra dei Sei giorni, con la linea Bar-Lev. Guerra d'attrito 1967-70.",geo:"suez"},
{n:"Alture del Golan",from:"1967-06",to:"1973-09",k:"line",src:"Natural Earth, linea di fatto",d:"Linea viola del cessate il fuoco tra Israele e Siria.",geo:"golan"},
/* Kippur */
{n:"Kippur: testa di ponte egiziana",from:"1973-10",to:"1973-10",k:"front",src:F2,d:"Dal 6 ottobre gli egiziani passano il Canale e tengono una fascia di 10-15 km.",p:[[32.5,31.2],[32.55,30.95],[32.62,30.65],[32.7,30.4],[32.72,30.15],[32.65,29.97]]},
{n:"Kippur: sacca israeliana",from:"1973-10",to:"1974-01",k:"front",src:F2,d:"Dal 15 ottobre Israele passa a Deversoir e arriva a 100 km dal Cairo, circondando la Terza Armata.",p:[[32.32,30.42],[32.1,30.4],[32,30.25],[32.05,30.05],[32.35,29.92],[32.55,29.95]]},
{n:"Kippur: Golan, saliente di Sasa",from:"1973-10",to:"1974-05",k:"front",src:F2,d:"Israele respinge i siriani e crea un saliente verso Damasco, a circa 40 km dalla città.",p:[[35.75,33.3],[35.92,33.35],[36.05,33.3],[36.15,33.15],[36,33.03],[35.9,32.85],[35.8,32.7]]},
{n:"Sinai: primo disimpegno",from:"1974-02",to:"1975-08",k:"line",src:F2,d:"Israele arretra di circa 20 km dal Canale.",p:[[33,31.05],[32.85,30.6],[32.82,30.2],[32.9,29.9]]},
{n:"Sinai: secondo disimpegno",from:"1975-09",to:"1979-12",k:"line",src:F2,d:"Sinai II: Israele lascia i passi di Mitla e Giddi.",p:[[33.15,31.1],[33.15,30.6],[33.1,30.1],[33.05,29.6]]},
{n:"Sinai: ritiro finale",from:"1980-01",to:"1982-04",k:"line",src:F2,d:"Dopo il trattato del 1979 Israele arretra alla linea El-Arish-Ras Muhammad, poi al confine il 25 aprile 1982.",p:[[33.8,31.15],[33.9,30.4],[34.1,29.5],[34.25,27.75]]},
/* Libano */
{n:"Libano: operazione Litani",from:"1978-03",to:"1978-06",k:"front",src:F2,d:"Israele occupa il sud fino al fiume Litani, arriva l'UNIFIL.",p:[[35.25,33.33],[35.47,33.34],[35.6,33.35],[35.7,33.35]]},
{n:"Libano: invasione del 1982",from:"1982-06",to:"1982-09",k:"front",src:F2,d:"Pace in Galilea: dal 6 giugno Israele arriva a Beirut, assediata fino ad agosto, e sulla strada Beirut-Damasco.",p:[[35.48,33.9],[35.6,33.83],[35.73,33.75],[35.8,33.55],[35.85,33.45]]},
{n:"Libano: linea dell'Awali",from:"1983-09",to:"1985-05",k:"line",src:F2,d:"Israele arretra sul fiume Awali, prima del ritiro nella fascia di sicurezza.",p:[[35.37,33.58],[35.5,33.6],[35.65,33.55],[35.8,33.45]]}
);

window.CONFLICTS.push(
{n:"Occupazione dell'Iran",from:"1945-01",to:"1946-05",at:[51.4,35.7],d:"Sovietici al nord e britannici al sud dal 1941. I sovietici restano oltre la scadenza: è la prima crisi della Guerra Fredda all'ONU."},
{n:"Settima Flotta nello Stretto",from:"1950-06",to:"1950-07",at:[119.6,24.3],d:"Truman schiera la flotta tra Cina e Taiwan allo scoppio della guerra di Corea."},
{n:"Prima crisi dello Stretto: Quemoy",from:"1954-09",to:"1955-05",at:[118.35,24.45],d:"La Cina bombarda Quemoy e Matsu. Gli USA firmano il trattato con Taiwan e minacciano l'atomica."},
{n:"Yijiangshan e Dachen",from:"1955-01",to:"1955-02",at:[121.93,28.45],d:"La Cina prende Yijiangshan, i nazionalisti lasciano le Dachen con la flotta USA."},
{n:"Seconda crisi dello Stretto: Quemoy",from:"1958-08",to:"1958-12",at:[118.35,24.45],d:"Bombardamento di Quemoy dal 23 agosto, convogli di rifornimento con la scorta USA."},
{n:"Occupazione delle Falkland",from:"1982-04",to:"1982-06",at:[-58.7,-51.7],d:"L'Argentina sbarca il 2 aprile, si arrende a Port Stanley il 14 giugno."}
);
window.EVENT_LOG.push(["1946-03","L'URSS non lascia l'Iran alla scadenza: crisi all'ONU."],["1954-09","Prima crisi dello Stretto di Taiwan."],["1958-08","Seconda crisi dello Stretto di Taiwan."],["1982-04","L'Argentina occupa le Falkland."],["1982-06","Resa argentina a Port Stanley."]);
/* Chiusure mancanti: basi che risultavano aperte oltre il 1991 */
window.BASE_END = {"Karlshorst":"1953-01","Milovice":"1991-06","Mátyásföld":"1991-06","Chinatown, Henoko":"1972-05"};
