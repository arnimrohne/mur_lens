"""
Baukasten für die Lernvideos „Gazet Morisyen erklärt“.

Ein Video ist ein Modul in lernvideos/ (z. B. lernvideos/wasser.py) mit Szenen, Texten je Sprache und Metadaten.
Dieser Baukasten liefert Zeichenhilfen (Cairo für Formen, Pillow für Texte), Ton (Piper), Musikteppich,
Untertitel (SRT) und den Zusammenbau mit Vor- und Abspann der Sendung.

    python3 lernvideo.py --video wasser --sprache de --stimmen <ordner mit Piper-Stimmen> --ausgabe <ordner>
"""

from __future__ import annotations

import argparse
import importlib
import math
import subprocess
import tempfile
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import cairo
from PIL import Image, ImageDraw

import erzeuge_sendung as es

B, H, FPS = 1920, 1080, 25
SPRACHE = 'de'  # wird in main() gesetzt
VIDEO = None  # das Video-Modul aus lernvideos/, wird in main() gesetzt

# Texte des Rahmens, die jedes Video braucht; das Video ergänzt seine eigenen in VIDEO.UI
BASIS_UI = {
    'en': {'GAZET MORISYEN ERKLÄRT': 'GAZET MORISYEN EXPLAINS', 'Quelle': 'Source'},
    'fr': {'GAZET MORISYEN ERKLÄRT': 'GAZET MORISYEN EXPLIQUE', 'Quelle': 'Source'},
}


def L(deutsch: str) -> str:
    """Bildtext in der Sprache der Fassung (Deutsch ist der Schlüssel)."""
    if SPRACHE == 'de':
        return deutsch
    eigene = getattr(VIDEO, 'UI', {}).get(SPRACHE, {}) if VIDEO else {}
    return eigene.get(deutsch, BASIS_UI.get(SPRACHE, {}).get(deutsch, deutsch))


def prozent(wert: float, stellen: int = 0) -> str:
    return f'{zahl_de(wert, stellen)}{"%" if SPRACHE == "en" else " %"}'


VOR = 0.5  # Sekunden Bild vor dem ersten Wort
NACH = 0.7  # Sekunden Bild nach dem letzten Wort

NAVY = (13 / 255, 32 / 255, 62 / 255)
WASSER = (53 / 255, 201 / 255, 165 / 255)  # Mint der Sendung, auf Navy gut sichtbar
WASSER_TIEF = (15 / 255, 110 / 255, 92 / 255)
ROT = (210 / 255, 46 / 255, 58 / 255)
WEISS = (1, 1, 1)
HELL = (196 / 255, 210 / 255, 230 / 255)
GRAU = (120 / 255, 140 / 255, 170 / 255)



