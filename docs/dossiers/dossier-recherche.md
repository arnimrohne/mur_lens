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
- Vor dem Push muss `dossiers.json` gültiges JSON sein. Die Website verwirft
  Dossiers mit ungültiger ID oder Rubrik stillschweigend.
