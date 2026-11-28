"""
Lernvideo „Wem gehört das Chagos-Archipel?“ (Dossier Chagos): Szenen, Texte je Sprache,
Vorschaubild-Texte und YouTube-Metadaten. Gebaut mit dem Baukasten lernvideo.py.
"""

from __future__ import annotations

import datetime as dt
import math

import cairo
from PIL import Image, ImageDraw

import erzeuge_sendung as es
import lernvideo as lv
from lernvideo import (B, GRAU, H, HELL, L, NAVY, ROT, Szene, WASSER, WEISS, glatt, leinwand, phase, qr_bild,
                       regionalkarte, runde_box, text, ueberschrift, zahl_de, zu_pil)

STAMM = 'lernvideo-chagos'  # Dateinamen: lernvideo-chagos.mp4, lernvideo-chagos-en.mp4, …
STAND_DATUM = dt.date(2026, 11, 28)
DOSSIER_URL = 'https://gazet.morisyen.de/dossier/chagos'

STAND = {'de': 'Stand: 28. November 2026', 'en': 'As of 28 November 2026', 'fr': 'Situation au 28 novembre 2026'}

UI_EN: dict[str, str] = {
    'VERTRAG': 'TREATY', 'Mauritius · Vereinigtes Königreich': 'Mauritius · United Kingdom',
    'Unterzeichnet am 22. Mai 2025': 'Signed on 22 May 2025', 'Mauritius': 'Mauritius',
    'Vereinigtes Königreich': 'United Kingdom', 'NICHT IN KRAFT': 'NOT IN FORCE',
    'Wem gehört das': 'Who owns the', 'Chagos-Archipel?': 'Chagos Archipelago?',
    'Madagaskar': 'Madagascar', 'Malediven': 'Maldives', 'Seychellen': 'Seychelles', 'La Réunion': 'Réunion',
    'Chagos-Archipel': 'Chagos Archipelago', 'Diego Garcia': 'Diego Garcia', 'Rodrigues': 'Rodrigues',
    'ENTFERNUNG': 'DISTANCE', 'Militärbasis': 'Military base', 'Vereinigtes Königreich und USA':
    'United Kingdom and USA',
    'Sept. 1965': 'Sept 1965', 'Nov. 1965': 'Nov 1965', 'Dez. 1965': 'Dec 1965', 'März 1968': 'March 1968',
    'bis 1973': 'by 1973',
    'Lancaster House: Zustimmung zur Abtrennung': 'Lancaster House: separation agreed',
    'Britisches Territorium im Indischen Ozean': 'British Indian Ocean Territory',
    'UN-Resolution 2066': 'UN Resolution 2066', 'Abkommen UK–USA zu Diego Garcia': 'UK–US agreement on Diego Garcia',
    'Unabhängigkeit ohne Chagos': 'Independence without Chagos', 'Vertreibung der Chagossen': 'Chagossians removed',
    'Kolonie Mauritius': 'Colony of Mauritius', 'Britisches Territorium': 'British territory',
    'IGH 2019': 'ICJ 2019', 'Die Vertreter waren nicht befugt': 'The representatives had no authority',
}
UI_FR: dict[str, str] = {
    'VERTRAG': 'TRAITÉ', 'Mauritius · Vereinigtes Königreich': 'Maurice · Royaume-Uni',
    'Unterzeichnet am 22. Mai 2025': 'Signé le 22 mai 2025', 'Mauritius': 'Maurice',
    'Vereinigtes Königreich': 'Royaume-Uni', 'NICHT IN KRAFT': 'PAS EN VIGUEUR',
    'Wem gehört das': 'À qui appartient', 'Chagos-Archipel?': "l'archipel des Chagos ?",
    'Madagaskar': 'Madagascar', 'Malediven': 'Maldives', 'Seychellen': 'Seychelles', 'La Réunion': 'La Réunion',
    'Chagos-Archipel': 'Archipel des Chagos', 'Diego Garcia': 'Diego Garcia', 'Rodrigues': 'Rodrigues',
    'ENTFERNUNG': 'DISTANCE', 'Militärbasis': 'Base militaire', 'Vereinigtes Königreich und USA':
    'Royaume-Uni et États-Unis',
    'Sept. 1965': 'Sept. 1965', 'Nov. 1965': 'Nov. 1965', 'Dez. 1965': 'Déc. 1965', 'März 1968': 'Mars 1968',
    'bis 1973': "jusqu'en 1973",
    'Lancaster House: Zustimmung zur Abtrennung': 'Lancaster House : séparation acceptée',
    'Britisches Territorium im Indischen Ozean': "Territoire britannique de l'océan Indien",
    'UN-Resolution 2066': 'Résolution 2066 de l’ONU', 'Abkommen UK–USA zu Diego Garcia':
    'Accord Royaume-Uni–États-Unis sur Diego Garcia',
    'Unabhängigkeit ohne Chagos': 'Indépendance sans les Chagos', 'Vertreibung der Chagossen':
    'Expulsion des Chagossiens',
    'Kolonie Mauritius': 'Colonie de Maurice', 'Britisches Territorium': 'Territoire britannique',
    'IGH 2019': 'CIJ 2019', 'Die Vertreter waren nicht befugt': "Les représentants n'étaient pas habilités",
}
UI = {'en': UI_EN, 'fr': UI_FR}

