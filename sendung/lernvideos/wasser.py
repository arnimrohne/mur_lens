"""
Lernvideo „Warum auf Mauritius das Wasser knapp wird“ (Dossier Wasserversorgung): Szenen, Texte je Sprache,
Vorschaubild-Texte und YouTube-Metadaten. Gebaut mit dem Baukasten lernvideo.py.
"""

from __future__ import annotations

import datetime as dt
import math
from pathlib import Path

import cairo
from PIL import Image, ImageDraw

import erzeuge_sendung as es
import lernvideo as lv
from lernvideo import (B, GRAU, H, HELL, L, NAVY, ROT, Szene, WASSER, WASSER_TIEF, WEISS, balken, balken_texte, behaelter, damm, glatt, insel_pfad, karten, kasse, leinwand, phase, prozent, qr_bild, runde_box, sonne, symbol, text, tropfen, ueberschrift, wolke, zahl_de, zu_pil)

STAMM = 'lernvideo-wasser'  # Dateinamen: lernvideo-wasser.mp4, lernvideo-wasser-en.mp4, …
STAND_DATUM = dt.date(2026, 11, 28)


STAND = {'de': 'Stand: 28. November 2026', 'en': 'As of 28 November 2026', 'fr': 'Situation au 28 novembre 2026'}


UI_EN = {
    'GAZET MORISYEN ERKLÄRT': 'GAZET MORISYEN EXPLAINS', 'Quelle': 'Source',
    '3–8 UHR': '3–8 AM', 'JEDEN ZWEITEN TAG': 'EVERY OTHER DAY',
    'Warum auf Mauritius': 'Why Mauritius is', 'das Wasser knapp wird': 'running short of water',
    'Haushalte': 'Households', 'Landwirtschaft': 'Farming', 'Industrie': 'Industry', 'Tourismus': 'Tourism',
    '7 große Reservoirs': '7 major reservoirs', 'Mio. m³': 'million m³',
    'SPEICHERVERMÖGEN ZUSAMMEN': 'COMBINED CAPACITY', '7 von 7 künstlich angelegt': 'All 7 are man-made',
    'ANTEIL AM GESAMTEN SPEICHER': 'SHARE OF TOTAL CAPACITY', 'Pegel': 'Level',
    'Füllstand der sieben Reservoirs': 'Level of the seven reservoirs', 'Vor einem Jahr': 'A year ago',
    'Saisonaler Schnitt': 'Seasonal average', '26.11.2026': '26 Nov 2026', 'Nov. 2025': 'Nov 2025',
    'Nov. 2026': 'Nov 2026', 'Nov. 2029': 'Nov 2029', 'offen': 'open', 'geschlossen': 'closed',
    'Wasser der CWA im Jahr 2024, in Mio. m³': 'CWA water in 2024, million m³', 'Aufbereitet': 'Treated',
    'Verkauft': 'Sold', 'Rund 60 % des Wassers bringen kein Geld ein': 'About 60% of the water earns no revenue',
    'Lecks': 'Leaks', 'Illegale Anschlüsse': 'Illegal connections', 'Abrechnungsfehler': 'Billing errors',
    'Rechnungshof, Dezember 2025': 'National Audit Office, December 2025', '10 JAHRE': '10 YEARS',
    'Anteil ohne Einnahmen': 'Share without revenue', 'STUDIE': 'STUDY',
    'VERLUST DER CWA LAUT MEDIENBERICHT': 'CWA LOSSES, ACCORDING TO MEDIA REPORTS', 'pro': 'per',
    'Monat': 'month', 'Staatshaushalt': 'State budget', 'Wasserpreise': 'Water tariffs', 'Tarif': 'Tariff',
    'SEITDEM UNVERÄNDERT': 'NO CHANGE SINCE 2012', 'GRATIS': 'FREE', 'bis 6 m³ im Monat': 'up to 6 m³ a month',
    'Ein neuer Anschluss': 'A new connection', 'BERECHNET': 'CHARGED', 'TATSÄCHLICHE KOSTEN': 'ACTUAL COST',
    'Schätzung 2009': '2009 estimate', 'Schätzung 2024': '2024 estimate',
    'Geschätzte Kosten, Mrd. Rupien': 'Estimated cost, billion rupees',
    'Damm von Rivière-des-Anguilles': 'Rivière-des-Anguilles dam', 'Ankündigung': 'Announced',
    'Baubeginn?': 'Construction starts?', 'Fertigstellung geplant': 'Completion planned',
    'KEIN UNTERZEICHNETER BAUVERTRAG BEKANNT': 'NO SIGNED CONSTRUCTION CONTRACT KNOWN',
    'Ministerium': 'Ministry', 'setzt auf neue Speicher': 'relies on new storage',
    'Rechnungshof': 'Audit Office', 'kritisiert die Verluste': 'criticises the losses', 'Fachleute': 'Experts',
    'Tarife zu niedrig, aber erst besserer Service': 'tariffs too low, but better service first',
    'tragen die Rationierung': 'bear the rationing', 'Wer will was?': 'Who wants what?',
    'Regenzeit': 'Rainy season', 'Füllt sie die Reservoirs wieder?': 'Will it refill the reservoirs?',
    'Tarife': 'Tariffs', 'Steigen sie, und wer wird geschützt?': 'Will they rise, and who is protected?',
    'Wie schnell wird das Netz dicht?': 'How fast will the network be fixed?', 'Offene Fragen': 'Open questions',
    'Kurz gesagt': 'In short', 'Zu wenig Regen': 'Too little rain', 'Zu viel Verlust': 'Too much loss',
    'Projekte, die warten': 'Projects still waiting',
    'DOSSIER: WASSERVERSORGUNG · STAND 28.11.2026': 'EXPLAINER: WATER SUPPLY · AS OF 28 NOV 2026',
    'Alle Quellen, Hintergründe und neue Meldungen': 'All sources, background and the latest news',
    'ZUM DOSSIER': 'READ THE EXPLAINER',
    'Foto: Diego Delso, CC BY-SA 4.0, Wikimedia Commons': 'Photo: Diego Delso, CC BY-SA 4.0, Wikimedia Commons',
    'CWA über allAfrica': 'CWA via allAfrica',
    'Ministerium für Energie und öffentliche Versorgung': 'Ministry of Energy and Public Utilities',
    'Ministerium; Statistics Mauritius (ODE)': 'Ministry; Statistics Mauritius (ODE)',
    'Water Resources Commission über ION News': 'Water Resources Commission via ION News',
    'CWA-Jahresbericht 2024–25': 'CWA Annual Report 2024–25', "NAO, L'Express, Ministerium": "NAO, L'Express, Ministry",
}