def glatt(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def phase(t: float, start: float, dauer: float) -> float:
    """0 → 1 zwischen start und start+dauer, weich."""
    return glatt((t - start) / dauer) if dauer > 0 else float(t >= start)


def hex_rgb(farbe) -> tuple[float, float, float]:
    return tuple(c / 255 for c in farbe)  # type: ignore[return-value]


def leinwand() -> tuple[cairo.ImageSurface, cairo.Context]:
    fl = cairo.ImageSurface(cairo.FORMAT_ARGB32, B, H)
    c = cairo.Context(fl)
    verlauf = cairo.LinearGradient(0, 0, 0, H)
    verlauf.add_color_stop_rgb(0, *hex_rgb(es.NAVY))
    verlauf.add_color_stop_rgb(1, *hex_rgb(es.NAVY_TIEF))
    c.set_source(verlauf)
    c.paint()
    return fl, c


def zu_pil(fl: cairo.ImageSurface) -> Image.Image:
    fl.flush()
    return Image.frombuffer('RGBA', (B, H), bytes(fl.get_data()), 'raw', 'BGRA', 0, 1).convert('RGB')


def runde_box(c: cairo.Context, x: float, y: float, b: float, h: float, r: float) -> None:
    r = min(r, b / 2, h / 2)
    c.new_sub_path()
    c.arc(x + b - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + b - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    c.close_path()


def tropfen(c: cairo.Context, x: float, y: float, r: float) -> None:
    """Wassertropfen, Spitze oben, Mittelpunkt des Bauchs bei (x, y)."""
    c.new_path()
    c.move_to(x, y - r * 2.1)
    c.curve_to(x + r * 0.35, y - r * 1.3, x + r, y - r * 0.6, x + r, y)
    c.arc(x, y, r, 0, math.pi)
    c.curve_to(x - r, y - r * 0.6, x - r * 0.35, y - r * 1.3, x, y - r * 2.1)
    c.close_path()


def text(bild: Image.Image, xy, inhalt: str, f, farbe=es.WEISS, anker='la', deckkraft: float = 1.0) -> None:
    if deckkraft <= 0:
        return
    if deckkraft >= 1:
        ImageDraw.Draw(bild).text(xy, inhalt, font=f, fill=farbe, anchor=anker)
        return
    ebene = Image.new('RGBA', bild.size, (0, 0, 0, 0))
    ImageDraw.Draw(ebene).text(xy, inhalt, font=f, fill=(*farbe, round(255 * deckkraft)), anchor=anker)
    bild.paste(ebene, (0, 0), ebene)


def zahl_de(wert: float, stellen: int = 1) -> str:
    """Zahl im Format der Fassung: de 92,2 / 1.200, en 92.2 / 1,200."""
    text = f'{wert:,.{stellen}f}'
    if SPRACHE == 'en':
        return text
    if SPRACHE == 'fr':
        return text.replace(',', ' ').replace('.', ',')
    return text.replace(',', '§').replace('.', ',').replace('§', '.')


def rahmen(bild: Image.Image, quelle: str, untertitel: str) -> None:
    z = ImageDraw.Draw(bild)
    logo = es.logo_weiss(54)
    bild.paste(logo, (64, 44), logo)
    es.gesperrt(z, (132, 62), L('GAZET MORISYEN ERKLÄRT'), es.mono(22, True), es.HELLBLAU, 0.12)
    if quelle:
        f = es.mono(20)
        z.text((B - 64, 62), f'{L("Quelle")}{" :" if SPRACHE == "fr" else ":"} {L(quelle)}', font=f, fill=es.HELLBLAU, anchor='ra')
    if untertitel:
        f = es.text_schrift(38)
        zeilen = es.umbrechen(z, untertitel, f, 1500)
        y = H - 70 - 50 * len(zeilen)
        ebene = Image.new('RGBA', bild.size, (0, 0, 0, 0))
        ze = ImageDraw.Draw(ebene)
        breite = max(z.textlength(zl, font=f) for zl in zeilen)
        ze.rounded_rectangle([(B - breite) / 2 - 28, y - 16, (B + breite) / 2 + 28, y + 50 * len(zeilen) + 8],
                             radius=14, fill=(6, 14, 28, 190))
        bild.paste(ebene, (0, 0), ebene)
        for i, zl in enumerate(zeilen):
            z.text((B / 2, y + i * 50), zl, font=f, fill=es.WEISS, anchor='ma')
    es.flaggenlinie(z, H - 8, 8)


@dataclass
class Szene:
    nr: int
    text: str
    quelle: str
    zeichne: Callable[[float, 'Szene'], Image.Image]
    saetze: list[tuple[float, float, str]] = field(default_factory=list)  # (von, bis, Satz) in Szenen-Sekunden
    dauer: float = 0.0

    def satz_start(self, i: int) -> float:
        return self.saetze[i][0] if i < len(self.saetze) else self.dauer


def insel_pfad(c: cairo.Context, x0: float, y0: float, hoehe: float) -> Callable[[float, float], tuple[float, float]]:
    ring = es._INSELN['mauritius']['umriss']
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    k = math.cos(math.radians(sum(ys) / len(ys)))
    m = hoehe / (max(ys) - min(ys))

    def punkt(lon: float, lat: float) -> tuple[float, float]:
        return x0 + (lon - min(xs)) * k * m, y0 + (max(ys) - lat) * m

    pts = es._chaikin([punkt(x, y) for x, y in ring], 3)
    c.new_path()
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path()
    return punkt


def symbol(c: cairo.Context, art: str, x: float, y: float, a: float) -> None:
    c.set_source_rgba(*WEISS, a)
    c.set_line_width(7)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    if art == 'haus':
        c.move_to(x - 60, y - 5)
        c.line_to(x, y - 60)
        c.line_to(x + 60, y - 5)
        c.stroke()
        c.rectangle(x - 45, y - 10, 90, 70)
        c.stroke()
        c.rectangle(x - 13, y + 20, 26, 40)
        c.fill()
    elif art == 'feld':
        for dx in (-34, 0, 34):
            c.move_to(x + dx, y + 60)
            c.line_to(x + dx, y - 60)
            c.stroke()
            for dy in (-30, 0, 30):
                c.move_to(x + dx - 9, y + dy)
                c.line_to(x + dx + 9, y + dy)
                c.stroke()
            c.move_to(x + dx, y - 40)
            c.curve_to(x + dx + 20, y - 55, x + dx + 30, y - 50, x + dx + 34, y - 36)
            c.stroke()
    elif art == 'fabrik':
        c.move_to(x - 65, y + 60)
        c.line_to(x - 65, y - 10)
        for i in range(3):
            c.line_to(x - 65 + i * 35 + 35, y - 35)
            c.line_to(x - 65 + i * 35 + 35, y - 10)
        c.line_to(x + 40, y - 10)
        c.line_to(x + 40, y - 70)
        c.line_to(x + 62, y - 70)
        c.line_to(x + 62, y + 60)
        c.close_path()
        c.stroke()
    elif art == 'hotel':
        c.move_to(x - 10, y + 60)
        c.curve_to(x - 2, y + 20, x + 10, y - 10, x + 6, y - 45)
        c.stroke()
        for w in (-150, -110, -60, -20, 20):
            r = math.radians(w)
            c.move_to(x + 6, y - 45)
            c.curve_to(x + 6 + math.cos(r) * 25, y - 45 + math.sin(r) * 25 - 12,
                       x + 6 + math.cos(r) * 55, y - 45 + math.sin(r) * 55 - 4,
                       x + 6 + math.cos(r) * 68, y - 45 + math.sin(r) * 68 + 14)
            c.stroke()
        c.move_to(x - 70, y + 60)
        c.line_to(x + 70, y + 60)
        c.stroke()


def behaelter(c: cairo.Context, x: float, y: float, b: float, h: float, fuellung: float, a: float,
              farbe=WASSER) -> None:
    if fuellung > 0:
        c.save()
        runde_box(c, x, y, b, h, 14)
        c.clip()
        c.set_source_rgba(*farbe, 0.9 * a)
        c.rectangle(x, y + h * (1 - fuellung), b, h * fuellung)
        c.fill()
        c.restore()
    c.set_source_rgba(1, 1, 1, a)
    c.set_line_width(4)
    runde_box(c, x, y, b, h, 14)
    c.stroke()


def damm(c: cairo.Context, x: float, y: float, a: float, farbe=WEISS) -> None:
    """Damm-Symbol: Trapez-Mauer, links Wasser."""
    c.set_source_rgba(*WASSER, 0.85 * a)
    c.rectangle(x - 46, y - 16, 34, 30)
    c.fill()
    c.set_source_rgba(*farbe, a)
    c.move_to(x - 12, y - 30)
    c.line_to(x + 6, y - 30)
    c.line_to(x + 26, y + 14)
    c.line_to(x - 12, y + 14)
    c.close_path()
    c.fill()


def balken(c: cairo.Context, werte: list[tuple[str, float, bool]], t: float, start: float, maximum: float,
           x0: float = 420, x1: float = 1500, basis: float = 780, hoehe: float = 470) -> list[tuple[float, float, float]]:
    """Senkrechte Balken, nacheinander wachsend; gibt (x-Mitte, y-Oberkante, Fortschritt) je Balken zurück."""
    n = len(werte)
    breite = min(220, (x1 - x0) / n * 0.55)
    schritt = (x1 - x0) / n
    lage = []
    c.set_source_rgba(1, 1, 1, 0.6)
    c.set_line_width(3)
    c.move_to(x0 - 30, basis)
    c.line_to(x1 + 30, basis)
    c.stroke()
    for i, (_, wert, hervor) in enumerate(werte):
        p = phase(t, start + i * 0.6, 0.9)
        xm = x0 + schritt * (i + 0.5)
        h = hoehe * wert / maximum * p
        c.set_source_rgba(*(ROT if hervor else WASSER), 0.95 if p > 0 else 0)
        runde_box(c, xm - breite / 2, basis - h, breite, h + 0.01, 10)
        c.fill()
        c.rectangle(xm - breite / 2, basis - min(h, 10), breite, min(h, 10))
        c.fill()
        lage.append((xm, basis - h, p))
    return lage


def balken_texte(bild: Image.Image, werte: list[tuple[str, float, bool]], lage, einheit: str, stellen: int = 1,
                 basis: float = 780) -> None:
    for (label, wert, hervor), (xm, y, p) in zip(werte, lage):
        if p <= 0:
            continue
        st = stellen if wert % 1 else 0
        einh = '%' if einheit == ' %' and SPRACHE == 'en' else einheit
        text(bild, (xm, y - 74), f'{zahl_de(wert * p, st)}{einh}', es.titel_schrift(56),
             (255, 120, 128) if hervor else es.WEISS, 'ma', min(1.0, p * 2))
        text(bild, (xm, basis + 22), L(label), es.mono(26, True), es.HELLBLAU, 'ma', min(1.0, p * 2))


def ueberschrift(bild: Image.Image, inhalt: str, t: float, y: float = 150) -> None:
    text(bild, (B / 2, y), inhalt, es.titel_schrift(64), anker='ma', deckkraft=phase(t, 0, 0.5))


def wolke(c: cairo.Context, x: float, y: float, a: float, farbe=HELL) -> None:
    c.set_source_rgba(*farbe, a)
    for dx, dy, r in ((-60, 10, 45), (-10, -20, 62), (50, 0, 50), (90, 20, 34)):
        c.arc(x + dx, y + dy, r, 0, 2 * math.pi)
        c.fill()
    runde_box(c, x - 105, y + 5, 230, 50, 25)
    c.fill()


def sonne(c: cairo.Context, x: float, y: float, a: float, dreh: float = 0) -> None:
    c.set_source_rgba(1, 0.78, 0.25, a)
    c.arc(x, y, 50, 0, 2 * math.pi)
    c.fill()
    c.set_line_width(7)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(10):
        w = dreh + k / 10 * 2 * math.pi
        c.move_to(x + math.cos(w) * 68, y + math.sin(w) * 68)
        c.line_to(x + math.cos(w) * 92, y + math.sin(w) * 92)
        c.stroke()


def kasse(c: cairo.Context, x: float, y: float, b: float, h: float, stand: float, a: float) -> None:
    c.set_source_rgba(1, 1, 1, a)
    c.set_line_width(5)
    runde_box(c, x, y, b, h, 16)
    c.stroke()
    c.set_source_rgba(1, 0.78, 0.25, 0.9 * a)
    c.rectangle(x + 12, y + h - 12 - (h - 24) * stand, b - 24, (h - 24) * stand)
    c.fill()


def karten(t: float, s: Szene, eintraege: list[tuple[str, str]], titel: str, fragen: bool = False) -> Image.Image:
    fl, c = leinwand()
    n = len(eintraege)
    b, abstand = (380 if n == 4 else 480), 40
    x0 = (B - (n * b + (n - 1) * abstand)) / 2
    starts = [s.satz_start(i + 1) if i + 1 < len(s.saetze) else 0.8 + i * 1.5 for i in range(n)]
    if fragen:
        starts = [s.satz_start(i) if i < len(s.saetze) else 0.8 + i * 1.5 for i in range(n)]
    for i in range(n):
        p = phase(t, starts[i] - 0.2, 0.5)
        if p <= 0:
            continue
        c.set_source_rgba(1, 1, 1, 0.1 * p)
        runde_box(c, x0 + i * (b + abstand), 300 + 40 * (1 - p), b, 460, 20)
        c.fill()
        c.set_source_rgba(*(ROT if fragen else WASSER), p)
        runde_box(c, x0 + i * (b + abstand), 300 + 40 * (1 - p), b, 12, 6)
        c.fill()
    bild = zu_pil(fl)
    ueberschrift(bild, titel, t)
    for i, (kopf, zeile) in enumerate(eintraege):
        p = phase(t, starts[i] - 0.2, 0.5)
        x = x0 + i * (b + abstand) + b / 2
        if fragen:
            text(bild, (x, 360), '?', es.titel_schrift(120), (255, 120, 128), 'ma', p)
        text(bild, (x, 520 if fragen else 360), L(kopf), es.titel_schrift(44), anker='ma', deckkraft=p)
        z = ImageDraw.Draw(bild)
        for k, zl in enumerate(es.umbrechen(z, L(zeile), es.text_schrift(34), b - 60)):
            text(bild, (x, (590 if fragen else 450) + k * 46), zl, es.text_schrift(34), es.HELLBLAU, 'ma', p)
    return bild


REGION = Path(__file__).resolve().parents[1] / 'lib' / 'zeitung' / 'region-indischer-ozean.json'


def regionalkarte(c: cairo.Context, ausschnitt: tuple[float, float, float, float], x0: float, y0: float, hoehe: float,
                  a: float = 1.0) -> Callable[[float, float], tuple[float, float]]:
    """Küsten des westlichen Indischen Ozeans (Natural Earth, wie die Dossier-Karte) im Ausschnitt (W, S, O, N);
    zeichnet das Land und gibt die Umrechnung lon/lat → Bildpunkt zurück."""
    import json

    w, s, o, n = ausschnitt
    k = math.cos(math.radians((s + n) / 2))
    m = hoehe / (n - s)

    def punkt(lon: float, lat: float) -> tuple[float, float]:
        return x0 + (lon - w) * k * m, y0 + (n - lat) * m

    if a > 0:
        c.save()
        c.rectangle(x0, y0, (o - w) * k * m, hoehe)
        c.clip()
        for ring in json.loads(REGION.read_text(encoding='utf-8'))['land']:
            xs, ys = [p[0] for p in ring], [p[1] for p in ring]
            if max(xs) < w - 1 or min(xs) > o + 1 or max(ys) < s - 1 or min(ys) > n + 1:
                continue
            c.move_to(*punkt(*ring[0]))
            for q in ring[1:]:
                c.line_to(*punkt(*q))
            c.close_path()
        c.set_source_rgba(1, 1, 1, 0.13 * a)
        c.fill_preserve()
        c.set_source_rgba(*HELL, 0.55 * a)
        c.set_line_width(1.5)
        c.stroke()
        c.restore()
    return punkt


def entfernung_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = math.pi / 180
    h = (math.sin((lat2 - lat1) * r / 2) ** 2
         + math.cos(lat1 * r) * math.cos(lat2 * r) * math.sin((lon2 - lon1) * r / 2) ** 2)
    return 6371 * 2 * math.asin(math.sqrt(h))


URL_SPRECHEN = {'de': 'gazet punkt morisyen punkt D E', 'en': 'gazet dot morisyen dot D E',
                'fr': 'gazet point morisyen point D E'}


MONATE = ('Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November',
          'Dezember')


def saetze_trennen(inhalt: str) -> list[str]:
    """Trennt an Satzenden, aber nicht nach einem Datum wie „26. November“."""
    import re

    teile: list[str] = []
    for stueck in re.split(r'(?<=[.!?])\s+', inhalt):
        if teile and re.search(r'\b\d{1,2}\.$', teile[-1]) and stueck.startswith(MONATE):
            teile[-1] += ' ' + stueck
        elif stueck.strip():
            teile.append(stueck)
    return teile


def sprich(sprecher: es.Sprecher, szene: Szene, arbeit: Path) -> Path:
    """Spricht Satz für Satz, merkt sich die Zeiten für Untertitel und Animation, legt VOR/NACH Stille an."""
    import re

    rate = sprecher.rate
    teile = saetze_trennen(szene.text)
    pcm = bytearray(b'\x00\x00' * int(rate * VOR))
    for i, satz in enumerate(teile):
        datei = arbeit / f's{szene.nr}-{i}.wav'
        sprecher.sprich(satz.replace('gazet.morisyen.de', URL_SPRECHEN[SPRACHE]), datei)
        with wave.open(str(datei)) as w:
            daten = w.readframes(w.getnframes())
        # Sprich() hängt PAUSE_S Stille an; die bleibt als Satzpause
        von = len(pcm) / 2 / rate
        pcm += daten
        szene.saetze.append((von, len(pcm) / 2 / rate - es.PAUSE_S, satz))
    pcm += b'\x00\x00' * int(rate * max(0.0, NACH - es.PAUSE_S))
    szene.dauer = len(pcm) / 2 / rate
    ziel = arbeit / f'szene{szene.nr}.wav'
    with wave.open(str(ziel), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(pcm))
    return ziel


def rendere(szene: Szene, ton: Path, ziel: Path) -> None:
    proc = subprocess.Popen(
        ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{B}x{H}',
         '-r', str(FPS), '-i', '-', '-i', str(ton), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
         '-pix_fmt', 'yuv420p', '-r', str(FPS), '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-ac', '2',
         '-shortest', '-movflags', '+faststart', str(ziel)], stdin=subprocess.PIPE)
    assert proc.stdin
    for n in range(math.ceil(szene.dauer * FPS)):
        t = n / FPS
        bild = szene.zeichne(t, szene)
        rahmen(bild, szene.quelle, '')  # Untertitel kommen als SRT-Datei zu YouTube
        # weiche Blende am Anfang und Ende jeder Szene
        blende = min(1.0, t / 0.3, (szene.dauer - t) / 0.3)
        if blende < 1:
            bild = Image.blend(Image.new('RGB', bild.size, es.NAVY_TIEF), bild, max(0.0, blende))
        proc.stdin.write(bild.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f'ffmpeg für Szene {szene.nr} fehlgeschlagen')


def musik_teppich(dauer: float, ziel: Path, arbeit: Path) -> None:
    """Ruhiger Klangteppich (D-Dur, I–IV–vi–V, 72 BPM): gezupfte Nylon-Gitarre, weiche Fläche, Bass; FluidR3-Soundfont."""
    import mido

    tpb, bpm = 480, 72
    sek_takt = 4 * 60 / bpm
    takte = math.ceil(dauer / sek_takt) + 1
    mid = mido.MidiFile(ticks_per_beat=tpb)
    tempo = mido.MidiTrack()
    tempo.append(mido.MetaMessage('set_tempo', tempo=round(60_000_000 / bpm), time=0))
    mid.tracks.append(tempo)
    akkorde = {'D': ['D3', 'A3', 'D4', 'F#4'], 'G': ['G2', 'D3', 'G3', 'B3'], 'Bm': ['B2', 'F#3', 'B3', 'D4'],
               'A': ['A2', 'E3', 'A3', 'C#4']}
    folge = ['D', 'G', 'Bm', 'A']

    def note(n: str) -> int:
        namen = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
        return 12 * (int(n[-1]) + 1) + namen[n[:-1]]

    def spur(kanal: int, programm: int, lautst: int, ereignisse: list) -> mido.MidiTrack:
        tr = mido.MidiTrack()
        tr.append(mido.Message('program_change', channel=kanal, program=programm, time=0))
        tr.append(mido.Message('control_change', channel=kanal, control=7, value=lautst, time=0))
        tr.append(mido.Message('control_change', channel=kanal, control=91, value=70, time=0))
        jetzt = 0
        for zeit, msg in sorted(ereignisse, key=lambda e: (e[0], e[1].type == 'note_on')):
            tr.append(msg.copy(time=zeit - jetzt))
            jetzt = zeit
        return tr

    gitarre, flaeche, bass = [], [], []
    for takt in range(takte):
        akk = akkorde[folge[takt % 4]]
        t0 = takt * 4 * tpb
        muster = [0, 2, 1, 3, 2, 1, 3, 2]  # Achtel-Arpeggio
        for k, idx in enumerate(muster):
            n = note(akk[idx])
            gitarre += [(t0 + k * tpb // 2, mido.Message('note_on', channel=0, note=n, velocity=52 if k else 64)),
                        (t0 + k * tpb // 2 + tpb, mido.Message('note_off', channel=0, note=n, velocity=0))]
        for n in akk[1:]:
            flaeche += [(t0, mido.Message('note_on', channel=1, note=note(n) + 12, velocity=40)),
                        (t0 + 4 * tpb - 10, mido.Message('note_off', channel=1, note=note(n) + 12, velocity=0))]
        bass += [(t0, mido.Message('note_on', channel=2, note=note(akk[0]) - 12 if akk[0][-1] == '3' else note(akk[0]),
                                   velocity=60)),
                 (t0 + 2 * tpb, mido.Message('note_off', channel=2, note=0, velocity=0))]
    bass = [(z, m if m.type == 'note_on' else m.copy(note=bass[i - 1][1].note)) for i, (z, m) in enumerate(bass)]
    mid.tracks += [spur(0, 24, 100, gitarre), spur(1, 89, 70, flaeche), spur(2, 32, 85, bass)]
    mid.save(str(arbeit / 'teppich.mid'))
    roh = arbeit / 'teppich-roh.wav'
    subprocess.run(['fluidsynth', '-ni', '-q', '-g', '0.6', '-r', '48000', '-F', str(roh),
                    '/usr/share/sounds/sf2/FluidR3_GM.sf2', str(arbeit / 'teppich.mid')], check=True)
    es.ffmpeg('-i', str(roh), '-t', f'{dauer:.3f}', '-af',
              f'loudnorm=I=-36:TP=-9:LRA=11,afade=t=in:d=2,afade=t=out:st={max(0.0, dauer - 3):.3f}:d=3',
              '-ar', '48000', '-ac', '2', str(ziel))


def srt_zeit(s: float) -> str:
    ms = round(s * 1000)
    return f'{ms // 3_600_000:02d}:{ms // 60_000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def qr_bild(groesse: int, url: str) -> Image.Image:
    import qrcode

    qr = qrcode.QRCode(border=2, box_size=10)
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color='#0d203e', back_color='white').convert('RGB').resize((groesse, groesse),
                                                                                       Image.NEAREST)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stimmen', type=Path, required=True)
    p.add_argument('--ausgabe', type=Path, required=True)
    p.add_argument('--video', default='wasser', help='Modul in lernvideos/, z. B. wasser')
    p.add_argument('--nur', type=int, nargs='*', help='nur diese Szenen (Nummern)')
    p.add_argument('--sprache', choices=['de', 'en', 'fr'], default='de')
    a = p.parse_args()
    global SPRACHE, VIDEO
    SPRACHE = a.sprache
    VIDEO = importlib.import_module(f'lernvideos.{a.video}')
    SZENEN = VIDEO.SZENEN
    if SPRACHE != 'de':
        for szene in SZENEN:
            szene.text = VIDEO.TEXTE[SPRACHE][szene.nr]
    a.ausgabe.mkdir(parents=True, exist_ok=True)
    arbeit = Path(tempfile.mkdtemp(prefix='lernvideo-'))
    es.lade_franzoesische_namen(a.stimmen)  # Ortsnamen französisch aussprechen, wie in der Sendung
    sprecher = es.Sprecher(a.stimmen / f'{es.STIMMEN[SPRACHE][0]}.onnx', SPRACHE)
    teile = []
    start = 0.0  # Startzeit der aktuellen Szene im fertigen Video
    if not a.nur or 0 in a.nur:
        vorspann = arbeit / 'vorspann.mp4'
        start = es.vorspann_video(SPRACHE, vorspann)
        teile.append(vorspann)
    musik_von = start
    untertitel = []
    for szene in SZENEN:
        if a.nur and szene.nr not in a.nur:
            continue
        ton = sprich(sprecher, szene, arbeit)
        ziel = arbeit / f'szene{szene.nr}.mp4'
        rendere(szene, ton, ziel)
        teile.append(ziel)
        echte_dauer = es.dauer_von(ziel)
        untertitel += [(start + von, start + bis, satz) for von, bis, satz in szene.saetze]
        start += echte_dauer
        print(f'Szene {szene.nr}: {echte_dauer:.1f} s')
    musik_bis = start
    if not a.nur or SZENEN[-1].nr in a.nur:  # Abspann-Folie der Sendung mit Erkennungsmelodie
        abspann = arbeit / 'abspann.mp4'
        es.abspann_video(SPRACHE, VIDEO.STAND_DATUM, abspann)
        teile.append(abspann)
    liste = arbeit / 'liste.txt'
    liste.write_text(''.join(f"file '{t}'\n" for t in teile))
    stamm = (VIDEO.STAMM if not a.nur else f'{VIDEO.STAMM}-teil') + ('' if SPRACHE == 'de' else f'-{SPRACHE}')
    ohne_musik = arbeit / 'ohne-musik.mp4'
    es.ffmpeg('-f', 'concat', '-safe', '0', '-i', str(liste), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
              '-pix_fmt', 'yuv420p', '-r', str(FPS), '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-ac', '2',
              str(ohne_musik))
    teppich = arbeit / 'teppich.wav'
    musik_teppich(musik_bis - musik_von, teppich, arbeit)
    ms = round(musik_von * 1000)
    ziel = a.ausgabe / f'{stamm}.mp4'
    es.ffmpeg('-i', str(ohne_musik), '-i', str(teppich), '-filter_complex',
              f'[1:a]adelay={ms}|{ms}[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]',
              '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
              '-movflags', '+faststart', str(ziel))
    srt = a.ausgabe / f'{stamm}.{SPRACHE}.srt'
    srt.write_text(''.join(f'{i}\n{srt_zeit(von)} --> {srt_zeit(bis)}\n{satz}\n\n'
                           for i, (von, bis, satz) in enumerate(untertitel, 1)), encoding='utf-8')
    print(ziel, srt)


if __name__ == '__main__':
    # Über den Modulnamen starten, damit lernvideos/* denselben Zustand (SPRACHE, VIDEO) sieht
    import lernvideo

    lernvideo.main()
