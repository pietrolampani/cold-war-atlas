/* Microstati e possedimenti minori assenti in CShapes. Contorni da Natural Earth; date e campi da memoria, non verificati. */
Object.assign(window.ALIGN, {
3903:"Grenada|1945-09 c Colonia britannica|1974-02 u Indipendenza|1979-03 s Rivoluzione di Bishop, vicina a Cuba|1983-10 u Invasione USA",
3904:"Saint Lucia|1945-09 c Colonia britannica|1979-02 u Indipendenza",
3905:"Saint Vincent|1945-09 c Colonia britannica|1979-10 u Indipendenza",
3906:"Dominica|1945-09 c Colonia britannica|1978-11 u Indipendenza",
3907:"Antigua e Barbuda|1945-09 c Colonia britannica|1981-11 u Indipendenza",
3908:"Saint Kitts e Nevis|1945-09 c Colonia britannica|1983-09 u Indipendenza",
3909:"Seychelles|1945-09 c Colonia britannica|1976-06 N Indipendenza",
3910:"São Tomé e Príncipe|1945-09 c Colonia portoghese|1975-07 s Indipendenza",
3911:"Samoa|1945-09 c Amministrazione neozelandese|1962-01 u Indipendenza",
3912:"Tonga|1945-09 c Protettorato britannico|1970-06 u Indipendenza",
3913:"Vanuatu|1945-09 c Nuove Ebridi, condominio anglo-francese|1980-07 N Indipendenza",
3914:"Kiribati|1945-09 c Isole Gilbert, britanniche|1979-07 u Indipendenza",
3915:"Tuvalu|1945-09 c Isole Ellice, britanniche|1978-10 u Indipendenza",
3916:"Nauru|1945-09 c Amministrazione australiana|1968-01 u Indipendenza",
3917:"Isole Marshall|1945-09 c Amministrazione USA|1986-10 U Libera associazione con gli USA",
3918:"Micronesia|1945-09 c Amministrazione USA|1986-11 U Libera associazione con gli USA",
3919:"Palau|1945-09 c Amministrazione USA",
3920:"Monaco|1945-09 N Principato",
3921:"Liechtenstein|1945-09 N Principato",
3922:"San Marino|1945-09 N Repubblica",
3923:"Andorra|1945-09 N Principato",
3924:"Macao|1945-09 c Colonia portoghese",
3925:"Hong Kong|1945-09 c Colonia britannica",
3926:"Bermuda|1945-09 c Colonia britannica",
3927:"Isole Cayman|1945-09 c Colonia britannica",
3928:"Turks e Caicos|1945-09 c Colonia britannica",
3929:"Isole Vergini britanniche|1945-09 c Colonia britannica",
3930:"Isole Vergini americane|1945-09 U Territorio USA",
3931:"Guam|1945-09 U Territorio USA",
3932:"Samoa americane|1945-09 U Territorio USA",
3933:"Marianne Settentrionali|1945-09 c Amministrazione USA",
3934:"Isole Cook|1945-09 c Amministrazione neozelandese",
3935:"Niue|1945-09 c Amministrazione neozelandese",
3936:"Sant'Elena|1945-09 c Colonia britannica",
3937:"Anguilla|1945-09 c Colonia britannica",
3938:"Montserrat|1945-09 c Colonia britannica",
3939:"Aruba e Antille olandesi|1945-09 c Colonia olandese",
3940:"Isole Fær Øer|1945-09 u Territorio danese",
});
window.EMPIRES.nz = { n: "Amministrazione neozelandese", color: "#4a7f6a", rot: 45 };
Object.assign(window.COLONIAL, {
3903:"uk|Grenada",3904:"uk|Saint Lucia",3905:"uk|Saint Vincent",3906:"uk|Dominica",3907:"uk|Antigua",3908:"uk|Saint Kitts",3909:"uk|Seychelles",3910:"pt|São Tomé e Príncipe",3911:"nz|Samoa",3912:"uk|Tonga",3913:"uk|Nuove Ebridi",3914:"uk|Isole Gilbert",3915:"uk|Isole Ellice",3916:"au|Nauru",3917:"us|Territorio del Pacifico",3918:"us|Territorio del Pacifico",3919:"us|Territorio del Pacifico",3924:"pt|Macao",3925:"uk|Hong Kong",3926:"uk|Bermuda",3927:"uk|Isole Cayman",3928:"uk|Turks e Caicos",3929:"uk|Isole Vergini britanniche",3933:"us|Territorio del Pacifico",3934:"nz|Isole Cook",3935:"nz|Niue",3936:"uk|Sant'Elena",3937:"uk|Anguilla",3938:"uk|Montserrat",3939:"nl|Antille olandesi",
});
/* Capitali dei microstati, a memoria: [codice, da, a, nome, lat, lon] in mesi assoluti */
window.CAPITALS = window.CAPITALS.concat([
[3903,"St. George's",12.05,-61.75],[3904,"Castries",14.01,-60.99],[3905,"Kingstown",13.16,-61.22],[3906,"Roseau",15.3,-61.39],[3907,"Saint John's",17.12,-61.85],[3908,"Basseterre",17.3,-62.72],[3909,"Victoria",-4.62,55.45],[3910,"São Tomé",0.34,6.73],[3911,"Apia",-13.83,-171.76],[3912,"Nuku'alofa",-21.14,-175.2],[3913,"Port Vila",-17.74,168.32],[3914,"Tarawa",1.33,173],[3915,"Funafuti",-8.52,179.2],[3916,"Yaren",-0.55,166.92],[3917,"Majuro",7.09,171.38],[3918,"Palikir",6.92,158.16],[3920,"Monaco",43.73,7.42],[3921,"Vaduz",47.14,9.52],[3922,"San Marino",43.94,12.46],[3923,"Andorra la Vella",42.51,1.52],
].map(function (r) { return [r[0], 1945 * 12, 1991 * 12 + 11, r[1], r[2], r[3]]; }));

