# Nachrichtensendung (MVP)

`erzeuge_sendung.py` macht aus `daten.json` (Branch `zeitung-daten`) täglich drei Videos:
Deutsch, Französisch, Englisch, je 1920×1080. Dazu gibt es pro Sprache ein Vorschaubild
und eine Textdatei mit Titel, Beschreibung (Kapitel und Quellen) und Tags für YouTube.

- **Inhalt:** Themen mit Meldung in den letzten 24 Stunden, Top-Themen zuerst, höchstens 8.
- **Bild:** Standbild-Folien in der Farbwelt der Website, mit GM-Logo und Flaggenstreifen.
  Keine Fotos oder Grafiken aus den Quellen.
- **Ton:** Piper TTS (Zahlen werden vorher mit num2words ausgeschrieben, lange deutsche Zusammensetzungen mit compound-split an der Wortfuge getrennt), frei nutzbare Stimmen. Die Namensnennung steht in jeder Videobeschreibung.
  Die Aussprache schwieriger Wörter (Orte, Abkürzungen, Beträge, Uhrzeiten) regelt `aussprache.json`.
  Dort können weitere Wörter ergänzt werden.
  - Deutsch: Thorsten (CC0)
  - Französisch: SIWIS (CC BY 4.0)
  - Englisch: Cori (gemeinfrei)
- **Wetter:** Zum Schluss die Vorhersage für Mauritius, Rodrigues und La Réunion (MET Norway, CC BY 4.0; `wetter.py`). Ist der Dienst nicht erreichbar, entfällt der Block.
- **Schriften:** Bricolage Grotesque, Source Serif 4 und IBM Plex Mono, alle unter OFL (siehe `schriften/`).

## Ablauf

Der Workflow `.github/workflows/sendung.yml` läuft täglich um 05:20 UTC (09:20 Uhr Mauritius).
Man kann ihn auch von Hand starten: GitHub → Actions → „Nachrichtensendung“ → *Run workflow*.
Das Ergebnis liegt 14 Tage als Artefakt `sendung-JJJJ-MM-TT` (ZIP) am Lauf.

## Automatischer Upload auf YouTube

Nach dem Rendern lädt `youtube_upload.py` jedes Video hoch und setzt Titel, Beschreibung,
Tags, Kategorie „Nachrichten“, Sprache, den Hinweis „synthetische Inhalte“ und das Vorschaubild.
Jedes Video kommt in die Playlist seiner Sprache. Die Playlists legt das Skript beim ersten
Lauf selbst an.

- **Sichtbarkeit:** standardmäßig `private`. Über die Repository-Variable `YT_SICHTBARKEIT`
  (GitHub → Settings → Secrets and variables → Actions → Variables) lässt sie sich auf
  `unlisted` oder `public` stellen.
- **Einschränkung von Google:** Neue, noch nicht geprüfte API-Projekte dürfen nur privat
  hochladen. Bis Google das Projekt geprüft hat, schaltet man die Videos im YouTube Studio
  von Hand auf öffentlich. Die Prüfung beantragt man über das Formular „YouTube API Services –
  Audit and Quota Extension“.

### Einmalige Einrichtung

1. **Projekt anlegen:** https://console.cloud.google.com → neues Projekt „Gazet Morisyen“.
2. **API aktivieren:** „APIs & Dienste“ → „Bibliothek“ → „YouTube Data API v3“ → Aktivieren.
3. **OAuth-Zustimmungsbildschirm** (bzw. „Google Auth Platform“):
   - Nutzertyp „Extern“.
   - App-Name „Gazet Morisyen“, Support- und Kontakt-E-Mail eintragen.
   - Unter „Zielgruppe“ den Veröffentlichungsstatus auf **„In Produktion“** stellen.
     Im Status „Test“ verfällt der Zugang nach 7 Tagen.
4. **Client anlegen:** „Clients“ bzw. „Anmeldedaten“ → „OAuth-Client-ID erstellen“.
   - Typ „Webanwendung“.
   - Unter „Autorisierte Weiterleitungs-URIs“: `https://developers.google.com/oauthplayground`
   - Client-ID und Clientschlüssel notieren.
5. **Refresh-Token erzeugen:** https://developers.google.com/oauthplayground
   - Zahnrad oben rechts → „Use your own OAuth credentials“ → Client-ID und Clientschlüssel eintragen.
   - Links unter „Input your own scopes“:
     `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube`
   - „Authorize APIs“ → mit dem Google-Konto des YouTube-Kanals anmelden.
   - Den Hinweis „Google hat diese App nicht überprüft“ über „Erweitert“ → „Weiter“ bestätigen.
   - „Exchange authorization code for tokens“ → den **Refresh token** kopieren.
6. **GitHub-Secrets anlegen:** GitHub → Settings → Secrets and variables → Actions →
   „New repository secret“:
   - `YT_CLIENT_ID`
   - `YT_CLIENT_SECRET`
   - `YT_REFRESH_TOKEN`

Ohne diese Secrets läuft alles wie bisher, nur ohne Upload. Die Videos liegen dann weiter als
Artefakt am Lauf.

### Von Hand hochladen (falls nötig)

1. Das Artefakt `sendung-JJJJ-MM-TT` am Workflow-Lauf herunterladen und entpacken.
2. Im YouTube Studio die `.mp4` hochladen.
3. Titel, Beschreibung und Tags aus der `-youtube.txt` übernehmen.
4. Die `-vorschau.png` als Vorschaubild setzen.
5. Bei „Veränderte oder synthetische Inhalte“ **Ja** wählen.

## Lokal ausführen

```bash
pip install -r sendung/requirements.txt   # dazu ffmpeg
python sendung/erzeuge_sendung.py --daten daten.json --stimmen stimmen --ausgabe ausgabe
```

Die Stimmen lädt der Workflow von huggingface.co/rhasspy/piper-voices herunter (siehe dort).

## Vorspann und Erkennungsmelodie

- **Ablauf:** Vor jeder Sendung läuft ein Vorspann von 3,5 s, die Logo-Animation in `erzeuge_sendung.py` (`vorspann_video`).
- **Musik:** Die Melodie liegt fertig in `vorspann.wav` und wurde einmalig mit `vorspann_musik.py` erzeugt.
  - Gitarre, Akkordeon, Kontrabass und Bläser stammen aus dem Soundfont FluidR3_GM (MIT-Lizenz, Debian-Paket `fluid-soundfont-gm`) und werden mit FluidSynth gespielt.
  - Die Séga-Trommeln (Ravanne, Maravanne, Triangel) synthetisiert `jingle.py`.
- **Neu erzeugen:** `apt-get install fluidsynth fluid-soundfont-gm && pip install mido && python3 vorspann_musik.py`
- **Ersatz:** Fehlt `vorspann.wav`, erzeugt `jingle.py` eine rein synthetische Fassung.