UI_FR = {
    'GAZET MORISYEN ERKLÄRT': 'GAZET MORISYEN EXPLIQUE', 'Quelle': 'Source',
    '3–8 UHR': '3 H – 8 H', 'JEDEN ZWEITEN TAG': 'UN JOUR SUR DEUX',
    'Warum auf Mauritius': "Pourquoi l'eau", 'das Wasser knapp wird': 'manque à Maurice',
    'Haushalte': 'Ménages', 'Landwirtschaft': 'Agriculture', 'Industrie': 'Industrie', 'Tourismus': 'Tourisme',
    '7 große Reservoirs': '7 grands réservoirs', 'Mio. m³': 'millions de m³',
    'SPEICHERVERMÖGEN ZUSAMMEN': 'CAPACITÉ TOTALE', '7 von 7 künstlich angelegt': 'Les 7 sont artificiels',
    'ANTEIL AM GESAMTEN SPEICHER': 'PART DE LA CAPACITÉ TOTALE', 'Pegel': 'Niveau',
    'Füllstand der sieben Reservoirs': 'Remplissage des sept réservoirs', 'Vor einem Jahr': 'Il y a un an',
    'Saisonaler Schnitt': 'Moyenne saisonnière', '26.11.2026': '26/11/2026', 'Nov. 2025': 'nov. 2025',
    'Nov. 2026': 'nov. 2026', 'Nov. 2029': 'nov. 2029', 'offen': 'ouvert', 'geschlossen': 'fermé',
    'Wasser der CWA im Jahr 2024, in Mio. m³': 'Eau de la CWA en 2024, millions de m³', 'Aufbereitet': 'Traitée',
    'Verkauft': 'Vendue', 'Rund 60 % des Wassers bringen kein Geld ein': "Environ 60 % de l'eau ne rapporte rien",
    'Lecks': 'Fuites', 'Illegale Anschlüsse': 'Branchements illégaux', 'Abrechnungsfehler': 'Erreurs de facturation',
    'Rechnungshof, Dezember 2025': "Bureau de l'audit, décembre 2025", '10 JAHRE': '10 ANS',
    'Anteil ohne Einnahmen': 'Part non facturée', 'STUDIE': 'ÉTUDE',
    'VERLUST DER CWA LAUT MEDIENBERICHT': 'PERTES DE LA CWA SELON LA PRESSE', 'pro': 'par', 'Monat': 'mois',
    'Staatshaushalt': "Budget de l'État", 'Wasserpreise': "Tarifs de l'eau", 'Tarif': 'Tarif',
    'SEITDEM UNVERÄNDERT': 'INCHANGÉ DEPUIS 2012', 'GRATIS': 'GRATUIT', 'bis 6 m³ im Monat': "jusqu'à 6 m³ par mois",
    'Ein neuer Anschluss': 'Un nouveau branchement', 'BERECHNET': 'FACTURÉ', 'TATSÄCHLICHE KOSTEN': 'COÛT RÉEL',
    'Schätzung 2009': 'Estimation 2009', 'Schätzung 2024': 'Estimation 2024',
    'Geschätzte Kosten, Mrd. Rupien': 'Coût estimé, milliards de roupies',
    'Damm von Rivière-des-Anguilles': 'Barrage de Rivière-des-Anguilles', 'Ankündigung': 'Annonce',
    'Baubeginn?': 'Début des travaux ?', 'Fertigstellung geplant': 'Achèvement prévu',
    'KEIN UNTERZEICHNETER BAUVERTRAG BEKANNT': 'AUCUN CONTRAT DE CONSTRUCTION SIGNÉ CONNU',
    'Ministerium': 'Ministère', 'setzt auf neue Speicher': 'mise sur de nouveaux réservoirs',
    'Rechnungshof': "Bureau de l'audit", 'kritisiert die Verluste': 'critique les pertes', 'Fachleute': 'Spécialistes',
    'Tarife zu niedrig, aber erst besserer Service': "tarifs trop bas, mais d'abord un meilleur service",
    'tragen die Rationierung': 'subissent le rationnement', 'Wer will was?': 'Qui veut quoi ?',
    'Regenzeit': 'Saison des pluies', 'Füllt sie die Reservoirs wieder?': 'Remplira-t-elle les réservoirs ?',
    'Tarife': 'Tarifs', 'Steigen sie, und wer wird geschützt?': 'Vont-ils augmenter, et qui sera protégé ?',
    'Wie schnell wird das Netz dicht?': 'Quand le réseau sera-t-il réparé ?', 'Offene Fragen': 'Questions ouvertes',
    'Kurz gesagt': 'En bref', 'Zu wenig Regen': 'Trop peu de pluie', 'Zu viel Verlust': 'Trop de pertes',
    'Projekte, die warten': 'Des projets en attente',
    'DOSSIER: WASSERVERSORGUNG · STAND 28.11.2026': 'DOSSIER : EAU · SITUATION AU 28/11/2026',
    'Alle Quellen, Hintergründe und neue Meldungen': 'Sources, contexte et dernières nouvelles',
    'ZUM DOSSIER': 'LIRE LE DOSSIER',
    'Foto: Diego Delso, CC BY-SA 4.0, Wikimedia Commons': 'Photo : Diego Delso, CC BY-SA 4.0, Wikimedia Commons',
    'CWA über allAfrica': 'CWA via allAfrica',
    'Ministerium für Energie und öffentliche Versorgung': "Ministère de l'Énergie et des Services publics",
    'Ministerium; Statistics Mauritius (ODE)': 'Ministère ; Statistics Mauritius (ODE)',
    'Water Resources Commission über ION News': 'Water Resources Commission via ION News',
    'CWA-Jahresbericht 2024–25': 'Rapport annuel CWA 2024-2025', "NAO, L'Express, Ministerium": "NAO, L'Express, Ministère",
}


