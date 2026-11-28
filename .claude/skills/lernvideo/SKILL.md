---
name: lernvideo
description: Erstellt aus einem Dossier der Gazet Morisyen ein vertontes Lernvideo „Gazet Morisyen erklärt“ (DE/EN/FR) mit animierten Grafiken, Vorschaubild, Untertiteln und privatem YouTube-Upload. Verwenden, wenn ein Lernvideo, Erklärvideo oder Storyboard zu einem Dossier gewünscht ist (z. B. „Erstelle ein Lernvideo zum Dossier Chagos“).
---

# Lernvideo „Gazet Morisyen erklärt“

Ein Lernvideo erklärt ein Dossier (`dossiers.json` auf dem Branch `zeitung-daten`) in einigen Minuten: Sprecherstimme
(Piper, wie in der Sendung), jede Aussage eine eigene Grafik-Animation, Musikteppich, Vor- und Abspann der Sendung.
Vorbild und Referenz ist das erste Video „Warum auf Mauritius das Wasser knapp wird“ (`sendung/lernvideos/wasser.py`).

Arbeite mit dem Menschen zusammen: Titel, Storyboard, Pilot und jede Sprachfassung werden **freigegeben**, bevor es
weitergeht. Sprache mit ihm: Deutsch.

## Dateien

| Datei | Zweck |
|---|---|
| `sendung/lernvideo.py` | Baukasten: Zeichenhilfen (Cairo für Formen, Pillow für Texte), Szene, Ton, Musik, SRT, Zusammenbau. Aufruf `python3 lernvideo.py --video <name> --sprache de --stimmen <ordner> --ausgabe <ordner> [--nur 3 4]` |
| `sendung/lernvideos/<name>.py` | **Ein Modul je Video**: Szenen-Funktionen, `SZENEN` (deutscher Text, Quelle), `TEXTE` (en/fr, gleiche Satzzahl), `UI` (Bildtexte en/fr, Deutsch ist der Schlüssel), `STAMM`, `STAND_DATUM`, `DOSSIER_URL`, `VORSCHAU`, `VORSCHAU_FOTO`, `YOUTUBE`, `QUELLEN`, `FOTO_SEITE` |
| `sendung/lernvideo_vorschau.py` | Vorschaubild 1280×720 aus `VORSCHAU` des Moduls |
| `sendung/lernvideo_pruefen.py` | Prüfungen: `satzzahl`, `kontaktbogen`, `timing`, `transkript` |
| `sendung/lernvideo_upload.py` | privater Upload direkt in den Kanal (keine Playlist), Vorschaubild, Untertitel |
| `.github/workflows/lernvideo.yml` | von Hand starten mit `video`, `sprachen`, `hochladen`; erzeugt und lädt hoch |
| `sendung/aussprache.json` | Aussprache-Verzeichnis (gilt auch für die Sendung) |
| `sendung/requirements-lernvideo.txt` | zusätzliche Pakete (pycairo, qrcode, mido); System: ffmpeg, fluidsynth, fluid-soundfont-gm, libcairo2-dev |

## Ablauf

1. **Dossier lesen** (aktueller Stand von `zeitung-daten`): kurz, warum, entwicklung, chronik, akteure, zahlen,
   grafiken, offen, quellen.
2. **Storyboard als Dokument** (Claude Docs, Typ „Docs“): Titelvorschläge (DE/FR/EN, eine Empfehlung, Reihentitel
   „Gazet Morisyen erklärt“), Eckdaten, Abschnitt **Datierung und neue Fassungen**, Storyboard-Tabelle
   `Nr. | Zeit | Sprechertext | Grafik-Animation | Quelle`, Quellen und nächste Schritte.