PAPIER = (232 / 255, 238 / 255, 246 / 255)
TINTE = (13, 32, 62)
ROT_HELL = (255, 120, 128)


# ----------------------------------------------------------------- Szene 1: der Vertrag

def unterschrift(c: cairo.Context, x: float, y: float, breite: float, p: float) -> None:
    """Handschriftlicher Schwung, der sich mit p (0–1) von links nach rechts zeichnet."""
    if p <= 0:
        return
    n = 80
    c.set_source_rgb(*NAVY)
    c.set_line_width(4)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(int(n * p) + 1):
        u = i / n
        px = x + breite * u
        py = y - 22 * math.sin(u * 9.5) * (1 - 0.6 * u) - 10 * math.sin(u * 23)
        (c.move_to if i == 0 else c.line_to)(px, py)
    c.stroke()


def stempel(bild: Image.Image, mitte: tuple[float, float], inhalt: str, p: float) -> None:
    if p <= 0:
        return
    f = es.titel_schrift(78)
    z = ImageDraw.Draw(bild)
    b = int(z.textlength(inhalt, font=f)) + 90
    ebene = Image.new('RGBA', (b, 170), (0, 0, 0, 0))
    ze = ImageDraw.Draw(ebene)
    farbe = (210, 46, 58, round(235 * min(1.0, p * 1.5)))
    ze.rounded_rectangle([6, 6, b - 6, 164], radius=18, outline=farbe, width=9)
    ze.text((b / 2, 88), inhalt, font=f, fill=farbe, anchor='mm')
    groesse = 1.5 - 0.5 * glatt(p)
    ebene = ebene.resize((round(b * groesse), round(170 * groesse)))
    ebene = ebene.rotate(11, expand=True, resample=Image.BICUBIC)
    bild.paste(ebene, (round(mitte[0] - ebene.width / 2), round(mitte[1] - ebene.height / 2)), ebene)


