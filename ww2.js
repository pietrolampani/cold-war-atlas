/* Le colonie asiatiche hanno stato di colonia: dove il Giappone le tiene lo dicono le tavole dell'Army Map Service (Occupato dal Giappone). */
/* Gennaio-agosto 1945, compilato a mano da memoria: non verificato su fonti.
   Stati: A Alleati, X Asse, O occupato dall'Asse, N neutrale, c colonia. Le righe si aggiungono prima di quelle del dopoguerra. */
window.ALIGN[255] = "Germania|1945-01 X Reich tedesco, si arrende l'8 maggio";
window.ALIGN[730] = "Corea|1945-01 c Colonia giapponese";
window.ALIGN[7351] = "Sachalin del Sud|1945-01 c Territorio giapponese, occupato dai sovietici in agosto";
var WW2 = {
260:"1945-01 X Reich tedesco|1945-05 u Zone di occupazione occidentali",265:"1945-01 X Reich tedesco|1945-05 s Zona di occupazione sovietica",
740:"1945-01 X Impero giapponese, si arrende il 15 agosto e firma il 2 settembre",800:"1945-01 X Alleata del Giappone",
305:"1945-01 X Annessa al Reich|1945-05 N Occupata dalle quattro potenze",310:"1945-01 s L'est è occupato dai sovietici, con il governo provvisorio di Debrecen; a ovest il governo Szálasi, alleato del Reich|1945-04 s Occupazione sovietica",
325:"1945-01 A Regno del Sud cobelligerante; al nord la Repubblica di Salò fino ad aprile",
290:"1945-01 s Il governo di Lublino sostenuto da Mosca tiene l'est; l'ovest è ancora tedesco fino a marzo|1945-05 s Governo sostenuto da Mosca",315:"1945-01 s L'est della Slovacchia e la Rutenia sono già sovietici; Boemia-Moravia e il resto della Slovacchia sotto il Reich|1945-05 s Liberata",
210:"1945-01 O Il nord è ancora occupato|1945-05 A Liberati",390:"1945-01 O Occupata dalla Germania|1945-05 A Liberata",385:"1945-01 O Occupata dalla Germania|1945-05 A Liberata",
345:"1945-01 A Partigiani di Tito; Croazia ustascia fino a maggio",339:"1945-01 s Regime di Hoxha",355:"1945-01 s Governo del Fronte patriottico, cambia campo nel 1944",360:"1945-01 s Cambia campo nell'agosto 1944",375:"1945-01 N Armistizio con l'URSS dal settembre 1944",
350:"1945-01 A Liberata nel 1944",235:"1945-01 N Neutrale",640:"1945-01 N Neutrale|1945-02 A Dichiara guerra alla Germania",160:"1945-01 N Neutrale|1945-03 A Dichiara guerra all'Asse",670:"1945-01 N Neutrale|1945-03 A Dichiara guerra all'Asse",651:"1945-01 N Non belligerante|1945-02 A Dichiara guerra all'Asse",
811:"1945-01 c Indocina francese sotto controllo giapponese",812:"1945-01 c Indocina francese sotto controllo giapponese",815:"1945-01 c Indocina francese sotto controllo giapponese; a marzo il colpo di mano giapponese",
850:"1945-01 c Indie olandesi occupate dal Giappone",821:"1945-01 c Occupata dal Giappone",822:"1945-01 c Occupata dal Giappone",827:"1945-01 c Occupata dal Giappone",823:"1945-01 c Occupato dal Giappone",824:"1945-01 c Occupato dal Giappone",835:"1945-01 c Occupato dal Giappone",860:"1945-01 c Occupato dal Giappone",
775:"1945-01 c Occupata dal Giappone|1945-05 c Rangoon ripresa dai britannici",840:"1945-01 c Occupate dal Giappone|1945-02 c Manila liberata, il territorio torna agli USA",713:"1945-01 c Formosa, colonia giapponese",
712:"1945-01 A Satellite sovietico, entra in guerra in agosto",710:"1945-01 A Governo nazionalista, in guerra col Giappone; il nord-est è il Manciukuò",700:"1945-01 N Neutrale",
};
for (var code in window.ALIGN) {
  var parts = window.ALIGN[code].split("|"), first = parts[1] || "";
  if (WW2[code]) { parts.splice(1, 0, WW2[code]); }
  else if (first.startsWith("1945-09")) {
    var st = first.split(" ")[1];
    if (st === "c" || st === "N") parts.splice(1, 0, "1945-01 " + first.slice(8));
    else parts.splice(1, 0, "1945-01 A Con gli Alleati");
  }
  window.ALIGN[code] = parts.join("|");
}
window.EMPIRES.jp = { n: "Impero giapponese", color: "#6a4a3a", rot: 0 };
window.COLONIAL[730] = "jp|Corea"; window.COLONIAL[7351] = "jp|Sachalin del Sud"; window.COLONIAL[713] = "jp|Formosa";