/* Fronti europei del 1945, più fitti: tracciati a mano da memoria tra città e fiumi. Sostituiscono i precedenti. */
window.LINES_WW2 = function () {
  var W = "Ricostruzione a mano da memoria tra città e fiumi, situazione a fine mese";
  window.LINES = window.LINES.filter(function (l) { return ["Fronte orientale", "Fronte occidentale", "Linea Gotica", "Italia: offensiva finale"].indexOf(l.n) < 0; });
  window.LINES.push(
  {n:"Fronte orientale",from:"1945-01",to:"1945-01",k:"front",src:W,d:"Vistola-Oder: dal 12 gennaio i sovietici sfondano. A fine mese sono sull'Oder a Küstrin, Breslavia è minacciata, la Prussia Orientale è isolata a Tolkemit. Budapest è ancora assediata.",p:[[19.55,54.33],[19.4,54.15],[18.8,53.75],[18.77,53.49],[17.9,53.35],[17,53.3],[16.4,53.25],[15.9,53.05],[15.1,52.8],[14.62,52.59],[14.55,52.35],[14.66,52.14],[15.1,52],[15.5,51.94],[16.09,51.75],[16.43,51.4],[16.95,51.2],[17.45,50.95],[17.93,50.67],[18.22,50.09],[18.65,49.95],[19.04,49.82],[19.5,49.6],[20.03,49.48],[20.6,49.15],[21.26,48.72],[20.8,48.3],[20.1,48.05],[19.67,47.67],[19.3,47.78],[18.95,47.8],[18.6,47.65],[18.3,47.35],[18.1,47.05],[17.75,46.55],[17.7,45.97],[18.2,45.75],[18.95,45.45],[19.3,44.95],[19.2,44.4],[19.35,43.9],[18.9,43.3]]},
  {n:"Fronte orientale",from:"1945-02",to:"1945-02",k:"front",src:W,d:"Pomerania orientale e Slesia. Budapest cade il 13, Breslavia è assediata fino a maggio.",p:[[18.9,54.4],[18.2,54.3],[17.4,54.2],[16.8,54.05],[16.1,53.75],[15.3,53.4],[14.75,53.25],[14.62,52.6],[14.55,52.3],[14.7,51.85],[14.95,51.3],[15.3,51.1],[15.9,50.95],[16.6,50.85],[17.4,50.65],[18.1,50.25],[18.7,49.95],[19.3,49.6],[20.2,49.35],[20.3,49],[19.2,48.3],[19.05,47.9],[18.4,47.7],[18,47.4],[17.4,46.6],[17.7,46],[18.2,45.8],[19.2,45.2],[19.2,44.2],[18.9,43.5]]},
  {n:"Fronte orientale",from:"1945-03",to:"1945-03",k:"front",src:W,d:"I sovietici sul Baltico da Danzica a Stettino. Fallisce l'offensiva tedesca sul Balaton, si apre la via di Vienna.",p:[[14.5,53.95],[14.6,53.45],[14.42,53.3],[14.45,52.9],[14.62,52.6],[14.5,52.2],[14.7,51.7],[14.95,51.15],[15.8,50.95],[16.6,50.6],[17.6,50.25],[18.3,49.9],[19,49.5],[20,48.9],[19.2,48.4],[18.6,48.1],[17.5,47.75],[16.9,47.55],[16.5,46.95],[16.6,46.45],[17,45.9],[18,45.45],[18.6,45.2],[19.2,44.3],[18.6,43.8]]},
  {n:"Fronte orientale",from:"1945-04",to:"1945-04",k:"front",src:W,d:"Dal 16 aprile le alture di Seelow, Berlino accerchiata il 25. Sovietici e americani si incontrano a Torgau. Vienna è caduta il 13.",p:[[12.1,54.1],[13.1,54.05],[13.6,53.6],[13.3,53.15],[13.1,52.75],[12.95,52.4],[12.85,52],[13,51.55],[13.7,51.35],[14.3,50.95],[15,50.75],[16,50.45],[17,49.75],[17.3,49.3],[16.9,48.85],[16.55,48.5],[16,47.9],[15.8,47.45],[15.5,46.8],[16.2,46.3],[15.6,45.6],[14.9,45.1],[14.5,44.9]]},
  {n:"Fronte occidentale",from:"1945-01",to:"1945-01",k:"front",src:W,d:"Il saliente delle Ardenne è riassorbito: si torna alle linee di dicembre, sul Roer e la frontiera del Reich. Sacca di Colmar ancora tedesca.",p:[[3.4,51.4],[4.3,51.7],[5.1,51.72],[5.86,51.84],[6,51.3],[6.25,50.95],[6.48,50.8],[6.25,50.6],[6.13,50.28],[6.3,49.95],[6.5,49.5],[6.99,49.23],[7.6,49.05],[8.2,48.97],[7.8,48.55],[7.6,48.25],[7.36,48.05],[7.15,47.72]]},
  {n:"Fronte occidentale",from:"1945-02",to:"1945-02",k:"front",src:W,d:"Operazioni Veritable e Grenade: Foresta del Reichswald, gli Alleati verso il Reno, sacca di Colmar eliminata.",p:[[3.5,51.7],[4.7,51.8],[5.9,51.82],[6.4,51.75],[6.55,51.45],[6.7,51.1],[6.75,50.75],[6.5,50.25],[6.6,49.85],[6.75,49.4],[7.6,49.1],[8.2,48.95],[7.8,48.4],[7.6,47.95],[7.55,47.6]]},
  {n:"Fronte occidentale",from:"1945-03",to:"1945-03",k:"front",src:W,d:"Remagen il 7 marzo, Plunder il 23: il Reno è passato su tutto il fronte. Si chiude la sacca della Ruhr.",p:[[4.5,52.05],[5.9,51.95],[6.9,51.95],[7.6,51.95],[8.3,51.85],[8.9,51.3],[8.8,50.8],[9.1,50.3],[9.3,49.9],[9.1,49.4],[8.5,49.05],[8.1,48.95],[7.6,47.6]]},
  {n:"Fronte occidentale",from:"1945-04",to:"1945-04",k:"front",src:W,d:"Bremen e Amburgo sotto attacco, gli Alleati fermi sull'Elba e il Mulde. A sud Monaco cade il 30, verso il Brennero.",p:[[8.4,53.6],[8.8,53.1],[9.9,53.45],[10.8,53.15],[11.3,52.9],[11.9,52.6],[12.2,52.1],[12.5,51.6],[12.8,51.2],[12.9,50.8],[12.4,50.3],[12.7,49.7],[13.5,48.75],[13,48.2],[12.5,47.8],[11.4,47.3],[10.4,47.1],[9.6,47.45]]},
  {n:"Linea Gotica",from:"1945-01",to:"1945-03",k:"front",src:W,d:"Il fronte italiano è fermo dall'autunno, da Massa agli Appennini fino al Senio e alle valli di Comacchio.",p:[[10.1,44.02],[10.3,44.1],[10.6,44.15],[10.95,44.17],[11.25,44.25],[11.5,44.25],[11.75,44.3],[11.95,44.35],[12.1,44.55],[12.25,44.6]]}
  );
};
