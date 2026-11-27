# Auftrag: Dossier-Recherche (Sonnet)

Dieser Lauf wird gestartet, wenn in `dossiers.json` (Branch `zeitung-daten`) ein
Eintrag unter `vorschlaege` steht. Er arbeitet genau **einen** Vorschlag aus,
schreibt ihn als Dossier nach `dossiers` und entfernt den Vorschlag. Danach
committet und pusht er nur auf `zeitung-daten`.

## Format
Maßgeblich ist das Wasserversorgungs-Dossier als Vorlage. Pflichtfelder:
`id`, `rubrik`, `stand`, `titel`, `kurz`. Optionale Felder: `warum`,
`entwicklung`, `chronik`, `akteure`, `zahlen`, `grafiken` (Format wie
`update.grafik`: 2–5 Balken), `offen`, `themen`, `stichworte`, `quellen`.
Alle Texte gibt es in DE, FR und EN; Absätze werden durch eine Leerzeile
getrennt.

## Bild
- Suche über die Commons-API, immer mit User-Agent "GazetMorisyen/1.0 (https://gazet.morisyen.de)", höchstens 5 API-Aufrufe pro Lauf; bei HTTP 429 eine Minute warten und es einmal erneut versuchen, sonst ohne Bild weitermachen:
  curl -s -A "GazetMorisyen/1.0 (https://gazet.morisyen.de)" "https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=<Suchbegriff>&gsrnamespace=6&gsrlimit=15&prop=imageinfo&iiprop=extmetadata|size|url&iiurlwidth=1920&iiextmetadatafilter=LicenseShortName|LicenseUrl|Artist|ImageDescription&format=json"
- Erlaubt sind nur die Lizenzen CC0, Public domain (PD-…), CC BY x.0 und CC BY-SA x.0. Nicht erlaubt sind NC-, ND- und GFDL-only-Lizenzen und alles ohne klare Lizenz.
- Keine erkennbaren Privatpersonen im Vordergrund, keine Logos und keine Werbung. Mindestens 1280 Pixel breit, Querformat.
- Lade die Datei über die thumburl (1920 Pixel, Host thumb.wikimedia.org) herunter. Speichere sie mit Pillow als JPEG (quality 82, höchstens 1920 Pixel breit) unter `bilder/<dossier-id>.jpg` im Branch zeitung-daten und committe sie mit `git add bilder/<dossier-id>.jpg dossiers.json`.
- Feld im Dossier:
  "bild": {"src": "https://raw.githubusercontent.com/arnimrohne/mur_lens/zeitung-daten/bilder/<dossier-id>.jpg", "breite": <px>, "hoehe": <px>,
           "alt": {"de","fr","en"} (sachliche Beschreibung, was zu sehen ist), "urheber": Artist ohne HTML,
           "seite": "https://commons.wikimedia.org/wiki/File:…" (descriptionurl), "lizenz": LicenseShortName, "lizenzUrl": LicenseUrl}
- Das Bild wird nicht beschnitten oder bearbeitet, nur verkleinert. Ohne passendes freies Bild bleibt "bild" weg.
- Bestehende Dossiers ohne Bild bekommen bei der nächsten Aktualisierung eines.

## Regeln
- Jede Zahl, jedes Datum und jede Position braucht eine `quelle` (https-URL),
  die der Lauf selbst aufgerufen hat. Was sich nicht belegen lässt, bleibt weg.
- Vorrang haben Primärquellen (Ministerien, Statistics Mauritius, NAO,
  Bank of Mauritius, Jahresberichte). Danach kommen etablierte Medien
  (L'Express, Le Mauricien, Defimedia, ION News, Mauritius Times).
- Die Darstellung bleibt neutral. Unter „Wer will was“ steht jede Seite mit
  ihrer eigenen, belegten Position, ohne Wertung.
- `kurz` umfasst höchstens 3 Sätze. `warum` und `entwicklung` haben je 2–4
  Absätze. Die `chronik` hat 4–10 Einträge mit `datum` (DE) und `datumI18n`
  (FR/EN).
- `offen` enthält echte offene Fragen, keine rhetorischen.
- `themen` nennt die passenden Themen-IDs aus `daten.json`.
- `stand` ist der Zeitpunkt des Laufs. Bestehende Dossiers werden
  aktualisiert, wenn eine neue Meldung den Stand verändert (neuer Chronik-Eintrag,
  neue Zahl).
- Bei wiederkehrenden Themen (`rhythmus` gesetzt) gehört in die `chronik` jede
  Runde der letzten Jahre mit dem Kernwert (z. B. Lohnausgleich 2022–2026 in Rupien
  oder Prozent). Eine passende `grafik` zeigt die Werte im Jahresvergleich.
  Unter `offen` steht, was bei der nächsten Runde ansteht und wann.
- Vor dem Push muss `dossiers.json` gültiges JSON sein. Die Website verwirft
  Dossiers mit ungültiger ID oder Rubrik stillschweigend.
