# Guida passo passo: come aprire e scaricare l'Atlante della Guerra Fredda

Questa guida è per chi non ha mai usato GitHub. Non serve installare niente e non serve un account GitHub.

Ci sono due modi per usare la carta:

1. **Aprirla online**: è il modo più semplice, basta un clic.
2. **Scaricarla sul computer**: utile se vuoi tenerne una copia tua.

---

## Modo 1 – Aprirla online (consigliato)

1. Apri questo indirizzo nel browser (Chrome, Edge, Firefox o Safari):

   **https://pietrolampani.github.io/cold-war-atlas/**

2. Aspetta qualche secondo che la carta si carichi.
3. Fatto. Puoi aggiungerla ai preferiti per ritrovarla.

---

## Modo 2 – Scaricarla sul computer

### Passo 1: apri la pagina del progetto

Vai a **https://github.com/pietrolampani/cold-war-atlas**

Vedrai un elenco di file e cartelle. Non serve aprirli uno per uno: li scarichi tutti insieme.

### Passo 2: scarica il file ZIP

1. In alto a destra, sopra l'elenco dei file, c'è un **pulsante verde** con scritto **`<> Code`**. Cliccalo.
2. Si apre un piccolo menu. In fondo clicca **Download ZIP**.
3. Il browser scarica un file chiamato **`cold-war-atlas-main.zip`** (circa 15 MB), di solito nella cartella **Download**.

### Passo 3: estrai il file ZIP

Il file ZIP è un "pacchetto" compresso: va aperto ed estratto prima di usarlo.

**Su Windows**

1. Apri la cartella **Download**.
2. Clicca con il **tasto destro** su `cold-war-atlas-main.zip`.
3. Scegli **Estrai tutto…**, poi **Estrai**.
4. Si apre una nuova cartella chiamata `cold-war-atlas-main`.

**Su Mac**

1. Apri la cartella **Download**.
2. Fai **doppio clic** su `cold-war-atlas-main.zip`.
3. Accanto compare la cartella `cold-war-atlas-main`.

> ⚠️ Non aprire i file direttamente da dentro lo ZIP senza estrarlo: la carta non si caricherebbe.

### Passo 4: apri la carta

1. Entra nella cartella `cold-war-atlas-main`.
2. Fai **doppio clic** sul file **`index.html`**.
   Su Windows potrebbe chiamarsi solo `index`, con l'icona del browser.
3. La carta si apre nel browser.

Se il doppio clic apre un altro programma, ad esempio un editor di testo:
clicca con il **tasto destro** su `index.html` → **Apri con** → scegli **Chrome**, **Edge** o **Firefox**.

> 🌐 Serve comunque una **connessione a Internet**: la pagina scarica alcuni componenti (la libreria che disegna la carta e i
> caratteri tipografici) da Internet ogni volta che si apre.

### Passo 5 (facoltativo): spostala dove preferisci

Puoi spostare l'intera cartella `cold-war-atlas-main` dove vuoi, ad esempio sul Desktop o in Documenti.
Tieni sempre **tutti i file insieme nella stessa cartella**: `index.html` da solo non basta.

---

## Come si usa la carta

- **Scorrere il tempo**: usa i pulsanti **‹** e **›** sotto la carta per andare indietro o avanti di un mese, oppure
  trascina il cursore rosso sulla linea del tempo (o cliccaci sopra) per saltare a un anno.
- **Animazione**: il pulsante **▶ Play** fa scorrere i mesi da solo; accanto scegli la velocità (ad esempio "6 mesi/s").
- **Ingrandire**: usa la rotellina del mouse, i pulsanti **+** e **−** in alto a destra, oppure due dita sul touchpad o sul
  telefono. Il pulsante **⌂** torna alla vista del mondo.
- **Spostarsi**: tieni premuto il mouse sulla carta e trascina.
- **Informazioni**: passa sopra uno Stato, una zona o un simbolo per vedere il nome; **clicca** per aprire la scheda con i
  dettagli nel pannello a destra (sul telefono, sotto la carta).
- **Vai a**: nel pannello a destra ci sono scorciatoie per luoghi particolari (Muro di Berlino, Checkpoint Charlie, Gibilterra…).
- **Berlino**: ingrandendo molto su Berlino compaiono il Muro, i settori, i valichi e gli edifici.

---

## Problemi frequenti

| Problema | Cosa fare |
|---|---|
| La pagina resta bianca o vuota | Controlla di avere Internet. Controlla di aver **estratto** lo ZIP (Passo 3) e di aprire `index.html` dalla cartella estratta. |
| Si apre un editor con tanto testo | Hai aperto il file con il programma sbagliato: tasto destro → **Apri con** → il tuo browser. |
| La carta è lenta | È normale al primo avvio e con gli ingrandimenti forti: i dati sono tanti. Chiudi altre schede del browser. |
| Mancano le foto dei leader | È voluto: le foto non sono incluse per ragioni di licenza. Le schede hanno comunque nome e link a Wikipedia. |
| Ho scaricato una versione vecchia | Ripeti il **Passo 2** per scaricare lo ZIP aggiornato e sostituisci la cartella. |

---

## Per chi è un po' più esperto (facoltativo)

Se preferisci aprire la carta tramite un piccolo server locale, con il comportamento identico a quello online:

1. Installa **Python** da https://www.python.org/downloads/ (su Windows spunta "Add Python to PATH" durante l'installazione).
2. Apri il terminale nella cartella `cold-war-atlas-main`.
   Su Windows: apri la cartella, clicca sulla barra dell'indirizzo, scrivi `cmd` e premi Invio.
3. Scrivi questo comando e premi Invio:

   ```
   python -m http.server 8000
   ```

4. Apri nel browser **http://localhost:8000**
5. Per fermare il server, torna al terminale e premi **Ctrl + C**.

Se usi `git`, puoi anche clonare il progetto:

```
git clone https://github.com/pietrolampani/cold-war-atlas.git
```