UI = {'en': UI_EN, 'fr': UI_FR}


ORTE_HOOK = [('Curepipe', -20.3163, 57.5259), ('Vacoas', -20.2981, 57.4783), ('Phoenix', -20.2917, 57.4972),
             ('Floréal', -20.3120, 57.4950)]


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
    text(bild, (rx + 560, 500), L('3–8 UHR'), f, es.HELLBLAU, 'ma', phase(t, t2 + 0.6, 0.5))
    text(bild, (rx, 708), L('JEDEN ZWEITEN TAG'), f, es.HELLBLAU, 'la', phase(t, t2 + 1.2, 0.5))
    return bild


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
    text(bild, (B / 2, 460), L('Warum auf Mauritius'), es.titel_schrift(104), anker='ma', deckkraft=a)
    text(bild, (B / 2, 580), L('das Wasser knapp wird'), es.titel_schrift(104), anker='ma', deckkraft=a)
    text(bild, (B / 2, 740), STAND[lv.SPRACHE].upper(), es.mono(30, True), es.HELLBLAU, 'ma', phase(t, 1.6, 0.6))
    return bild


SEKTOREN = [('haus', 'Haushalte', -1, -1), ('feld', 'Landwirtschaft', 1, -1), ('fabrik', 'Industrie', -1, 1),
            ('hotel', 'Tourismus', 1, 1)]


