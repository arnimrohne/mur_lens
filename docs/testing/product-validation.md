# Product Validation Sprint 4.1

**Ziel:** Qualität des aktuellen MVP mit ~50 realen Preisetiketten messen – bevor neue Features entwickelt werden.

**App-Stand:** Sprint 4 (Kamera → OCR → Preiserkennung → EUR-Umrechnung, statischer Kurs 50 MUR/EUR)

**Datum:** [Testlauf eintragen]  
**Tester:** [Name eintragen]  
**Gerät:** [Hersteller, Modell, OS, Version eintragen]

---

## 1. Testprotokoll

### 1.1 Vorbereitung (einmalig)

1. App auf dem Testgerät öffnen, `/scan` aufrufen
2. Kamera-Berechtigung erteilen
3. Akkuladung ≥ 50 % sicherstellen (verhindert CPU-Throttling)
4. Gerät nicht auf Energiesparmodus
5. Testtabelle `test-log.csv` öffnen (Vorlage: `test-log-template.csv`)

### 1.2 Durchführung (pro Etikett)

| Schritt | Aktion |
|---|---|
| 1 | Test-ID in der Tabelle anlegen |
| 2 | Etikett-Kategorie und erwarteten Preis notieren |
| 3 | Lichtbedingung und Abstand notieren |
| 4 | Auf „Aufnehmen" tippen |
| 5 | Gerät ruhig halten (~30 cm Abstand, Etikett im Bildmittelpunkt) |
| 6 | Ergebnis ablesen: erkannter MUR-Betrag und EUR-Betrag |
| 7 | Outcome-Kategorie eintragen (→ Abschnitt 3) |
| 8 | `processingTimeMs` aus dem Debug-Panel notieren |
| 9 | Bei Fehlschlag: JSON über „↓ JSON speichern" herunterladen, Dateiname notieren |
| 10 | Beobachtungen im Notizfeld festhalten |

### 1.3 Testlabel-Verteilung (50 Tests)

| Gruppe | Beschreibung | Anzahl |
|---|---|---|
| A – Baseline | Klare Supermarkt-Etiketten, gutes Licht, ~30 cm, gerader Winkel | 20 |
| B – Bedingungen | Gleiche Etiketten, aber wechselnde Bedingungen (Abstand, Winkel, Licht) | 10 |
| C – Formate | Ungewöhnliche Formate: Dezimalpreise, sehr große/kleine Beträge, Punkt als Tausendertrenner | 8 |
| D – Umgebung | Bekleidung, Elektronik, Marktstand (verschiedene Schriftbilder) | 7 |
| E – Grenzen | Herausfordernde Fälle: kleines Etikett, schlechtes Licht, handgeschrieben, Wasserzeichen | 5 |

**Lichtbedingungen:**
- `daylight` – direktes Tageslicht oder Fensterplatz
- `indoor-artificial` – Innenraum Neonlicht / LED
- `indoor-dim` – Innenraum gedämpft, kein direktes Licht
- `glare` – Reflexion auf dem Etikett sichtbar

**Abstände:** 20 cm / 30 cm / 50 cm  
**Winkel:** 0° (senkrecht) / 15° / 30°

---

## 2. Erfolgsmetriken

### 2.1 Primäre Kennzahlen (berechnet aus dem Testlog)

| Metrik | Formel | Ziel MVP |
|---|---|---|
| **End-to-End-Erfolgsquote** | Korrekte Resultate / Gesamt-Tests | ≥ 70 % |
| **Erkennungsrate** | Irgendein Preis gefunden / Gesamt | ≥ 80 % |
| **Genauigkeit (Precision)** | Korrekte / gefundene Preise | ≥ 85 % |
| **False-Positive-Rate** | Falsche Preise / gefundene Preise | ≤ 10 % |
| **False-Negative-Rate** | Nicht gefundene Preise / Gesamt | ≤ 20 % |
| **OCR-Zeit p50** | Median von `processingTimeMs` | ≤ 2 000 ms |
| **OCR-Zeit p95** | 95. Perzentil von `processingTimeMs` | ≤ 4 000 ms |
| **Absturzrate** | App-Abstürze / Gesamt-Tests | 0 % |

### 2.2 Sekundäre Kennzahlen

