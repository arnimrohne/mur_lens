"""
Erkennungsmelodie der Sendung (ca. 3,5 s), vollständig synthetisiert – keine fremden Samples, keine Lizenzfragen.

Aufbau: Séga im ternären Schwung – die Ravanne (Rahmentrommel) trägt durchgehend den Rhythmus,
dazu Maravanne (Rassel) und Triangel; darunter ein runder Bass, darüber eine Melodie auf warmem E-Piano in D-Dur; Akkordschläge bei 1,5 s und zum Schluss.
"""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

RATE = 48000
DAUER = 3.5


def _zeit(dauer: float) -> np.ndarray:
    return np.arange(int(dauer * RATE)) / RATE


def _hz(note: str) -> float:
    namen = {'C': -9, 'C#': -8, 'D': -7, 'D#': -6, 'E': -5, 'F': -4, 'F#': -3, 'G': -2, 'G#': -1, 'A': 0, 'A#': 1, 'B': 2}
    ton, oktave = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((namen[ton] + 12 * (oktave - 4)) / 12)


def _epiano(freq: float, dauer: float = 1.2, laut: float = 0.4) -> np.ndarray:
    """Warmes E-Piano (FM-Synthese, Modulationsindex klingt schnell ab – rund statt spitz)."""
    t = _zeit(dauer)
    index = 1.6 * np.exp(-t * 7) + 0.25
    ton = np.sin(2 * np.pi * freq * t + index * np.sin(2 * np.pi * freq * t))
    ton += 0.25 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 6)
    huelle = np.minimum(1.0, t / 0.004) * np.exp(-t * 2.2) * np.clip((dauer - t) / 0.15, 0, 1)
    return laut * ton * huelle


def _bass(freq: float, dauer: float = 0.45, laut: float = 0.5) -> np.ndarray:
    """Runder Bass (gezupft): Grundton mit wenigen Obertönen."""
    t = _zeit(dauer)
    ton = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t * 8) \
        + 0.12 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-t * 14)
    huelle = np.minimum(1.0, t / 0.006) * np.exp(-t * 3.5) * np.clip((dauer - t) / 0.05, 0, 1)
    return laut * ton * huelle


def _akkord(noten: list[str], dauer: float, laut: float) -> np.ndarray:
    return sum(_epiano(_hz(n), dauer, laut / len(noten) * 2.2) for n in noten)


def _flaeche(freqs: list[float], dauer: float, laut: float = 0.12) -> np.ndarray:
    t = _zeit(dauer)
    s = np.zeros_like(t)
    for f in freqs:
        for verstimmung in (-0.15, 0.15):
            for n in range(1, 4):
                s += np.sin(2 * np.pi * (f + verstimmung) * n * t + n) / (n ** 2.2)
    huelle = np.minimum(1.0, t / 0.25) * np.clip((dauer - t) / 1.2, 0, 1)
    return laut * s / len(freqs) * huelle


def _rauschen(dauer: float, glaettung: float, seed: int) -> np.ndarray:
    r = np.random.default_rng(seed).standard_normal(int(dauer * RATE))
    if glaettung <= 0:
        return r
    # einfacher Tiefpass (einpolig)
    a = glaettung
    aus = np.empty_like(r)
    acc = 0.0
    for i, x in enumerate(r):
        acc = a * acc + (1 - a) * x
        aus[i] = acc
    return aus / (np.abs(aus).max() + 1e-9)


def _ravanne(laut: float = 0.55, tief: bool = True) -> np.ndarray:
    t = _zeit(0.35)
    f0, f1 = (120, 68) if tief else (210, 150)
    phase = 2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t * 30)) / RATE
    koerper = np.sin(phase) * np.exp(-t * (9 if tief else 16))
    schlag = _rauschen(0.35, 0.6, 7 if tief else 8) * np.exp(-t * 60) * 0.5
    return laut * (koerper + schlag)