def szene_sektoren(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    mx, my = B / 2, 520
    a = phase(t, 0, 0.6)
    c.set_source_rgba(*WASSER, a)
    tropfen(c, mx, my + 40, 70 * (0.6 + 0.4 * a))
    c.fill()
    t2 = s.satz_start(1) if len(s.saetze) > 1 else 4.0  # rot erst bei „Wird es knapp …“
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
        text(bild, (mx + sx * 470, my + sy * 190 + 70), L(name), es.titel_schrift(36), anker='ma', deckkraft=p)
    return bild


def szene_reservoirs(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    b, h, abstand = 150, 300, 48
    x0 = (B - (7 * b + 6 * abstand)) / 2
    t2 = s.satz_start(1) if len(s.saetze) > 1 else 4.0  # „Zusammen fassen sie …“
    m = phase(t, t2, 1.4)  # 0 = sieben Behälter, 1 = ein gemeinsames Becken
    bx, by, bb, bh = (B - 1100) / 2, 250, 1100, 340
    for i in range(7):
        a = phase(t, 0.2 + i * 0.15, 0.4)
        f = phase(t, 0.6 + i * 0.15, 1.4)
        x = x0 + i * (b + abstand)
        rx, ry, rb, rh = x + (bx - x) * m, 280 + (by - 280) * m, b + (bb - b) * m, h + (bh - h) * m
        if f > 0:
            c.set_source_rgba(*WASSER, a)
            c.save()
            runde_box(c, rx, ry, rb, rh, 14)
            c.clip()
            c.rectangle(rx, ry + rh * (1 - f), rb, rh * f)
            c.fill()
            c.restore()
        if m < 1:
            c.set_source_rgba(1, 1, 1, a * (1 - m))
            c.set_line_width(4)
            runde_box(c, rx, ry, rb, rh, 14)
            c.stroke()
    if m > 0:
        c.set_source_rgba(1, 1, 1, m)
        c.set_line_width(5)
        runde_box(c, bx, by, bb, bh, 18)
        c.stroke()
    bild = zu_pil(fl)
    text(bild, (B / 2, 640), L('7 große Reservoirs'), es.titel_schrift(70), anker='ma',
         deckkraft=phase(t, 0.6, 0.5) * (1 - phase(t, t2, 0.4)))
    zaehler = phase(t, t2 + 0.3, 2.2)
    zahl = phase(t, t2 + 0.5, 0.4)
    if zahl > 0:
        text(bild, (B / 2, 640), f'{zahl_de(92.2 * zaehler)} {L("Mio. m³")}', es.titel_schrift(110), anker='ma', deckkraft=zahl)
        text(bild, (B / 2, 780), L('SPEICHERVERMÖGEN ZUSAMMEN'), es.mono(26, True), es.HELLBLAU, 'ma', zahl)
    return bild


STAUSEEN = [(1885, 'Mare-aux-Vacoas'), (1914, 'La Ferme'), (1929, 'La Nicolière'), (1948, 'Mare Longue'),
            (1952, 'Piton du Milieu'), (2002, 'Midlands'), (2017, 'Bagatelle')]


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
    text(bild, (B / 2, 220), L('7 von 7 künstlich angelegt'), es.titel_schrift(84), anker='ma', deckkraft=phase(t, 0, 0.6))
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
    text(bild, (x + b / 2, y + h + 104), f'{zahl_de(25.9)} {L("Mio. m³")}', es.mono(34, True), es.HELLBLAU, 'ma', phase(t, 0.5, 0.5))
    prozent_wert = round(anteil * 100 * p)
    text(bild, (kx, ky - 40), prozent(prozent_wert), es.titel_schrift(96), anker='ma', deckkraft=phase(t, 0.8, 0.4))
    text(bild, (kx, ky + r + 40), L('ANTEIL AM GESAMTEN SPEICHER'), es.mono(26, True), es.HELLBLAU, 'ma',
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
    text(bild, (B / 2, by + bh + 30), f'{L("Pegel")} {prozent(round(pegel * 100))}', es.mono(30, True), es.HELLBLAU, 'ma')
    return bild


FUELLSTAND = [('Vor einem Jahr', 69.7, False), ('Saisonaler Schnitt', 55.2, False), ('26.11.2026', 44.0, True)]


def szene_fuellstand(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    lage = balken(c, FUELLSTAND, t, 0.6, 100)
    bild = zu_pil(fl)
    ueberschrift(bild, L('Füllstand der sieben Reservoirs'), t)
    balken_texte(bild, FUELLSTAND, lage, ' %')
    return bild


FOTO = Path(__file__).resolve().parents[2] / 'public' / 'bilder' / 'wasserversorgung.jpg'


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
        z_.text((B - 40, H - 120), L('Foto: Diego Delso, CC BY-SA 4.0, Wikimedia Commons'), font=es.mono(22),
                fill=es.WEISS, anchor='ra', stroke_width=3, stroke_fill=(0, 0, 0))
        return bild
    fl, c = leinwand()
    links = 0.74
    rechts = 0.74 - 0.41 * phase(t, 0.8, 2.2)
    behaelter(c, 560, 300, 280, 380, links, phase(t, 0, 0.5))
    behaelter(c, 1080, 300, 280, 380, rechts, phase(t, 0.2, 0.5), ROT if rechts < 0.6 else WASSER)
    bild = zu_pil(fl)
    ueberschrift(bild, 'Mare-aux-Vacoas', t)
    text(bild, (700, 710), L('Nov. 2025'), es.mono(30, True), es.HELLBLAU, 'ma')
    text(bild, (1220, 710), L('Nov. 2026'), es.mono(30, True), es.HELLBLAU, 'ma')
    text(bild, (700, 230), prozent(74), es.titel_schrift(56), anker='ma', deckkraft=phase(t, 0.3, 0.5))
    text(bild, (1220, 230), prozent(round(rechts * 100)), es.titel_schrift(56), (255, 120, 128), 'ma',
         phase(t, 0.5, 0.5))
    return bild


def schieber_oeffnung(t: float) -> float:
    """Takt von 4 s: 1,6 s offen, 0,6 s schließen, 1,2 s zu, 0,6 s öffnen (0 = zu, 1 = offen)."""
    z = t % 4.0
    if z < 1.6:
        return 1.0
    if z < 2.2:
        return 1 - glatt((z - 1.6) / 0.6)
    if z < 3.4:
        return 0.0
    return glatt((z - 3.4) / 0.6)


def szene_cwa(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    y, dicke = 580, 80
    links, rechts, mitte = 240, 1680, B / 2
    oeffnung = schieber_oeffnung(max(0.0, t - 0.8)) if t > 0.8 else 1.0
    # Rohr
    c.set_source_rgba(*HELL, 1)
    runde_box(c, links, y - dicke / 2 - 10, rechts - links, dicke + 20, 20)
    c.fill()
    # Wasser links: immer
    c.set_source_rgba(*WASSER_TIEF, 1)
    c.rectangle(links + 10, y - dicke / 2, mitte - 40 - links - 10, dicke)
    c.fill()
    # Wasser rechts: nur bei offenem Schieber, läuft aus, wenn er schließt
    c.set_source_rgba(*WASSER_TIEF, oeffnung)
    c.rectangle(mitte + 40, y - dicke / 2, rechts - 10 - mitte - 40, dicke)
    c.fill()
    # Fließstreifen
    c.set_line_width(6)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(9):
        x = links + 30 + ((t * 220 + k * 90) % (mitte - 80 - links))
        c.set_source_rgba(*WASSER, 0.9)
        c.move_to(x, y)
        c.line_to(x + 40, y)
        c.stroke()
        if oeffnung > 0.05:
            x2 = mitte + 60 + ((t * 220 * oeffnung + k * 90) % (rechts - 100 - mitte - 60))
            c.set_source_rgba(*WASSER, 0.9 * oeffnung)
            c.move_to(x2, y)
            c.line_to(x2 + 40, y)
            c.stroke()
    # Gehäuse des Schiebers
    c.set_source_rgba(*GRAU, 1)
    runde_box(c, mitte - 60, y - dicke / 2 - 150, 120, dicke + 190, 16)
    c.fill()
    # Schieberplatte: oben = offen, unten = zu
    platte_y = y - dicke / 2 - 10 - (dicke + 10) * oeffnung
    c.set_source_rgba(*ROT, 1)
    runde_box(c, mitte - 34, platte_y, 68, dicke + 20, 8)
    c.fill()
    # Spindel und Handrad (dreht sich, während der Schieber fährt)
    spindel_oben = y - dicke / 2 - 230
    c.set_source_rgba(1, 1, 1, 1)
    c.set_line_width(10)
    c.move_to(mitte, platte_y)
    c.line_to(mitte, spindel_oben)
    c.stroke()
    winkel = -oeffnung * 4 * math.pi
    r = 90
    c.set_line_width(12)
    c.save()
    c.translate(mitte, spindel_oben)
    c.scale(1, 0.32)  # Rad schräg von vorn
    c.arc(0, 0, r, 0, 2 * math.pi)
    c.stroke()
    for k in range(4):
        w = winkel + k * math.pi / 2
        c.move_to(0, 0)
        c.line_to(math.cos(w) * r, math.sin(w) * r)
        c.stroke()
    c.restore()
    bild = zu_pil(fl)
    text(bild, (260, 170), 'CWA', es.titel_schrift(110), deckkraft=phase(t, 0, 0.5))
    text(bild, (264, 300), 'CENTRAL WATER AUTHORITY', es.mono(28, True), es.HELLBLAU, 'la', phase(t, 0.3, 0.5))
    text(bild, (B / 2, y + 120), L('offen') if oeffnung > 0.5 else L('geschlossen'), es.mono(34, True), es.WEISS, 'ma')
    return bild


VERKAUF = [('Aufbereitet', 332, False), ('Verkauft', 115, True)]


def szene_verkauf(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    t1 = s.satz_start(1) if len(s.saetze) > 1 else 1.5  # „2024 hat die CWA 332 … aufbereitet“
    t2 = s.satz_start(2) if len(s.saetze) > 2 else 4.0  # „Verkauft wurden … 115 …“
    leer = ('', 0, False)
    lage1 = balken(c, [VERKAUF[0], leer], t, t1, 340, x0=560, x1=1360)
    lage2 = balken(c, [leer, VERKAUF[1]], t, t2 - 0.6, 340, x0=560, x1=1360)
    bild = zu_pil(fl)
    ueberschrift(bild, L('Wasser der CWA im Jahr 2024, in Mio. m³'), t)
    balken_texte(bild, [VERKAUF[0]], lage1[:1], '', 0)
    balken_texte(bild, [VERKAUF[1]], lage2[1:], '', 0)
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
    text(bild, (B / 2, 150), L('Rund 60 % des Wassers bringen kein Geld ein'), es.titel_schrift(60), anker='ma',
         deckkraft=phase(t, 0.3, 0.6))
    f = es.mono(24, True)
    for (x, _), name in zip(ziele, ('Lecks', 'Illegale Anschlüsse', 'Abrechnungsfehler')):
        text(bild, (x, 920), L(name).upper(), f, es.HELLBLAU, 'ma', a)
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
    ueberschrift(bild, L('Rechnungshof, Dezember 2025'), t)
    text(bild, (600, 780), L('10 JAHRE'), es.mono(28, True), es.HELLBLAU, 'ma', phase(t, 0.5, 0.5))
    text(bild, (300, 330), L('Anteil ohne Einnahmen'), es.titel_schrift(36), deckkraft=phase(t, 0.8, 0.5))
    for k in range(4):
        q = phase(t, t2 + k * 0.45, 0.4)
        text(bild, (1385 + k * 24, 725 - k * 110 - 40 * (1 - q)), L('STUDIE'), es.mono(30, True), es.NAVY, 'mm', q)
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
    text(bild, (B / 2, 300), {'de': f'Rs {round(wert)} Mio.', 'en': f'Rs {round(wert)} million', 'fr': f'Rs {round(wert)} millions'}[lv.SPRACHE], es.titel_schrift(150), (255, 120, 128), 'ma',
         phase(t, 0.2, 0.4))
    text(bild, (B / 2, 520), L('VERLUST DER CWA LAUT MEDIENBERICHT'), es.mono(28, True), es.HELLBLAU, 'ma',
         phase(t, 0.6, 0.5))
    text(bild, (B / 2, 760), L('pro'), es.titel_schrift(44), es.NAVY, 'ma', a)
    text(bild, (B / 2, 810), L('Monat'), es.titel_schrift(44), es.NAVY, 'ma', a)
    return bild


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
    text(bild, (1410, 800), L('Staatshaushalt'), es.titel_schrift(48), anker='ma', deckkraft=phase(t, 0.4, 0.5))
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
    ueberschrift(bild, L('Wasserpreise'), t)
    text(bild, (x0 + 100, y - 118), L('Tarif'), es.titel_schrift(36), es.NAVY, 'ma')
    text(bild, (x0, y + 24), '2012', es.mono(30, True), es.HELLBLAU, 'ma')
    text(bild, (x1, y + 24), '2026', es.mono(30, True), es.HELLBLAU, 'ma', phase(t, 1.4, 0.4))
    text(bild, (680, y + 90), L('SEITDEM UNVERÄNDERT'), es.mono(28, True), (255, 120, 128), 'ma', phase(t, 1.6, 0.5))
    a = phase(t, t2, 0.6)
    text(bild, (1450, 595), '6 m³', es.titel_schrift(40), es.NAVY, 'mm', a)
    st = phase(t, t2 + 0.8, 0.3)
    if st > 0:
        ebene = Image.new('RGBA', bild.size, (0, 0, 0, 0))
        ze = ImageDraw.Draw(ebene)
        ze.rounded_rectangle([1320, 720, 1580, 800], 12, outline=(255, 120, 128, round(255 * st)), width=6)
        ze.text((1450, 760), L('GRATIS'), font=es.mono(44, True), fill=(255, 120, 128, round(255 * st)), anchor='mm')
        ebene = ebene.rotate(-8, center=(1450, 760))
        bild.paste(ebene, (0, 0), ebene)
    text(bild, (1450, 830), L('bis 6 m³ im Monat'), es.mono(26, True), es.HELLBLAU, 'ma', st)
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
    ueberschrift(bild, L('Ein neuer Anschluss'), t)
    text(bild, (1080, 640), L('BERECHNET'), es.mono(28, True), es.HELLBLAU, 'ma', klein)
    text(bild, (1420, 700), L('TATSÄCHLICHE KOSTEN'), es.mono(28, True), (255, 120, 128), 'ma', phase(t, 1.6, 0.4))
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
    t1 = s.satz_start(1) if len(s.saetze) > 1 else 3.0  # „Angekündigt … 2009, 2,6 Milliarden“
    t2 = s.satz_start(2) if len(s.saetze) > 2 else 6.0  # „2024 … 9,4 Milliarden“
    werte = [('Schätzung 2009', 2.6, False), ('Schätzung 2024', 9.4, True)]
    leer = ('', 0, False)
    lage1 = balken(c, [werte[0], leer], t, t1, 10, x0=900, x1=1700, basis=800, hoehe=470)
    lage2 = balken(c, [leer, werte[1]], t, t2 - 0.6, 10, x0=900, x1=1700, basis=800, hoehe=470)
    bild = zu_pil(fl)
    text(bild, (x, y + 40), 'Rivière-des-Anguilles', es.titel_schrift(34), anker='ma', deckkraft=phase(t, 0.6, 0.5))
    text(bild, (1300, 150), L('Geschätzte Kosten, Mrd. Rupien'), es.titel_schrift(50), anker='ma',
         deckkraft=phase(t, t1, 0.5))
    balken_texte(bild, werte[:1], lage1[:1], '', 1, basis=800)
    balken_texte(bild, werte[1:], lage2[1:], '', 1, basis=800)
    return bild


def szene_bauzeit(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    x0, x1, y = 260, 1660, 540
    punkte = [(2009.0, 'Ankündigung'), (2026.9, 'Baubeginn?'), (2029.9, 'Fertigstellung geplant')]

    def xpos(j: float) -> float:
        return {2009.0: 420, 2026.9: 1040, 2029.9: 1560}[j]

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
    ueberschrift(bild, L('Damm von Rivière-des-Anguilles'), t)
    for i, ((j, name), datum) in enumerate(zip(punkte, ('2009', L('Nov. 2026'), L('Nov. 2029')))):
        p = phase(t, 0.5 + i * 0.8, 0.4)
        text(bild, (xpos(j), y - 90), datum, es.mono(32, True), es.HELLBLAU, 'ma', p)
        text(bild, (xpos(j), y + 40), L(name), es.titel_schrift(40), (255, 120, 128) if i == 1 else es.WEISS, 'ma', p)
    t2 = s.satz_start(1) if len(s.saetze) > 1 else 3.0
    text(bild, (B / 2, 760), L('KEIN UNTERZEICHNETER BAUVERTRAG BEKANNT'), es.mono(30, True), (255, 120, 128), 'ma',
         phase(t, t2, 0.5))
    return bild


AKTEURE = [('Ministerium', 'setzt auf neue Speicher'), ('Rechnungshof', 'kritisiert die Verluste'),
           ('Fachleute', 'Tarife zu niedrig, aber erst besserer Service'), ('Haushalte', 'tragen die Rationierung')]


def szene_akteure(t: float, s: Szene) -> Image.Image:
    return karten(t, s, AKTEURE, L('Wer will was?'))


FRAGEN = [('Regenzeit', 'Füllt sie die Reservoirs wieder?'), ('Tarife', 'Steigen sie, und wer wird geschützt?'),
          ('Lecks', 'Wie schnell wird das Netz dicht?')]


def szene_offen(t: float, s: Szene) -> Image.Image:
    return karten(t, s, FRAGEN, L('Offene Fragen'), fragen=True)


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
    ueberschrift(bild, L('Kurz gesagt'), t)
    for x, name, p in zip(xs, ('Zu wenig Regen', 'Zu viel Verlust', 'Projekte, die warten'), a):
        text(bild, (x, 740), L(name), es.titel_schrift(46), anker='ma', deckkraft=p)
    return bild


DOSSIER_URL = 'https://gazet.morisyen.de/dossier/wasserversorgung'


def szene_ende(t: float, s: Szene) -> Image.Image:
    fl, c = leinwand()
    bild = zu_pil(fl)
    logo = es.logo_weiss(150)
    a = phase(t, 0, 0.6)
    if a > 0:
        bild.paste(logo, (260, 300), logo)
    text(bild, (440, 330), 'gazet.morisyen.de', es.titel_schrift(96), deckkraft=a)
    text(bild, (444, 460), L('DOSSIER: WASSERVERSORGUNG · STAND 28.11.2026'), es.mono(30, True), es.HELLBLAU, 'la',
         phase(t, 0.5, 0.5))
    text(bild, (444, 520), L('Alle Quellen, Hintergründe und neue Meldungen'), es.text_schrift(38), es.WEISS, 'la',
         phase(t, 0.8, 0.5))
    q = phase(t, 1.0, 0.5)
    if q > 0:
        qr = qr_bild(300, DOSSIER_URL)
        ebene = Image.new('RGB', qr.size)
        bild.paste(Image.blend(Image.new('RGB', qr.size, es.NAVY), qr, q), (1380, 280))
        text(bild, (1530, 600), L('ZUM DOSSIER'), es.mono(26, True), es.HELLBLAU, 'ma', q)
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


# Englische Fassung: gleiche Satzzahl und Reihenfolge je Szene wie im Deutschen (die Animation folgt den Satzanfängen)
TEXT_EN = {
    1: 'In November 2026, Curepipe, Vacoas, Phoenix and Floréal only had running water every other day. And even '
       'then, only from three to eight in the morning.',
    2: "Why is water running short on a tropical island? Let's take a look. As of late November 2026.",
    3: 'The whole island needs water: households, farming, industry and tourism. When it runs short, everyone '
       'feels it.',
    4: 'Mauritius stores its drinking water mainly in seven large reservoirs. Together they hold around 92 million '
       'cubic metres.',
    41: 'All seven are man-made. The oldest is Mare-aux-Vacoas: in 1885 a first dam, just one metre high, was built '
        'there on marshy land. The newest is the Bagatelle Dam, completed in 2017.',
    5: 'The largest is Mare-aux-Vacoas, with almost 26 million cubic metres, more than a quarter of the total.',
    6: 'The reservoirs are filled by rain. When it fails to come, the levels drop. That is exactly what happened '
       'in 2026.',
    7: 'On 26 November, the seven reservoirs were only 44 per cent full. A year earlier it was almost 70 per cent, '
       'and the seasonal average is around 55.',
    8: 'At Mare-aux-Vacoas the fall is especially sharp: around 33 per cent in mid-November, compared with 74 a '
       'year earlier.',
    9: 'When levels fall, the Central Water Authority, or CWA, restricts supply. Water then only flows at certain '
       'hours.',
    10: "But it is not only rain that is missing. In 2024 the CWA treated 332 million cubic metres of water. Only "
        "115 million of it was sold, just over a third.",
    11: 'Experts estimate that around 60 per cent of the water brings in no money. It seeps away through old, '
        'leaking pipes, flows off through illegal connections or is billed incorrectly.',
    12: 'In December 2025, the National Audit Office found that this share has risen over ten years. And solutions '
        'keep being put off by yet more studies.',
    13: 'According to media reports, this costs the CWA around 540 million rupees. Every month.',
    14: "These losses weigh on the CWA's finances, and ultimately on the state budget.",
    15: 'At the same time, water tariffs have not been adjusted since 2012. Households using no more than six cubic '
        'metres a month pay nothing at all.',
    16: 'The CWA also points out that a new connection costs it many times what it charges for it.',
    17: 'Great hopes rest on a new dam at Rivière-des-Anguilles in the south. It was announced in 2009, at a cost of '
        '2.6 billion rupees. By 2024 the estimate had risen to around 9.4 billion.',
    18: 'According to the energy minister, construction is due to start in November 2026 and finish in 2029. But no '
        'signed construction contract is known so far.',
    19: 'Those involved set different priorities. The ministry is betting on new storage. The National Audit Office '
        'criticises the losses. Experts consider the tariffs too low, but want better service first. And households '
        'bear the brunt of the rationing.',
    20: 'Questions remain: Will the rainy season bring enough water? Will tariffs rise, and how will low-income '
        'households be protected? And how quickly will the leaks be fixed?',
    21: 'In short: too little rain, too much loss, and projects the island has been waiting on for years.',
    22: 'For more background, all sources and the latest news on water supply, visit gazet.morisyen.de. And for our '
        'daily news from Mauritius, stay with us here on our channel. See you soon!',
}


TEXT_FR = {
    1: "En novembre 2026, à Curepipe, Vacoas, Phoenix et Floréal, l'eau ne coulait au robinet qu'un jour sur deux. "
       "Et encore, seulement de trois à huit heures du matin.",
    2: "Pourquoi l'eau manque-t-elle sur une île tropicale ? C'est ce que nous allons voir. Situation à fin novembre "
       "2026.",
    3: "Toute l'île a besoin d'eau : les ménages, l'agriculture, l'industrie et le tourisme. Quand elle manque, tout le "
       "monde le ressent.",
    4: 'Maurice stocke son eau potable surtout dans sept grands réservoirs. Ensemble, ils contiennent environ 92 '
       'millions de mètres cubes.',
    41: "Les sept sont des lacs artificiels. Le plus ancien est Mare-aux-Vacoas : en 1885, un premier barrage d'un "
        "mètre de haut y est construit dans une zone marécageuse. Le plus récent est le barrage de Bagatelle, achevé "
        "en 2017.",
    5: "Le plus grand est Mare-aux-Vacoas, avec près de 26 millions de mètres cubes, plus d'un quart du total.",
    6: "Les réservoirs sont alimentés par la pluie. Quand elle manque, les niveaux baissent. C'est exactement ce qui "
       "s'est passé en 2026.",
    7: "Le 26 novembre, les sept réservoirs n'étaient remplis qu'à 44 pour cent. Un an plus tôt, ils l'étaient à près "
       "de 70 pour cent, et la moyenne saisonnière est d'environ 55.",
    8: 'À Mare-aux-Vacoas, la baisse est particulièrement nette : environ 33 pour cent à la mi-novembre, contre 74 un '
       'an plus tôt.',
    9: "Quand les niveaux baissent, la Central Water Authority, la CWA, restreint la distribution. L'eau ne coule alors "
       "qu'à certaines heures.",
    10: "Mais il ne manque pas seulement de la pluie. En 2024, la CWA a traité 332 millions de mètres cubes d'eau. "
        "Seuls 115 millions ont été vendus, soit à peine plus d'un tiers.",
    11: "Selon des spécialistes, environ 60 pour cent de l'eau ne rapporte rien. Elle se perd dans des conduites "
        "vétustes qui fuient, part par des branchements illégaux ou est mal facturée.",
    12: "En décembre 2025, le Bureau de l'audit a constaté que cette part avait augmenté en dix ans. Et les solutions "
        "sont sans cesse repoussées par de nouvelles études.",
    13: 'Selon la presse, cela coûte à la CWA environ 540 millions de roupies. Chaque mois.',
    14: "Ces pertes pèsent sur les finances de la CWA, et donc, au bout du compte, sur le budget de l'État.",
    15: "Dans le même temps, les tarifs de l'eau n'ont pas été révisés depuis 2012. Les ménages qui consomment au plus "
        "six mètres cubes par mois ne paient rien.",
    16: "La CWA souligne aussi qu'un nouveau branchement lui coûte bien plus que ce qu'elle facture.",
    17: 'De grands espoirs reposent sur un nouveau barrage à Rivière-des-Anguilles, dans le Sud. Il a été annoncé en '
        "2009, pour 2,6 milliards de roupies. En 2024, l'estimation atteignait environ 9,4 milliards.",
    18: "Selon le ministre de l'Énergie, les travaux doivent commencer en novembre 2026 et s'achever en 2029. Mais "
        "aucun contrat de construction signé n'est connu à ce jour.",
    19: "Les acteurs ont des priorités différentes. Le ministère mise sur de nouvelles capacités de stockage. Le "
        "Bureau de l'audit critique les pertes. Les spécialistes jugent les tarifs trop bas, mais veulent d'abord un "
        "meilleur service. Et les ménages subissent le rationnement.",
    20: "Restent des questions : la saison des pluies apportera-t-elle assez d'eau ? Les tarifs vont-ils augmenter, et "
        "comment protéger les ménages modestes ? Et à quelle vitesse les fuites seront-elles réparées ?",
    21: "En bref : trop peu de pluie, trop de pertes et des projets que l'île attend depuis des années.",
    22: "Plus de contexte, toutes les sources et les dernières nouvelles sur l'approvisionnement en eau : rendez-vous "
        "sur gazet.morisyen.de. Et nos informations quotidiennes de Maurice, c'est ici, sur notre chaîne. À bientôt !",
}


TEXTE = {'en': TEXT_EN, 'fr': TEXT_FR}


# ----------------------------------------------------------------- Vorschaubild und YouTube

VORSCHAU_FOTO = FOTO
VORSCHAU = {
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

FOTO_SEITE = 'https://commons.wikimedia.org/wiki/File:Mare_aux_Vacoas,_Mauricio,_2025-09-25,_DD_77-82_PAN.jpg'
QUELLEN = [
    ('Ministry of Energy and Public Utilities – Water Resources Unit',
     'https://publicutilities.govmu.org/Pages/Water%20Sector/WRU.aspx'),
    ('Statistics Mauritius (ODE) – Water Reservoirs', 'https://ode.govmu.org/water-reservoirs'),
    ('National Audit Office – Water Report', 'https://nao.govmu.org/nao/wp-content/uploads/2026/02/water_report.pdf'),
    ('CWA Annual Report 2024–2025',
     'https://cwa.govmu.org/cwa/wp-content/uploads/2026/09/CWA_Annual-Report-2024-2025.pdf'),
    ('ION News', 'https://ionnews.mu/ressources-en-eau-les-reservoirs-reculent-a-44-au-26-novembre-2026/'),
    ("L'Express", 'https://lexpress.mu/s/eau-60-de-pertes-des-tarifs-trop-bas-le-verdict-des-specialistes-565115'),
    ('allAfrica / L\'Express', 'https://fr.allafrica.com/stories/202611180579.html'),
    ('newsmoris', 'https://newsmoris.com/cwa-loses-60-of-supply-amid-mounting-financial-deficits/'),
    ('Maurice Info',
     'https://maurice-info.mu/2026/03/04/le-barrage-de-riviere-des-anguilles-est-un-projet-phare-pour-le-sud.html'),
]

YOUTUBE = {
    'de': {
        'datei': 'lernvideo-wasser',
        'titel': 'Warum auf Mauritius das Wasser knapp wird (Stand Nov. 2026) | Gazet Morisyen erklärt',
        'text': ('Warum wird auf einer tropischen Insel das Wasser knapp? Wir erklären die Wasserversorgung auf '
                 'Mauritius: sieben künstliche Stauseen, sinkende Füllstände, hohe Verluste im Netz, eingefrorene '
                 'Tarife und der geplante Damm von Rivière-des-Anguilles.\n\n'
                 'Stand: 28. November 2026. Neuere Entwicklungen, alle Zahlen und Hintergründe im Dossier:\n'
                 f'{DOSSIER_URL}'),
        'quellen': 'Quellen', 'foto': 'Foto Mare-aux-Vacoas: Diego Delso, CC BY-SA 4.0, Wikimedia Commons',
        'ki': ('Hinweis: Die Sprecherstimme ist synthetisch (Piper, Stimme „Thorsten“). Grafiken und Animationen: '
               'Gazet Morisyen.'),
        'tags': ['Mauritius', 'Wasser', 'Wasserversorgung', 'Mare aux Vacoas', 'CWA', 'Dürre', 'Erklärvideo',
                 'Gazet Morisyen'],
        'untertitel': 'Deutsch',
    },
    'en': {
        'datei': 'lernvideo-wasser-en',
        'titel': 'Why Mauritius is running short of water (as of Nov 2026) | Gazet Morisyen explains',
        'text': ('Why is water running short on a tropical island? We explain water supply in Mauritius: seven '
                 'man-made reservoirs, falling levels, heavy losses in the network, frozen tariffs and the planned '
                 'Rivière-des-Anguilles dam.\n\n'
                 'As of 28 November 2026. Later developments, all figures and background in our explainer:\n'
                 f'{DOSSIER_URL}'),
        'quellen': 'Sources', 'foto': 'Photo of Mare-aux-Vacoas: Diego Delso, CC BY-SA 4.0, Wikimedia Commons',
        'ki': 'Note: the narration uses a synthetic voice (Piper, voice "Cori"). Graphics and animation: Gazet Morisyen.',
        'tags': ['Mauritius', 'water', 'water supply', 'Mare aux Vacoas', 'CWA', 'drought', 'explainer',
                 'Gazet Morisyen'],
        'untertitel': 'English',
    },
    'fr': {
        'datei': 'lernvideo-wasser-fr',
        'titel': "Pourquoi l'eau manque à Maurice (situation nov. 2026) | Gazet Morisyen explique",
        'text': ("Pourquoi l'eau manque-t-elle sur une île tropicale ? Nous expliquons l'approvisionnement en eau à "
                 'Maurice : sept lacs artificiels, des niveaux en baisse, de fortes pertes sur le réseau, des tarifs '
                 'gelés et le projet de barrage de Rivière-des-Anguilles.\n\n'
                 'Situation au 28 novembre 2026. Évolutions récentes, chiffres et contexte dans notre dossier :\n'
                 f'{DOSSIER_URL}'),
        'quellen': 'Sources', 'foto': 'Photo de Mare-aux-Vacoas : Diego Delso, CC BY-SA 4.0, Wikimedia Commons',
        'ki': 'Remarque : la voix est synthétique (Piper, voix « SIWIS »). Graphiques et animations : Gazet Morisyen.',
        'tags': ['Maurice', 'eau', 'approvisionnement en eau', 'Mare-aux-Vacoas', 'CWA', 'sécheresse',
                 'explication', 'Gazet Morisyen'],
        'untertitel': 'Français',
    },
}
