#!/usr/bin/env python3
"""
Gazet Morisyen – tägliche Nachrichtensendung als Video (MVP mit Standbildern).

Liest daten.json (Branch zeitung-daten), wählt die Themen der letzten 24 Stunden,
spricht sie mit Piper-Stimmen in Deutsch, Französisch und Englisch und rendert
je Sprache ein MP4 (1920×1080) samt Vorschaubild und YouTube-Texten.

Aufruf:
  python erzeuge_sendung.py --daten daten.json --stimmen <ordner> --ausgabe <ordner>
          [--sprachen de,fr,en] [--jetzt 2026-11-27T09:00:00+04:00]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HIER = Path(__file__).resolve().parent
SCHRIFTEN = HIER / 'schriften'
LOGO = HIER.parent / 'public' / 'icons' / 'gazet-logo.png'

BREITE, HOEHE = 1920, 1080
RAND = 120
MU = dt.timezone(dt.timedelta(hours=4))  # Mauritius, keine Sommerzeit

# Farbwelt der Website
BG = '#fdfaf5'
FG = '#14181f'
MUTED = '#6b6357'
LINE = '#ece3d7'
LAGOON = '#0f6e5c'
ROT = '#c8323c'
FLAGGE = ['#c8323c', '#1f4fa3', '#e0a800', '#1f8a4c']

MAX_THEMEN = 8
PAUSE_S = 0.8  # Stille nach jedem Abschnitt

STIMMEN = {
    'de': ('de_DE-thorsten-high', 'Thorsten-Voice (CC0)'),
    'fr': ('fr_FR-siwis-medium', 'SIWIS French Speech Synthesis Database (CC BY 4.0)'),
    'en': ('en_GB-cori-high', 'Cori, LibriVox (public domain)'),
}

RUBRIKEN = {
    'de': {'politik': 'Politik', 'wirtschaft': 'Wirtschaft', 'soziales': 'Soziales', 'umwelt': 'Umwelt',
           'justiz': 'Polizei & Justiz', 'sport': 'Sport', 'alltag': 'Kultur'},
    'fr': {'politik': 'Politique', 'wirtschaft': 'Économie', 'soziales': 'Société', 'umwelt': 'Environnement',
           'justiz': 'Police & justice', 'sport': 'Sport', 'alltag': 'Culture'},
    'en': {'politik': 'Politics', 'wirtschaft': 'Business', 'soziales': 'Society', 'umwelt': 'Environment',
           'justiz': 'Police & courts', 'sport': 'Sport', 'alltag': 'Culture'},
}

WOCHENTAGE = {
    'de': ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'],
    'fr': ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'],
    'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
}
MONATE = {
    'de': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober',
           'November', 'Dezember'],
    'fr': ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre',
           'novembre', 'décembre'],
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
           'November', 'December'],
}

T = {
    'de': {
        'untertitel': 'Die Tageszeitung für Mauritius',
        'sendung': 'Nachrichten aus Mauritius',
        'top': 'Top-Thema',
        'quelle': 'Quelle',
        'quellen': 'Quellen',
        'zuvor': 'Zuvor',
        'mehr': 'Alle Meldungen und Quellen',
        'newsletter': 'Newsletter: gazet.morisyen.de/newsletter',
        'kapitel_start': 'Begrüßung',
        'kapitel_ende': 'Verabschiedung',
        'titel': 'Nachrichten aus Mauritius · {datum_kurz} | Gazet Morisyen',
        'ki': 'Sprecherstimme synthetisch erzeugt (Piper TTS, Stimme: {stimme}). Texte: eigene Zusammenfassungen der Redaktion Gazet Morisyen.',
        'impressum': 'Impressum: https://gazet.morisyen.de/impressum',
        'heute_themen': 'Die Themen',
    },
    'fr': {
        'untertitel': 'Le quotidien de Maurice',
        'sendung': "L'actualité de Maurice",
        'top': 'À la une',
        'quelle': 'Source',
        'quellen': 'Sources',
        'zuvor': 'Auparavant',
        'mehr': 'Toutes les infos et sources',
        'newsletter': 'Newsletter : gazet.morisyen.de/newsletter',
        'kapitel_start': 'Introduction',
        'kapitel_ende': 'Conclusion',
        'titel': "L'actualité de Maurice · {datum_kurz} | Gazet Morisyen",
        'ki': 'Voix de synthèse (Piper TTS, voix : {stimme}). Textes : résumés rédigés par Gazet Morisyen.',
        'impressum': 'Mentions légales : https://gazet.morisyen.de/impressum',
        'heute_themen': 'Au sommaire',
    },
    'en': {
        'untertitel': 'The daily paper for Mauritius',
        'sendung': 'News from Mauritius',
        'top': 'Top story',
        'quelle': 'Source',
        'quellen': 'Sources',
        'zuvor': 'Previously',
        'mehr': 'All stories and sources',
        'newsletter': 'Newsletter: gazet.morisyen.de/newsletter',
        'kapitel_start': 'Welcome',
        'kapitel_ende': 'Goodbye',
        'titel': 'News from Mauritius · {datum_kurz} | Gazet Morisyen',
        'ki': 'Synthetic narrator voice (Piper TTS, voice: {stimme}). Texts: original summaries by Gazet Morisyen.',
        'impressum': 'Legal notice: https://gazet.morisyen.de/impressum',
        'heute_themen': 'In this edition',
    },
}

# Wechselnde Begrüßungen und Verabschiedungen: Gruß × Beiwort × Wort, je Tag eine andere Kombination.
GRUSS = {
    'de': {
        'gruss': ['Herzlich willkommen', 'Willkommen', 'Ich begrüße Sie', 'Schön, dass Sie dabei sind. Willkommen'],
        'beiwort': ['aktuellen', 'neuesten', 'heutigen'],
        'wort': ['Nachrichten', 'Meldungen', 'Themen'],
        'satz': '{gruss} zu den {beiwort} {wort} aus Mauritius.',
        'abschied': [
            'Das waren die {wort} für heute. Alle Meldungen mit Quellen finden Sie auf gazet punkt morisyen punkt de. Bis morgen.',
            'So weit die {wort} aus Mauritius. Mehr dazu auf gazet punkt morisyen punkt de. Ich wünsche Ihnen einen schönen Tag.',
            'Das war es für heute. Alle Quellen und weitere Meldungen auf gazet punkt morisyen punkt de. Auf Wiedersehen.',
        ],
    },
    'fr': {
        'gruss': ['Bonjour et bienvenue', 'Bienvenue', 'Je vous souhaite la bienvenue', 'Ravi de vous retrouver. Bienvenue'],
        'beiwort': ['', 'dernières', 'principales'],
        'wort': ['nouvelles', 'informations', 'actualités'],
        'satz': '{gruss}. Voici les {beiwort} {wort} de Maurice.',
        'abschied': [
            "C'est tout pour aujourd'hui. Retrouvez toutes les {wort} et leurs sources sur gazet point morisyen point de. À demain.",
            "Voilà pour les {wort} de Maurice. Plus de détails sur gazet point morisyen point de. Bonne journée.",
            "C'était l'essentiel du jour. Toutes les sources sur gazet point morisyen point de. Au revoir.",
        ],
    },
    'en': {
        'gruss': ['Hello and welcome', 'Welcome', 'Good to have you with us. Welcome', 'A warm welcome'],
        'beiwort': ['the latest', "today's", 'the top'],
        'wort': ['news', 'headlines', 'stories'],
        'satz': '{gruss} to {beiwort} {wort} from Mauritius.',
        'abschied': [
            "That's all for today. You'll find every story and its sources at gazet dot morisyen dot de. See you tomorrow.",
            'And those were the {wort} from Mauritius. More at gazet dot morisyen dot de. Have a good day.',
            "That's it for now. All sources at gazet dot morisyen dot de. Goodbye.",
        ],
    },
}


def gruss_und_abschied(sprache: str, tag: dt.date) -> tuple[str, str]:
    k = GRUSS[sprache]
    n = tag.toordinal()
    wort = k['wort'][n % len(k['wort'])]
    satz = k['satz'].format(gruss=k['gruss'][(n // 3) % len(k['gruss'])],
                            beiwort=k['beiwort'][(n // 2) % len(k['beiwort'])], wort=wort)
    abschied = k['abschied'][n % len(k['abschied'])].format(wort=wort)
    return re.sub(r'\s+', ' ', satz), abschied


# ----------------------------------------------------------------- Daten

def iso(wert: str) -> dt.datetime:
    return dt.datetime.fromisoformat(wert.replace('Z', '+00:00'))


def datum_lang(tag: dt.date, sprache: str) -> str:
    wt = WOCHENTAGE[sprache][tag.weekday()]
    mo = MONATE[sprache][tag.month - 1]
    if sprache == 'de':
        return f'{wt}, der {tag.day}. {mo} {tag.year}'
    if sprache == 'fr':
        tag_text = '1er' if tag.day == 1 else str(tag.day)
        return f'{wt} {tag_text} {mo} {tag.year}'
    return f'{wt}, {tag.day} {mo} {tag.year}'


def datum_anzeige(tag: dt.date, sprache: str) -> str:
    """Datum für Bild und Titel (ohne „der“)."""
    return datum_lang(tag, sprache).replace(', der ', ', ')


def datum_kurz(tag: dt.date, sprache: str) -> str:
    if sprache == 'en':
        return f'{tag.day} {MONATE["en"][tag.month - 1][:3]} {tag.year}'
    if sprache == 'fr':
        return f'{tag.day:02d}/{tag.month:02d}/{tag.year}'
    return f'{tag.day:02d}.{tag.month:02d}.{tag.year}'


def feld(update: dict, name: str, sprache: str) -> str:
    if sprache != 'de':
        wert = (update.get('i18n') or {}).get(sprache, {}).get(name)
        if wert:
            return wert
    return update.get(name, '')


@dataclass
class Beitrag:
    thema: dict
    update: dict
    top: bool

    @property
    def vorher(self) -> dict | None:
        updates = self.thema.get('updates', [])
        return updates[1] if len(updates) > 1 else None


def saetze(text: str) -> list[str]:
    text = re.sub(r'\s+', ' ', text).strip()
    return [x for x in re.split(r'(?<=[.!?…])\s+(?=[A-ZÀ-ÖØ-Þ0-9«„"])', text) if x]


def kuerze(text: str, zeichen: int) -> str:
    """Die ersten ganzen Sätze bis etwa `zeichen` Zeichen."""
    ergebnis = ''
    for satz in saetze(text):
        if ergebnis and len(ergebnis) + len(satz) > zeichen:
            break
        ergebnis = f'{ergebnis} {satz}'.strip()
    return ergebnis


def sendetext(b: Beitrag, name: str, sprache: str) -> str:
    """Vom Redaktions-Agenten geschriebener Sende-Text (update.sendung.<sprache>.<name>), falls vorhanden."""
    return ((b.update.get('sendung') or {}).get(sprache) or {}).get(name, '').strip()


def sprech_beitrag(b: Beitrag, sprache: str) -> str:
    """Was der Sprecher liest: ohne Schlagzeile; mit kurzem Rückblick, wenn es vorher schon Meldungen gab."""
    eigen = sendetext(b, 'sprechtext', sprache)
    if eigen:
        return eigen
    text = feld(b.update, 'text', sprache)
    if b.vorher:
        rueck = kuerze(feld(b.vorher, 'text', sprache), 160)
        if rueck:
            text += f' {T[sprache]["zuvor"]}: {rueck}'
    return text


def anzeige_beitrag(b: Beitrag, sprache: str) -> str:
    return sendetext(b, 'kurz', sprache) or kuerze(feld(b.update, 'text', sprache), 230)


def waehle_themen(daten: dict, jetzt: dt.datetime) -> list[Beitrag]:
    """Themen mit Meldung in den letzten 24 Stunden; Top-Themen zuerst, sonst neueste zuerst."""
    themen = [t for t in daten.get('topics', []) if t.get('status') != 'archiv' and t.get('updates')]
    grenze = jetzt - dt.timedelta(hours=24)

    def top_aktuell(t: dict) -> bool:
        if t.get('top'):
            return True
        seit = t.get('topSeit')
        return bool(seit) and iso(seit) >= grenze

    frisch = [t for t in themen if iso(t['aktualisiert']) >= grenze or top_aktuell(t)]
    if len(frisch) < 3:  # ruhiger Tag: mit den neuesten Themen auffüllen
        rest = sorted((t for t in themen if t not in frisch), key=lambda t: t['aktualisiert'], reverse=True)
        frisch += rest[: 3 - len(frisch)]

    frisch.sort(key=lambda t: (not t.get('top'), not top_aktuell(t), -iso(t['aktualisiert']).timestamp()))
    return [Beitrag(t, t['updates'][0], top_aktuell(t)) for t in frisch[:MAX_THEMEN]]


# ----------------------------------------------------------------- Sprache

AUSSPRACHE = json.loads((HIER / 'aussprache.json').read_text(encoding='utf-8'))


def aussprache(text: str, sprache: str) -> str:
    """Wendet das Aussprache-Verzeichnis an (nur für den Ton)."""
    regeln = AUSSPRACHE.get(sprache, {})
    for muster, ersatz in regeln.get('muster', []):
        text = re.sub(muster, ersatz, text)
    for wort in sorted(regeln.get('woerter', {}), key=len, reverse=True):
        text = re.sub(rf'(?<![\w-]){re.escape(wort)}(?![\w-])', regeln['woerter'][wort], text)
    wortweise = set(regeln.get('abkuerzungen_wortweise', []))

    def buchstabiere(m: re.Match) -> str:
        w = m.group(0)
        return w if w in wortweise else ' '.join(w)

    return re.sub(r'(?<![\w])[A-Z]{2,5}(?![a-zäöüéèàç])', buchstabiere, text)


def sprechtext(text: str, sprache: str = 'de') -> str:
    """Bereinigt Text für die Sprachausgabe."""
    text = re.sub(r'https?://\S+', '', text)
    text = text.replace('«', '').replace('»', '').replace('„', '').replace('“', '').replace('"', '')
    text = text.replace(' – ', ', ').replace(' — ', ', ')
    text = re.sub(r'\s+', ' ', text)
    return aussprache(text.strip(), sprache)


class Sprecher:
    def __init__(self, modell: Path, sprache: str):
        self.sprache = sprache
        from piper import PiperVoice, SynthesisConfig  # erst hier: Bildtests brauchen kein Piper

        self.stimme = PiperVoice.load(str(modell))
        self.konfig = SynthesisConfig(length_scale=1.06)
        self.rate = self.stimme.config.sample_rate

    def sprich(self, text: str, ziel: Path, mindestens: float = 0.0) -> float:
        with wave.open(str(ziel), 'wb') as datei:
            self.stimme.synthesize_wav(sprechtext(text, self.sprache), datei, syn_config=self.konfig)
            # Stille anhängen
            datei.writeframes(b'\x00\x00' * int(self.rate * PAUSE_S))
        with wave.open(str(ziel), 'rb') as datei:
            dauer = datei.getnframes() / datei.getframerate()
        if dauer < mindestens:  # z. B. Startfolie: lange genug zum Lesen der Themen
            with wave.open(str(ziel), 'rb') as datei:
                params, frames = datei.getparams(), datei.readframes(datei.getnframes())
            with wave.open(str(ziel), 'wb') as datei:
                datei.setparams(params)
                datei.writeframes(frames + b'\x00\x00' * int(self.rate * (mindestens - dauer)))
            dauer = mindestens
        return dauer


# ----------------------------------------------------------------- Bilder

def schrift(name: str, groesse: int, gewicht: int | None = None) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(SCHRIFTEN / name), groesse)
    if gewicht is not None:
        achsen = f.get_variation_axes()
        werte = []
        for achse in achsen:
            n = achse['name'].decode() if isinstance(achse['name'], bytes) else achse['name']
            if n == 'Weight':
                werte.append(gewicht)
            elif n.lower().startswith('optical'):
                werte.append(min(achse['maximum'], max(achse['minimum'], groesse * 0.75)))
            else:
                werte.append(achse['default'])
        f.set_variation_by_axes(werte)
    return f


def titel_schrift(g: int) -> ImageFont.FreeTypeFont:
    return schrift('BricolageGrotesque.ttf', g, 760)


def text_schrift(g: int) -> ImageFont.FreeTypeFont:
    return schrift('SourceSerif4.ttf', g, 400)


def mono(g: int, medium: bool = False) -> ImageFont.FreeTypeFont:
    return schrift('IBMPlexMono-Medium.ttf' if medium else 'IBMPlexMono-Regular.ttf', g)


def umbrechen(zeichnung: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, breite: int) -> list[str]:
    zeilen: list[str] = []
    for absatz in text.split('\n'):
        woerter = absatz.split()
        if not woerter:
            zeilen.append('')
            continue
        zeile = woerter[0]
        for wort in woerter[1:]:
            probe = f'{zeile} {wort}'
            if zeichnung.textlength(probe, font=f) <= breite:
                zeile = probe
            else:
                zeilen.append(zeile)
                zeile = wort
        zeilen.append(zeile)
    return zeilen


def gesperrt(zeichnung: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, f, farbe: str, abstand: float = 0.12,
             rechts: bool = False) -> None:
    """Mono-Text in Großbuchstaben mit Laufweite (wie auf der Website)."""
    text = text.upper()
    zusatz = f.size * abstand
    breite = sum(zeichnung.textlength(z, font=f) + zusatz for z in text) - zusatz
    x, y = xy
    if rechts:
        x -= breite
    for z in text:
        zeichnung.text((x, y), z, font=f, fill=farbe)
        x += zeichnung.textlength(z, font=f) + zusatz


_logo_cache: dict[int, Image.Image] = {}


def logo(groesse: int) -> Image.Image:
    if groesse not in _logo_cache:
        _logo_cache[groesse] = Image.open(LOGO).convert('RGBA').resize((groesse, groesse), Image.LANCZOS)
    return _logo_cache[groesse]


def grundbild(sprache: str, tag: dt.date, seite: str | None = None) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    bild = Image.new('RGB', (BREITE, HOEHE), BG)
    z = ImageDraw.Draw(bild)
    streifen = BREITE / 4
    for i, farbe in enumerate(FLAGGE):
        z.rectangle([round(i * streifen), 0, round((i + 1) * streifen), 14], fill=farbe)
    # Kopfzeile
    bild.paste(logo(76), (RAND - 6, 46), logo(76))
    z.text((RAND + 86, 52), 'Gazet Morisyen', font=titel_schrift(40), fill=FG)
    gesperrt(z, (RAND + 88, 102), T[sprache]['sendung'], mono(20), MUTED)
    gesperrt(z, (BREITE - RAND, 62), datum_anzeige(tag, sprache), mono(22, True), FG, 0.06, rechts=True)
    if seite:
        gesperrt(z, (BREITE - RAND, 98), seite, mono(20), MUTED, 0.06, rechts=True)
    z.line([RAND, 150, BREITE - RAND, 150], fill=LINE, width=2)
    return bild, z


def bild_intro(sprache: str, tag: dt.date, schlagzeilen: list[str], ziel: Path) -> None:
    bild = Image.new('RGB', (BREITE, HOEHE), BG)
    z = ImageDraw.Draw(bild)
    streifen = BREITE / 4
    for i, farbe in enumerate(FLAGGE):
        z.rectangle([round(i * streifen), 0, round((i + 1) * streifen), 18], fill=farbe)
    gross = 230
    bild.paste(logo(gross), (RAND - 20, 110), logo(gross))
    z.text((RAND + gross + 10, 150), 'Gazet Morisyen', font=titel_schrift(116), fill=FG)
    gesperrt(z, (RAND + gross + 16, 290), T[sprache]['untertitel'], mono(28), MUTED)
    gesperrt(z, (RAND, 400), datum_anzeige(tag, sprache), mono(32, True), LAGOON, 0.08)
    z.line([RAND, 462, BREITE - RAND, 462], fill=LINE, width=2)
    gesperrt(z, (RAND, 492), T[sprache]['heute_themen'], mono(24, True), ROT)
    f = titel_schrift(38)
    nr = mono(25, True)
    zeilen_h = 56
    platz = (HOEHE - 60 - 545) // zeilen_h
    for i, titel in enumerate(schlagzeilen[:platz]):
        y = 545 + i * zeilen_h
        z.text((RAND, y + 8), f'{i + 1:02d}', font=nr, fill=MUTED)
        text = titel
        while z.textlength(text, font=f) > BREITE - 2 * RAND - 80 and ' ' in text:
            text = text.rsplit(' ', 1)[0].rstrip(' ,:;–-') + ' …'
        z.text((RAND + 80, y), text, font=f, fill=FG)
    bild.save(ziel)


def bild_beitrag(sprache: str, tag: dt.date, b: Beitrag, nummer: int, anzahl: int, ziel: Path) -> None:
    bild, z = grundbild(sprache, tag, f'{nummer} / {anzahl}')
    breite = BREITE - 2 * RAND
    y = 200
    marke = RUBRIKEN[sprache].get(b.thema.get('rubrik', ''), '')
    if b.thema.get('ort'):
        marke += f' · {b.thema["ort"]}'
    if b.top:
        marke = f'{T[sprache]["top"]} · {marke}'
    gesperrt(z, (RAND, y), marke, mono(26, True), ROT)
    y += 62

    titel = feld(b.update, 'titel', sprache)
    for g in (92, 84, 76, 68, 60):
        f = titel_schrift(g)
        zeilen = umbrechen(z, titel, f, breite)
        if len(zeilen) <= 3:
            break
    for zeile in zeilen[:3]:
        z.text((RAND, y), zeile, font=f, fill=FG)
        y += round(f.size * 1.12)
    y += 40

    # Rückblick als eine Zeile unten, falls es frühere Meldungen gibt
    unten = HOEHE - 150
    if b.vorher:
        vorher_titel = feld(b.vorher, 'titel', sprache)
        tag_vorher = iso(b.vorher['zeit']).astimezone(MU).date()
        kopf = f'{T[sprache]["zuvor"]} · {tag_vorher.day:02d}.{tag_vorher.month:02d}.'
        fz = mono(24, True)
        fv = text_schrift(32)
        while z.textlength(vorher_titel, font=fv) > breite and ' ' in vorher_titel:
            vorher_titel = vorher_titel.rsplit(' ', 1)[0].rstrip(' ,:;–-') + ' …'
        unten -= 118
        z.line([RAND, unten, RAND + 80, unten], fill=LAGOON, width=4)
        gesperrt(z, (RAND, unten + 20), kopf, fz, LAGOON, 0.08)
        z.text((RAND, unten + 58), vorher_titel, font=fv, fill=MUTED)
        unten -= 30

    text = anzeige_beitrag(b, sprache)
    platz = unten - y
    for g in (48, 44, 40, 36, 33):
        f = text_schrift(g)
        zh = round(g * 1.45)
        zeilen = umbrechen(z, text, f, breite)
        if len(zeilen) * zh <= platz:
            break
    max_zeilen = max(1, platz // zh)
    if len(zeilen) > max_zeilen:
        zeilen = zeilen[:max_zeilen]
        zeilen[-1] = zeilen[-1].rstrip(' .,;:') + ' …'
    for zeile in zeilen:
        z.text((RAND, y), zeile, font=f, fill=FG)
        y += zh

    quellen = [q.get('name', '') for q in b.update.get('quellen', []) if q.get('name')]
    if quellen:
        wort = T[sprache]['quellen' if len(quellen) > 1 else 'quelle']
        z.line([RAND, HOEHE - 118, BREITE - RAND, HOEHE - 118], fill=LINE, width=2)
        z.text((RAND, HOEHE - 92), f'{wort}: ' + ' · '.join(dict.fromkeys(quellen)), font=mono(26), fill=MUTED)
        gesperrt(z, (BREITE - RAND, HOEHE - 90), 'gazet.morisyen.de', mono(24, True), LAGOON, 0.04, rechts=True)
    bild.save(ziel)


def bild_outro(sprache: str, tag: dt.date, ziel: Path) -> None:
    bild = Image.new('RGB', (BREITE, HOEHE), BG)
    z = ImageDraw.Draw(bild)
    streifen = BREITE / 4
    for i, farbe in enumerate(FLAGGE):
        z.rectangle([round(i * streifen), HOEHE - 18, round((i + 1) * streifen), HOEHE], fill=farbe)
    g = 320
    bild.paste(logo(g), ((BREITE - g) // 2, 120), logo(g))
    f = titel_schrift(96)
    text = 'gazet.morisyen.de'
    z.text(((BREITE - z.textlength(text, font=f)) / 2, 500), text, font=f, fill=LAGOON)
    f2 = mono(32)
    for i, zeile in enumerate([T[sprache]['mehr'], T[sprache]['newsletter']]):
        z.text(((BREITE - z.textlength(zeile, font=f2)) / 2, 660 + i * 60), zeile, font=f2, fill=MUTED)
    bild.save(ziel)


def bild_vorschau(sprache: str, tag: dt.date, ziel: Path) -> None:
    """YouTube-Vorschaubild 1280×720: Logo und Datum."""
    w, h = 1280, 720
    bild = Image.new('RGB', (w, h), BG)
    z = ImageDraw.Draw(bild)
    for i, farbe in enumerate(FLAGGE):
        z.rectangle([round(i * w / 4), 0, round((i + 1) * w / 4), 22], fill=farbe)
        z.rectangle([round(i * w / 4), h - 22, round((i + 1) * w / 4), h], fill=farbe)
    g = 430
    bild.paste(logo(g), ((w - g) // 2, 70), logo(g))
    f = mono(46, True)
    text = datum_kurz(tag, sprache)
    abstand = 46 * 0.14
    breite = sum(z.textlength(c, font=f) + abstand for c in text) - abstand
    gesperrt(z, (round((w - breite) / 2), 560), text, f, LAGOON, 0.14)
    bild.save(ziel)


# ----------------------------------------------------------------- Video

def ffmpeg(*args: str) -> None:
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *args], check=True)


def abschnitt_video(bild: Path, ton: Path, ziel: Path) -> None:
    ffmpeg('-loop', '1', '-framerate', '25', '-i', str(bild), '-i', str(ton),
           '-c:v', 'libx264', '-tune', 'stillimage', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
           '-r', '25', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-ac', '2', '-shortest', '-movflags', '+faststart',
           str(ziel))


def zeitmarke(sekunden: float) -> str:
    s = int(sekunden)
    return f'{s // 60:02d}:{s % 60:02d}'


@dataclass
class Abschnitt:
    kapitel: str
    sprechen: str
    bild: Path
    dauer: float = 0.0
    quellen: list[dict] = field(default_factory=list)
    mindestens: float = 0.0


def erzeuge(daten: dict, sprache: str, stimmen: Path, ausgabe: Path, jetzt: dt.datetime) -> dict:
    t = T[sprache]
    tag = jetzt.astimezone(MU).date()
    beitraege = waehle_themen(daten, jetzt)
    einleitung = ''
    if daten.get('einleitung'):
        einleitung = daten['einleitung'].get(sprache) or daten['einleitung'].get('de', '')
    gruss, abschied = gruss_und_abschied(sprache, tag)

    arbeit = Path(tempfile.mkdtemp(prefix=f'sendung-{sprache}-'))
    abschnitte: list[Abschnitt] = []

    intro = arbeit / '00-intro.png'
    schlagzeilen = [feld(b.update, 'titel', sprache) for b in beitraege]
    bild_intro(sprache, tag, schlagzeilen, intro)
    abschnitte.append(Abschnitt(t['kapitel_start'], gruss, intro, mindestens=7.0))

    for i, b in enumerate(beitraege, 1):
        pfad = arbeit / f'{i:02d}-thema.png'
        bild_beitrag(sprache, tag, b, i, len(beitraege), pfad)
        abschnitte.append(Abschnitt(feld(b.update, 'titel', sprache), sprech_beitrag(b, sprache), pfad,
                                    quellen=b.update.get('quellen', [])))

    outro = arbeit / '99-outro.png'
    bild_outro(sprache, tag, outro)
    abschnitte.append(Abschnitt(t['kapitel_ende'], abschied, outro))

    modell, stimme_name = STIMMEN[sprache]
    sprecher = Sprecher(stimmen / f'{modell}.onnx', sprache)
    teile = []
    for i, a in enumerate(abschnitte):
        ton = arbeit / f'{i:02d}.wav'
        a.dauer = sprecher.sprich(a.sprechen, ton, a.mindestens)
        teil = arbeit / f'{i:02d}.mp4'
        abschnitt_video(a.bild, ton, teil)
        teile.append(teil)

    liste = arbeit / 'liste.txt'
    liste.write_text(''.join(f"file '{p}'\n" for p in teile))
    ausgabe.mkdir(parents=True, exist_ok=True)
    stamm = f'gazet-morisyen-{tag.isoformat()}-{sprache}'
    video = ausgabe / f'{stamm}.mp4'
    ffmpeg('-f', 'concat', '-safe', '0', '-i', str(liste), '-c', 'copy', '-movflags', '+faststart', str(video))
    bild_vorschau(sprache, tag, ausgabe / f'{stamm}-vorschau.png')

    # YouTube-Texte
    kapitel, quellen_zeilen, start = [], [], 0.0
    for a in abschnitte:
        kapitel.append(f'{zeitmarke(start)} {a.kapitel}')
        start += a.dauer
    for b in beitraege:
        quellen_zeilen.append(f'• {feld(b.update, "titel", sprache)}')
        for q in b.update.get('quellen', []):
            quellen_zeilen.append(f'  {q.get("name", "")}: {q.get("url", "")}')
    titel = t['titel'].format(datum_kurz=datum_kurz(tag, sprache))[:100]
    beschreibung = '\n'.join([
        einleitung or t['sendung'],
        '',
        f'{t["heute_themen"]}:',
        *kapitel,
        '',
        f'{t["quellen"]}:',
        *quellen_zeilen,
        '',
        '🌐 https://gazet.morisyen.de',
        '✉️ https://gazet.morisyen.de/newsletter',
        '',
        t['ki'].format(stimme=stimme_name),
        t['impressum'],
    ])
    (ausgabe / f'{stamm}-youtube.txt').write_text(
        f'TITEL:\n{titel}\n\nBESCHREIBUNG:\n{beschreibung}\n\nTAGS:\n'
        'Mauritius, Maurice, Nachrichten, actualités, news, Port-Louis, Rodrigues, Gazet Morisyen\n',
        encoding='utf-8')
    shutil.rmtree(arbeit, ignore_errors=True)
    return {'sprache': sprache, 'video': str(video), 'dauer_s': round(start, 1), 'themen': len(beitraege)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--daten', required=True, type=Path)
    p.add_argument('--stimmen', required=True, type=Path)
    p.add_argument('--ausgabe', required=True, type=Path)
    p.add_argument('--sprachen', default='de,fr,en')
    p.add_argument('--jetzt', help='ISO-Zeit, Standard: jetzt')
    a = p.parse_args()

    daten = json.loads(a.daten.read_text(encoding='utf-8'))
    jetzt = iso(a.jetzt) if a.jetzt else dt.datetime.now(dt.timezone.utc)
    stand = iso(daten['stand'])
    if jetzt - stand > dt.timedelta(hours=36):
        print(f'Daten veraltet (Stand {daten["stand"]}) – keine Sendung.', file=sys.stderr)
        return 2
    for sprache in a.sprachen.split(','):
        print(json.dumps(erzeuge(daten, sprache.strip(), a.stimmen, a.ausgabe, jetzt), ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