| Metrik | Beschreibung |
|---|---|
| **Confidence-Schwellwert-Analyse** | Confidence der True Positives vs. False Negatives – ergibt ob 0.40 optimal ist |
| **Erfolgsquote nach Gruppe** | A/B/C/D/E getrennt auswerten – zeigt wo die Engine versagt |
| **Betragsfehler-Verteilung** | Bei False Positives: Differenz erkannter vs. echter Betrag |
| **Erfolgsquote nach Licht** | Welche Lichtbedingung ist kritisch? |

---

## 3. Fehlerklassifizierung

Für jedes **nicht korrekte** Ergebnis wird genau eine Kategorie vergeben:

### Kategorie 1 – False Negative (kein Preis angezeigt)

| Code | Bedeutung | Erkennbar an |
|---|---|---|
| `FN-0` | OCR komplett leer (0 Wörter erkannt) | Debug-Panel: leere Liste |
| `FN-C` | OCR hat Text, aber Confidence unter Schwellwert | Debug-Panel: Wörter vorhanden, alle rot (< 40 %) |
| `FN-P` | Text erkannt, aber kein Preis-Muster (kein „Rs", „MUR" etc.) | Debug-Panel: Wörter vorhanden, kein Währungssymbol |
| `FN-M` | Preis-Muster gefunden, aber Merge-Fehler (Ziffern nicht korrekt zusammengesetzt) | JSON: items vorhanden, Merging-Logik scheitert |

### Kategorie 2 – False Positive (falscher Preis angezeigt)

| Code | Bedeutung | Beispiel |
|---|---|---|
| `FP-M` | Größenordnungsfehler | 1 250 → 125 oder 12 500 |
| `FP-V` | Wertfehler (gleiche Größenordnung) | 1 250 → 1 200 |
| `FP-W` | Falsches Element erkannt (Artikelnummer, Gewicht, Barcode-Zahl) | Artikelnummer 9876 wird als Preis erkannt |

### Kategorie 3 – Technischer Fehler

| Code | Bedeutung |
|---|---|
| `ERR-CAM` | Kamera nicht bereit / Berechtigung verweigert |
| `ERR-OCR` | Tesseract-Worker-Fehler (Exception) |
| `ERR-CRASH` | App-Absturz |

### Kategorie 4 – Außerhalb des Scope

| Code | Bedeutung |
|---|---|
| `OOS` | Etikett enthält keinen für die App lösbaren Preis (handgeschrieben unleserlich, nicht-lateinische Zeichen) |

---

## 4. Dokumentationsformat

### 4.1 CSV-Testlog

Vorlage: `test-log-template.csv` (im gleichen Verzeichnis)

Pflichtfelder pro Zeile:

```
test_id, date, expected_amount, label_category, lighting, distance_cm,
angle_deg, outcome, extracted_amount, confidence_pct, ocr_time_ms,
error_code, notes, json_file
```

**outcome-Werte:** `correct` | `no-price` | `wrong-price` | `app-error`

### 4.2 Gespeicherte JSON-Dateien

Für alle Tests mit `outcome ≠ correct` wird via „↓ JSON speichern" die `RecognitionResult`-Datei gespeichert.

Namenskonvention: `<test_id>-<label_category>-<outcome>.json`  
Beispiel: `T023-supermarket-FN-C.json`

Diese Dateien werden in `__tests__/fixtures/recognition/` abgelegt und können direkt als neue Unit-Test-Fixtures verwendet werden.

### 4.3 Aggregierter Abschlussbericht

Nach Abschluss der 50 Tests: `docs/testing/validation-report-v1.md` ausfüllen (Vorlage am Ende dieses Dokuments, Abschnitt 6).

---

## 5. MVP-Kriterien

Das MVP gilt als **bestanden**, wenn **alle** der folgenden Bedingungen erfüllt sind:

| # | Kriterium | Schwelle |
|---|---|---|
| M1 | End-to-End-Erfolgsquote (alle 50 Tests) | ≥ 70 % |
| M2 | End-to-End-Erfolgsquote (nur Gruppe A – Baseline) | ≥ 85 % |
| M3 | False-Positive-Rate | ≤ 10 % |
| M4 | OCR-Zeit p95 | ≤ 4 000 ms |
| M5 | App-Abstürze | 0 |

