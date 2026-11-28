#!/usr/bin/env python3
"""
Lädt die Lernvideos „Gazet Morisyen erklärt“ privat auf YouTube hoch – direkt in den Kanal, in keine Playlist.
Setzt Vorschaubild und lädt die SRT-Untertitel hoch.

Zugangsdaten wie bei der Sendung aus YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (GitHub-Secrets).
Bereits hochgeladene Titel werden übersprungen (nur Vorschaubild und Untertitel werden aufgefrischt).

    python lernvideo_upload.py --ausgabe <ordner> [--sprachen de,en,fr]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from youtube_upload import dienst, mit_wiederholung, setze_vorschau, vorhandene_uploads

KATEGORIE_BILDUNG = '27'  # Education
DOSSIER = 'https://gazet.morisyen.de/dossier/wasserversorgung'
FOTO = 'https://commons.wikimedia.org/wiki/File:Mare_aux_Vacoas,_Mauricio,_2025-09-25,_DD_77-82_PAN.jpg'
QUELLEN = [
    ('Ministry of Energy and Public Utilities – Water Resources Unit',
     'https://publicutilities.govmu.org/Pages/Water%20Sector/WRU.aspx'),
    ('Statistics Mauritius (ODE) – Water Reservoirs', 'https://ode.govmu.org/water-reservoirs'),
    ('National Audit Office – Water Report', 'https://nao.govmu.org/nao/wp-content/uploads/2026/02/water_report.pdf'),
    ('CWA Annual Report 2024–2025',
     'https://cwa.govmu.org/cwa/wp-content/uploads/2026/09/CWA_Annual-Report-2024-2025.pdf'),
    ('ION News', 'https://ionnews.mu/ressources-en-eau-les-reservoirs-reculent-a-44-au-26-novembre-2026/'),
    ("L'Express", 'https://lexpress.mu/s/eau-60-de-pertes-des-tarifs-trop-bas-le-verdict-des-specialistes-565115'),
    ('allAfrica / L\'Express', 'https://fr.allafrica.com/stories/202611180579.html'),
    ('newsmoris', 'https://newsmoris.com/cwa-loses-60-of-supply-amid-mounting-financial-deficits/'),
    ('Maurice Info',
     'https://maurice-info.mu/2026/03/04/le-barrage-de-riviere-des-anguilles-est-un-projet-phare-pour-le-sud.html'),
]

META = {
    'de': {
        'datei': 'lernvideo-wasser',
        'titel': 'Warum auf Mauritius das Wasser knapp wird (Stand Nov. 2026) | Gazet Morisyen erklärt',
        'text': ('Warum wird auf einer tropischen Insel das Wasser knapp? Wir erklären die Wasserversorgung auf '
                 'Mauritius: sieben künstliche Stauseen, sinkende Füllstände, hohe Verluste im Netz, eingefrorene '
                 'Tarife und der geplante Damm von Rivière-des-Anguilles.\n\n'
                 'Stand: 28. November 2026. Neuere Entwicklungen, alle Zahlen und Hintergründe im Dossier:\n'
                 f'{DOSSIER}'),
        'quellen': 'Quellen', 'foto': 'Foto Mare-aux-Vacoas: Diego Delso, CC BY-SA 4.0, Wikimedia Commons',
        'ki': ('Hinweis: Die Sprecherstimme ist synthetisch (Piper, Stimme „Thorsten“). Grafiken und Animationen: '
               'Gazet Morisyen.'),
        'tags': ['Mauritius', 'Wasser', 'Wasserversorgung', 'Mare aux Vacoas', 'CWA', 'Dürre', 'Erklärvideo',
                 'Gazet Morisyen'],
        'untertitel': 'Deutsch',
    },
    'en': {
        'datei': 'lernvideo-wasser-en',
        'titel': 'Why Mauritius is running short of water (as of Nov 2026) | Gazet Morisyen explains',
        'text': ('Why is water running short on a tropical island? We explain water supply in Mauritius: seven '
                 'man-made reservoirs, falling levels, heavy losses in the network, frozen tariffs and the planned '
                 'Rivière-des-Anguilles dam.\n\n'
                 'As of 28 November 2026. Later developments, all figures and background in our explainer:\n'
                 f'{DOSSIER}'),
        'quellen': 'Sources', 'foto': 'Photo of Mare-aux-Vacoas: Diego Delso, CC BY-SA 4.0, Wikimedia Commons',
        'ki': 'Note: the narration uses a synthetic voice (Piper, voice "Cori"). Graphics and animation: Gazet Morisyen.',
        'tags': ['Mauritius', 'water', 'water supply', 'Mare aux Vacoas', 'CWA', 'drought', 'explainer',
                 'Gazet Morisyen'],
        'untertitel': 'English',
    },
    'fr': {
        'datei': 'lernvideo-wasser-fr',
        'titel': "Pourquoi l'eau manque à Maurice (situation nov. 2026) | Gazet Morisyen explique",
        'text': ("Pourquoi l'eau manque-t-elle sur une île tropicale ? Nous expliquons l'approvisionnement en eau à "
                 'Maurice : sept lacs artificiels, des niveaux en baisse, de fortes pertes sur le réseau, des tarifs '
                 'gelés et le projet de barrage de Rivière-des-Anguilles.\n\n'
                 'Situation au 28 novembre 2026. Évolutions récentes, chiffres et contexte dans notre dossier :\n'
                 f'{DOSSIER}'),
        'quellen': 'Sources', 'foto': 'Photo de Mare-aux-Vacoas : Diego Delso, CC BY-SA 4.0, Wikimedia Commons',
        'ki': 'Remarque : la voix est synthétique (Piper, voix « SIWIS »). Graphiques et animations : Gazet Morisyen.',
        'tags': ['Maurice', 'eau', 'approvisionnement en eau', 'Mare-aux-Vacoas', 'CWA', 'sécheresse',
                 'explication', 'Gazet Morisyen'],
        'untertitel': 'Français',
    },
}


def beschreibung(m: dict) -> str:
    quellen = '\n'.join(f'- {name}: {url}' for name, url in QUELLEN)
    return f"{m['text']}\n\n{m['quellen']}:\n{quellen}\n\n{m['foto']}\n{FOTO}\n\n{m['ki']}"


def lade_untertitel(yt, video_id: str, srt: Path, sprache: str, name: str) -> None:
    from googleapiclient.http import MediaFileUpload

    if not srt.exists():
        return
    try:
        vorhanden = mit_wiederholung(lambda: yt.captions().list(part='snippet', videoId=video_id))
        if any(c['snippet']['language'] == sprache for c in vorhanden.get('items', [])):
            print(f'  {sprache}: Untertitel schon vorhanden')
            return
        mit_wiederholung(lambda: yt.captions().insert(
            part='snippet',
            body={'snippet': {'videoId': video_id, 'language': sprache, 'name': name, 'isDraft': False}},
            media_body=MediaFileUpload(str(srt), mimetype='application/octet-stream')))
        print(f'  {sprache}: Untertitel hochgeladen')
    except Exception as fehler:  # noqa: BLE001 – Untertitel lassen sich auch in YouTube Studio nachreichen
        print(f'  {sprache}: Untertitel nicht hochgeladen ({fehler})')


def lade_hoch(yt, ordner: Path, sprache: str, vorhanden: dict[str, str]) -> str:
    from googleapiclient.http import MediaFileUpload

    m = META[sprache]
    video = ordner / f"{m['datei']}.mp4"
    if m['titel'] in vorhanden:
        video_id = vorhanden[m['titel']]
        print(f'  {sprache}: schon hochgeladen → https://youtu.be/{video_id}')
    else:
        body = {
            'snippet': {'title': m['titel'], 'description': beschreibung(m), 'tags': m['tags'],
                        'categoryId': KATEGORIE_BILDUNG, 'defaultLanguage': sprache, 'defaultAudioLanguage': sprache},
            'status': {'privacyStatus': 'private', 'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True,
                       'license': 'youtube', 'embeddable': True},
        }
        anfrage = yt.videos().insert(part='snippet,status', body=body, media_body=MediaFileUpload(
            str(video), mimetype='video/mp4', chunksize=8 * 1024 * 1024, resumable=True))
        antwort = None
        while antwort is None:
            fortschritt, antwort = anfrage.next_chunk()
            if fortschritt:
                print(f'  {sprache}: {int(fortschritt.progress() * 100)} %')
        video_id = antwort['id']
        print(f'  {sprache}: hochgeladen → https://youtu.be/{video_id} (privat)')
    setze_vorschau(yt, video_id, ordner / f'vorschau-{sprache}.png', sprache)
    lade_untertitel(yt, video_id, ordner / f"{m['datei']}.{sprache}.srt", sprache, m['untertitel'])
    return video_id


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ausgabe', required=True, type=Path)
    p.add_argument('--sprachen', default='de,en,fr')
    a = p.parse_args()
    if not all(os.environ.get(k) for k in ('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN')):
        print('YouTube-Zugang nicht eingerichtet – Upload übersprungen.')
        return 0
    yt = dienst()
    vorhanden = vorhandene_uploads(yt)
    fehler = []
    for sprache in [s.strip() for s in a.sprachen.split(',') if s.strip()]:
        try:
            lade_hoch(yt, a.ausgabe, sprache, vorhanden)
        except Exception as f:  # noqa: BLE001 – die anderen Sprachen trotzdem hochladen
            print(f'  {sprache}: FEHLER {f}', file=sys.stderr)
            fehler.append(sprache)
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.stdout.reconfigure(line_buffering=True)
    sys.exit(main())