def _shaker(laut: float = 0.08) -> np.ndarray:
    t = _zeit(0.09)
    r = np.random.default_rng(3).standard_normal(len(t))
    hoch = np.diff(r, prepend=0.0)  # Hochpass
    return laut * hoch * np.exp(-t * 55) * np.minimum(1.0, t / 0.01)


def _ravanne_schlag(laut: float = 0.35, seed: int = 11) -> np.ndarray:
    """Heller Randschlag („ka“) auf der Ravanne: kurzer, gestimmter Klang mit Fell-Rascheln."""
    t = _zeit(0.18)
    koerper = np.sin(2 * np.pi * 330 * t) * np.exp(-t * 38) + 0.5 * np.sin(2 * np.pi * 520 * t) * np.exp(-t * 55)
    rasseln = np.diff(np.random.default_rng(seed).standard_normal(len(t)), prepend=0.0) * np.exp(-t * 45) * 0.35
    return laut * (koerper + rasseln)


def _maravanne(laut: float = 0.1, seed: int = 5) -> np.ndarray:
    """Maravanne (Rassel aus Zuckerrohr und Samen): weiches, längeres Rauschen."""
    t = _zeit(0.14)
    r = np.random.default_rng(seed).standard_normal(len(t))
    hoch = r - np.concatenate(([0.0], r[:-1])) * 0.6
    huelle = np.minimum(1.0, t / 0.025) * np.exp(-t * 28)
    return laut * hoch * huelle


def _triangel(laut: float = 0.07) -> np.ndarray:
    t = _zeit(0.6)
    ton = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((4200, 1.0), (5650, 0.6), (7300, 0.35)))
    return laut * ton * np.exp(-t * 7) * np.minimum(1.0, t / 0.001)


def _boom(laut: float = 0.7) -> np.ndarray:
    t = _zeit(1.2)
    phase = 2 * np.pi * np.cumsum(38 + 50 * np.exp(-t * 6)) / RATE
    return laut * np.sin(phase) * np.exp(-t * 3.2)


def _setze(spur: np.ndarray, klang: np.ndarray, ab: float, pan: float = 0.0) -> None:
    i = int(ab * RATE)
    n = min(len(klang), spur.shape[1] - i)
    if n <= 0:
        return
    links, rechts = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    spur[0, i:i + n] += klang[:n] * links * 1.41
    spur[1, i:i + n] += klang[:n] * rechts * 1.41


def _hall(spur: np.ndarray) -> np.ndarray:
    aus = spur.copy()
    for verz, anteil, seite in ((0.031, 0.25, 0), (0.047, 0.22, 1), (0.071, 0.18, 0), (0.113, 0.14, 1), (0.167, 0.1, 0)):
        d = int(verz * RATE)
        aus[seite, d:] += spur[1 - seite, :-d] * anteil
        aus[1 - seite, d:] += spur[seite, :-d] * anteil * 0.7
    return aus


