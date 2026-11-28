"""
YouTube-Vorschaubild (1280×720) für das Lernvideo „Gazet Morisyen erklärt: Wasser“.

    python3 lernvideo_vorschau.py --sprache de --ziel vorschau.png [--variante foto|grafik]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

import erzeuge_sendung as es

W, H = 1280, 720
FOTO = Path(__file__).resolve().parent.parent / 'public' / 'bilder' / 'wasserversorgung.jpg'

TEXTE = {
    'de': {'reihe': 'GAZET MORISYEN ERKLÄRT', 'titel': ['Warum auf Mauritius', 'das Wasser', 'knapp wird'],
           'zahl': '44 %', 'zahl_text': 'Füllstand der Reservoirs', 'stand': 'STAND: NOV. 2026',
           'foto': 'Foto: Diego Delso, CC BY-SA 4.0'},
    'en': {'reihe': 'GAZET MORISYEN EXPLAINS', 'titel': ['Why Mauritius is', 'running short', 'of water'],
           'zahl': '44%', 'zahl_text': 'reservoir level', 'stand': 'AS OF NOV 2026',
           'foto': 'Photo: Diego Delso, CC BY-SA 4.0'},
    'fr': {'reihe': 'GAZET MORISYEN EXPLIQUE', 'titel': ["Pourquoi l'eau", 'manque', 'à Maurice'],
           'zahl': '44 %', 'zahl_text': 'remplissage des réservoirs', 'stand': 'SITUATION : NOV. 2026',
           'foto': 'Photo : Diego Delso, CC BY-SA 4.0'},
}


def vorschau(sprache: str, ziel: Path) -> None:
    t = TEXTE[sprache]
    bild = es.verlauf(es.NAVY, es.NAVY_TIEF).resize((W, H))
    # rechts: Foto des Stausees mit trockenem Ufer, nach links weich in Navy
    foto = Image.open(FOTO).convert('RGB')
    fh = H
    fw = round(foto.width * fh / foto.height)
    foto = foto.resize((fw, fh), Image.LANCZOS)
    breite = 720
    x0 = (fw - breite) // 2 + 80
    ausschnitt = foto.crop((x0, 0, x0 + breite, fh))
    ausschnitt = Image.blend(Image.new('RGB', ausschnitt.size, es.NAVY_TIEF), ausschnitt, 0.82)  # etwas abdunkeln
    maske = Image.new('L', (breite, fh), 255)
    mz = ImageDraw.Draw(maske)
    for x in range(420):
        mz.line([x, 0, x, fh], fill=round(255 * (x / 420) ** 1.8))
    bild.paste(ausschnitt, (W - breite, 0), maske)
    z = ImageDraw.Draw(bild)
    links = 60
    logo = es.logo_weiss(70)
    bild.paste(logo, (links, 48), logo)
    es.gesperrt(z, (links + 88, 70), t['reihe'], es.mono(26, True), es.HELLBLAU, 0.12)
    # Titel groß
    f = es.titel_schrift(86)
    y = 170
    z.rectangle([links, y + 10, links + 12, y + 3 * 100 - 16], fill=es.ROT_TV)
    for i, zeile in enumerate(t['titel']):
        z.text((links + 34, y + i * 100), zeile, font=f, fill=es.WEISS, stroke_width=2, stroke_fill=es.NAVY_TIEF)
    # Kennzahl als rotes Schild
    y2 = y + 3 * 100 + 30
    fz = es.titel_schrift(64)
    zb = z.textlength(t['zahl'], font=fz)
    z.rounded_rectangle([links + 34, y2, links + 34 + zb + 44, y2 + 86], radius=14, fill=es.ROT_TV)
    z.text((links + 56, y2 + 6), t['zahl'], font=fz, fill=es.WEISS)
    z.text((links + 34 + zb + 66, y2 + 26), t['zahl_text'], font=es.titel_schrift(34), fill=es.WEISS, stroke_width=3,
           stroke_fill=es.NAVY_TIEF)
    es.gesperrt(z, (links + 36, y2 + 116), t['stand'], es.mono(24, True), es.HELLBLAU, 0.12)
    z.text((W - 16, H - 30), t['foto'], font=es.mono(15), fill=es.WEISS, anchor='rs', stroke_width=2,
           stroke_fill=(0, 0, 0))
    for i, farbe in enumerate(es.FLAGGE):
        z.rectangle([round(i * W / 4), H - 12, round((i + 1) * W / 4), H], fill=farbe)
    bild.save(ziel)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sprache', choices=list(TEXTE), default='de')
    p.add_argument('--ziel', type=Path, required=True)
    a = p.parse_args()
    vorschau(a.sprache, a.ziel)
    print(a.ziel)
