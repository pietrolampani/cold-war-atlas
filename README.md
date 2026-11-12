# Atlante della Guerra Fredda

Carta interattiva del mondo dal gennaio 1945 al dicembre 1991, mese per mese, con i confini dell'epoca: schieramenti,
imperi coloniali, occupazioni, fronti dei conflitti, basi, test nucleari, leader ed elezioni. Si ingrandisce fino al
dettaglio di Berlino (Muro, settori, valichi).

**Aprila online: https://pietrolampani.github.io/cold-war-atlas/**

Non sei pratico di GitHub? Leggi la **[guida passo passo per aprirla e scaricarla](GUIDA.md)**.

In locale basta aprire `index.html` dalla cartella estratta (serve Internet per D3 e i caratteri), oppure servirla via HTTP:

```
python -m http.server 8765
```

## Cosa c'è

- `index.html` – la pagina (HTML, CSS e JavaScript, con D3 e TopoJSON da CDN).
- `*.js` – i dati: confini (`borders*.js`), territori e occupazioni (`territories.js`, `occupation.js`), fronti
  (`fronts*.js`, `lines*.js`), conflitti (`vietnam.js`, `chinawar.js`, `afghanistan.js`, `ogaden.js`, `sands.js`, …),
  leader, elezioni, test nucleari, acque, coste OSM a tasselli (`land/`), dettaglio di Berlino (`detail.js`).
- `tools/` – gli script Python che hanno generato i dati (scaricamento, unione e semplificazione dei poligoni,
  ricostruzioni da video, ecc.).

Le foto dei leader non sono nel repository: hanno licenze Wikimedia miste. La pagina funziona senza.

## Fonti e licenze dei dati

- Confini storici: [CShapes 2.0](https://icr.ethz.ch/data/cshapes/), CC BY-NC-SA 4.0 (uso non commerciale).
- Muro, acque, edifici, coste di dettaglio, Länder, distretti e quartieri: © [OpenStreetMap](https://www.openstreetmap.org/copyright)
  contributors, ODbL.
- Zone di occupazione e Berlino Ovest: [OpenHistoricalMap](https://www.openhistoricalmap.org/), CC0.
- Coste, laghi, fiumi e confini moderni: [Natural Earth](https://www.naturalearthdata.com/), pubblico dominio.
- Test nucleari: SIPRI tramite Tidy Tuesday. Elezioni: ParlGov. Leader: Wikidata e Archigos 4.1.

Schieramenti, fronti, basi ed eventi sono una compilazione non verificata; alcune ricostruzioni (zone dei conflitti,
fronti del 1945 nel Pacifico, linee interne della Stiria nel 1945) sono approssimate e dichiarate nelle schede della carta.
