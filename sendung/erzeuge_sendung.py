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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wetter as wetterdienst  # noqa: E402

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
SATZ_PAUSE_S = 0.45  # Pause zwischen zwei Sätzen
KOMMA_PAUSE_S = 0.25  # Pause nach Doppelpunkt oder Semikolon

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
        'wetter': ('Wetter heute', 'Wetter morgen'),
        'regen': 'Regen',
        'wetterquelle': 'Wetterdaten: MET Norway (CC BY 4.0)',
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
        'wetter': ('Météo du jour', 'Météo de demain'),
        'regen': 'Pluie',
        'wetterquelle': 'Données météo : MET Norway (CC BY 4.0)',
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
        'wetter': ('Weather today', 'Weather tomorrow'),
        'regen': 'Rain',
        'wetterquelle': 'Weather data: MET Norway (CC BY 4.0)',
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
            'Das waren die {wort} für heute. Alle Meldungen mit Quellen finden Sie auf gazet punkt morisyen punkt D E. Bis morgen.',
            'So weit die {wort} aus Mauritius. Mehr dazu auf gazet punkt morisyen punkt D E. Ich wünsche Ihnen einen schönen Tag.',
            'Das war es für heute. Alle Quellen und weitere Meldungen auf gazet punkt morisyen punkt D E. Auf Wiedersehen.',
        ],
    },
    'fr': {
        'gruss': ['Bonjour et bienvenue', 'Bienvenue', 'Je vous souhaite la bienvenue', 'Ravi de vous retrouver. Bienvenue'],
        'beiwort': ['', 'dernières', 'principales'],
        'wort': ['nouvelles', 'informations', 'actualités'],
        'satz': '{gruss}. Voici les {beiwort} {wort} de Maurice.',
        'abschied': [
            "C'est tout pour aujourd'hui. Retrouvez toutes les {wort} et leurs sources sur gazet point morisyen point D E. À demain.",
            "Voilà pour les {wort} de Maurice. Plus de détails sur gazet point morisyen point D E. Bonne journée.",
            "C'était l'essentiel du jour. Toutes les sources sur gazet point morisyen point D E. Au revoir.",
        ],
    },
    'en': {
        'gruss': ['Hello and welcome', 'Welcome', 'Good to have you with us. Welcome', 'A warm welcome'],
        'beiwort': ['the latest', "today's", 'the top'],
        'wort': ['news', 'headlines', 'stories'],
        'satz': '{gruss} to {beiwort} {wort} from Mauritius.',
        'abschied': [
            "That's all for today. You'll find every story and its sources at gazet dot morisyen dot D E. See you tomorrow.",
            'And those were the {wort} from Mauritius. More at gazet dot morisyen dot D E. Have a good day.',
            "That's it for now. All sources at gazet dot morisyen dot D E. Goodbye.",
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


def stichpunkte(b: Beitrag, sprache: str) -> list[str]:
    """Stichpunkte (gekürzte Fassung) für die Folie, geschrieben vom Redaktions-Agenten (sendung.<sprache>.stichpunkte)."""
    eigen = ((b.update.get('sendung') or {}).get(sprache) or {}).get('stichpunkte')
    if isinstance(eigen, list) and eigen:
        return [str(x).strip() for x in eigen if str(x).strip()][:5]
    return []  # ohne Kurzfassung der Redaktion: nur Schlagzeile und Rückblick


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


# --- Ordnungszahlen bei Datumsangaben ("25. Februar" → "fünfundzwanzigste Februar")

_EINER = ['', 'ein', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben', 'acht', 'neun']
_ORD_DE = {1: 'erste', 2: 'zweite', 3: 'dritte', 4: 'vierte', 5: 'fünfte', 6: 'sechste', 7: 'siebte', 8: 'achte',
           9: 'neunte', 10: 'zehnte', 11: 'elfte', 12: 'zwölfte', 13: 'dreizehnte', 14: 'vierzehnte',
           15: 'fünfzehnte', 16: 'sechzehnte', 17: 'siebzehnte', 18: 'achtzehnte', 19: 'neunzehnte'}


def ordnungszahl_de(n: int, gebeugt: bool) -> str:
    if n in _ORD_DE:
        wort = _ORD_DE[n]
    else:
        zehner = {2: 'zwanzig', 3: 'dreißig'}[n // 10]
        wort = (f'{_EINER[n % 10]}und{zehner}' if n % 10 else zehner) + 'ste'
    return wort + ('n' if gebeugt else '')


def _num2words(*args, **kwargs) -> str:
    from num2words import num2words

    return num2words(*args, **kwargs)


_GEBEUGT_VOR = re.compile(r'(?:\b(?:am|vom|zum|beim|im|seit|ab|dem|den|des)\s+)$', re.I)


def daten_sprechen(text: str, sprache: str) -> str:
    if sprache == 'de':
        monate = MONATE['de']

        def ersetze(m: re.Match, monat: str, rest: str = '') -> str:
            tag = int(m.group(1))
            if not 1 <= tag <= 31:
                return m.group(0)
            gebeugt = bool(_GEBEUGT_VOR.search(text[:m.start()]))
            return f'{ordnungszahl_de(tag, gebeugt)} {monat}{rest}'

        # 25.11.2026 / 25.11.
        text = re.sub(r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})?(?!\d)',
                      lambda m: ersetze(m, monate[int(m.group(2)) - 1] if 1 <= int(m.group(2)) <= 12 else m.group(2),
                                        f' {m.group(3)}' if m.group(3) else ''), text)
        # 25. Februar
        text = re.sub(rf'\b(\d{{1,2}})\.\s+({"|".join(monate)})\b', lambda m: ersetze(m, m.group(2)), text)
        # „der 55. Jahrestag“, „zum 3. Mal“: Ordnungszahl nach Artikel/Präposition
        def allgemein(m: re.Match) -> str:
            gebeugt = m.group(1).lower() in {'am', 'vom', 'zum', 'beim', 'im', 'dem', 'den', 'des', 'seinem',
                                             'ihrem', 'seinen', 'ihren', 'zur'}
            wort = _num2words(int(m.group(2)), lang='de', to='ordinal')
            return f'{m.group(1)} {wort}{"n" if gebeugt else ""}'

        text = re.sub(r'\b(der|die|das|dem|den|des|am|vom|zum|zur|beim|im|sein|seine|seinem|seinen|ihr|ihre|ihrem|ihren)'
                      r'\s+(\d{1,4})\.(?=\s+[A-ZÄÖÜ])', allgemein, text, flags=re.I)
    elif sprache == 'fr':
        text = re.sub(r'\b1(er|re)\b', lambda m: 'premier' if m.group(1) == 'er' else 'première', text)
        text = re.sub(r'\b(\d{1,4})(?:e|ème)\b', lambda m: _num2words(int(m.group(1)), lang='fr', to='ordinal'), text)
    if sprache == 'en':
        text = re.sub(r'\b(\d{1,4})(st|nd|rd|th)\b', lambda m: _num2words(int(m.group(1)), lang='en', to='ordinal'), text)
        monate = '|'.join(MONATE['en'])
        text = re.sub(rf'\b(?:on\s+)?(\d{{1,2}})\s+({monate})\b',
                      lambda m: f'{"on " if m.group(0).lower().startswith("on") else ""}the '
                                f'{_num2words(int(m.group(1)), lang="en", to="ordinal")} of {m.group(2)}', text)
    return text


# --- Französische Namen in der deutschen und englischen Stimme

_FR_ZU = {
    'de': [('ɑ̃', 'aŋ'), ('ɛ̃', 'ɛŋ'), ('ɔ̃', 'ɔŋ'), ('œ̃', 'œŋ'), ('ʁ', 'r'), ('ɥ', 'y'), ('-', ' ')],
    'en': [('ɑ̃', 'ɒŋ'), ('ɛ̃', 'aŋ'), ('ɔ̃', 'ɒŋ'), ('œ̃', 'aŋ'), ('ʁ', 'ɹ'), ('ɥ', 'w'), ('y', 'uː'), ('ø', 'ɜː'),
           ('œ', 'ɜː'), ('-', ' ')],
}
_FR_NAMEN: dict[str, dict[str, str]] = {}


def lade_franzoesische_namen(stimmen: Path) -> None:
    """Ermittelt mit der französischen Stimme die Lautung der Namen aus aussprache.json → 'franzoesisch'."""
    namen = AUSSPRACHE.get('franzoesisch', [])
    modell = stimmen / f'{STIMMEN["fr"][0]}.onnx'
    if not namen or not modell.exists() or _FR_NAMEN:
        return
    from piper import PiperVoice

    fr = PiperVoice.load(str(modell))
    for sprache, tabelle in _FR_ZU.items():
        ziel = _FR_NAMEN.setdefault(sprache, {})
        for name in namen:
            laute = ' '.join(''.join(satz) for satz in fr.phonemize(name)).strip()
            for alt, neu in tabelle:
                laute = laute.replace(alt, neu)
            ziel[name] = f'[[ {laute} ]]'


# --- Zahlen ausschreiben (die Stimme bekommt keine Ziffern)

_ZAHL = {
    'de': (re.compile(r'(?<![\w\[])(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?(?![\w])'), '.', ' Komma '),
    'fr': (re.compile(r'(?<![\w\[])(\d{1,3}(?:[ \u00a0\u202f]\d{3})+|\d+)(?:,(\d+))?(?![\w])'), ' \u00a0\u202f', ' virgule '),
    'en': (re.compile(r'(?<![\w\[])(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?(?![\w])'), ',', ' point '),
}


_WEIBLICH_DE_WOERTER = {'person', 'frau', 'stunde', 'woche', 'minute', 'sekunde', 'million', 'milliarde', 'rupie',
                        'familie', 'schule', 'insel', 'stadt', 'partei', 'firma', 'tonne', 'nacht', 'klasse', 'runde'}
_WEIBLICH_FR = {'personne', 'femme', 'heure', 'semaine', 'minute', 'seconde', 'roupie', 'famille', 'école', 'île',
                'ville', 'fois', 'année', 'journée', 'tonne', 'nuit', 'victime', 'enquête'}


def _weiblich_de(wort: str) -> bool:
    w = wort.lower()
    return w in _WEIBLICH_DE_WOERTER or w.endswith(('ung', 'heit', 'keit', 'schaft', 'ion', 'tät', 'ie', 'in', 'ik'))


def zahlen_sprechen(text: str, sprache: str) -> str:
    from num2words import num2words

    if sprache == 'en':  # 7.15 pm → seven fifteen pm
        text = re.sub(r'\b(\d{1,2})[.:](\d{2})\s?(am|pm)\b',
                      lambda m: f'{num2words(int(m.group(1)), lang="en")} '
                                f'{"o\'clock" if m.group(2) == "00" else num2words(int(m.group(2)), lang="en")} {m.group(3)}',
                      text)
    muster, tausender, komma = _ZAHL[sprache]

    def ersetze(m: re.Match) -> str:
        ganz = int(re.sub(f'[{re.escape(tausender)}]', '', m.group(1)))
        nachkomma = m.group(2)
        if not nachkomma and len(m.group(1)) == 4 and 1100 <= ganz <= 2099:  # Jahreszahl (ohne Tausenderpunkt)
            if sprache == 'en':
                return num2words(ganz, lang='en', to='year')
            if sprache == 'de':  # „neunzehnhunderteinundsiebzig“, nicht „tausendneunhundert…“
                return num2words(ganz, lang='de', to='year')
        wort = num2words(ganz, lang=sprache)
        if sprache == 'de':  # „tausendzweihundert“ statt „eintausendzweihundert“
            wort = re.sub(r'^ein(tausend|hundert)', r'\1', wort)
        if nachkomma:
            return wort + komma + ' '.join(num2words(int(z), lang=sprache) for z in nachkomma)
        folgt = re.match(r'\s+([A-Za-zÀ-ÿ]+)', text[m.end():])
        if sprache == 'de' and ganz == 1 and folgt:
            return 'eine' if _weiblich_de(folgt.group(1)) else 'ein'
        if sprache == 'fr' and ganz == 1 and folgt:
            return 'une' if folgt.group(1).lower() in _WEIBLICH_FR else 'un'
        if sprache == 'en' and ganz == 1 and re.match(r'\s+[A-Za-z]', text[m.end():]):
            return 'one'
        return wort

    text = muster.sub(ersetze, text)
    if sprache == 'fr':  # „de une roupie“ → „d'une roupie“
        text = re.sub(r'\b([Dd])e (une?)\b', r"\1'\2", text)
    return text


_FUGE_SCHWELLE = 0.45
# Vorsilben sind keine Wortfugen: „Zurückhaltung“, „Aufnahme“, „Vorbereitung“ bleiben ganz.
_VORSILBEN = {'zurück', 'aus', 'auf', 'ab', 'an', 'ein', 'vor', 'nach', 'über', 'unter', 'durch', 'mit', 'bei',
              'gegen', 'um', 'weg', 'her', 'hin', 'fort', 'los', 'wieder', 'zusammen', 'voran', 'heraus', 'hinaus',
              'herein', 'hinein', 'vorbei', 'entgegen', 'miss', 'zer', 'ver', 'ent', 'emp'}


def wortfugen_trennen(text: str) -> str:
    """Trennt lange deutsche Zusammensetzungen an der Wortfuge („Sonderausschuss“ → „Sonder Ausschuss“),
    damit die Stimme die Teile nicht falsch zerlegt. Nur bei sicherer Trennung; Lautschrift bleibt unberührt."""
    try:
        from compound_split import char_split
    except ImportError:
        return text

    ausnahmen = set(AUSSPRACHE.get('de', {}).get('nicht_trennen', []))

    def trenne(m: re.Match) -> str:
        wort = m.group(0)
        if wort in ausnahmen:
            return wort
        wert, links, rechts = char_split.split_compound(wort)[0]
        schwelle = _FUGE_SCHWELLE if len(wort) >= 10 else 0.6  # kurze Wörter nur bei sicherer Trennung
        if wert < schwelle or len(links) < 3 or len(rechts) < 3 or links.lower() in _VORSILBEN:
            return wort
        # Endung „s“ (Fugen-s) bleibt beim linken Teil
        return f'{wort[:len(links)]} {wort[len(links):].capitalize()}' if wort.lower().startswith(links.lower()) else wort

    teile = re.split(r'(\[\[.*?\]\])', text)
    return ''.join(t if t.startswith('[[') else re.sub(r'(?<![\w-])[A-ZÄÖÜ][a-zäöüß]{6,}(?![\w-])', trenne, t)
                   for t in teile)


def aussprache(text: str, sprache: str) -> str:
    """Wendet das Aussprache-Verzeichnis an (nur für den Ton)."""
    regeln = AUSSPRACHE.get(sprache, {})
    text = daten_sprechen(text, sprache)
    for muster, ersatz in regeln.get('muster', []):
        text = re.sub(muster, ersatz, text)
    text = zahlen_sprechen(text, sprache)
    woerter = {**_FR_NAMEN.get(sprache, {}), **regeln.get('woerter', {})}
    for wort in sorted(woerter, key=len, reverse=True):
        text = re.sub(rf'(?<!\w){re.escape(wort)}(?![\w-])', lambda _m, w=wort: woerter[w], text)
        if sprache == 'de' and woerter[wort].startswith('[['):  # auch am Anfang von Zusammensetzungen: „Heroinhandel“
            text = re.sub(rf'(?<!\w){re.escape(wort)}(?=[a-zäöüß]{{3,}})', lambda _m, w=wort: woerter[w] + ' ', text)
    if sprache == 'de':
        text = wortfugen_trennen(text)
    wortweise = set(regeln.get('abkuerzungen_wortweise', []))

    def buchstabiere(m: re.Match) -> str:
        w = m.group(0)
        return w if w in wortweise else ' '.join(w)

    return re.sub(r'(?<![\w\[])[A-Z]{2,5}(?![a-zäöüéèàç])', buchstabiere, text)


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
        # Satz für Satz sprechen und Pausen selbst setzen: Endet ein Satz mit Lautschrift ([[ … ]]),
        # verliert Piper sonst den Satzpunkt und zieht zwei Sätze ohne Pause zusammen.
        saetze_ = [x for x in re.split(r'(?<=[.!?…:;])\s+', sprechtext(text, self.sprache)) if x.strip()]
        with wave.open(str(ziel), 'wb') as datei:
            datei.setnchannels(1)
            datei.setsampwidth(2)
            datei.setframerate(self.rate)
            for i, satz in enumerate(saetze_):
                for stueck in self.stimme.synthesize(satz, syn_config=self.konfig):
                    datei.writeframes(stueck.audio_int16_bytes)
                pause = SATZ_PAUSE_S if satz.rstrip()[-1:] in '.!?…' else KOMMA_PAUSE_S
                if i < len(saetze_) - 1:
                    datei.writeframes(b'\x00\x00' * int(self.rate * pause))
            # Stille am Ende des Abschnitts
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


# Entwurf A „Abendnachrichten“: dunkelblauer Grund, weißes Senderlogo, Bauchbinde, Quellenleiste
NAVY = (13, 32, 62)
NAVY_HELL = (20, 52, 96)
NAVY_TIEF = (8, 18, 36)
LEISTE = (6, 14, 28)
WEISS = (255, 255, 255)
HELLBLAU = (196, 210, 230)
MINT = (53, 201, 165)
ROT_TV = (210, 46, 58)
SCHWARZ = (20, 24, 31)
LOGO_WEISS = HIER / 'logo-weiss.png'
_weiss_cache: dict[tuple[int, float], Image.Image] = {}


def logo_weiss(groesse: int, deckkraft: float = 1.0) -> Image.Image:
    schluessel = (groesse, deckkraft)
    if schluessel not in _weiss_cache:
        bild = Image.open(LOGO_WEISS).convert('RGBA').resize((groesse, groesse), Image.LANCZOS)
        if deckkraft < 1:
            bild.putalpha(bild.split()[3].point(lambda v: int(v * deckkraft)))
        _weiss_cache[schluessel] = bild
    return _weiss_cache[schluessel]


def verlauf(oben: tuple, unten: tuple) -> Image.Image:
    bild = Image.new('RGB', (BREITE, HOEHE), oben)
    z = ImageDraw.Draw(bild)
    for y in range(HOEHE):
        t = y / HOEHE
        z.line([0, y, BREITE, y], fill=tuple(round(oben[i] + (unten[i] - oben[i]) * t) for i in range(3)))
    return bild


def flaggenlinie(z: ImageDraw.ImageDraw, y: int, hoehe: int) -> None:
    b = BREITE / 4
    for i, farbe in enumerate(FLAGGE):
        z.rectangle([round(i * b), y, round((i + 1) * b), y + hoehe], fill=farbe)


def marke(z: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, hinter, vorder) -> int:
    f = mono(24, True)
    x, y = xy
    breite = z.textlength(text, font=f)
    z.rectangle([x, y, x + breite + 36, y + 44], fill=hinter)
    z.text((x + 18, y + 8), text, font=f, fill=vorder)
    return round(x + breite + 36)


def senderkopf(bild: Image.Image, z: ImageDraw.ImageDraw, sprache: str, tag: dt.date, seite: str | None) -> None:
    bild.paste(logo_weiss(92), (70, 50), logo_weiss(92))
    z.text((180, 60), 'Gazet Morisyen', font=titel_schrift(34), fill=WEISS)
    gesperrt(z, (182, 106), T[sprache]['sendung'], mono(18, True), HELLBLAU, 0.1)
    gesperrt(z, (BREITE - 70, 64), datum_anzeige(tag, sprache), mono(22, True), HELLBLAU, 0.06, rechts=True)
    if seite:
        gesperrt(z, (BREITE - 70, 100), seite, mono(22, True), HELLBLAU, 0.06, rechts=True)


def bild_intro(sprache: str, tag: dt.date, ziel: Path) -> None:
    bild = verlauf(NAVY, NAVY_TIEF)
    bild.paste(logo_weiss(1100, 0.05), (BREITE - 900, -60), logo_weiss(1100, 0.05))
    z = ImageDraw.Draw(bild)
    flaggenlinie(z, HOEHE - 10, 10)
    g = 380
    bild.paste(logo_weiss(g), ((BREITE - g) // 2, 200), logo_weiss(g))
    f = titel_schrift(72)
    text = 'Gazet Morisyen'
    z.text(((BREITE - z.textlength(text, font=f)) / 2, 612), text, font=f, fill=WEISS)
    unter = f'{T[sprache]["sendung"]}  ·  {datum_kurz(tag, sprache)}'
    f2 = mono(28, True)
    abstand = 28 * 0.1
    breite = sum(z.textlength(c, font=f2) + abstand for c in unter.upper()) - abstand
    gesperrt(z, (round((BREITE - breite) / 2), 714), unter, f2, HELLBLAU, 0.1)
    bild.save(ziel)


def bild_beitrag(sprache: str, tag: dt.date, b: Beitrag, nummer: int, anzahl: int, ziel: Path) -> None:
    bild = verlauf(NAVY_HELL, NAVY)
    bild.paste(logo_weiss(900, 0.06), (BREITE - 760, 40), logo_weiss(900, 0.06))
    z = ImageDraw.Draw(bild)
    senderkopf(bild, z, sprache, tag, f'{nummer} / {anzahl}')

    # Bauchbinde mit Schlagzeile (unten)
    titel = feld(b.update, 'titel', sprache)
    innen = BREITE - 140 - 50 - 50
    for g in (72, 66, 60, 54):
        ft = titel_schrift(g)
        zeilen = umbrechen(z, titel, ft, innen)
        if len(zeilen) <= 2:
            break
    zeilen = zeilen[:2]
    zh = round(ft.size * 1.12)
    binde_h = 44 + len(zeilen) * zh
    binde_y = HOEHE - 80 - 50 - binde_h
    z.rectangle([70, binde_y, BREITE - 70, binde_y + binde_h], fill=WEISS)
    z.rectangle([70, binde_y, 84, binde_y + binde_h], fill=ROT_TV)
    y = binde_y + 18
    for zeile in zeilen:
        z.text((120, y), zeile, font=ft, fill=NAVY)
        y += zh
    x = 70
    if b.top:
        x = marke(z, (x, binde_y - 44), T[sprache]['top'].upper(), ROT_TV, WEISS)
    rubrik = RUBRIKEN[sprache].get(b.thema.get('rubrik', ''), '')
    if b.thema.get('ort'):
        rubrik += f' · {b.thema["ort"]}'
    marke(z, (x, binde_y - 44), rubrik.upper(), SCHWARZ if b.top else ROT_TV, WEISS)

    # Kernpunkte (gekürzte Fassung) und Rückblick, oberhalb der Bauchbinde
    oben, unten = 230, binde_y - 44 - 40
    zuvor_h = 0
    if b.vorher:
        zuvor_h = 60
    punkte = stichpunkte(b, sprache)
    if punkte:
        platz = unten - oben - zuvor_h
        for g in (48, 44, 40, 36):
            fp = text_schrift(g)
            pzh = round(g * 1.3)
            luecke = round(g * 0.5)
            bloecke = [umbrechen(z, p, fp, 1250) for p in punkte]
            hoehe = sum(len(bl) * pzh for bl in bloecke) + luecke * (len(bloecke) - 1)
            if hoehe <= platz:
                break
        y = oben
        for bl in bloecke:
            if y + len(bl) * pzh > unten - zuvor_h:
                break
            q = round(g * 0.3)
            my = y + round(pzh * 0.55)
            z.rectangle([110, my - q // 2, 110 + q, my + q // 2], fill=MINT)
            for zeile in bl:
                z.text((160, y), zeile, font=fp, fill=WEISS)
                y += pzh
            y += luecke
        zuvor_y = y + 6
    else:
        zuvor_y = unten - zuvor_h
    if b.vorher:
        tag_vorher = iso(b.vorher['zeit']).astimezone(MU).date()
        kopf = f'{T[sprache]["zuvor"]} {tag_vorher.day:02d}.{tag_vorher.month:02d}.'.upper() + '  '
        fk, fv = mono(22, True), text_schrift(30)
        x0 = 160 if punkte else 110
        z.text((x0, zuvor_y + 6), kopf, font=fk, fill=MINT)
        rest = feld(b.vorher, 'titel', sprache)
        breite = BREITE - 140 - x0 - z.textlength(kopf, font=fk)
        while z.textlength(rest, font=fv) > breite and ' ' in rest:
            rest = rest.rsplit(' ', 1)[0].rstrip(' ,:;–-') + ' …'
        z.text((x0 + z.textlength(kopf, font=fk), zuvor_y), rest, font=fv, fill=HELLBLAU)

    # Quellenleiste
    z.rectangle([0, HOEHE - 80, BREITE, HOEHE], fill=LEISTE)
    flaggenlinie(z, HOEHE - 80, 4)
    quellen = [q.get('name', '') for q in b.update.get('quellen', []) if q.get('name')]
    if quellen:
        wort = T[sprache]['quellen' if len(quellen) > 1 else 'quelle']
        z.text((70, HOEHE - 56), f'{wort}: ' + ' · '.join(dict.fromkeys(quellen)), font=mono(24), fill=HELLBLAU)
    f = mono(24, True)
    z.text((BREITE - 70 - z.textlength('gazet.morisyen.de', font=f), HOEHE - 56), 'gazet.morisyen.de', font=f, fill=MINT)
    bild.save(ziel)


def wettersymbol(z: ImageDraw.ImageDraw, mx: int, my: int, art: str, g: int = 150) -> None:
    """Einfache Wettersymbole: Sonne, Wolke, Regen, Gewitter, Nebel."""
    gelb, wolke, tropfen = (245, 200, 74), (235, 241, 248), (120, 180, 255)
    r = g // 2

    def sonne(cx, cy, rr):
        for i in range(8):
            import math
            w = i * math.pi / 4
            z.line([cx + math.cos(w) * rr * 1.35, cy + math.sin(w) * rr * 1.35,
                    cx + math.cos(w) * rr * 1.75, cy + math.sin(w) * rr * 1.75], fill=gelb, width=max(4, rr // 6))
        z.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=gelb)

    def wolke_(cx, cy, s, farbe=wolke):
        z.ellipse([cx - s * 1.0, cy - s * 0.35, cx - s * 0.1, cy + s * 0.45], fill=farbe)
        z.ellipse([cx - s * 0.55, cy - s * 0.75, cx + s * 0.45, cy + s * 0.35], fill=farbe)
        z.ellipse([cx + s * 0.05, cy - s * 0.45, cx + s * 0.95, cy + s * 0.45], fill=farbe)
        z.rectangle([cx - s * 0.55, cy, cx + s * 0.5, cy + s * 0.45], fill=farbe)

    if art == 'klar':
        sonne(mx, my, round(r * 0.55))
    elif art in ('heiter', 'wolkig'):
        sonne(mx - r * 0.3, my - r * 0.3, round(r * (0.45 if art == 'heiter' else 0.4)))
        wolke_(mx + r * 0.15, my + r * 0.2, r * (0.6 if art == 'heiter' else 0.8))
    elif art in ('bedeckt', 'nebel'):
        wolke_(mx, my - r * 0.1, r * 0.9, (205, 214, 226))
        if art == 'nebel':
            for i in range(3):
                y = my + r * 0.5 + i * r * 0.22
                z.line([mx - r * 0.8, y, mx + r * 0.8, y], fill=(205, 214, 226), width=max(4, r // 10))
    else:
        wolke_(mx, my - r * 0.25, r * 0.85, (205, 214, 226))
        if art == 'gewitter':
            z.polygon([(mx, my + r * 0.2), (mx - r * 0.25, my + r * 0.65), (mx - r * 0.02, my + r * 0.65),
                       (mx - r * 0.15, my + r), (mx + r * 0.3, my + r * 0.45), (mx + r * 0.05, my + r * 0.45),
                       (mx + r * 0.2, my + r * 0.2)], fill=gelb)
        else:
            anzahl = 3 if art == 'regen' else 2
            for i in range(anzahl):
                x = mx + (i - (anzahl - 1) / 2) * r * 0.45
                z.line([x, my + r * 0.4, x - r * 0.12, my + r * 0.8], fill=tropfen, width=max(5, r // 9))


def bild_wetter(sprache: str, tag: dt.date, wetter: list, morgen: bool, ziel: Path) -> None:
    bild = verlauf(NAVY_HELL, NAVY)
    bild.paste(logo_weiss(900, 0.06), (BREITE - 760, 40), logo_weiss(900, 0.06))
    z = ImageDraw.Draw(bild)
    senderkopf(bild, z, sprache, tag, None)
    t = T[sprache]
    marke(z, (70, 190), t['wetter'][1 if morgen else 0].upper(), ROT_TV, WEISS)
    spalten, abstand = 3, 40
    breite = (BREITE - 140 - abstand * (spalten - 1)) // spalten
    oben, unten = 270, HOEHE - 80 - 60
    for i, w in enumerate(wetter):
        x = 70 + i * (breite + abstand)
        karte = Image.new('RGBA', (breite, unten - oben), (255, 255, 255, 22))
        bild.paste(karte, (x, oben), karte)
        z.rectangle([x, oben, x + breite, oben + 8], fill=FLAGGE[i % 4] if i < 3 else MINT)
        name = wetterdienst.NAMEN[sprache][w.ort]
        fn = titel_schrift(56)
        z.text((x + (breite - z.textlength(name, font=fn)) / 2, oben + 40), name, font=fn, fill=WEISS)
        wettersymbol(z, x + breite // 2, oben + 250, w.art, 170)
        art = wetterdienst.ART_TEXT[sprache][w.art]
        fa = text_schrift(40)
        z.text((x + (breite - z.textlength(art, font=fa)) / 2, oben + 380), art, font=fa, fill=HELLBLAU)
        temp = f'{w.tmin}° / {w.tmax}°'
        ft = titel_schrift(84)
        z.text((x + (breite - z.textlength(temp, font=ft)) / 2, oben + 440), temp, font=ft, fill=WEISS)
        info = f'{t["regen"]} {str(w.regen_mm).replace(".", ",") if sprache != "en" else w.regen_mm} mm  ·  Wind {w.wind_kmh} km/h'
        fi = mono(24, True)
        z.text((x + (breite - z.textlength(info, font=fi)) / 2, oben + 560), info, font=fi, fill=HELLBLAU)
    z.rectangle([0, HOEHE - 80, BREITE, HOEHE], fill=LEISTE)
    flaggenlinie(z, HOEHE - 80, 4)
    z.text((70, HOEHE - 56), t['wetterquelle'], font=mono(24), fill=HELLBLAU)
    f = mono(24, True)
    z.text((BREITE - 70 - z.textlength('gazet.morisyen.de', font=f), HOEHE - 56), 'gazet.morisyen.de', font=f, fill=MINT)
    bild.save(ziel)


def bild_outro(sprache: str, tag: dt.date, ziel: Path) -> None:
    bild = verlauf(NAVY, NAVY_TIEF)
    bild.paste(logo_weiss(1100, 0.05), (BREITE - 900, -60), logo_weiss(1100, 0.05))
    z = ImageDraw.Draw(bild)
    flaggenlinie(z, HOEHE - 10, 10)
    g = 300
    bild.paste(logo_weiss(g), ((BREITE - g) // 2, 150), logo_weiss(g))
    f = titel_schrift(92)
    text = 'gazet.morisyen.de'
    z.text(((BREITE - z.textlength(text, font=f)) / 2, 520), text, font=f, fill=WEISS)
    f2 = mono(30, True)
    for i, zeile in enumerate([T[sprache]['mehr'], T[sprache]['newsletter']]):
        z.text(((BREITE - z.textlength(zeile, font=f2)) / 2, 680 + i * 58), zeile, font=f2, fill=HELLBLAU if i else MINT)
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
    bild_intro(sprache, tag, intro)
    abschnitte.append(Abschnitt(t['kapitel_start'], gruss, intro, mindestens=5.0))

    for i, b in enumerate(beitraege, 1):
        pfad = arbeit / f'{i:02d}-thema.png'
        bild_beitrag(sprache, tag, b, i, len(beitraege), pfad)
        abschnitte.append(Abschnitt(feld(b.update, 'titel', sprache), sprech_beitrag(b, sprache), pfad,
                                    quellen=b.update.get('quellen', [])))

    vorhersage = wetterdienst.hole_wetter(jetzt if abs((jetzt - dt.datetime.now(dt.timezone.utc)).days) < 1
                                          else dt.datetime.now(dt.timezone.utc))
    if vorhersage:
        inseln, morgen = vorhersage
        pfad = arbeit / '98-wetter.png'
        bild_wetter(sprache, tag, inseln, morgen, pfad)
        abschnitte.append(Abschnitt(t['wetter'][1 if morgen else 0], wetterdienst.sprechtext(inseln, morgen, sprache), pfad))

    outro = arbeit / '99-outro.png'
    bild_outro(sprache, tag, outro)
    abschnitte.append(Abschnitt(t['kapitel_ende'], abschied, outro))

    modell, stimme_name = STIMMEN[sprache]
    lade_franzoesische_namen(stimmen)
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
        *([t['wetterquelle']] if vorhersage else []),
        t['impressum'],
    ])
    (ausgabe / f'{stamm}-youtube.txt').write_text(
        f'TITEL:\n{titel}\n\nBESCHREIBUNG:\n{beschreibung}\n\nTAGS:\n'
        'Mauritius, Maurice, Nachrichten, actualités, news, Port-Louis, Rodrigues, Gazet Morisyen\n',
        encoding='utf-8')
    # Maschinenlesbar für den automatischen YouTube-Upload (youtube_upload.py)
    ohne_klammern = str.maketrans({'<': '‹', '>': '›'})  # YouTube lehnt < und > ab
    (ausgabe / f'{stamm}-youtube.json').write_text(json.dumps({
        'sprache': sprache,
        'datum': tag.isoformat(),
        'video': video.name,
        'vorschau': f'{stamm}-vorschau.png',
        'titel': titel.translate(ohne_klammern)[:100],
        'beschreibung': beschreibung.translate(ohne_klammern)[:4900],
        'tags': ['Mauritius', 'Maurice', 'Nachrichten', 'actualités', 'news', 'Port-Louis', 'Rodrigues',
                 'Gazet Morisyen'],
    }, ensure_ascii=False, indent=1), encoding='utf-8')
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