3. **Vollständigkeits-Abgleich** (siehe unten), dann Freigabe einholen.
4. **Pilot**: Vorspann und die ersten 4–6 Szenen bauen, prüfen, schicken, Rückmeldung einarbeiten.
5. **Alle Szenen** bauen, Kontaktbogen prüfen, Video rechnen, Transkript prüfen, schicken.
6. **Korrekturen** des Menschen umsetzen (Aussprache, Timing, Darstellung), erneut prüfen.
7. **EN, dann FR**: Texte mit **gleicher Satzzahl und Reihenfolge** je Szene, Bildtexte in `UI`, Prüfungen, schicken.
8. **Vorschaubilder** (DE, dann EN/FR), schicken.
9. **Merge und Upload** über den Workflow (nur nach Freigabe); danach die SRT-Dateien aus dem Artefakt des Laufs holen.
10. **Ins Dossier einbinden** (nach Freigabe): Vorschaubilder als JPEG nach `public/bilder/lernvideo-<name>-<sprache>.jpg`
    (Commit auf main), dann im Dossier auf `zeitung-daten` das Feld
    `"video": {"youtube": {"de": "<id>", "en": "<id>", "fr": "<id>"}, "vorschau": {"de": "/bilder/…", …}}` setzen.
    Die Seite zeigt das Video in der gewählten Sprache mit Zwei-Klick-Einbettung (youtube-nocookie).

## Vollständigkeits-Abgleich (vor dem Pilot und vor der Produktion)

- **Alles erfasst?** Jeden Dossier-Abschnitt mit dem Storyboard abgleichen. Fehlt eine belegte Aussage, wird sie eine
  Szene, oder der Verzicht wird begründet. Den Abgleich ausdrücklich durchführen und dem Menschen nennen, was ergänzt
  wurde.
- **Alles belegt?** Jede Zahl und jede Aussage braucht eine Quelle aus dem Dossier. Kommt etwas aus einer neuen Quelle
  (Seite selbst öffnen), wird zuerst das **Dossier ergänzt** (nur mit Freigabe), damit Video und Dossier übereinstimmen.
- **Widersprüche offen benennen**: unterschiedliche Zahlen aus verschiedenen Quellen getrennt zeigen und im Storyboard
  vermerken.
- **Länge folgt dem Inhalt**: keine feste Minutenzahl, nichts auffüllen, nichts Belegtes weglassen.
- Grafiken zeigen nur Zahlen aus den Quellen; wo das Dossier keine Einzelwerte nennt, nur die Tendenz (ohne Werte).

## Datierung

Ein YouTube-Video lässt sich nicht ergänzen. Deshalb: Titelkarte und Abspann zeigen den Stand, gesprochen wird
„Stand: Ende <Monat> <Jahr>“, der YouTube-Titel nennt den Monat. Neue Fassung nur bei gravierenden Änderungen;
die alte bleibt online und verweist (Beschreibung, angehefteter Kommentar) auf die neue.

## Gestaltung (bewährt)

- Navy-Verlauf der Sendung, Mint für Wasser/Positives, Rot für Warnung/Hervorhebung, Schrift wie die Sendung,
  Kopfzeile „GAZET MORISYEN ERKLÄRT“ links, „Quelle: …“ rechts, Flaggenlinie unten.
- Eine Aussage = eine Grafik. Elemente bauen sich in 0,4–1,5 s auf; **Ereignisse an Satzanfänge koppeln**
  (`s.satz_start(i)`), nicht an feste Sekunden, wenn ein Satz das Element einführt. Beispiele: rote Linien erst bei
  „Wird es knapp“, Becken wächst bei „Zusammen“, jeder Balken bei seinem Satz.
- Zustände nicht nur über Farbe zeigen (z. B. Schieber mit Handrad, Wasser fließt nur bei offenem Schieber).
- Fotos nur mit freier Lizenz und Bildnachweis im Bild und in der Beschreibung.
- Ortsnamen auf Karten mit Hinweislinien, wenn sie dicht liegen; fehlende Orte in `lib/zeitung/orte.json` ergänzen
  (Lage vorher prüfen, z. B. mit Karten des Menschen).
- Abspann: gazet.morisyen.de, Dossier mit Stand, QR-Code zur Dossier-Seite, danach Abspann-Folie der Sendung.
- Untertitel **nicht** einbrennen; SRT-Datei für YouTube.
- Musikteppich rund 20 dB unter der Stimme (macht `lernvideo.py`), Vor- und Abspann behalten ihre Musik.