def szene_vertrag(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    a = phase(t, 0, 0.6)
    x0, y0, b, h = 560, 170 + 30 * (1 - a), 800, 760
    c.set_source_rgba(0, 0, 0, 0.25 * a)
    runde_box(c, x0 + 14, y0 + 18, b, h, 18)
    c.fill()
    c.set_source_rgba(*PAPIER, a)
    runde_box(c, x0, y0, b, h, 18)
    c.fill()
    for i in range(7):  # Textzeilen des Vertrags
        lang = b - 160 - (90 if i % 3 == 2 else 0)
        c.set_source_rgba(*GRAU, 0.45 * a)
        runde_box(c, x0 + 80, y0 + 250 + i * 40, lang, 12, 6)
        c.fill()
    bis = s.satz_start(1) - 0.3
    unterschrift(c, x0 + 80, y0 + 610, 260, phase(t, 0.8, min(1.2, (bis - 0.8) / 2)))
    unterschrift(c, x0 + 460, y0 + 610, 260, phase(t, 0.8 + min(1.2, (bis - 0.8) / 2), min(1.2, (bis - 0.8) / 2)))
    c.set_source_rgba(*NAVY, 0.7 * a)
    c.set_line_width(2)
    for x in (x0 + 80, x0 + 460):
        c.move_to(x, y0 + 640)
        c.line_to(x + 260, y0 + 640)
    c.stroke()
    bild = zu_pil(fl)
    text(bild, (x0 + b / 2, y0 + 70), L('VERTRAG'), es.titel_schrift(64), TINTE, 'ma', a)
    text(bild, (x0 + b / 2, y0 + 155), L('Mauritius · Vereinigtes Königreich'), es.text_schrift(36), TINTE, 'ma', a)
    text(bild, (x0 + 80, y0 + 660), L('Mauritius'), es.mono(24, True), TINTE, 'la', a)
    text(bild, (x0 + 460, y0 + 660), L('Vereinigtes Königreich'), es.mono(24, True), TINTE, 'la', a)
    text(bild, (x0 + b / 2, y0 + h + 40), L('Unterzeichnet am 22. Mai 2025'), es.mono(28, True), es.HELLBLAU, 'ma',
         phase(t, 1.0, 0.5))
    stempel(bild, (x0 + b / 2 + 40, y0 + 330), L('NICHT IN KRAFT'), phase(t, s.satz_start(1) + 0.2, 0.45))
    return bild


# ----------------------------------------------------------------- Szene 2: Titel

def atoll(c: cairo.Context, x: float, y: float, r: float, a: float) -> None:
    """Stilisiertes Atoll wie Diego Garcia: Ring aus Land, im Norden offen, Lagune innen."""
    c.set_source_rgba(*WASSER, 0.28 * a)
    c.arc(x, y, r, 0, 2 * math.pi)
    c.fill()
    c.set_source_rgba(*HELL, a)
    c.set_line_width(r * 0.24)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.arc(x, y, r, -math.pi / 2 + 0.55, 3 * math.pi / 2 - 0.25)
    c.stroke()


def wellen(c: cairo.Context, t: float, y: float, a: float) -> None:
    c.set_line_width(3)
    for k in range(3):
        c.set_source_rgba(*WASSER, (0.5 - k * 0.13) * a)
        for i in range(0, B + 20, 20):
            yy = y + k * 34 + 9 * math.sin(i / 70 + t * 1.6 + k)
            (c.move_to if i == 0 else c.line_to)(i, yy)
        c.stroke()


def szene_titel(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    auf = phase(t, 0.1, 1.0)
    atoll(c, B / 2, 300 + 50 * (1 - auf), 105, auf)
    wellen(c, t, 395, phase(t, 0, 0.6))
    bild = zu_pil(fl)
    a = phase(t, 0.7, 0.7)
    text(bild, (B / 2, 500), L('Wem gehört das'), es.titel_schrift(104), anker='ma', deckkraft=a)
    text(bild, (B / 2, 620), L('Chagos-Archipel?'), es.titel_schrift(104), anker='ma', deckkraft=a)
    text(bild, (B / 2, 790), STAND[lv.SPRACHE].upper(), es.mono(30, True), es.HELLBLAU, 'ma',
         phase(t, s.satz_start(1) if len(s.saetze) > 1 else 1.6, 0.6))
    return bild


# ----------------------------------------------------------------- Karte (Szenen 3 ff.)

AUSSCHNITT = (42, -25, 80, 7)  # wie die Dossier-Karte
KARTE_X, KARTE_Y, KARTE_H = 80, 150, 860
# Name, lat, lon, Versatz der Beschriftung (dx, dy), Anker
ORTE = {
    'Mauritius': (-20.2, 57.55, (6, 22), 'la'),
    'Diego Garcia': (-7.31, 72.41, (24, 14), 'lm'),
    'Chagos-Archipel': (-5.6, 72.0, (0, -30), 'md'),
    'Malediven': (4.18, 73.51, (-22, 0), 'rm'),
    'Seychellen': (-4.68, 55.48, (22, 0), 'lm'),
    'Rodrigues': (-19.72, 63.42, (22, 0), 'lm'),
    'La Réunion': (-21.11, 55.53, (-18, 26), 'rm'),
    'Madagaskar': (-18.9, 47.5, (0, -12), 'md'),
}
CHAGOS_RAHMEN = (70.2, -8.4, 73.6, -4.4)  # W, S, O, N um die Atolle


def karte_grund(c: cairo.Context, a: float = 1.0):
    return regionalkarte(c, AUSSCHNITT, KARTE_X, KARTE_Y, KARTE_H, a)


def ort_punkt(c: cairo.Context, punkt, name: str, a: float, farbe=WEISS, puls_t: float | None = None) -> None:
    if a <= 0:
        return
    lat, lon, _, _ = ORTE[name]
    x, y = punkt(lon, lat)
    if puls_t is not None:
        w = (puls_t % 1.6) / 1.6
        c.set_source_rgba(*farbe, 0.4 * (1 - w) * a)
        c.arc(x, y, 12 + 30 * w, 0, 2 * math.pi)
        c.fill()
    c.set_source_rgba(*farbe, a)
    c.arc(x, y, 8, 0, 2 * math.pi)
    c.fill()


def ort_name(bild: Image.Image, punkt, name: str, a: float, farbe=es.WEISS, groesse: int = 32) -> None:
    lat, lon, (dx, dy), anker = ORTE[name]
    x, y = punkt(lon, lat)
    text(bild, (x + dx, y + dy), L(name), es.titel_schrift(groesse), farbe, anker, a)


def gestrichelt(c: cairo.Context, p0, p1, p: float, farbe, a: float, breite: float = 4) -> None:
    if p <= 0:
        return
    c.set_source_rgba(*farbe, a)
    c.set_line_width(breite)
    c.set_dash([14, 10])
    c.move_to(*p0)
    c.line_to(p0[0] + (p1[0] - p0[0]) * p, p0[1] + (p1[1] - p0[1]) * p)
    c.stroke()
    c.set_dash([])


def chagos_rahmen(c: cairo.Context, punkt, p: float, farbe=WEISS) -> tuple[float, float, float, float]:
    w, s, o, n = CHAGOS_RAHMEN
    x0, y0 = punkt(w, n)
    x1, y1 = punkt(o, s)
    if p > 0:
        c.set_source_rgba(*farbe, 0.08 * p)
        runde_box(c, x0, y0, x1 - x0, y1 - y0, 16)
        c.fill()
        c.set_source_rgba(*farbe, 0.9 * p)
        c.set_line_width(3)
        c.set_dash([12, 9], 0)
        runde_box(c, x0, y0, x1 - x0, y1 - y0, 16)
        c.stroke()
        c.set_dash([])
    return x0, y0, x1, y1


def pista(c: cairo.Context, x: float, y: float, a: float) -> None:
    """Start- und Landebahn als Zeichen für die Militärbasis."""
    c.set_source_rgba(*HELL, 0.9 * a)
    runde_box(c, x, y, 360, 54, 8)
    c.fill()
    c.set_source_rgba(*NAVY, a)
    for i in range(7):
        c.rectangle(x + 24 + i * 48, y + 23, 26, 8)
    c.fill()


RECHTS = 1180  # linker Rand der Textspalte neben der Karte


def szene_karte(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    a = phase(t, 0, 0.6)
    punkt = karte_grund(c, a)
    namen = ['Madagaskar', 'La Réunion', 'Mauritius', 'Rodrigues', 'Seychellen', 'Malediven', 'Chagos-Archipel']
    for i, name in enumerate(namen):
        ort_punkt(c, punkt, name, phase(t, 0.4 + i * 0.25, 0.3), WASSER if name == 'Mauritius' else WEISS)
    t2 = s.satz_start(1)
    linie = phase(t, 2.3, 1.2)
    mx, my = punkt(57.55, -20.2)
    dx, dy = punkt(72.41, -7.31)
    gestrichelt(c, (mx, my), (dx, dy), linie, HELL, 0.9)
    hervor = phase(t, t2, 0.5)
    ort_punkt(c, punkt, 'Diego Garcia', max(linie if linie >= 1 else 0, hervor), ROT if hervor > 0 else WEISS,
              t - t2 if hervor > 0 else None)
    pista(c, RECHTS, 650, phase(t, t2 + 0.5, 0.5))
    bild = zu_pil(fl)
    for i, name in enumerate(namen):
        ort_name(bild, punkt, name, phase(t, 0.5 + i * 0.25, 0.3), groesse=30)
    ort_name(bild, punkt, 'Diego Garcia', max(phase(t, 3.3, 0.4), hervor), ROT_HELL if hervor > 0 else es.WEISS, 30)
    km = phase(t, 2.6, 0.8)
    text(bild, (RECHTS, 260), L('ENTFERNUNG'), es.mono(28, True), es.HELLBLAU, 'la', km)
    text(bild, (RECHTS, 300), f'≈ {zahl_de(2150 * glatt(km), 0)} km', es.titel_schrift(110), anker='la',
         deckkraft=km)
    text(bild, (RECHTS, 440), 'Mauritius → Diego Garcia' if lv.SPRACHE != 'fr' else 'Maurice → Diego Garcia',
         es.text_schrift(36), es.HELLBLAU, 'la', km)
    text(bild, (RECHTS, 560), L('Militärbasis'), es.titel_schrift(56), ROT_HELL, 'la', phase(t, t2 + 0.3, 0.5))
    text(bild, (RECHTS, 740), L('Vereinigtes Königreich und USA'), es.text_schrift(38), es.WEISS, 'la',
         phase(t, t2 + 0.8, 0.5))
    return bild


# ----------------------------------------------------------------- Zeitstrahl 1965–1973 (Szenen 4–8)

ZEITSTRAHL = [
    ('Sept. 1965', 'Lancaster House: Zustimmung zur Abtrennung'),
    ('Nov. 1965', 'Britisches Territorium im Indischen Ozean'),
    ('Dez. 1965', 'UN-Resolution 2066'),
    ('1966', 'Abkommen UK–USA zu Diego Garcia'),
    ('März 1968', 'Unabhängigkeit ohne Chagos'),
    ('bis 1973', 'Vertreibung der Chagossen'),
]
ZS_Y0, ZS_ABSTAND = 190, 134


def zeitstrahl(c: cairo.Context | None, bild: Image.Image | None, t: float, starts: dict[int, float]) -> None:
    """Rechte Spalte: senkrechter Zeitstrahl. starts: Eintrag → Zeitpunkt, ab dem er erscheint (frühere stehen)."""
    letzter = max(starts)
    for i in range(letzter + 1):
        p = phase(t, starts.get(i, -1), 0.5)
        if p <= 0:
            continue
        neu = i in starts and starts[i] >= 0
        y = ZS_Y0 + i * ZS_ABSTAND
        if c is not None:
            c.set_source_rgba(*HELL, 0.35 * p)
            c.set_line_width(3)
            if i < letzter:
                c.move_to(RECHTS + 12, y + 14)
                c.line_to(RECHTS + 12, y + ZS_ABSTAND + 14)
                c.stroke()
            c.set_source_rgba(*(WASSER if neu else HELL), p)
            c.arc(RECHTS + 12, y + 14, 11 if neu else 8, 0, 2 * math.pi)
            c.fill()
        if bild is not None:
            datum, inhalt = ZEITSTRAHL[i]
            text(bild, (RECHTS + 44, y), L(datum).upper(), es.mono(26, True), es.HELLBLAU, 'la', p)
            z = ImageDraw.Draw(bild)
            for k, zl in enumerate(es.umbrechen(z, L(inhalt), es.text_schrift(34), 640)[:2]):
                text(bild, (RECHTS + 44, y + 36 + k * 42), zl, es.text_schrift(34),
                     es.WEISS if neu else (170, 186, 210), 'la', p)


def karte_kolonie(c: cairo.Context, bild_namen: list, punkt, t: float, trennung: float, territorium: float) -> None:
    """Mauritius und Chagos als eine Kolonie (Linie), die bei der Trennung reißt; danach Rahmen um Chagos."""
    mx, my = punkt(57.55, -20.2)
    cx, cy = punkt(72.0, -6.3)
    if trennung < 1:
        gestrichelt(c, (mx, my), (cx, cy), 1, WASSER, 0.85 * (1 - trennung))
    else:
        pass
    if trennung > 0:  # Lücke in der Mitte, rote Markierung
        qx, qy = (mx + cx) / 2, (my + cy) / 2
        c.set_source_rgba(*ROT, trennung)
        c.set_line_width(6)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        for sx in (-1, 1):
            c.move_to(qx - 22, qy - 22 * sx)
            c.line_to(qx + 22, qy + 22 * sx)
        c.stroke()
    for name in ('Madagaskar', 'Seychellen', 'Malediven'):
        ort_punkt(c, punkt, name, 1)
    ort_punkt(c, punkt, 'Mauritius', 1, WASSER)
    ort_punkt(c, punkt, 'Chagos-Archipel', 1, WASSER if trennung < 0.5 else HELL)
    ort_punkt(c, punkt, 'Diego Garcia', 1, WASSER if trennung < 0.5 else HELL)
    chagos_rahmen(c, punkt, territorium)


def szene_1965(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    punkt = karte_grund(c, 1)
    t2 = s.satz_start(1)
    trennung = phase(t, t2 - 1.3, 0.8)  # am Ende des ersten Satzes („abzutrennen“)
    territorium = phase(t, t2 + 0.3, 0.7)
    karte_kolonie(c, [], punkt, t, trennung, territorium)
    starts = {0: 0.3, 1: t2}
    zeitstrahl(c, None, t, starts)
    bild = zu_pil(fl)
    for name in ('Mauritius', 'Chagos-Archipel', 'Madagaskar', 'Seychellen', 'Malediven'):
        ort_name(bild, punkt, name, 1, groesse=30)
    mx, my = punkt(57.55, -20.2)
    cx, cy = punkt(72.0, -6.3)
    text(bild, ((mx + cx) / 2 - 30, (my + cy) / 2 + 20), L('Kolonie Mauritius'), es.mono(24, True), (150, 230, 205),
         'ra', phase(t, 0.4, 0.5) * (1 - trennung))
    x0, y0, x1, y1 = chagos_rahmen(c, punkt, 0)
    text(bild, ((x0 + x1) / 2, y1 + 16), L('Britisches Territorium'), es.mono(24, True), es.WEISS, 'ma', territorium)
    zeitstrahl(None, bild, t, starts)
    return bild


def waage(c: cairo.Context, x: float, y: float, a: float, neigung: float = 0.0) -> None:
    c.set_source_rgba(*WEISS, a)
    c.set_line_width(5)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(x, y - 50)
    c.line_to(x, y + 40)
    c.move_to(x - 30, y + 40)
    c.line_to(x + 30, y + 40)
    dy = 14 * neigung
    c.move_to(x - 55, y - 40 + dy)
    c.line_to(x + 55, y - 40 - dy)
    c.stroke()
    for sx, d in ((-55, dy), (55, -dy)):
        c.move_to(x + sx - 20, y - 40 + d + 30)
        c.line_to(x + sx, y - 40 + d)
        c.line_to(x + sx + 20, y - 40 + d + 30)
        c.stroke()
        c.arc(x + sx, y - 40 + d + 30, 20, 0, math.pi)
        c.stroke()


def szene_befugnis(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    punkt = karte_grund(c, 1)
    karte_kolonie(c, [], punkt, t, 1, 1)
    starts = {0: -1, 1: -1}
    zeitstrahl(c, None, t, starts)
    # Vermerk zum ersten Eintrag: Kasten mit Waage, Verbindung zum Punkt „Sept. 1965“
    p = phase(t, 0.4, 0.6)
    bx, by = RECHTS, 520
    if p > 0:
        c.set_source_rgba(*ROT, 0.8 * p)
        c.set_line_width(3)
        c.move_to(RECHTS + 12, ZS_Y0 + 14)
        c.curve_to(RECHTS - 40, ZS_Y0 + 120, RECHTS - 40, by + 40, bx, by + 60)
        c.stroke()
        c.set_source_rgba(*ROT, 0.16 * p)
        runde_box(c, bx, by, 660, 230, 18)
        c.fill()
        c.set_source_rgba(*ROT, p)
        runde_box(c, bx, by, 660, 230, 18)
        c.stroke()
        waage(c, bx + 100, by + 125, p, 0.6 * glatt(phase(t, 1.0, 0.8)))
    bild = zu_pil(fl)
    for name in ('Mauritius', 'Chagos-Archipel', 'Madagaskar', 'Seychellen', 'Malediven'):
        ort_name(bild, punkt, name, 1, groesse=30)
    x0, y0, x1, y1 = chagos_rahmen(c, punkt, 0)
    text(bild, ((x0 + x1) / 2, y1 + 16), L('Britisches Territorium'), es.mono(24, True), es.WEISS, 'ma', 1)
    zeitstrahl(None, bild, t, starts)
    text(bild, (bx + 200, by + 50), L('IGH 2019'), es.mono(28, True), ROT_HELL, 'la', p)
    z = ImageDraw.Draw(bild)
    for k, zl in enumerate(es.umbrechen(z, L('Die Vertreter waren nicht befugt'), es.titel_schrift(44), 430)):
        text(bild, (bx + 200, by + 95 + k * 54), zl, es.titel_schrift(44), es.WEISS, 'la', phase(t, 0.7, 0.5))
    return bild


# ----------------------------------------------------------------- Szenen und Texte

SZENEN = [
    Szene(1, 'Im Mai 2025 unterzeichneten Mauritius und Großbritannien einen Vertrag: Das Chagos-Archipel soll an '
             'Mauritius gehen. Doch bis heute ist dieser Vertrag nicht in Kraft.', 'House of Lords Library',
          szene_vertrag),
    Szene(2, 'Wem gehört das Chagos-Archipel, und warum ist das so umstritten? Stand: Ende November 2026.', '',
          szene_titel),
    Szene(3, 'Das Archipel liegt mitten im Indischen Ozean, rund 2.150 Kilometer nordöstlich von Mauritius. Seine '
             'bekannteste Insel ist Diego Garcia: Dort steht eine Militärbasis, die Großbritannien und die USA '
             'gemeinsam nutzen.', 'Natural Earth, Dossier', szene_karte),
    Szene(4, 'Im September 1965, noch vor der Unabhängigkeit, stimmten Vertreter der Kolonie Mauritius in London zu, '
             'das Archipel abzutrennen. Im November gründete Großbritannien daraus das Britische Territorium im '
             'Indischen Ozean.', 'IGH, House of Lords', szene_1965),
    Szene(5, 'Der Internationale Gerichtshof stellte 2019 fest: Die Vertreter waren dazu nach der damaligen '
             'Verfassung nicht befugt.', 'IGH-Gutachten 2019', szene_befugnis),
]

TEXT_EN: dict[int, str] = {}
TEXT_FR: dict[int, str] = {}
TEXTE = {'en': TEXT_EN, 'fr': TEXT_FR}

QUELLEN = [
    ('International Court of Justice – Advisory Opinion 2019 (worldcourts.com)',
     'https://www.worldcourts.com/icj/eng/decisions/2019.02.25_Mauritius.htm'),
    ('House of Lords Library – UK–Mauritius treaty',
     'https://lordslibrary.parliament.uk/uk-mauritius-treaty-on-the-chagos-archipelago/'),
]
