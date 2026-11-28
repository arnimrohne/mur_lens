#!/usr/bin/env python3
"""
Prüfwerkzeuge für Lernvideos „Gazet Morisyen erklärt“.

    python3 lernvideo_pruefen.py satzzahl --video wasser
        Gleiche Satzzahl je Szene in DE/EN/FR? (Die Animationen hängen an den Satzanfängen.)
    python3 lernvideo_pruefen.py kontaktbogen --video wasser --sprache en --ziel bogen.png
        Standbild jeder Szene (ohne Ton gerechnet) als Übersicht, um Texte, Überlappungen und Übersetzungen zu sehen.
    python3 lernvideo_pruefen.py timing --mp4 video.mp4 --srt video.en.srt --ziel timing.png [--suche "Together" ...]
        Je Satz (oder nur die gesuchten) ein Bild 0,3 s vor und 1,2 s nach dem Satzanfang: erscheint das Element zum Satz?
    python3 lernvideo_pruefen.py transkript --mp4 video.mp4 --sprache de [--whisper <python einer venv mit faster-whisper>]
        Transkription mit Zeiten, um Aussprachefehler zu finden (Zahlen, Namen, Fremdwörter).
"""

from __future__ import annotations

import argparse
import importlib
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

import lernvideo as lv


def video_modul(name: str):
    v = importlib.import_module(f'lernvideos.{name}')
    lv.VIDEO = v
    return v


def satzzahl(a) -> int:
    v = video_modul(a.video)
    fehler = 0
    for szene in v.SZENEN:
        de = len(lv.saetze_trennen(szene.text))
        for sp, texte in v.TEXTE.items():
            n = len(lv.saetze_trennen(texte[szene.nr]))
            if n != de:
                fehler += 1
                print(f'Szene {szene.nr}: de {de} Sätze, {sp} {n} Sätze')
    print('Satzzahl stimmt in allen Szenen.' if not fehler else f'{fehler} Abweichungen.')
    return 1 if fehler else 0


def kontaktbogen(a) -> int:
    v = video_modul(a.video)
    lv.SPRACHE = a.sprache
    bilder = []
    for szene in v.SZENEN:
        szene.saetze = [(0.5, 2.5, ''), (2.8, 5, ''), (5.3, 7, ''), (7.3, 9, ''), (9.3, 11, '')]
        szene.dauer = 12
        bild = szene.zeichne(a.zeit, szene)
        lv.rahmen(bild, szene.quelle, '')
        bilder.append(bild.resize((480, 270)))
    spalten = 4
    bogen = Image.new('RGB', (480 * spalten, 270 * ((len(bilder) + spalten - 1) // spalten)))
    for i, b in enumerate(bilder):
        bogen.paste(b, ((i % spalten) * 480, (i // spalten) * 270))
    bogen.save(a.ziel)
    print(a.ziel)
    return 0


def _sek(x: str) -> float:
    h, m, rest = x.split(':')
    s, ms = rest.split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def timing(a) -> int:
    srt = Path(a.srt).read_text(encoding='utf-8')
    saetze = [(_sek(m.group(1)), m.group(3)) for m in
              re.finditer(r'(\d\d:\d\d:\d\d,\d+) --> (\d\d:\d\d:\d\d,\d+)\n(.+)', srt)]
    if a.suche:
        saetze = [(t, s) for t, s in saetze if any(s.startswith(x) for x in a.suche)]
    bilder = []
    for t, satz in saetze:
        for versatz in (-0.3, 1.2):
            aus = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', str(max(0.0, t + versatz)), '-i', a.mp4,
                                  '-frames:v', '1', '-vf', 'scale=480:-1', '-f', 'image2pipe', '-vcodec', 'png', '-'],
                                 capture_output=True, check=True).stdout
            from io import BytesIO
            bilder.append(Image.open(BytesIO(aus)).convert('RGB'))
        print(f'{t:7.2f}  {satz[:70]}')
    bogen = Image.new('RGB', (960, 270 * len(saetze)))
    for i, b in enumerate(bilder):
        bogen.paste(b, ((i % 2) * 480, (i // 2) * 270))
    bogen.save(a.ziel)
    print(a.ziel)
    return 0


def transkript(a) -> int:
    skript = f'''
import subprocess, numpy as np
from faster_whisper import WhisperModel
roh = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', {a.mp4!r}, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                     capture_output=True, check=True).stdout
m = WhisperModel('small', device='cpu', compute_type='int8')
seg, _ = m.transcribe(np.frombuffer(roh, np.float32), language={a.sprache!r})
for s in seg:
    print(f'{{s.start:7.1f}}  {{s.text.strip()}}')
'''
    return subprocess.run([a.whisper, '-c', skript], env={'HF_HUB_DISABLE_XET': '1', **__import__('os').environ}).returncode


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    u = p.add_subparsers(dest='befehl', required=True)
    s = u.add_parser('satzzahl')
    s.add_argument('--video', default='wasser')
    k = u.add_parser('kontaktbogen')
    k.add_argument('--video', default='wasser')
    k.add_argument('--sprache', default='de')
    k.add_argument('--zeit', type=float, default=7.5, help='Zeitpunkt in der Szene (s), bei Szenendauer 12 s')
    k.add_argument('--ziel', required=True)
    t = u.add_parser('timing')
    t.add_argument('--mp4', required=True)
    t.add_argument('--srt', required=True)
    t.add_argument('--suche', nargs='*')
    t.add_argument('--ziel', required=True)
    r = u.add_parser('transkript')
    r.add_argument('--mp4', required=True)
    r.add_argument('--sprache', default='de')
    r.add_argument('--whisper', default=sys.executable, help='Python mit faster-whisper')
    a = p.parse_args()
    return {'satzzahl': satzzahl, 'kontaktbogen': kontaktbogen, 'timing': timing, 'transkript': transkript}[a.befehl](a)


if __name__ == '__main__':
    sys.exit(main())
