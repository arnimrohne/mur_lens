"""
Wettervorhersage für Mauritius, Rodrigues und La Réunion (MET Norway, CC BY 4.0).

Liefert je Insel Tiefst-/Höchstwert, vorherrschende Wetterlage, Regenmenge und
stärksten Wind für den restlichen Tag (bis 18 Uhr) bzw. für morgen, falls die
Sendung erst nachmittags entsteht.
"""

from __future__ import annotations

import datetime as dt
import json
import urllib.request
from collections import Counter
from dataclasses import dataclass

KENNUNG = 'GazetMorisyen/1.0 (+https://gazet.morisyen.de)'
URL = 'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}'
MU = dt.timezone(dt.timedelta(hours=4))  # Mauritius und Réunion: UTC+4

ORTE = [
    ('mauritius', -20.1609, 57.5012),  # Port-Louis
    ('rodrigues', -19.6833, 63.4167),  # Port Mathurin
    ('reunion', -20.8789, 55.4481),    # Saint-Denis
]

NAMEN = {
    'de': {'mauritius': 'Mauritius', 'rodrigues': 'Rodrigues', 'reunion': 'La Réunion'},
    'fr': {'mauritius': 'Maurice', 'rodrigues': 'Rodrigues', 'reunion': 'La Réunion'},
    'en': {'mauritius': 'Mauritius', 'rodrigues': 'Rodrigues', 'reunion': 'Réunion'},
}

ART_TEXT = {
    'de': {'klar': 'sonnig', 'heiter': 'meist sonnig', 'wolkig': 'teils bewölkt', 'bedeckt': 'bewölkt',
           'nebel': 'neblig', 'schauer': 'einzelne Schauer', 'regen': 'Regen', 'gewitter': 'Gewitter'},
    'fr': {'klar': 'ensoleillé', 'heiter': 'plutôt ensoleillé', 'wolkig': 'partiellement nuageux',
           'bedeckt': 'nuageux', 'nebel': 'brumeux', 'schauer': 'quelques averses', 'regen': 'pluie',
           'gewitter': 'orages'},
    'en': {'klar': 'sunny', 'heiter': 'mostly sunny', 'wolkig': 'partly cloudy', 'bedeckt': 'cloudy',
           'nebel': 'foggy', 'schauer': 'a few showers', 'regen': 'rain', 'gewitter': 'thunderstorms'},
}


def symbol_zu_art(symbol: str) -> str:
    """Wie lib/zeitung/wetter.ts → symbolZuArt."""
    name = symbol.split('_')[0]
    if 'thunder' in name:
        return 'gewitter'
    if 'showers' in name:
        return 'schauer'
    if 'rain' in name or 'sleet' in name or 'snow' in name:
        return 'regen'
    if name == 'fog':
        return 'nebel'
    if name == 'cloudy':
        return 'bedeckt'
    if name == 'partlycloudy':
        return 'wolkig'
    if name == 'fair':
        return 'heiter'
    return 'klar'


@dataclass
class InselWetter:
    ort: str
    tmin: int
    tmax: int
    art: str
    regen_mm: float
    wind_kmh: int


def zeitfenster(jetzt: dt.datetime) -> tuple[dt.datetime, dt.datetime, bool]:
    """Restlicher Tag bis 18 Uhr; ab 15 Uhr der morgige Tag (6–18 Uhr). Drittes Feld: ist es morgen?"""
    lokal = jetzt.astimezone(MU)
    if lokal.hour < 15:
        start = max(lokal, lokal.replace(hour=6, minute=0, second=0, microsecond=0))
        return start, lokal.replace(hour=18, minute=0, second=0, microsecond=0), False
    morgen = (lokal + dt.timedelta(days=1)).replace(minute=0, second=0, microsecond=0)
    return morgen.replace(hour=6), morgen.replace(hour=18), True


