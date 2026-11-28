"""
Lernvideo „Gazet Morisyen erklärt“ – Pilot: Szenen 0–5 des Storyboards „Warum auf Mauritius das Wasser knapp wird“.

Jede Szene ist eine Funktion bild(t, dauer) → Image; Formen zeichnet Cairo (glatte Kanten), Texte Pillow.
Der Sprechertext kommt von Piper (Sendungsstimme), die Szenenlänge richtet sich nach dem gesprochenen Text.

    python3 lernvideo.py --stimmen <ordner mit de_DE-thorsten-high.onnx> --ausgabe <ordner>
"""

from __future__ import annotations

import argparse
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
STAND = 'Stand: 28. November 2026'
VOR = 0.5  # Sekunden Bild vor dem ersten Wort
NACH = 0.7  # Sekunden Bild nach dem letzten Wort

NAVY = (13 / 255, 32 / 255, 62 / 255)
WASSER = (53 / 255, 201 / 255, 165 / 255)  # Mint der Sendung, auf Navy gut sichtbar
WASSER_TIEF = (15 / 255, 110 / 255, 92 / 255)
ROT = (210 / 255, 46 / 255, 58 / 255)
WEISS = (1, 1, 1)
HELL = (196 / 255, 210 / 255, 230 / 255)
GRAU = (120 / 255, 140 / 255, 170 / 255)


# ----------------------------------------------------------------- Hilfen

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
    return f'{wert:,.{stellen}f}'.replace(',', '§').replace('.', ',').replace('§', '.')


# ----------------------------------------------------------------- Rahmen (Kopf, Quelle, Untertitel)

def rahmen(bild: Image.Image, quelle: str, untertitel: str) -> None:
    z = ImageDraw.Draw(bild)
    logo = es.logo_weiss(54)
    bild.paste(logo, (64, 44), logo)
    es.gesperrt(z, (132, 62), 'GAZET MORISYEN ERKLÄRT', es.mono(22, True), es.HELLBLAU, 0.12)
    if quelle:
        f = es.mono(20)
        z.text((B - 64, 62), f'Quelle: {quelle}', font=f, fill=es.HELLBLAU, anchor='ra')
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


# ----------------------------------------------------------------- Szenen

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


# Szene 1: Rationierung -------------------------------------------------------

ORTE_HOOK = [('Curepipe', -20.3163, 57.5259), ('Vacoas', -20.2981, 57.4783), ('Phoenix', -20.2917, 57.4972),
             ('Floréal', -20.3020, 57.5050)]


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


# Beschriftung je Ort: Endpunkt der Hinweislinie relativ zum Ort
BESCHRIFTUNG = {'Vacoas': (-190, -70), 'Phoenix': (-150, -170), 'Floréal': (190, -150), 'Curepipe': (190, 40)}


