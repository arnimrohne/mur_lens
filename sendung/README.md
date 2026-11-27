# Nachrichtensendung (MVP)

`erzeuge_sendung.py` macht aus `daten.json` (Branch `zeitung-daten`) täglich drei Videos:
Deutsch, Französisch, Englisch, je 1920×1080. Dazu gibt es pro Sprache ein Vorschaubild
und eine Textdatei mit Titel, Beschreibung (Kapitel und Quellen) und Tags für YouTube.

- **Inhalt:** Themen mit Meldung in den letzten 24 Stunden, Top-Themen zuerst, höchstens 8.
- **Bild:** Standbild-Folien in der Farbwelt der Website, mit GM-Logo und Flaggenstreifen.
  Keine Fotos oder Grafiken aus den Quellen.
- **Ton:** Piper TTS, frei nutzbare Stimmen. Die Namensnennung steht in jeder Videobeschreibung.
  Die Aussprache schwieriger Wörter (Orte, Abkürzungen, Beträge, Uhrzeiten) regelt `aussprache.json`.
  Dort können weitere Wörter ergänzt werden.
  - Deutsch: Thorsten (CC0)
  - Französisch: SIWIS (CC BY 4.0)
  - Englisch: Cori (gemeinfrei)
- **Schriften:** Bricolage Grotesque, Source Serif 4 und IBM Plex Mono, alle unter OFL (siehe `schriften/`).

## Ablauf

Der Workflow `.github/workflows/sendung.yml` läuft täglich um 05:20 UTC (09:20 Uhr Mauritius).
Man kann ihn auch von Hand starten: GitHub → Actions → „Nachrichtensendung“ → *Run workflow*.
Das Ergebnis liegt 14 Tage als Artefakt `sendung-JJJJ-MM-TT` (ZIP) am Lauf.

## Hochladen auf YouTube (vorerst von Hand)

1. Das Artefakt herunterladen und entpacken.
2. Studio → Erstellen → Video hochladen: die `.mp4` der Sprache wählen.
3. Titel, Beschreibung und Tags aus der `-youtube.txt` übernehmen.
4. Die `-vorschau.png` als Thumbnail setzen.
5. Bei „Veränderte oder synthetische Inhalte“ **Ja** wählen, weil die Stimme synthetisch ist.
6. „Nicht speziell für Kinder“ wählen.
7. Optional eine Playlist je Sprache anlegen.

## Lokal ausführen

```bash
pip install -r sendung/requirements.txt   # dazu ffmpeg
python sendung/erzeuge_sendung.py --daten daten.json --stimmen stimmen --ausgabe ausgabe
```

Die Stimmen lädt der Workflow von huggingface.co/rhasspy/piper-voices herunter (siehe dort).