def auswerten(daten: dict, ort: str, von: dt.datetime, bis: dt.datetime) -> InselWetter | None:
    temps, arten, regen, wind = [], Counter(), 0.0, 0.0
    for eintrag in daten.get('properties', {}).get('timeseries', []):
        zeit = dt.datetime.fromisoformat(eintrag['time'].replace('Z', '+00:00'))
        if not von <= zeit <= bis:
            continue
        jetzt_werte = eintrag['data']['instant']['details']
        temps.append(jetzt_werte.get('air_temperature'))
        wind = max(wind, jetzt_werte.get('wind_speed') or 0)
        stunde = eintrag['data'].get('next_1_hours') or {}
        if stunde.get('summary', {}).get('symbol_code'):
            arten[symbol_zu_art(stunde['summary']['symbol_code'])] += 1
        regen += (stunde.get('details') or {}).get('precipitation_amount') or 0
    temps = [x for x in temps if x is not None]
    if not temps or not arten:
        return None
    if arten['gewitter']:
        art = 'gewitter'
    elif arten['regen'] >= 3:
        art = 'regen'
    elif arten['regen'] + arten['schauer'] >= 2:
        art = 'schauer'
    else:
        art = max(('klar', 'heiter', 'wolkig', 'bedeckt', 'nebel'), key=lambda a: arten[a])
    return InselWetter(ort, round(min(temps)), round(max(temps)), art, round(regen, 1), round(wind * 3.6))


def hole_wetter(jetzt: dt.datetime) -> tuple[list[InselWetter], bool] | None:
    """Vorhersage für alle drei Inseln; None, wenn der Dienst nicht erreichbar ist."""
    von, bis, morgen = zeitfenster(jetzt)
    ergebnis = []
    for ort, lat, lon in ORTE:
        anfrage = urllib.request.Request(URL.format(lat=lat, lon=lon),
                                         headers={'User-Agent': KENNUNG, 'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(anfrage, timeout=20) as antwort:
                daten = json.load(antwort)
        except Exception as fehler:  # noqa: BLE001 – Wetter ist optional
            print(f'Wetter für {ort} nicht verfügbar: {fehler}')
            return None
        insel = auswerten(daten, ort, von, bis)
        if insel is None:
            return None
        ergebnis.append(insel)
    return ergebnis, morgen


def sprechtext(wetter: list[InselWetter], morgen: bool, sprache: str) -> str:
    n, a = NAMEN[sprache], ART_TEXT[sprache]
    teile = []
    for i, w in enumerate(wetter):
        letzte = i == len(wetter) - 1
        if sprache == 'de':
            wind = ', mit kräftigem Wind' if w.wind_kmh >= 35 else ''
            vor = 'Und auf' if letzte else 'Auf'
            teile.append(f'{vor} {n[w.ort]}: {a[w.art]} bei {w.tmin} bis {w.tmax} Grad{wind}.')
        elif sprache == 'fr':
            wind = ', avec un vent soutenu' if w.wind_kmh >= 35 else ''
            vor = 'Et à' if letzte else 'À'
            ort = n[w.ort] if w.ort != 'mauritius' else 'Maurice'
            teile.append(f'{vor} {ort} : {a[w.art]}, de {w.tmin} à {w.tmax} degrés{wind}.')
        else:
            wind = ', with strong winds' if w.wind_kmh >= 35 else ''
            vor = 'And in' if letzte else 'In'
            teile.append(f'{vor} {n[w.ort]}: {a[w.art]}, {w.tmin} to {w.tmax} degrees{wind}.')
    einleitung = {
        'de': 'Zum Schluss das Wetter für morgen.' if morgen else 'Zum Schluss das Wetter für heute.',
        'fr': 'Pour terminer, la météo de demain.' if morgen else "Pour terminer, la météo d'aujourd'hui.",
        'en': "Finally, tomorrow's weather." if morgen else "Finally, today's weather.",
    }[sprache]
    return ' '.join([einleitung, *teile])
