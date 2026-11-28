"""
Lernvideo „Gazet Morisyen erklärt“ – alle Szenen des Storyboards „Warum auf Mauritius das Wasser knapp wird“.

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
             ('Floréal', -20.3120, 57.4950)]


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
BESCHRIFTUNG = {'Vacoas': (-190, -70), 'Phoenix': (-120, -170), 'Floréal': (-170, 90), 'Curepipe': (190, 40)}


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


# Szene 4a: Alle sieben künstlich --------------------------------------------

STAUSEEN = [(1885, 'Mare-aux-Vacoas'), (1914, 'La Ferme'), (1929, 'La Nicolière'), (1948, 'Mare Longue'),
            (1952, 'Piton du Milieu'), (2002, 'Midlands'), (2017, 'Bagatelle')]


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


def szene_stauseen(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    x0, x1, y = 200, B - 200, 600

    def xpos(jahr: int) -> float:
        return x0 + (jahr - 1880) / (2020 - 1880) * (x1 - x0)

    linie = phase(t, 0.3, 0.8)
    c.set_source_rgba(1, 1, 1, 0.8)
    c.set_line_width(4)
    c.move_to(x0, y)
    c.line_to(x0 + (x1 - x0) * linie, y)
    c.stroke()
    t_alt = s.satz_start(1) if len(s.saetze) > 1 else 2.5
    t_neu = s.satz_start(2) if len(s.saetze) > 2 else 6.0
    for i, (jahr, name) in enumerate(STAUSEEN):
        p = phase(t, 0.8 + i * 0.25, 0.4)
        if p <= 0:
            continue
        x = xpos(jahr)
        hervor = (name == 'Mare-aux-Vacoas' and t >= t_alt) or (name == 'Bagatelle' and t >= t_neu)
        oben = i % 2 == 0
        c.set_source_rgba(*(ROT if hervor else WEISS), p)
        c.arc(x, y, 10 if hervor else 7, 0, 2 * math.pi)
        c.fill()
        c.set_source_rgba(1, 1, 1, 0.5 * p)
        c.set_line_width(2)
        c.move_to(x, y + (-12 if oben else 12))
        c.line_to(x, y + (-70 if oben else 70))
        c.stroke()
        damm(c, x, y + (-118 if oben else 122), p, ROT if hervor else WEISS)
    bild = zu_pil(fl)
    text(bild, (B / 2, 220), '7 von 7 künstlich angelegt', es.titel_schrift(84), anker='ma', deckkraft=phase(t, 0, 0.6))
    for i, (jahr, name) in enumerate(STAUSEEN):
        p = phase(t, 0.9 + i * 0.25, 0.4)
        x = xpos(jahr)
        oben = i % 2 == 0
        hervor = (name == 'Mare-aux-Vacoas' and t >= t_alt) or (name == 'Bagatelle' and t >= t_neu)
        farbe = (255, 120, 128) if hervor else es.WEISS
        if oben:
            text(bild, (x, y - 268), str(jahr), es.mono(30, True), es.HELLBLAU, 'ma', p)
            text(bild, (x, y - 232), name, es.titel_schrift(30), farbe, 'ma', p)
        else:
            text(bild, (x, y + 160), str(jahr), es.mono(30, True), es.HELLBLAU, 'ma', p)
            text(bild, (x, y + 196), name, es.titel_schrift(30), farbe, 'ma', p)
    for jahr in (1900, 1950, 2000):
        text(bild, (xpos(jahr), y + 14), '', es.mono(20))
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
    Szene(41, 'Alle sieben sind künstliche Stauseen. Der älteste ist Mare-aux-Vacoas: 1885 entstand dort im Sumpfland '
              'ein erster, nur einen Meter hoher Damm. Der jüngste ist der Damm von Bagatelle aus dem Jahr 2017.',
          'Ministerium; Statistics Mauritius (ODE)', szene_stauseen),
    Szene(5, 'Das größte ist Mare-aux-Vacoas mit knapp 26 Millionen Kubikmetern, mehr als ein Viertel der gesamten '
             'Menge.', 'Ministerium für Energie und öffentliche Versorgung', szene_mav),
]



# ----------------------------------------------------------------- Szenen 6–22

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
        text(bild, (xm, y - 74), f'{zahl_de(wert * p, st)}{einheit}', es.titel_schrift(56),
             (255, 120, 128) if hervor else es.WEISS, 'ma', min(1.0, p * 2))
        text(bild, (xm, basis + 22), label, es.mono(26, True), es.HELLBLAU, 'ma', min(1.0, p * 2))


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


def szene_regen(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    t2 = s.satz_start(1) if len(s.saetze) > 1 else 3.0
    bx, by, bb, bh = B / 2 - 160, 420, 320, 380
    if t < t2:
        pegel = 0.25 + 0.6 * phase(t, 0.6, max(1.0, t2 - 0.8))
    else:
        pegel = 0.85 - 0.55 * phase(t, t2 + 0.3, max(1.5, s.dauer - t2 - 1.0))
    behaelter(c, bx, by, bb, bh, pegel, 1.0)
    wa = 1 - phase(t, t2, 0.8)
    if wa > 0:
        wolke(c, B / 2, 230, wa)
        for k in range(14):
            phase_k = ((t * 1.3 + k * 0.37) % 1.0)
            x = B / 2 - 100 + (k * 53) % 220
            y = 300 + phase_k * 110
            c.set_source_rgba(*WASSER, wa * (1 - phase_k))
            tropfen(c, x, y, 7)
            c.fill()
    sa = phase(t, t2, 0.8)
    if sa > 0:
        sonne(c, B / 2 + 330, 250, sa, t * 0.3)
    bild = zu_pil(fl)
    text(bild, (B / 2, by + bh + 30), f'Pegel {round(pegel * 100)} %', es.mono(30, True), es.HELLBLAU, 'ma')
    return bild


FUELLSTAND = [('Vor einem Jahr', 69.7, False), ('Saisonaler Schnitt', 55.2, False), ('26.11.2026', 44.0, True)]


def szene_fuellstand(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    lage = balken(c, FUELLSTAND, t, 0.6, 100)
    bild = zu_pil(fl)
    ueberschrift(bild, 'Füllstand der sieben Reservoirs', t)
    balken_texte(bild, FUELLSTAND, lage, ' %')
    return bild


FOTO = HIER_REPO = Path(__file__).resolve().parent.parent / 'public' / 'bilder' / 'wasserversorgung.jpg'


def szene_mav_pegel(t: float, s: Szene) -> Image.Image:
    foto_ab = max(3.6, s.dauer - 3.8)
    if t >= foto_ab:  # langsamer Zoom auf das Foto, mit Bildnachweis
        foto = Image.open(FOTO).convert('RGB')
        z = 1.0 + 0.08 * glatt((t - foto_ab) / max(1.0, s.dauer - foto_ab))
        hoehe = H * z
        breite = foto.width * hoehe / foto.height
        foto = foto.resize((round(breite), round(hoehe)), Image.LANCZOS)
        x = (foto.width - B) // 2
        y = (foto.height - H) // 2
        bild = foto.crop((x, y, x + B, y + H))
        a = phase(t, foto_ab, 0.5)
        if a < 1:
            bild = Image.blend(szene_mav_pegel(foto_ab - 0.04, s), bild, a)
        z_ = ImageDraw.Draw(bild)
        z_.text((B - 40, H - 120), 'Foto: Diego Delso, CC BY-SA 4.0, Wikimedia Commons', font=es.mono(22),
                fill=es.WEISS, anchor='ra', stroke_width=3, stroke_fill=(0, 0, 0))
        return bild
    fl, c = leinwand()
    links = 0.74
    rechts = 0.74 - 0.41 * phase(t, 0.8, 2.2)
    behaelter(c, 560, 300, 280, 380, links, phase(t, 0, 0.5))
    behaelter(c, 1080, 300, 280, 380, rechts, phase(t, 0.2, 0.5), ROT if rechts < 0.6 else WASSER)
    bild = zu_pil(fl)
    ueberschrift(bild, 'Mare-aux-Vacoas', t)
    text(bild, (700, 710), 'Nov. 2025', es.mono(30, True), es.HELLBLAU, 'ma')
    text(bild, (1220, 710), 'Nov. 2026', es.mono(30, True), es.HELLBLAU, 'ma')
    text(bild, (700, 230), '74 %', es.titel_schrift(56), anker='ma', deckkraft=phase(t, 0.3, 0.5))
    text(bild, (1220, 230), f'{round(rechts * 100)} %', es.titel_schrift(56), (255, 120, 128), 'ma',
         phase(t, 0.5, 0.5))
    return bild


def szene_cwa(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    y = 520
    # Leitung mit Ventil, das im Takt einer Uhr öffnet und schließt
    c.set_source_rgba(*HELL, phase(t, 0.2, 0.6))
    runde_box(c, 260, y - 30, 1400, 60, 30)
    c.fill()
    offen = (math.sin(t * 2.2) + 1) / 2 > 0.5
    c.set_source_rgba(*(WASSER if offen else ROT), 1)
    runde_box(c, B / 2 - 50, y - 90, 100, 180, 16)
    c.fill()
    c.set_source_rgba(1, 1, 1, 1)
    c.set_line_width(10)
    c.move_to(B / 2 - 70, y - 130)
    c.line_to(B / 2 + 70, y - 130)
    c.stroke()
    if offen:
        for k in range(5):
            xk = B / 2 + 80 + ((t * 300 + k * 140) % 700)
            c.set_source_rgba(*WASSER, 0.9)
            tropfen(c, xk, y + 8, 12)
            c.fill()
    # kleine Uhr
    ux, uy, r = 1500, 280, 90
    c.set_source_rgba(1, 1, 1, 0.9)
    c.set_line_width(5)
    c.arc(ux, uy, r, 0, 2 * math.pi)
    c.stroke()
    w = t * 1.1 - math.pi / 2
    c.move_to(ux, uy)
    c.line_to(ux + math.cos(w) * (r - 20), uy + math.sin(w) * (r - 20))
    c.stroke()
    bild = zu_pil(fl)
    text(bild, (400, 230), 'CWA', es.titel_schrift(120), deckkraft=phase(t, 0, 0.5))
    text(bild, (404, 370), 'CENTRAL WATER AUTHORITY', es.mono(28, True), es.HELLBLAU, 'la', phase(t, 0.3, 0.5))
    text(bild, (B / 2, y + 140), 'AUF' if offen else 'ZU', es.mono(40, True), es.WEISS, 'ma')
    return bild


VERKAUF = [('Aufbereitet', 332, False), ('Verkauft', 115, True)]


def szene_verkauf(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    t2 = s.satz_start(1) if len(s.saetze) > 1 else 1.5
    werte = [VERKAUF[0]] + ([VERKAUF[1]] if t >= t2 else [])
    lage = balken(c, werte + [('', 0, False)] * (2 - len(werte)), t, 0.5, 340, x0=560, x1=1360)
    bild = zu_pil(fl)
    ueberschrift(bild, 'Wasser der CWA im Jahr 2024, in Mio. m³', t)
    balken_texte(bild, werte, lage[:len(werte)], '', 0)
    return bild


def szene_verluste(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    t2 = s.satz_start(1) if len(s.saetze) > 1 else 3.0
    ziele = [(560, 760), (B / 2, 760), (1360, 760)]
    for i in range(10):
        x0, y0 = 330 + i * 140, 360
        verlust = i >= 4
        p = phase(t, t2 + (i - 4) * 0.35, 1.2) if verlust else 0
        if verlust:
            zx, zy = ziele[(i - 4) % 3]
            x, y = x0 + (zx - x0) * p, y0 + (zy - 60 - y0) * p
        else:
            x, y = x0, y0
        farbe = GRAU if verlust and phase(t, 0.6 + i * 0.1, 0.5) > 0.5 else WASSER
        c.set_source_rgba(*farbe, phase(t, i * 0.08, 0.4) * (1 - 0.5 * p))
        tropfen(c, x, y, 34)
        c.fill()
    a = phase(t, t2, 0.6)
    # Riss im Rohr
    c.set_source_rgba(*HELL, a)
    runde_box(c, 470, 790, 180, 40, 20)
    c.fill()
    c.set_source_rgba(*ROT, a)
    c.set_line_width(5)
    c.move_to(555, 785)
    c.line_to(565, 805)
    c.line_to(550, 818)
    c.line_to(562, 835)
    c.stroke()
    # Abzweig
    c.set_source_rgba(*HELL, a)
    runde_box(c, B / 2 - 90, 790, 180, 40, 20)
    c.fill()
    runde_box(c, B / 2 + 20, 830, 40, 70, 12)
    c.fill()
    # Zähler
    c.set_source_rgba(*HELL, a)
    c.arc(1360, 820, 52, 0, 2 * math.pi)
    c.set_line_width(6)
    c.stroke()
    bild = zu_pil(fl)
    text(bild, (B / 2, 150), 'Rund 60 % des Wassers bringen kein Geld ein', es.titel_schrift(60), anker='ma',
         deckkraft=phase(t, 0.3, 0.6))
    f = es.mono(24, True)
    for (x, _), name in zip(ziele, ('Lecks', 'Illegale Anschlüsse', 'Abrechnungsfehler')):
        text(bild, (x, 920), name.upper(), f, es.HELLBLAU, 'ma', a)
    text(bild, (1360, 795), '?', es.titel_schrift(48), (255, 120, 128), 'ma', a)
    return bild


def szene_rechnungshof(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    p = phase(t, 0.5, 1.6)
    c.set_source_rgba(*ROT, 1)
    c.set_line_width(10)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    x0, y0, x1, y1 = 260, 720, 960, 330
    c.move_to(x0, y0)
    c.line_to(x0 + (x1 - x0) * p, y0 + (y1 - y0) * p)
    c.stroke()
    if p > 0.95:
        c.move_to(x1, y1)
        c.line_to(x1 - 50, y1 + 5)
        c.move_to(x1, y1)
        c.line_to(x1 - 20, y1 + 48)
        c.stroke()
    c.set_source_rgba(1, 1, 1, 0.6)
    c.set_line_width(3)
    c.move_to(240, 760)
    c.line_to(1000, 760)
    c.stroke()
    t2 = s.satz_start(1) if len(s.saetze) > 1 else 3.0
    for k in range(4):
        q = phase(t, t2 + k * 0.45, 0.4)
        if q <= 0:
            continue
        c.set_source_rgba(*HELL, q)
        runde_box(c, 1220 + k * 24, 680 - k * 110 - 40 * (1 - q), 330, 90, 10)
        c.fill()
    bild = zu_pil(fl)
    ueberschrift(bild, 'Rechnungshof, Dezember 2025', t)
    text(bild, (600, 780), '10 JAHRE', es.mono(28, True), es.HELLBLAU, 'ma', phase(t, 0.5, 0.5))
    text(bild, (300, 330), 'Anteil ohne Einnahmen', es.titel_schrift(36), deckkraft=phase(t, 0.8, 0.5))
    for k in range(4):
        q = phase(t, t2 + k * 0.45, 0.4)
        text(bild, (1385 + k * 24, 725 - k * 110 - 40 * (1 - q)), 'STUDIE', es.mono(30, True), es.NAVY, 'mm', q)
    return bild


def szene_kosten(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    t2 = s.satz_start(1) if len(s.saetze) > 1 else 3.0
    a = phase(t, t2, 0.5)
    if a > 0:
        c.set_source_rgba(1, 1, 1, a)
        runde_box(c, B / 2 - 130, 640, 260, 230, 18)
        c.fill()
        c.set_source_rgba(*ROT, a)
        runde_box(c, B / 2 - 130, 640, 260, 60, 18)
        c.fill()
        c.rectangle(B / 2 - 130, 670, 260, 30)
        c.fill()
    bild = zu_pil(fl)
    wert = 540 * phase(t, 0.3, 2.2)
    text(bild, (B / 2, 300), f'Rs {round(wert)} Mio.', es.titel_schrift(150), (255, 120, 128), 'ma',
         phase(t, 0.2, 0.4))
    text(bild, (B / 2, 520), 'VERLUST DER CWA LAUT MEDIENBERICHT', es.mono(28, True), es.HELLBLAU, 'ma',
         phase(t, 0.6, 0.5))
    text(bild, (B / 2, 760), 'pro', es.titel_schrift(44), es.NAVY, 'ma', a)
    text(bild, (B / 2, 810), 'Monat', es.titel_schrift(44), es.NAVY, 'ma', a)
    return bild


def kasse(c: cairo.Context, x: float, y: float, b: float, h: float, stand: float, a: float) -> None:
    c.set_source_rgba(1, 1, 1, a)
    c.set_line_width(5)
    runde_box(c, x, y, b, h, 16)
    c.stroke()
    c.set_source_rgba(1, 0.78, 0.25, 0.9 * a)
    c.rectangle(x + 12, y + h - 12 - (h - 24) * stand, b - 24, (h - 24) * stand)
    c.fill()


def szene_haushalt(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    sinkt = phase(t, 0.8, 3.5)
    kasse(c, 330, 330, 300, 380, 0.8 - 0.5 * sinkt, phase(t, 0, 0.5))
    kasse(c, 1200, 260, 420, 520, 0.8 - 0.2 * phase(t, 1.6, 3.0), phase(t, 0.4, 0.5))
    a = phase(t, 0.8, 0.6)
    c.set_source_rgba(*ROT, a)
    c.set_line_width(8)
    c.set_dash([24, 16], -t * 80)
    c.move_to(660, 520)
    c.line_to(1160, 520)
    c.stroke()
    c.set_dash([])
    c.move_to(1160, 520)
    c.line_to(1120, 495)
    c.move_to(1160, 520)
    c.line_to(1120, 545)
    c.stroke()
    bild = zu_pil(fl)
    text(bild, (480, 740), 'CWA', es.titel_schrift(48), anker='ma')
    text(bild, (1410, 800), 'Staatshaushalt', es.titel_schrift(48), anker='ma', deckkraft=phase(t, 0.4, 0.5))
    return bild


def szene_tarife(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    t2 = s.satz_start(1) if len(s.saetze) > 1 else 3.5
    x0, x1, y = 260, 1100, 520
    c.set_source_rgba(1, 1, 1, 0.8)
    c.set_line_width(4)
    c.move_to(x0, y)
    c.line_to(x0 + (x1 - x0) * phase(t, 0.2, 1.4), y)
    c.stroke()
    # Preisschild bei 2012, Eis zieht auf
    c.set_source_rgba(*HELL, 1)
    c.move_to(x0 + 20, y - 150)
    c.line_to(x0 + 170, y - 150)
    c.line_to(x0 + 210, y - 105)
    c.line_to(x0 + 170, y - 60)
    c.line_to(x0 + 20, y - 60)
    c.close_path()
    c.fill()
    eis = phase(t, 1.2, 1.5)
    c.set_source_rgba(0.75, 0.9, 1, 0.55 * eis)
    c.set_line_width(4)
    for k in range(6):
        cx, cy = x0 + 40 + k * 28, y - 105 + (k % 2) * 18
        for w in range(3):
            ang = w * math.pi / 3
            c.move_to(cx - math.cos(ang) * 14 * eis, cy - math.sin(ang) * 14 * eis)
            c.line_to(cx + math.cos(ang) * 14 * eis, cy + math.sin(ang) * 14 * eis)
        c.stroke()
    a = phase(t, t2, 0.6)
    if a > 0:  # Haus mit Würfel 6 m³ und Stempel gratis
        hx, hy = 1450, 560
        c.set_source_rgba(1, 1, 1, a)
        c.set_line_width(8)
        c.move_to(hx - 130, hy - 40)
        c.line_to(hx, hy - 160)
        c.line_to(hx + 130, hy - 40)
        c.stroke()
        c.rectangle(hx - 100, hy - 50, 200, 170)
        c.stroke()
        c.set_source_rgba(*WASSER, a)
        runde_box(c, hx - 60, hy - 10, 120, 110, 10)
        c.fill()
    bild = zu_pil(fl)
    ueberschrift(bild, 'Wasserpreise', t)
    text(bild, (x0 + 100, y - 118), 'Tarif', es.titel_schrift(36), es.NAVY, 'ma')
    text(bild, (x0, y + 24), '2012', es.mono(30, True), es.HELLBLAU, 'ma')
    text(bild, (x1, y + 24), '2026', es.mono(30, True), es.HELLBLAU, 'ma', phase(t, 1.4, 0.4))
    text(bild, (680, y + 90), 'SEITDEM UNVERÄNDERT', es.mono(28, True), (255, 120, 128), 'ma', phase(t, 1.6, 0.5))
    a = phase(t, t2, 0.6)
    text(bild, (1450, 595), '6 m³', es.titel_schrift(40), es.NAVY, 'mm', a)
    st = phase(t, t2 + 0.8, 0.3)
    if st > 0:
        ebene = Image.new('RGBA', bild.size, (0, 0, 0, 0))
        ze = ImageDraw.Draw(ebene)
        ze.rounded_rectangle([1320, 720, 1580, 800], 12, outline=(255, 120, 128, round(255 * st)), width=6)
        ze.text((1450, 760), 'GRATIS', font=es.mono(44, True), fill=(255, 120, 128, round(255 * st)), anchor='mm')
        ebene = ebene.rotate(-8, center=(1450, 760))
        bild.paste(ebene, (0, 0), ebene)
    text(bild, (1450, 830), 'bis 6 m³ im Monat', es.mono(26, True), es.HELLBLAU, 'ma', st)
    return bild


def szene_anschluss(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    c.set_source_rgba(*HELL, phase(t, 0, 0.5))
    runde_box(c, 260, 600, 600, 50, 25)
    c.fill()
    runde_box(c, 780, 420, 50, 230, 20)
    c.fill()
    c.set_source_rgba(1, 1, 1, phase(t, 0.3, 0.5))
    c.set_line_width(8)
    c.move_to(700, 420)
    c.line_to(805, 330)
    c.line_to(910, 420)
    c.stroke()
    c.rectangle(725, 410, 160, 120)
    c.stroke()
    klein = phase(t, 0.8, 0.5)
    gross = phase(t, 1.6, 1.6)
    for (x, sk, a, farbe) in ((1080, 1.0, klein, HELL), (1420, 1.0 + 1.2 * gross, phase(t, 1.6, 0.4), ROT)):
        if a <= 0:
            continue
        c.save()
        c.translate(x, 520)
        c.scale(sk, sk)
        c.set_source_rgba(*farbe, a)
        c.move_to(-70, -40)
        c.line_to(40, -40)
        c.line_to(75, 0)
        c.line_to(40, 40)
        c.line_to(-70, 40)
        c.close_path()
        c.fill()
        c.restore()
    bild = zu_pil(fl)
    ueberschrift(bild, 'Ein neuer Anschluss', t)
    text(bild, (1080, 640), 'BERECHNET', es.mono(28, True), es.HELLBLAU, 'ma', klein)
    text(bild, (1420, 700), 'TATSÄCHLICHE KOSTEN', es.mono(28, True), (255, 120, 128), 'ma', phase(t, 1.6, 0.4))
    return bild


def szene_damm(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    punkt = insel_pfad(c, 160, 200, 680)
    c.set_source_rgba(1, 1, 1, 0.08)
    c.fill_preserve()
    c.set_source_rgba(1, 1, 1, 0.9)
    c.set_line_width(4)
    c.stroke()
    x, y = punkt(57.5528, -20.4867)
    damm(c, x, y, phase(t, 0.4, 0.5), ROT)
    t2 = s.satz_start(1) if len(s.saetze) > 1 else 3.0
    werte = [('Schätzung 2009', 2.6, False), ('Schätzung 2024', 9.4, True)]
    lage = balken(c, [werte[0]] + ([werte[1]] if t >= t2 + 2.0 else [('', 0, False)]), t, t2, 10,
                  x0=900, x1=1700, basis=800, hoehe=470)
    bild = zu_pil(fl)
    text(bild, (x, y + 40), 'Rivière-des-Anguilles', es.titel_schrift(34), anker='ma', deckkraft=phase(t, 0.6, 0.5))
    text(bild, (1300, 150), 'Geschätzte Kosten, Mrd. Rupien', es.titel_schrift(50), anker='ma',
         deckkraft=phase(t, t2, 0.5))
    sichtbar = [werte[0]] + ([werte[1]] if t >= t2 + 2.0 else [])
    balken_texte(bild, sichtbar, lage[:len(sichtbar)], '', 1, basis=800)
    return bild


def szene_bauzeit(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    x0, x1, y = 260, 1660, 540
    punkte = [(2009.0, 'Ankündigung'), (2026.9, 'Baubeginn?'), (2029.9, 'Fertigstellung geplant')]

    def xpos(j: float) -> float:
        return {2009.0: 420, 2026.9: 1060, 2029.9: 1500}[j]

    c.set_source_rgba(1, 1, 1, 0.8)
    c.set_line_width(4)
    c.move_to(x0, y)
    c.line_to(700, y)
    c.move_to(760, y)
    c.line_to(xpos(2026.9), y)
    c.stroke()
    for dx in (700, 730):  # Bruchzeichen: die Achse ist zwischen 2009 und 2026 verkürzt
        c.move_to(dx - 8, y + 18)
        c.line_to(dx + 22, y - 18)
        c.stroke()
    c.set_dash([14, 12])
    c.move_to(xpos(2026.9), y)
    c.line_to(x1, y)
    c.stroke()
    c.set_dash([])
    for i, (j, _) in enumerate(punkte):
        p = phase(t, 0.4 + i * 0.8, 0.4)
        blink = 0.5 + 0.5 * math.sin(t * 6) if i == 1 else 1
        c.set_source_rgba(*(ROT if i == 1 else WEISS), p * blink)
        c.arc(xpos(j), y, 14, 0, 2 * math.pi)
        c.fill()
    bild = zu_pil(fl)
    ueberschrift(bild, 'Damm von Rivière-des-Anguilles', t)
    for i, ((j, name), datum) in enumerate(zip(punkte, ('2009', 'Nov. 2026', 'Nov. 2029'))):
        p = phase(t, 0.5 + i * 0.8, 0.4)
        text(bild, (xpos(j), y - 90), datum, es.mono(32, True), es.HELLBLAU, 'ma', p)
        text(bild, (xpos(j), y + 40), name, es.titel_schrift(40), (255, 120, 128) if i == 1 else es.WEISS, 'ma', p)
    t2 = s.satz_start(1) if len(s.saetze) > 1 else 3.0
    text(bild, (B / 2, 760), 'KEIN UNTERZEICHNETER BAUVERTRAG BEKANNT', es.mono(30, True), (255, 120, 128), 'ma',
         phase(t, t2, 0.5))
    return bild


AKTEURE = [('Ministerium', 'setzt auf neue Speicher'), ('Rechnungshof', 'kritisiert die Verluste'),
           ('Fachleute', 'Tarife zu niedrig, aber erst besserer Service'), ('Haushalte', 'tragen die Rationierung')]


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
        text(bild, (x, 520 if fragen else 360), kopf, es.titel_schrift(44), anker='ma', deckkraft=p)
        z = ImageDraw.Draw(bild)
        for k, zl in enumerate(es.umbrechen(z, zeile, es.text_schrift(34), b - 60)):
            text(bild, (x, (590 if fragen else 450) + k * 46), zl, es.text_schrift(34), es.HELLBLAU, 'ma', p)
    return bild


def szene_akteure(t: float, s: Szene) -> Image.Image:
    return karten(t, s, AKTEURE, 'Wer will was?')


FRAGEN = [('Regenzeit', 'Füllt sie die Reservoirs wieder?'), ('Tarife', 'Steigen sie, und wer wird geschützt?'),
          ('Lecks', 'Wie schnell wird das Netz dicht?')]


def szene_offen(t: float, s: Szene) -> Image.Image:
    return karten(t, s, FRAGEN, 'Offene Fragen', fragen=True)


def szene_fazit(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    xs = [480, B / 2, 1440]
    a = [phase(t, 0.3 + i * 0.6, 0.5) for i in range(3)]
    if a[0] > 0:
        sonne(c, xs[0], 330, a[0], t * 0.3)
        behaelter(c, xs[0] - 90, 470, 180, 220, 0.15, a[0], ROT)
    if a[1] > 0:
        c.set_source_rgba(*HELL, a[1])
        runde_box(c, xs[1] - 150, 450, 300, 60, 30)
        c.fill()
        zyklus = (t % 1.2) / 1.2
        c.set_source_rgba(*WASSER, a[1] * (1 - zyklus))
        tropfen(c, xs[1], 540 + 120 * zyklus, 16)
        c.fill()
    if a[2] > 0:
        c.set_source_rgba(1, 0.78, 0.25, a[2])
        c.move_to(xs[2], 330)
        c.line_to(xs[2] + 130, 560)
        c.line_to(xs[2] - 130, 560)
        c.close_path()
        c.fill()
        c.set_source_rgba(*NAVY, a[2])
        c.rectangle(xs[2] - 8, 410, 16, 90)
        c.fill()
        c.arc(xs[2], 525, 10, 0, 2 * math.pi)
        c.fill()
    bild = zu_pil(fl)
    ueberschrift(bild, 'Kurz gesagt', t)
    for x, name, p in zip(xs, ('Zu wenig Regen', 'Zu viel Verlust', 'Projekte, die warten'), a):
        text(bild, (x, 740), name, es.titel_schrift(46), anker='ma', deckkraft=p)
    return bild


DOSSIER_URL = 'https://gazet.morisyen.de/dossier/wasserversorgung'


def qr_bild(groesse: int) -> Image.Image:
    import qrcode

    qr = qrcode.QRCode(border=2, box_size=10)
    qr.add_data(DOSSIER_URL)
    qr.make(fit=True)
    return qr.make_image(fill_color='#0d203e', back_color='white').convert('RGB').resize((groesse, groesse),
                                                                                       Image.NEAREST)


def szene_ende(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    bild = zu_pil(fl)
    logo = es.logo_weiss(150)
    a = phase(t, 0, 0.6)
    if a > 0:
        bild.paste(logo, (260, 300), logo)
    text(bild, (440, 330), 'gazet.morisyen.de', es.titel_schrift(96), deckkraft=a)
    text(bild, (444, 460), 'DOSSIER: WASSERVERSORGUNG · STAND 28.11.2026', es.mono(30, True), es.HELLBLAU, 'la',
         phase(t, 0.5, 0.5))
    text(bild, (444, 520), 'Alle Quellen, Hintergründe und neue Meldungen', es.text_schrift(38), es.WEISS, 'la',
         phase(t, 0.8, 0.5))
    q = phase(t, 1.0, 0.5)
    if q > 0:
        qr = qr_bild(300)
        ebene = Image.new('RGB', qr.size)
        bild.paste(Image.blend(Image.new('RGB', qr.size, es.NAVY), qr, q), (1380, 280))
        text(bild, (1530, 600), 'ZUM DOSSIER', es.mono(26, True), es.HELLBLAU, 'ma', q)
    return bild


SZENEN_WEITER = [
    Szene(6, 'Gefüllt werden die Reservoirs vom Regen. Bleibt er aus, sinken die Pegel. Genau das ist 2026 passiert.',
          '', szene_regen),
    Szene(7, 'Am 26. November waren die sieben Reservoirs nur noch zu 44 Prozent gefüllt. Ein Jahr zuvor waren es '
             'fast 70 Prozent, im Schnitt dieser Jahreszeit rund 55.', 'Water Resources Commission über ION News',
          szene_fuellstand),
    Szene(8, 'Bei Mare-aux-Vacoas ist der Rückgang besonders deutlich: Mitte November rund 33 Prozent, ein Jahr zuvor '
             '74.', 'allAfrica / L\'Express', szene_mav_pegel),
    Szene(9, 'Sinken die Pegel, schränkt die Central Water Authority, kurz CWA, die Versorgung ein. Dann fließt das '
             'Wasser nur noch zu bestimmten Stunden.', '', szene_cwa),
    Szene(10, 'Doch es fehlt nicht nur Regen. 2024 hat die CWA 332 Millionen Kubikmeter Wasser aufbereitet. Verkauft '
              'wurden davon nur 115 Millionen, also gut ein Drittel.', 'Statistics Mauritius', szene_verkauf),
    Szene(11, 'Fachleute schätzen: Rund 60 Prozent des Wassers bringen kein Geld ein. Es versickert in alten, '
              'undichten Leitungen, fließt über illegale Anschlüsse ab oder wird falsch abgerechnet.', 'L\'Express',
          szene_verluste),
    Szene(12, 'Der Rechnungshof hat im Dezember 2025 festgestellt: Dieser Anteil ist über zehn Jahre gestiegen. Und '
              'Lösungen werden immer wieder durch neue Studien aufgeschoben.', 'National Audit Office',
          szene_rechnungshof),
    Szene(13, 'Das kostet die CWA nach Medienberichten rund 540 Millionen Rupien. Jeden Monat.', 'newsmoris',
          szene_kosten),
    Szene(14, 'Diese Verluste belasten die Finanzen der CWA und damit am Ende auch den Staatshaushalt.', '',
          szene_haushalt),
    Szene(15, 'Gleichzeitig wurden die Wasserpreise seit 2012 nicht mehr angepasst. Wer höchstens sechs Kubikmeter im '
              'Monat verbraucht, zahlt gar nichts.', 'CWA-Jahresbericht 2024–25', szene_tarife),
    Szene(16, 'Die CWA weist außerdem darauf hin: Ein neuer Anschluss kostet sie ein Vielfaches dessen, was sie dafür '
              'berechnet.', 'CWA-Jahresbericht 2024–25', szene_anschluss),
    Szene(17, 'Große Hoffnung ruht auf einem neuen Damm bei Rivière-des-Anguilles im Süden. Angekündigt wurde er 2009, '
              'für 2,6 Milliarden Rupien. 2024 lag die Schätzung bei rund 9,4 Milliarden.', 'National Audit Office',
          szene_damm),
    Szene(18, 'Laut Energieminister soll der Bau im November 2026 beginnen und 2029 fertig sein. Ein unterzeichneter '
              'Bauvertrag ist bisher aber nicht bekannt.', 'Maurice Info', szene_bauzeit),
    Szene(19, 'Die Beteiligten setzen unterschiedliche Schwerpunkte. Das Ministerium baut auf neue Speicher. Der '
              'Rechnungshof kritisiert die Verluste. Fachleute halten die Tarife für zu niedrig, wollen aber zuerst '
              'besseren Service. Und die Haushalte tragen die Folgen der Rationierung.',
          'NAO, L\'Express, Ministerium', szene_akteure),
    Szene(20, 'Offen bleibt: Bringt die Regenzeit genug Wasser? Werden die Tarife steigen, und wie werden Haushalte '
              'mit wenig Geld geschützt? Und wie schnell werden die Lecks gestopft?', '', szene_offen),
    Szene(21, 'Kurz gesagt: zu wenig Regen, zu viel Verlust und Projekte, auf die die Insel seit Jahren wartet.', '',
          szene_fazit),
    Szene(22, 'Mehr Hintergründe, alle Quellen und die neuesten Meldungen zur Wasserversorgung finden Sie auf '
              'gazet.morisyen.de. Und unsere täglichen Nachrichten aus Mauritius gibt es hier auf unserem Kanal. '
              'Bis bald!', '', szene_ende),
]


SZENEN += SZENEN_WEITER

# ----------------------------------------------------------------- Ton und Zusammenbau

def sprich(sprecher: es.Sprecher, szene: Szene, arbeit: Path) -> Path:
    """Spricht Satz für Satz, merkt sich die Zeiten für Untertitel und Animation, legt VOR/NACH Stille an."""
    import re

    rate = sprecher.rate
    teile = [x for x in re.split(r'(?<=[.!?])\s+', szene.text) if x.strip()]
    pcm = bytearray(b'\x00\x00' * int(rate * VOR))
    for i, satz in enumerate(teile):
        datei = arbeit / f's{szene.nr}-{i}.wav'
        sprecher.sprich(satz.replace('gazet.morisyen.de', 'gazet punkt morisyen punkt D E'), datei)
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
    if not a.nur or 0 in a.nur:
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
    if not a.nur or 22 in a.nur:  # Abspann-Folie der Sendung mit Erkennungsmelodie
        abspann = arbeit / 'abspann.mp4'
        es.abspann_video('de', es.dt.date(2026, 11, 28), abspann)
        teile.append(abspann)
    liste = arbeit / 'liste.txt'
    liste.write_text(''.join(f"file '{t}'\n" for t in teile))
    ziel = a.ausgabe / ('lernvideo-wasser.mp4' if not a.nur else 'lernvideo-wasser-teil.mp4')
    es.ffmpeg('-f', 'concat', '-safe', '0', '-i', str(liste), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
              '-pix_fmt', 'yuv420p', '-r', str(FPS), '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-ac', '2',
              '-movflags', '+faststart', str(ziel))
    print(ziel)


if __name__ == '__main__':
    main()
