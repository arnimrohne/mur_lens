#!/usr/bin/env python3
"""
Lädt die fertigen Sendungen auf YouTube hoch und sortiert sie in die Playlist ihrer Sprache.

Zugangsdaten nur aus Umgebungsvariablen (GitHub-Secrets), nie aus dem Code:
  YT_CLIENT_ID, YT_CLIENT_SECRET   OAuth-Client aus der Google Cloud
  YT_REFRESH_TOKEN                 einmalig erzeugt (siehe sendung/README.md)
Optional:
  YT_SICHTBARKEIT                  private (Standard) | unlisted | public

Fehlen die Zugangsdaten, wird der Upload übersprungen (kein Fehler).

Aufruf: python youtube_upload.py --ausgabe <ordner>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

PLAYLISTS = {
    'de': ('Nachrichten aus Mauritius (Deutsch)',
           'Die tägliche Nachrichtensendung von Gazet Morisyen auf Deutsch. Alle Meldungen und Quellen: https://gazet.morisyen.de'),
    'fr': ("L'actualité de Maurice (Français)",
           "Le journal quotidien de Gazet Morisyen en français. Toutes les informations et sources : https://gazet.morisyen.de"),
    'en': ('News from Mauritius (English)',
           'The daily news bulletin from Gazet Morisyen in English. All stories and sources: https://gazet.morisyen.de'),
}
KATEGORIE_NACHRICHTEN = '25'  # News & Politics
SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube']


def dienst():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    zugang = Credentials(
        token=None,
        refresh_token=os.environ['YT_REFRESH_TOKEN'],
        client_id=os.environ['YT_CLIENT_ID'],
        client_secret=os.environ['YT_CLIENT_SECRET'],
        token_uri='https://oauth2.googleapis.com/token',
        scopes=SCOPES,
    )
    return build('youtube', 'v3', credentials=zugang, cache_discovery=False)


def mit_wiederholung(anfrage_bauen, versuche: int = 5):
    """Führt eine API-Anfrage aus; bei vorübergehenden Fehlern (409/429/5xx) mit Pause erneut."""
    from googleapiclient.errors import HttpError

    for versuch in range(versuche):
        try:
            return anfrage_bauen().execute()
        except HttpError as fehler:
            if fehler.resp.status not in (409, 429, 500, 502, 503, 504) or versuch == versuche - 1:
                raise
            pause = 5 * 2 ** versuch
            print(f'  vorübergehender Fehler {fehler.resp.status}, neuer Versuch in {pause} s')
            time.sleep(pause)


def vorhandene_uploads(yt) -> dict[str, str]:
    """Titel → Video-ID der letzten Uploads des Kanals (verhindert Doppel-Uploads bei Wiederholung)."""
    kanal = mit_wiederholung(lambda: yt.channels().list(part='contentDetails', mine=True))
    eintraege = kanal.get('items', [])
    if not eintraege:
        return {}
    uploads = eintraege[0]['contentDetails']['relatedPlaylists']['uploads']
    antwort = mit_wiederholung(lambda: yt.playlistItems().list(part='snippet', playlistId=uploads, maxResults=50))
    return {e['snippet']['title']: e['snippet']['resourceId']['videoId'] for e in antwort.get('items', [])}


def in_playlist(yt, playlist: str, video_id: str) -> None:
    antwort = mit_wiederholung(lambda: yt.playlistItems().list(part='snippet', playlistId=playlist, maxResults=50))
    if any(e['snippet']['resourceId']['videoId'] == video_id for e in antwort.get('items', [])):
        return
    mit_wiederholung(lambda: yt.playlistItems().insert(part='snippet', body={
        'snippet': {'playlistId': playlist, 'resourceId': {'kind': 'youtube#video', 'videoId': video_id}},
    }))


def playlist_id(yt, sprache: str, sichtbarkeit: str) -> str:
    titel, beschreibung = PLAYLISTS[sprache]
    anfrage = yt.playlists().list(part='snippet', mine=True, maxResults=50)
    while anfrage is not None:
        antwort = anfrage.execute()
        for eintrag in antwort.get('items', []):
            if eintrag['snippet']['title'] == titel:
                return eintrag['id']
        anfrage = yt.playlists().list_next(anfrage, antwort)
    neu = mit_wiederholung(lambda: yt.playlists().insert(part='snippet,status', body={
        'snippet': {'title': titel, 'description': beschreibung, 'defaultLanguage': sprache},
        'status': {'privacyStatus': 'public' if sichtbarkeit == 'public' else 'unlisted'},
    }))
    print(f'Playlist angelegt: {titel} ({neu["id"]})')
    time.sleep(5)  # frisch angelegte Playlists sind nicht sofort beschreibbar
    return neu['id']


def lade_hoch(yt, ordner: Path, meta: dict, sichtbarkeit: str, vorhanden: dict[str, str]) -> str:
    from googleapiclient.http import MediaFileUpload

    sprache = meta['sprache']
    if meta['titel'] in vorhanden:
        video_id = vorhanden[meta['titel']]
        print(f'  {sprache}: schon hochgeladen → https://youtu.be/{video_id}')
        in_playlist(yt, playlist_id(yt, sprache, sichtbarkeit), video_id)
        return video_id
    body = {
        'snippet': {
            'title': meta['titel'],
            'description': meta['beschreibung'],
            'tags': meta['tags'],
            'categoryId': KATEGORIE_NACHRICHTEN,
            'defaultLanguage': sprache,
            'defaultAudioLanguage': sprache,
        },
        'status': {
            'privacyStatus': sichtbarkeit,
            'selfDeclaredMadeForKids': False,
            'containsSyntheticMedia': True,  # Sprecherstimme ist synthetisch
            'license': 'youtube',
            'embeddable': True,
        },
    }
    medien = MediaFileUpload(str(ordner / meta['video']), mimetype='video/mp4', chunksize=8 * 1024 * 1024,
                             resumable=True)
    anfrage = yt.videos().insert(part='snippet,status', body=body, media_body=medien)
    antwort = None
    while antwort is None:
        fortschritt, antwort = anfrage.next_chunk()
        if fortschritt:
            print(f'  {sprache}: {int(fortschritt.progress() * 100)} %')
    video_id = antwort['id']
    print(f'  {sprache}: hochgeladen → https://youtu.be/{video_id} ({antwort["status"]["privacyStatus"]})')

    vorschau = ordner / meta['vorschau']
    if vorschau.exists():
        try:
            yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(vorschau), mimetype='image/png')).execute()
        except Exception as fehler:  # noqa: BLE001 – eigenes Vorschaubild braucht einen verifizierten Kanal
            print(f'  {sprache}: Vorschaubild nicht gesetzt ({fehler})')

    in_playlist(yt, playlist_id(yt, sprache, sichtbarkeit), video_id)
    return video_id


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ausgabe', required=True, type=Path)
    a = p.parse_args()

    if not all(os.environ.get(k) for k in ('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN')):
        print('YouTube-Zugang nicht eingerichtet (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN) – Upload übersprungen.')
        return 0
    sichtbarkeit = os.environ.get('YT_SICHTBARKEIT', 'private').strip() or 'private'
    if sichtbarkeit not in ('private', 'unlisted', 'public'):
        print(f'Ungültige Sichtbarkeit {sichtbarkeit!r}', file=sys.stderr)
        return 2

    metas = sorted(a.ausgabe.glob('*-youtube.json'))
    if not metas:
        print('Keine Sendung gefunden – nichts hochzuladen.')
        return 0
    yt = dienst()
    vorhanden = vorhandene_uploads(yt)
    ergebnis, fehler = {}, []
    for pfad in metas:
        meta = json.loads(pfad.read_text(encoding='utf-8'))
        try:
            ergebnis[meta['sprache']] = lade_hoch(yt, a.ausgabe, meta, sichtbarkeit, vorhanden)
        except Exception as f:  # noqa: BLE001 – die anderen Sprachen trotzdem hochladen
            print(f'  {meta["sprache"]}: FEHLER {f}', file=sys.stderr)
            fehler.append(meta['sprache'])
    (a.ausgabe / 'youtube-ergebnis.json').write_text(json.dumps(ergebnis, indent=1), encoding='utf-8')
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.stdout.reconfigure(line_buffering=True)
    sys.exit(main())
