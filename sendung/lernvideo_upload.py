#!/usr/bin/env python3
"""
Lädt ein Lernvideo „Gazet Morisyen erklärt“ (Modul in lernvideos/) auf YouTube hoch (Standard: privat) – direkt in den Kanal, in keine Playlist.
Setzt Vorschaubild und lädt die SRT-Untertitel hoch.

Zugangsdaten wie bei der Sendung aus YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (GitHub-Secrets).
Bereits hochgeladene Titel werden übersprungen (nur Vorschaubild und Untertitel werden aufgefrischt).

    python lernvideo_upload.py --video wasser --ausgabe <ordner> [--sprachen de,en,fr] [--sichtbarkeit public]
    python lernvideo_upload.py --video wasser --ausgabe . --sichtbarkeit public --nur-sichtbarkeit   # nur veröffentlichen
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path

from youtube_upload import dienst, mit_wiederholung, setze_vorschau, vorhandene_uploads

KATEGORIE_BILDUNG = '27'  # Education
VIDEO = None  # Video-Modul aus lernvideos/, wird in main() gesetzt


def beschreibung(m: dict) -> str:
    quellen = '\n'.join(f'- {name}: {url}' for name, url in VIDEO.QUELLEN)
    foto = f"\n\n{m['foto']}\n{VIDEO.FOTO_SEITE}" if m.get('foto') else ''
    return f"{m['text']}\n\n{m['quellen']}:\n{quellen}{foto}\n\n{m['ki']}"


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


def status(sichtbarkeit: str) -> dict:
    return {'privacyStatus': sichtbarkeit, 'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True,
            'license': 'youtube', 'embeddable': True}


def setze_sichtbarkeit(yt, video_id: str, sichtbarkeit: str, sprache: str) -> None:
    """Ändert die Sichtbarkeit eines vorhandenen Videos (z. B. privat → öffentlich)."""
    jetzt = mit_wiederholung(lambda: yt.videos().list(part='status', id=video_id))['items'][0]['status']['privacyStatus']
    if jetzt == sichtbarkeit:
        print(f'  {sprache}: schon {sichtbarkeit}')
        return
    mit_wiederholung(lambda: yt.videos().update(part='status', body={'id': video_id, 'status': status(sichtbarkeit)}))
    neu = mit_wiederholung(lambda: yt.videos().list(part='status', id=video_id))['items'][0]['status']['privacyStatus']
    print(f'  {sprache}: Sichtbarkeit {jetzt} → {neu} (https://youtu.be/{video_id})')
    if neu != sichtbarkeit:
        raise RuntimeError(f'YouTube hat die Sichtbarkeit nicht auf {sichtbarkeit} gesetzt (steht auf {neu})')


def lade_hoch(yt, ordner: Path, sprache: str, vorhanden: dict[str, str], sichtbarkeit: str = 'private',
              nur_sichtbarkeit: bool = False) -> str:
    from googleapiclient.http import MediaFileUpload

    m = VIDEO.YOUTUBE[sprache]
    video = ordner / f"{m['datei']}.mp4"
    if m['titel'] in vorhanden:
        video_id = vorhanden[m['titel']]
        print(f'  {sprache}: schon hochgeladen → https://youtu.be/{video_id}')
        setze_sichtbarkeit(yt, video_id, sichtbarkeit, sprache)
        if nur_sichtbarkeit:
            return video_id
    elif nur_sichtbarkeit:
        raise RuntimeError(f'kein Video mit dem Titel „{m["titel"]}“ im Kanal gefunden')
    else:
        body = {
            'snippet': {'title': m['titel'], 'description': beschreibung(m), 'tags': m['tags'],
                        'categoryId': KATEGORIE_BILDUNG, 'defaultLanguage': sprache, 'defaultAudioLanguage': sprache},
            'status': status(sichtbarkeit),
        }
        anfrage = yt.videos().insert(part='snippet,status', body=body, media_body=MediaFileUpload(
            str(video), mimetype='video/mp4', chunksize=8 * 1024 * 1024, resumable=True))
        antwort = None
        while antwort is None:
            fortschritt, antwort = anfrage.next_chunk()
            if fortschritt:
                print(f'  {sprache}: {int(fortschritt.progress() * 100)} %')
        video_id = antwort['id']
        print(f'  {sprache}: hochgeladen → https://youtu.be/{video_id} ({sichtbarkeit})')
    setze_vorschau(yt, video_id, ordner / f'vorschau-{sprache}.png', sprache)
    lade_untertitel(yt, video_id, ordner / f"{m['datei']}.{sprache}.srt", sprache, m['untertitel'])
    return video_id


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ausgabe', required=True, type=Path)
    p.add_argument('--sprachen', default='de,en,fr')
    p.add_argument('--video', default='wasser', help='Modul in lernvideos/')
    p.add_argument('--sichtbarkeit', choices=['private', 'unlisted', 'public'], default='private')
    p.add_argument('--nur-sichtbarkeit', action='store_true',
                   help='nichts hochladen, nur die Sichtbarkeit der vorhandenen Videos setzen')
    a = p.parse_args()
    global VIDEO
    VIDEO = importlib.import_module(f'lernvideos.{a.video}')
    if not all(os.environ.get(k) for k in ('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN')):
        print('YouTube-Zugang nicht eingerichtet – Upload übersprungen.')
        return 0
    yt = dienst()
    vorhanden = vorhandene_uploads(yt)
    fehler = []
    for sprache in [s.strip() for s in a.sprachen.split(',') if s.strip()]:
        try:
            lade_hoch(yt, a.ausgabe, sprache, vorhanden, a.sichtbarkeit, a.nur_sichtbarkeit)
        except Exception as f:  # noqa: BLE001 – die anderen Sprachen trotzdem hochladen
            print(f'  {sprache}: FEHLER {f}', file=sys.stderr)
            fehler.append(sprache)
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.stdout.reconfigure(line_buffering=True)
    sys.exit(main())
