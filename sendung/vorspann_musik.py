"""
Erkennungsmelodie mit aufgenommenen Instrumenten (einmalig erzeugen, Ergebnis: vorspann.wav).

Melodie, Gitarre, Akkordeon, Bass und Bläser kommen aus dem Soundfont FluidR3_GM (MIT-Lizenz,
Debian-Paket fluid-soundfont-gm), gespielt mit FluidSynth. Die Séga-Trommeln (Ravanne, Maravanne,
Triangel) kommen aus jingle.py. Benötigt: fluidsynth, fluid-soundfont-gm, mido.

    python3 vorspann_musik.py [ziel.wav]
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import mido
import numpy as np

import jingle

HIER = Path(__file__).resolve().parent
SOUNDFONT = Path('/usr/share/sounds/sf2/FluidR3_GM.sf2')
TPB = 480                      # Ticks pro Viertel; Viertel = 0,5 s (120 BPM) = ein Séga-Schlag
TRIOLE = TPB // 3

# General-MIDI-Programme
GITARRE, AKKORDEON, BASS, BLAESER = 25, 21, 32, 61


def note(name: str) -> int:
    namen = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    return 12 * (int(name[-1]) + 1) + namen[name[:-1]]


class Spur:
    def __init__(self, kanal: int, programm: int, lautstaerke: int, pan: int):
        self.kanal = kanal
        self.ereignisse: list[tuple[int, mido.Message]] = [
            (0, mido.Message('program_change', channel=kanal, program=programm)),
            (0, mido.Message('control_change', channel=kanal, control=7, value=lautstaerke)),
            (0, mido.Message('control_change', channel=kanal, control=10, value=pan)),
            (0, mido.Message('control_change', channel=kanal, control=91, value=50)),  # Hall
        ]

    def spiele(self, noten: list[str], start: int, dauer: int, staerke: int = 90, schrumm: int = 0) -> None:
        for i, n in enumerate(noten):
            versatz = i * schrumm
            self.ereignisse.append((start + versatz, mido.Message('note_on', channel=self.kanal, note=note(n), velocity=staerke)))
            self.ereignisse.append((start + versatz + dauer, mido.Message('note_off', channel=self.kanal, note=note(n), velocity=0)))

    def als_track(self) -> mido.MidiTrack:
        track = mido.MidiTrack()
        jetzt = 0
        for zeit, msg in sorted(self.ereignisse, key=lambda e: (e[0], e[1].type == 'note_on')):
            track.append(msg.copy(time=zeit - jetzt))
            jetzt = zeit
        return track


def komponiere(ziel: Path) -> None:
    mid = mido.MidiFile(ticks_per_beat=TPB)
    tempo = mido.MidiTrack()
    tempo.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
    mid.tracks.append(tempo)

    gitarre = Spur(0, GITARRE, 92, 40)
    akkordeon = Spur(1, AKKORDEON, 100, 80)
    bass = Spur(2, BASS, 115, 64)
    blaeser = Spur(3, BLAESER, 82, 70)

    akkorde = {'D': ['D3', 'A3', 'D4', 'F#4'], 'G': ['D3', 'G3', 'B3', 'D4'], 'A': ['E3', 'A3', 'C#4', 'E4']}
    # Gitarre: Séga-Schlag „lang – kurz kurz“ auf den Triolen; I – IV – V, dann D
    for schlag, akk in enumerate(['D', 'G', 'A', 'D', 'D']):
        t0 = schlag * TPB
        gitarre.spiele(akkorde[akk], t0, TRIOLE * 2 - 20, 96, schrumm=12)
        gitarre.spiele(list(reversed(akkorde[akk])), t0 + 2 * TRIOLE, TRIOLE - 20, 74, schrumm=10)
    # Bass: Grundtöne
    for schlag, n in enumerate(['D2', 'G2', 'A2']):
        bass.spiele([n], schlag * TPB, TPB - 40, 105)
        bass.spiele([n.replace('2', '3')], schlag * TPB + 2 * TRIOLE, TRIOLE - 20, 80)
    # Akkordeon: Melodie bis zum Akkordschlag, dann gehaltener Akkord
    melodie = [(0, 'A4'), (2, 'D5'), (3, 'F#5'), (5, 'A5'), (6, 'G5'), (7, 'F#5'), (8, 'E5')]
    for triole, n in melodie:
        akkordeon.spiele([n], triole * TRIOLE, TRIOLE * 2 - 30 if triole in (3, 6) else TRIOLE - 20, 100)
    haupt = 3 * TPB  # 1,5 s: Name erscheint
    akkordeon.spiele(['D4', 'F#4', 'A4', 'D5'], haupt, int(1.3 * TPB * 2) - 60, 92)
    bass.spiele(['D2'], haupt, TPB * 2, 115)
    blaeser.spiele(['D3', 'A3', 'D4', 'F#4'], haupt, TPB - 60, 100)
    # Schluss bei 3,0 s mit dem Dreifachschlag der Trommeln
    ende = 6 * TPB
    for i, n in enumerate(['A3', 'C#4']):
        blaeser.spiele([n], ende - (2 - i) * (TRIOLE * 2 // 3), TRIOLE // 2, 85)
    blaeser.spiele(['D3', 'A3', 'D4', 'F#4'], ende, TPB // 2, 112)
    akkordeon.spiele(['D4', 'F#4', 'A4', 'D5'], ende, TPB // 2, 105)
    gitarre.spiele(akkorde['D'], ende, TPB // 2, 105, schrumm=8)
    bass.spiele(['D2'], ende, TPB // 2, 120)

    for spur in (gitarre, akkordeon, bass, blaeser):
        mid.tracks.append(spur.als_track())
    mid.save(str(ziel))


def lies(pfad: Path) -> np.ndarray:
    with wave.open(str(pfad)) as w:
        assert w.getframerate() == jingle.RATE and w.getsampwidth() == 2
        daten = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64) / 32768
        return daten.reshape(-1, w.getnchannels()).T


def erzeuge(ziel: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        komponiere(tmp / 'melodie.mid')
        subprocess.run(['fluidsynth', '-ni', '-q', '-g', '0.7', '-r', str(jingle.RATE), '-F', str(tmp / 'instrumente.wav'),
                        str(SOUNDFONT), str(tmp / 'melodie.mid')], check=True)
        jingle.erzeuge_jingle(tmp / 'trommeln.wav', mit_melodie=False)
        instrumente = lies(tmp / 'instrumente.wav')
        trommeln = lies(tmp / 'trommeln.wav')
    n = int(jingle.DAUER * jingle.RATE)
    mix = np.zeros((2, n))
    mix[:, :min(n, instrumente.shape[1])] += instrumente[:, :n] * 1.0
    mix[:, :min(n, trommeln.shape[1])] += trommeln[:, :n] * 0.9
    t = np.arange(n) / jingle.RATE
    mix *= np.clip((jingle.DAUER - t) / 0.35, 0, 1)
    mix /= np.abs(mix).max() / 10 ** (-1 / 20)
    with wave.open(str(ziel), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(jingle.RATE)
        w.writeframes((mix.T * 32767).astype('<i2').tobytes())


if __name__ == '__main__':
    erzeuge(Path(sys.argv[1]) if len(sys.argv) > 1 else HIER / 'vorspann.wav')