def erzeuge_jingle(ziel: Path) -> float:
    spur = np.zeros((2, int(DAUER * RATE)))
    # Séga im ternären Schwung: ein Schlag = 0,5 s, unterteilt in Triolen.
    schlag = 0.5
    tri = schlag / 3

    # Ravanne trägt den Rhythmus durchgehend: tiefer Schlag („boum“) auf der Eins, Randschläge („ka-ta“) dazwischen.
    for b in range(6):
        start = b * schlag
        _setze(spur, _ravanne(0.62 if b % 2 == 0 else 0.5, True), start, pan=-0.15)
        if b == 5:
            continue  # letzter Schlag vor dem Schluss bleibt frei für den Dreifachschlag
        _setze(spur, _ravanne_schlag(0.3, seed=11 + b), start + 2 * tri, pan=0.2)
        if b % 2 == 1:
            _setze(spur, _ravanne_schlag(0.22, seed=31 + b), start + tri, pan=0.25)
        if b in (2, 5):  # kleiner Wirbel als Steigerung
            _setze(spur, _ravanne(0.34, False), start + 2.5 * tri, pan=0.1)
    # Schluss: Dreifachschlag „ta-ta-BOUM“ – zwei Randschläge, dann alle Rhythmusinstrumente zusammen
    ende = 3.0
    _setze(spur, _ravanne_schlag(0.42, seed=91), ende - 2 * tri / 1.5, pan=0.2)
    _setze(spur, _ravanne_schlag(0.48, seed=92), ende - tri / 1.5, pan=-0.2)
    _setze(spur, _ravanne(0.85, True), ende)
    _setze(spur, _ravanne_schlag(0.4, seed=93), ende, pan=0.15)
    _setze(spur, _maravanne(0.22, seed=94), ende, pan=0.45)
    _setze(spur, _triangel(0.1), ende, pan=-0.5)
    # Maravanne auf allen Triolen bis kurz vor den Schluss, Betonung auf der Eins
    for k in range(int((ende - 0.3) / tri)):
        _setze(spur, _maravanne(0.13 if k % 3 == 0 else 0.08, seed=5 + k), k * tri, pan=0.45)
    # Triangel auf der letzten Triole jedes Schlags
    for b in range(5):
        _setze(spur, _triangel(0.06), b * schlag + 2 * tri, pan=-0.5)

    # Bass: Grundton auf jedem Schlag, Wechsel D – A – D (ternär federnd)
    for b, note in enumerate(('D2', 'D2', 'A1', 'A1', 'D2', 'A1')):
        _setze(spur, _bass(_hz(note), 0.32, 0.55), b * schlag)
        _setze(spur, _bass(_hz(note) * 2, 0.15, 0.25), b * schlag + 2 * tri)

    # Melodie auf warmem E-Piano, mit Terz darunter für mehr Fülle
    for zeit, oben, unten in ((0.0, 'A4', 'F#4'), (2 * tri, 'D5', 'A4'), (schlag, 'F#5', 'D5'), (schlag + 2 * tri, 'A5', 'F#5'),
                              (2 * schlag, 'E5', 'C#5'), (2 * schlag + tri, 'F#5', 'D5'), (2 * schlag + 2 * tri, 'A5', 'F#5')):
        _setze(spur, _epiano(_hz(oben) / 2, 0.6, 0.36), zeit, pan=0.2)
        _setze(spur, _epiano(_hz(unten) / 2, 0.6, 0.24), zeit, pan=-0.2)

    # Akkordschlag bei 1,5 s (mit dem Namen im Bild)
    _setze(spur, _akkord(['D3', 'A3', 'D4', 'F#4', 'A4'], 1.6, 0.6), 1.5)
    _setze(spur, _bass(_hz('D1') * 2, 1.0, 0.7), 1.5)
    _setze(spur, _boom(0.5), 1.5)
    _setze(spur, _flaeche([_hz(n) for n in ('D3', 'A3', 'F#4')], DAUER - 1.45, laut=0.16), 1.45)
    # Schlussakkord zusammen mit dem Dreifachschlag
    _setze(spur, _akkord(['D3', 'A3', 'D4', 'F#4'], 0.5, 0.55), ende)
    _setze(spur, _bass(_hz('D2'), 0.5, 0.7), ende)

    spur = _hall(spur)
    # sanft ausblenden, normalisieren auf -1 dBFS
    t = _zeit(DAUER)
    spur *= np.clip((DAUER - t) / 0.35, 0, 1)  # kurz ausblenden, der Schlussschlag bleibt hörbar
    spur /= np.abs(spur).max() / 10 ** (-1 / 20)
    daten = (spur.T * 32767).astype('<i2')
    with wave.open(str(ziel), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(daten.tobytes())
    return DAUER


if __name__ == '__main__':
    import sys
    print(erzeuge_jingle(Path(sys.argv[1] if len(sys.argv) > 1 else 'jingle.wav')))