/* Fronti di fine mese, tracciati a mano */
var W2 = "Ricostruzione a mano da memoria, situazione a fine mese";
window.LINES.push(
{n:"Fronte orientale",from:"1945-01",to:"1945-01",k:"front",src:W2,d:"Offensiva Vistola-Oder: l'Armata Rossa raggiunge l'Oder a Küstrin e isola la Prussia Orientale.",p:[[19.4,54.3],[18,53.6],[16.4,53],[14.7,52.6],[14.8,51.9],[15.5,51.4],[17,50.9],[18.2,50.1],[19,49.7],[20,49],[19.2,48.3],[19.05,47.5],[18.2,47],[17.7,46.4],[18.2,45.8],[19,45.4],[19.4,44.9],[19.3,44]]},
{n:"Fronte orientale",from:"1945-02",to:"1945-02",k:"front",src:W2,d:"Pomerania e Slesia. Budapest cade il 13 febbraio.",p:[[18.9,54.4],[16.5,54.1],[15,53.3],[14.6,52.6],[14.7,51.9],[15,51.1],[16.5,50.9],[18.2,50.1],[19.3,49.6],[19.2,48.3],[19.05,47.9],[18,47.4],[17.4,46.6],[18.2,45.8],[19.2,45.2],[19.2,44.2]]},
{n:"Fronte orientale",from:"1945-03",to:"1945-03",k:"front",src:W2,d:"Il fronte è sull'Oder e sul Neisse. Fallisce l'offensiva tedesca sul Balaton.",p:[[14.6,54],[14.6,53.4],[14.6,52.6],[14.7,51.6],[15,51],[16.5,50.6],[17.8,50.2],[19,49.5],[20,48.9],[18.6,48.1],[16.9,47.6],[16.5,46.9],[17,45.9],[18.6,45.2],[19.2,44.3]]},
{n:"Fronte orientale",from:"1945-04",to:"1945-04",k:"front",src:W2,d:"Berlino accerchiata. Sovietici e americani si incontrano a Torgau il 25 aprile. Vienna cade il 13.",p:[[14,54],[13.5,53],[13,52.6],[12.9,52],[13,51.55],[14.3,50.9],[16,50.4],[17,49.6],[16.6,48.7],[15.9,47.7],[15.5,46.8],[16.5,46.2],[15.5,45.4],[14.5,44.9]]},
{n:"Sacca di Curlandia",from:"1945-01",to:"1945-05",k:"front",src:W2,d:"Il Gruppo d'armate tedesco resiste in Lettonia fino alla resa.",p:[[23.3,57.1],[23.2,56.85],[23.0,56.7],[22.6,56.62],[22.3,56.55],[21.9,56.45],[21.5,56.4],[21.15,56.35],[20.95,56.3]]},
{n:"Prussia Orientale",from:"1945-02",to:"1945-04",k:"front",src:W2,d:"Sacca di Heiligenbeil e assedio di Königsberg, che cade il 9 aprile.",p:[[20.1,54.8],[20.7,54.55],[20.5,54.3],[19.8,54.4]]},
{n:"Fronte occidentale",from:"1945-01",to:"1945-01",k:"front",src:W2,d:"Le Ardenne sono riassorbite: si torna alle posizioni di dicembre.",p:[[3.4,51.35],[4.7,51.7],[5.9,51.2],[6.1,50.7],[6.1,50],[6.7,49.3],[7.5,49],[8.2,49],[7.6,48.1],[7.1,47.6]]},
{n:"Fronte occidentale",from:"1945-02",to:"1945-02",k:"front",src:W2,d:"Operazioni Veritable e Grenade verso il Reno.",p:[[3.5,51.7],[4.7,51.8],[6,51.8],[6.6,51.3],[6.7,50.7],[6.5,50],[6.7,49.4],[7.6,49.1],[8.2,48.9],[7.6,47.9],[7.2,47.6]]},
{n:"Fronte occidentale",from:"1945-03",to:"1945-03",k:"front",src:W2,d:"Il Reno è passato a Remagen il 7 marzo e nell'operazione Plunder il 23.",p:[[4.5,52],[6,51.9],[6.9,51.7],[7.5,51.4],[7.4,50.7],[8.3,50.1],[8.4,49.4],[8.1,49],[7.6,47.6]]},
{n:"Fronte occidentale",from:"1945-04",to:"1945-04",k:"front",src:W2,d:"Sacca della Ruhr chiusa, gli Alleati fermi sull'Elba.",p:[[8,54],[9.9,53.5],[10.9,53],[11.9,52.6],[12.7,51.9],[13,51.5],[12.3,50.5],[12.7,49.7],[13.5,48.7],[12.9,48],[11.4,47.3],[10.1,47.4]]},
{n:"Linea Gotica",from:"1945-01",to:"1945-03",k:"front",src:W2,d:"Il fronte italiano è fermo dall'autunno tra Massa e Ravenna.",p:[[10.1,44],[10.6,44.1],[11,44.15],[11.4,44.2],[11.7,44.25],[12.2,44.45]]},
{n:"Birmania",from:"1945-01",to:"1945-02",k:"front",src:W2,d:"La XIV Armata avanza verso l'Irrawaddy.",p:[[93.5,20.3],[94.6,21.3],[95.4,22.2],[96.1,22.8],[97.6,23.7]]},
{n:"Birmania",from:"1945-03",to:"1945-04",k:"front",src:W2,d:"Mandalay presa il 20 marzo, corsa verso Rangoon.",p:[[94.3,18.5],[95.2,19.3],[96.1,19.6],[96.9,19.9],[97.6,20.8]]},
{n:"Fronte cinese",from:"1945-01",to:"1945-08",k:"line",src:W2,d:"Il Giappone tiene l'est della Cina e il corridoio verso l'Indocina.",p:[[113,37],[111.5,34.6],[113,32.5],[111.3,30.5],[112,27.5],[110,25],[107.5,22.3]]},
{n:"Luzon",from:"1945-01",to:"1945-02",k:"front",src:W2,d:"Sbarco nel golfo di Lingayen il 9 gennaio, Manila combattuta fino a marzo.",p:[[120.3,16],[120.8,15.2],[121.1,14.6]]},
{n:"Okinawa",from:"1945-04",to:"1945-06",k:"front",src:W2,d:"Linea di Shuri a sud dell'isola. La battaglia finisce il 22 giugno.",p:[[127.68,26.22],[127.74,26.24],[127.8,26.27]]},
);

