/* Nei conflitti che hanno le zone occupate il fronte è il bordo tratteggiato delle zone: le linee tracciate a mano si tolgono.
   Il sentiero di Ho Chi Minh non è un fronte ma una via di rifornimento: tracciato più fitto, con i rami principali. */
(function () {
  var DROP = /^(Cina: |Vietnam: |Afghanistan: )/;
  var NAMES = ["Sentiero di Ho Chi Minh", "Fronte di Corea", "Linea Kansas"];
  window.LINES = window.LINES.filter(function (l) { return !DROP.test(l.n) && NAMES.indexOf(l.n) < 0; });
  var S = "Ricostruzione dalle carte del sistema logistico di Truong Son (Gruppo 559), semplificata";
  window.LINES.push(
    { n: "Sentiero di Ho Chi Minh", from: "1959-05", to: "1975-04", k: "route", src: S,
      d: "Asse principale: da Vinh al passo di Mu Gia, poi nel Laos per Tchepone, Saravane e Attopeu, nella Cambogia nord-orientale e fino alle basi della Zona C presso Tay Ninh. Nel 1959 è un sentiero a piedi, dal 1965 una rete di strade camionabili.",
      p: [[105.67, 18.33], [105.78, 17.68], [105.95, 17.35], [106.13, 17.0], [106.23, 16.68], [106.35, 16.3], [106.42, 15.9], [106.45, 15.72], [106.6, 15.3], [106.83, 14.81], [107.15, 14.55], [107.4, 14.3], [107.45, 13.9], [107.3, 13.4], [107.25, 12.85], [107.1, 12.3], [106.85, 11.85], [106.55, 11.45]] },
    { n: "Sentiero di Ho Chi Minh: passo di Ban Karai", from: "1965-01", to: "1973-01", k: "route", src: S, d: "Secondo ingresso nel Laos dal Quang Binh, molto bombardato dall'operazione Steel Tiger.",
      p: [[106.12, 17.6], [106.13, 17.2], [106.23, 16.68]] },
    { n: "Sentiero di Ho Chi Minh: valle di A Shau", from: "1966-01", to: "1975-04", k: "route", src: S, d: "Ramo verso la valle di A Shau e Hue.",
      p: [[106.45, 16.4], [106.8, 16.32], [107.05, 16.25], [107.3, 16.2]] },
    { n: "Sentiero di Ho Chi Minh: verso Khe Sanh", from: "1966-01", to: "1975-04", k: "route", src: S, d: "Ramo lungo la Route 9 verso Khe Sanh e la zona demilitarizzata.",
      p: [[106.23, 16.68], [106.5, 16.65], [106.73, 16.63], [106.85, 16.62]] },
    { n: "Sentiero di Sihanouk", from: "1966-01", to: "1970-03", k: "route", src: S, d: "Rifornimenti sbarcati a Sihanoukville e portati in camion fino al confine vietnamita, finché il colpo di stato di Lon Nol (marzo 1970) chiude il porto.",
      p: [[103.52, 10.63], [104.2, 11.0], [104.9, 11.5], [105.6, 11.4], [106.0, 11.1]] }
  );
})();