## Prüfungen (jede Runde)

```
cd sendung
python3 lernvideo_pruefen.py satzzahl --video <name>
python3 lernvideo_pruefen.py kontaktbogen --video <name> --sprache en --ziel bogen-en.png   # ansehen!
python3 lernvideo_pruefen.py timing --mp4 <video> --srt <srt> --ziel timing.png --suche "<Satzanfang>" …
python3 lernvideo_pruefen.py transkript --mp4 <video> --sprache de --whisper <python mit faster-whisper>
```

- Kontaktbogen jeder Sprache ansehen: abgeschnittene oder überlappende Texte, noch deutsche Wörter, Zahlformat
  (de 92,2 / en 92.2 / fr 92,2 und „44 %“ vs. „44%“).
- Timing: Element darf 0,3 s vor dem Satz noch nicht da sein und muss 1,2 s danach sichtbar sein.
- Transkript: Namen, Zahlen, Daten, Fremdwörter. Whisper verhört sich bei Eigennamen; im Zweifel die Phoneme prüfen
  (`PiperVoice.phonemize`).
- Nach Umbauten am Baukasten: Bilder vorher/nachher pixelgenau vergleichen.

## Aussprache (Stolperfallen)

- Satztrennung: Ein Punkt nach einer Zahl vor einem Monatsnamen („26. November“) ist kein Satzende
  (`saetze_trennen` beachtet das). Sonst wird „sechsundzwanzig“ statt „sechsundzwanzigsten“ gesprochen.
- Lautschrift in `aussprache.json` nur im **espeak-Stil**, wie die Stimme trainiert wurde (`r`, nicht `ʁ`; z. B.
  „Tarife“ `[[ tarˈiːfə ]]`, „Service“ `[[ zˈœɾvɪs ]]`). Vorher mit `PiperVoice.phonemize` vergleichen.
- Wortfugen-Trennung zerlegt Fremdwörter („Ser Vice“): Lautschrift-Eintrag oder `nicht_trennen`.
- Französische Ortsnamen stehen in `aussprache.json` unter `franzoesisch`; `lernvideo.py` lädt sie automatisch.
- Webadresse wird gesprochen als „gazet punkt/dot/point morisyen punkt/dot/point D E“ (`URL_SPRECHEN`).

## Upload

- Workflow „Lernvideo“ mit `video=<name>`, `sprachen=de,en,fr`, `hochladen=true` starten. Videos sind **privat**,
  Kategorie Bildung, synthetische Inhalte markiert, keine Playlist. Bereits vorhandene Titel werden übersprungen.
- Die Stimme spricht bei jedem Lauf minimal anders (Zehntelsekunden). **Die SRT-Dateien müssen aus demselben Lauf
  stammen wie die Videos**: Artefakt `lernvideo-<name>` des Workflow-Laufs herunterladen.
- Untertitel-Upload per API braucht die Berechtigung `youtube.force-ssl`; ohne sie lädt der Mensch die SRT in
  YouTube Studio hoch (Untertitel → Datei hochladen → „Mit Zeitangaben“).
- Veröffentlichen nur auf ausdrücklichen Wunsch: Workflow mit `nur_sichtbarkeit=true`, `sichtbarkeit=public`
  (lädt nichts neu hoch, rendert nicht, prüft danach den neuen Status).

## Ein neues Video anlegen

1. `sendung/lernvideos/<name>.py` nach dem Muster von `wasser.py` anlegen (Kopf mit `STAMM`, `STAND_DATUM`).
2. Szenen-Funktionen `szene_…(t, s) -> Image` mit den Helfern aus `lernvideo.py` schreiben; Bildtexte immer über
   `L('…')`, Zahlen über `zahl_de`/`prozent`, Sprache über `lv.SPRACHE`.
3. `SZENEN`, `TEXTE`, `UI`, `VORSCHAU`, `YOUTUBE`, `QUELLEN` füllen.
4. Neue Zeichenhelfer, die mehrere Videos brauchen, in `lernvideo.py` aufnehmen.