**Rationale:**
- M2 ist strenger als M1: Die App muss auf typischen, guten Etiketten zuverlässig funktionieren.
- M3 ist kritischer als M1: Ein falsch angezeigter Preis untergräbt das Vertrauen stärker als kein Preis.
- M5 ist nicht verhandelbar: Ein Absturz ist für eine PWA inakzeptabel.

Das MVP gilt als **gescheitert** (Sprint 5 blockiert), wenn:
- M1 < 50 % (fundamentales Erkennungsproblem)
- M3 > 20 % (Engine erzeugt zu viele Phantompreise)
- M5 > 0 (technische Instabilität)

---

## 6. Dauerhaft zu erfassende Metriken

Diese Metriken sollten bei jedem größeren Test-Batch und bei jedem Release aktualisiert werden.

### 6.1 Kernmetriken (müssen immer vorhanden sein)

| Metrik | Granularität | Warum |
|---|---|---|
| End-to-End-Erfolgsquote | Gesamt + je Gruppe | Primäre Produktqualitätskennzahl |
| False-Positive-Rate | Gesamt | Vertrauenskritisch |
| OCR-Zeit (p50, p95) | Gesamt + je Geräteklasse | UX-Qualität |
| Confidence-Verteilung | Histogramm (0–100 %) | Kalibrierung des Schwellwerts |
| Fehler-Kategorien | Anteil FN-0, FN-C, FN-P, FP-M usw. | Priorisierung der nächsten Fixes |

### 6.2 Regressionsmetriken (nach jedem Release)

Nach jedem Sprint werden die **gleichen 50 Etiketten** (oder eine repr. Teilmenge von ≥ 20) erneut getestet:

| Metrik | Ziel |
|---|---|
| Δ Erfolgsquote vs. Vorversion | ≥ 0 % (keine Regression) |
| Δ OCR-Zeit p95 vs. Vorversion | ≤ +10 % |
| Δ False-Positive-Rate vs. Vorversion | ≤ 0 % (keine Verschlechterung) |

### 6.3 Langfristige Trendmetriken

Sobald genug Datenpunkte (≥ 200 echte Tests) gesammelt sind:

| Metrik | Erkenntnisgewinn |
|---|---|
| Erfolgsquote nach Lichtbedingung | Gibt an ob ein Bild-Preprocessing nötig ist |
| Erfolgsquote nach Abstand | Zeigt ob der Kamera-Viewport optimiert werden muss |
| Confidence-Schwellwert-Optimum | Empirisch bestimmen: welches Threshold maximiert Precision×Recall |
| Häufigste Fehler-Codes | Priorisiert die Roadmap (z. B. FN-C → Threshold senken; FN-P → mehr Währungs-Patterns) |
| Vergleich Modell/Gerät | Zeigt ob Tesseract auf Mittelklasse-Smartphones akzeptabel schnell ist |

---

## 7. Vorlage: Abschlussbericht

```markdown
# Validation Report v1

**Datum:** YYYY-MM-DD  
**Tester:** ...  
**Gerät:** ...  
**App-Version / Commit:** ...

## Ergebnisse

| Metrik             | Wert   | Ziel   | Status |
|--------------------|--------|--------|--------|
| E2E-Erfolgsquote   |        | ≥ 70 % |        |
| Baseline (Gruppe A)|        | ≥ 85 % |        |
| False-Positive-Rate|        | ≤ 10 % |        |
| OCR-Zeit p95       |        | ≤ 4 s  |        |
| Abstürze           |        | 0      |        |

**MVP bestanden:** JA / NEIN

## Fehlerverteilung

| Code  | Anzahl | Anteil |
|-------|--------|--------|
| FN-0  |        |        |
| FN-C  |        |        |
| FN-P  |        |        |
| FN-M  |        |        |
| FP-M  |        |        |
| FP-V  |        |        |
| FP-W  |        |        |
| ERR-* |        |        |
| OOS   |        |        |

## Schwachstellen (nach Priorität)

1. ...
2. ...
3. ...

## Empfohlene nächste Schritte

- [ ] ...
- [ ] ...

## Neue Fixture-Dateien (für Regressionstests)

- `__tests__/fixtures/recognition/T0xx-...json` – [Beschreibung]
```