def szene_hook(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    auf = phase(t, 0, 0.8)
    punkt = insel_pfad(c, 250, 170, 720)
    c.set_source_rgba(1, 1, 1, 0.08 * auf)
    c.fill_preserve()
    c.set_source_rgba(1, 1, 1, 0.9 * auf)
    c.set_line_width(4)
    c.stroke()
    # Orte nacheinander: Punkt mit Puls, Hinweislinie nach außen
    for i, (name, lat, lon) in enumerate(ORTE_HOOK):
        p = phase(t, 0.9 + i * 0.55, 0.35)
        if p <= 0:
            continue
        x, y = punkt(lon, lat)
        dx, dy = BESCHRIFTUNG[name]
        c.set_source_rgba(1, 1, 1, 0.7 * p)
        c.set_line_width(2)
        c.move_to(x, y)
        c.line_to(x + dx * p, y + dy * p)
        c.stroke()
        puls = (t - 0.9 - i * 0.55) % 1.6 / 1.6
        c.set_source_rgba(*ROT, 0.35 * (1 - puls) * p)
        c.arc(x, y, 10 + 26 * puls, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgba(*ROT, p)
        c.arc(x, y, 9 * p, 0, 2 * math.pi)
        c.fill()
    # rechte Seite: Hahn, Uhr, Kalender (ab dem zweiten Satz, spätestens nach 3,2 s)
    t2 = min(s.satz_start(1), 3.2)
    rx = 1060
    a = phase(t, t2 - 1.2, 0.6)
    if a > 0:  # Wasserhahn mit fallendem Tropfen
        c.set_source_rgba(*HELL, a)
        runde_box(c, rx, 240, 230, 60, 16)
        c.fill()
        runde_box(c, rx + 165, 240, 62, 150, 16)
        c.fill()
        runde_box(c, rx + 55, 196, 66, 52, 10)
        c.fill()
        zyklus = ((t - t2 + 1.2) % 1.8) / 1.8
        ty = 420 + 150 * zyklus ** 2
        c.set_source_rgba(*WASSER, a * (1 - zyklus * 0.7))
        tropfen(c, rx + 196, ty, 17)
        c.fill()
    a = phase(t, t2, 0.6)
    if a > 0:  # Uhr mit grünem Segment 3–8 Uhr
        ux, uy, r = rx + 560, 330, 140
        c.set_source_rgba(1, 1, 1, 0.1 * a)
        c.arc(ux, uy, r, 0, 2 * math.pi)
        c.fill()
        seg = phase(t, t2 + 0.4, 0.9)
        start = -math.pi / 2 + 3 / 12 * 2 * math.pi
        c.move_to(ux, uy)
        c.arc(ux, uy, r, start, start + seg * 5 / 12 * 2 * math.pi)
        c.close_path()
        c.set_source_rgba(*WASSER, 0.85 * a)
        c.fill()
        c.set_source_rgba(1, 1, 1, a)
        c.set_line_width(5)
        c.arc(ux, uy, r, 0, 2 * math.pi)
        c.stroke()
        for st in range(12):
            w = st / 12 * 2 * math.pi - math.pi / 2
            c.move_to(ux + math.cos(w) * (r - 18), uy + math.sin(w) * (r - 18))
            c.line_to(ux + math.cos(w) * (r - 5), uy + math.sin(w) * (r - 5))
            c.stroke()
    for i in range(10):  # Kalenderstreifen: jeder zweite Tag ausgegraut
        p = phase(t, t2 + 0.6 + i * 0.12, 0.3)
        if p <= 0:
            continue
        c.set_source_rgba(*(WASSER if i % 2 == 0 else GRAU), (0.9 if i % 2 == 0 else 0.35) * p)
        runde_box(c, rx + i * 72, 610, 60, 76, 10)
        c.fill()
    bild = zu_pil(fl)
    for i, (name, lat, lon) in enumerate(ORTE_HOOK):
        p = phase(t, 1.1 + i * 0.55, 0.35)
        x, y = punkt(lon, lat)
        dx, dy = BESCHRIFTUNG[name]
        text(bild, (x + dx + (-10 if dx < 0 else 10), y + dy), name, es.titel_schrift(36),
             anker='rm' if dx < 0 else 'lm', deckkraft=p)
    f = es.mono(28, True)
    text(bild, (rx + 560, 500), '3–8 UHR', f, es.HELLBLAU, 'ma', phase(t, t2 + 0.6, 0.5))
    text(bild, (rx, 708), 'JEDEN ZWEITEN TAG', f, es.HELLBLAU, 'la', phase(t, t2 + 1.2, 0.5))
    return bild


# Szene 2: Titelkarte ---------------------------------------------------------

def szene_titel(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    # Tropfen fällt, trifft bei 1,0 s auf, Wellen breiten sich aus
    if t < 1.0:
        y = -60 + (380 + 60) * glatt(t / 1.0) ** 1.6
        c.set_source_rgb(*WASSER)
        tropfen(c, B / 2, y, 26)
        c.fill()
    else:
        for k in range(3):
            w = (t - 1.0 - k * 0.35) / 2.2
            if 0 < w < 1:
                c.set_source_rgba(*WASSER, 0.6 * (1 - w))
                c.set_line_width(4)
                c.save()
                c.translate(B / 2, 380)
                c.scale(1, 0.28)
                c.arc(0, 0, 80 + 620 * w, 0, 2 * math.pi)
                c.restore()
                c.stroke()
    bild = zu_pil(fl)
    a = phase(t, 0.9, 0.7)
    text(bild, (B / 2, 460), 'Warum auf Mauritius', es.titel_schrift(104), anker='ma', deckkraft=a)
    text(bild, (B / 2, 580), 'das Wasser knapp wird', es.titel_schrift(104), anker='ma', deckkraft=a)
    text(bild, (B / 2, 740), STAND.upper(), es.mono(30, True), es.HELLBLAU, 'ma', phase(t, 1.6, 0.6))
    return bild


# Szene 3: Wer braucht Wasser -------------------------------------------------

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


SEKTOREN = [('haus', 'Haushalte', -1, -1), ('feld', 'Landwirtschaft', 1, -1), ('fabrik', 'Industrie', -1, 1),
            ('hotel', 'Tourismus', 1, 1)]


def szene_sektoren(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    mx, my = B / 2, 520
    a = phase(t, 0, 0.6)
    c.set_source_rgba(*WASSER, a)
    tropfen(c, mx, my + 40, 70 * (0.6 + 0.4 * a))
    c.fill()
    t2 = min(s.satz_start(1), 4.0)
    for i, (art, _, sx, sy) in enumerate(SEKTOREN):
        p = phase(t, 0.6 + i * 0.5, 0.5)
        if p <= 0:
            continue
        x, y = mx + sx * 470, my + sy * 190
        # Leitung vom Tropfen zum Symbol, beim „alle spüren es“ wird sie rot gestrichelt
        rot = phase(t, t2, 0.6)
        c.set_source_rgba(*(WASSER if rot < 0.5 else ROT), 0.7 * p)
        c.set_line_width(4)
        if rot >= 0.5:
            c.set_dash([14, 12])
        c.move_to(mx + sx * 90, my + sy * 30)
        c.line_to(mx + sx * 90 + (x - sx * 120 - mx - sx * 90) * p, my + sy * 30 + (y - my - sy * 30) * p)
        c.stroke()
        c.set_dash([])
        symbol(c, art, x, y - 20, p)
    bild = zu_pil(fl)
    for i, (_, name, sx, sy) in enumerate(SEKTOREN):
        p = phase(t, 0.8 + i * 0.5, 0.5)
        text(bild, (mx + sx * 470, my + sy * 190 + 70), name, es.titel_schrift(36), anker='ma', deckkraft=p)
    return bild


# Szene 4: Sieben Reservoirs --------------------------------------------------

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


def szene_reservoirs(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    b, h, abstand = 150, 300, 48
    x0 = (B - (7 * b + 6 * abstand)) / 2
    for i in range(7):
        a = phase(t, 0.2 + i * 0.15, 0.4)
        f = phase(t, 0.6 + i * 0.15, 1.4)
        behaelter(c, x0 + i * (b + abstand), 280, b, h, f, a)
    bild = zu_pil(fl)
    zaehler = phase(t, 1.0, max(2.0, s.satz_start(1) + 1.6 - 1.0))
    sichtbar = phase(t, 0.9, 0.4)
    wert = 92.2 * zaehler
    text(bild, (B / 2, 640), f'{zahl_de(wert)} Mio. m³', es.titel_schrift(110), anker='ma', deckkraft=sichtbar)
    text(bild, (B / 2, 780), 'SPEICHERVERMÖGEN DER SIEBEN GROSSEN RESERVOIRS', es.mono(26, True), es.HELLBLAU, 'ma',
         sichtbar)
    return bild


# Szene 5: Mare-aux-Vacoas ----------------------------------------------------

def szene_mav(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    w = phase(t, 0, 1.0)
    # großer Behälter links
    b, h = 260 + 60 * w, 420
    x, y = 360, 230
    behaelter(c, x, y, b, h, 1.0, 1.0)
    # Kreisdiagramm rechts: Anteil 25,89 / 92,2
    anteil = 25.89 / 92.2
    p = phase(t, 0.8, 1.6)
    kx, ky, r = 1330, 440, 210
    c.set_source_rgba(1, 1, 1, 0.12)
    c.arc(kx, ky, r, 0, 2 * math.pi)
    c.fill()
    if p > 0:
        c.move_to(kx, ky)
        c.arc(kx, ky, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * anteil * p)
        c.close_path()
        c.set_source_rgb(*WASSER)
        c.fill()
    c.set_source_rgb(1, 1, 1)
    c.set_line_width(4)
    c.arc(kx, ky, r, 0, 2 * math.pi)
    c.stroke()
    bild = zu_pil(fl)
    text(bild, (x + b / 2, y + h + 40), 'Mare-aux-Vacoas', es.titel_schrift(46), anker='ma')
    text(bild, (x + b / 2, y + h + 104), '25,9 Mio. m³', es.mono(34, True), es.HELLBLAU, 'ma', phase(t, 0.5, 0.5))
    prozent = round(anteil * 100 * p)
    text(bild, (kx, ky - 40), f'{prozent} %', es.titel_schrift(96), anker='ma', deckkraft=phase(t, 0.8, 0.4))
    text(bild, (kx, ky + r + 40), 'ANTEIL AM GESAMTEN SPEICHER', es.mono(26, True), es.HELLBLAU, 'ma',
         phase(t, 1.4, 0.5))
    return bild


SZENEN = [
    Szene(1, 'Im November 2026 kam in Curepipe, Vacoas, Phoenix und Floréal nur jeden zweiten Tag Wasser aus dem '
             'Hahn. Und auch das nur von drei bis acht Uhr morgens.', 'CWA über allAfrica', szene_hook),
    Szene(2, 'Warum wird auf einer tropischen Insel das Wasser knapp? Das schauen wir uns an. Stand: Ende November '
             '2026.', '', szene_titel),
    Szene(3, 'Wasser braucht die ganze Insel: die Haushalte, die Landwirtschaft, die Industrie und der Tourismus. '
             'Wird es knapp, spüren es alle.', '', szene_sektoren),
    Szene(4, 'Mauritius speichert sein Trinkwasser vor allem in sieben großen Reservoirs. Zusammen fassen sie rund '
             '92 Millionen Kubikmeter.', 'Ministerium für Energie und öffentliche Versorgung', szene_reservoirs),
    Szene(5, 'Das größte ist Mare-aux-Vacoas mit knapp 26 Millionen Kubikmetern, mehr als ein Viertel der gesamten '
             'Menge.', 'Ministerium für Energie und öffentliche Versorgung', szene_mav),
]


# ----------------------------------------------------------------- Ton und Zusammenbau

def sprich(sprecher: es.Sprecher, szene: Szene, arbeit: Path) -> Path:
    """Spricht Satz für Satz, merkt sich die Zeiten für Untertitel und Animation, legt VOR/NACH Stille an."""
    import re

    rate = sprecher.rate
    teile = [x for x in re.split(r'(?<=[.!?])\s+', szene.text) if x.strip()]
    pcm = bytearray(b'\x00\x00' * int(rate * VOR))
    for i, satz in enumerate(teile):
        datei = arbeit / f's{szene.nr}-{i}.wav'
        sprecher.sprich(satz, datei)
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
        satz = next((st for von, bis, st in szene.saetze if von - 0.15 <= t <= bis + 0.3), '')
        rahmen(bild, szene.quelle, satz)
        # weiche Blende am Anfang und Ende jeder Szene
        blende = min(1.0, t / 0.3, (szene.dauer - t) / 0.3)
        if blende < 1:
            bild = Image.blend(Image.new('RGB', bild.size, es.NAVY_TIEF), bild, max(0.0, blende))
        proc.stdin.write(bild.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f'ffmpeg für Szene {szene.nr} fehlgeschlagen')


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stimmen', type=Path, required=True)
    p.add_argument('--ausgabe', type=Path, required=True)
    p.add_argument('--nur', type=int, nargs='*', help='nur diese Szenen (Nummern)')
    a = p.parse_args()
    a.ausgabe.mkdir(parents=True, exist_ok=True)
    arbeit = Path(tempfile.mkdtemp(prefix='lernvideo-'))
    es.lade_franzoesische_namen(a.stimmen)  # Ortsnamen französisch aussprechen, wie in der Sendung
    sprecher = es.Sprecher(a.stimmen / 'de_DE-thorsten-high.onnx', 'de')
    teile = []
    if not a.nur:
        vorspann = arbeit / 'vorspann.mp4'
        es.vorspann_video('de', vorspann)
        teile.append(vorspann)
    for szene in SZENEN:
        if a.nur and szene.nr not in a.nur:
            continue
        ton = sprich(sprecher, szene, arbeit)
        ziel = arbeit / f'szene{szene.nr}.mp4'
        rendere(szene, ton, ziel)
        teile.append(ziel)
        print(f'Szene {szene.nr}: {szene.dauer:.1f} s')
    liste = arbeit / 'liste.txt'
    liste.write_text(''.join(f"file '{t}'\n" for t in teile))
    ziel = a.ausgabe / 'lernvideo-wasser-pilot.mp4'
    es.ffmpeg('-f', 'concat', '-safe', '0', '-i', str(liste), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
              '-pix_fmt', 'yuv420p', '-r', str(FPS), '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-ac', '2',
              '-movflags', '+faststart', str(ziel))
    print(ziel)


if __name__ == '__main__':
    main()