window.BATTLES.push(
["Ardenne","1945-01","1945-01",50,5.7,"Ultima offensiva tedesca a occidente, respinta entro fine mese."],
["Vistola-Oder","1945-01","1945-02",52.2,19,"In tre settimane i sovietici percorrono 500 km."],
["Auschwitz","1945-01","1945-01",50.03,19.18,"Il campo è liberato il 27 gennaio."],
["Budapest","1945-01","1945-02",47.5,19.05,"Assedio concluso il 13 febbraio."],
["Manila","1945-02","1945-03",14.6,120.98,"Battaglia in città, oltre 100.000 civili morti."],
["Dresda","1945-02","1945-02",51.05,13.74,"Bombardamento alleato del 13-15 febbraio."],
["Iwo Jima","1945-02","1945-03",24.78,141.32,"Oltre 20.000 giapponesi morti, la bandiera sul Suribachi."],
["Remagen","1945-03","1945-03",50.58,7.25,"Gli americani prendono intatto il ponte sul Reno."],
["Tokyo","1945-03","1945-03",35.68,139.75,"Bombardamento incendiario del 9-10 marzo, circa 100.000 morti."],
["Lago Balaton","1945-03","1945-03",46.9,18,"Ultima offensiva tedesca a est, fermata."],
["Mandalay","1945-03","1945-03",21.97,96.08,"Vittoria decisiva di Slim in Birmania."],
["Königsberg","1945-04","1945-04",54.71,20.51,"La fortezza cade il 9 aprile."],
["Okinawa","1945-04","1945-06",26.3,127.8,"Ultima grande battaglia del Pacifico."],
["Sacca della Ruhr","1945-04","1945-04",51.45,7.4,"Oltre 300.000 tedeschi prigionieri."],
["Bologna","1945-04","1945-04",44.49,11.34,"Liberata il 21 aprile."],
["Berlino","1945-04","1945-05",52.52,13.4,"Hitler si uccide il 30 aprile, la città cade il 2 maggio."],
["Praga","1945-05","1945-05",50.08,14.42,"Insurrezione e arrivo dei sovietici, ultimi combattimenti in Europa."],
["Rangoon","1945-05","1945-05",16.8,96.15,"Presa dai britannici dal mare."],
["Hiroshima","1945-08","1945-08",34.39,132.45,"Prima bomba atomica usata in guerra, 6 agosto."],
["Nagasaki","1945-08","1945-08",32.77,129.87,"Seconda bomba, 9 agosto."],
["Manciuria","1945-08","1945-08",45,126,"L'Armata del Kwantung crolla in dieci giorni."]
);

window.EVENT_LOG.unshift(
["1945-01","Battaglia delle Ardenne vinta dagli Alleati. Offensiva Vistola-Oder. Liberata Auschwitz."],["1945-02","Conferenza di Jalta. Bombardamento di Dresda. Iwo Jima."],["1945-03","Il Reno è passato a Remagen. Bombardamento di Tokyo."],["1945-04","Muore Roosevelt. Liberazione in Italia, ucciso Mussolini. Hitler si suicida. Incontro sull'Elba."],["1945-05","Resa tedesca, 8 maggio: la guerra in Europa è finita."],["1945-06","Fine della battaglia di Okinawa. Firmata la Carta delle Nazioni Unite."],["1945-07","Trinity: primo test atomico. Conferenza di Potsdam. Attlee sostituisce Churchill."],["1945-08","Hiroshima e Nagasaki. L'URSS attacca il Giappone, che annuncia la resa."]
);
