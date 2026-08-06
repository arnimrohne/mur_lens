# Recognition Fixtures

Test-Fixtures für den PriceExtractor.

Jede Datei ist ein gespeichertes `RecognitionResult` – identisch mit dem Output des `TesseractProvider`.

---

## Format

```ts
interface RecognitionResult {
  provider: string;           // z. B. "tesseract"
  processingTimeMs: number;   // reine OCR-Zeit ohne Worker-Init
  items: RecognitionItem[];
}

interface TextItem {
  type: "text";
  value: string;              // erkanntes Wort, bereits getrimmt
  confidence: number;         // 0.0–1.0 (Tesseract 0–100 / 100)
  boundingBox?: {
    x: number;                // linke Kante in Pixeln
    y: number;                // obere Kante in Pixeln
    width: number;
    height: number;
  };
}
```

---

## Fixtures

| Datei | Beschreibt | Erwartetes Ergebnis |
|---|---|---|
| `mur-1250-clean.json` | Klares Label "Rs 1,250" | `{ amount: 1250, currency: "MUR" }` |
| `mur-ocr-zero.json` | OCR liest "O" statt "0": "1,25O" | `{ amount: 1250, currency: "MUR" }` |
| `mur-spaced-number.json` | Zahl aufgeteilt: "Rs", "1", "250" als drei Wörter | `{ amount: 1250, currency: "MUR" }` |
| `mur-period-sep.json` | Punkt als Tausendertrennzeichen: "1.250" | `{ amount: 1250, currency: "MUR" }` |
| `mur-currency-separate-line.json` | "Rs" und Zahl auf separaten Zeilen, zusätzliches Label-Wort | `{ amount: 1250, currency: "MUR" }` |
| `mur-low-confidence.json` | Sehr schlechte Bildqualität, Confidence < 40% | `null` (kein verlässlicher Preis) |
| `empty-no-text.json` | Kein Text erkannt (leeres Bild) | `null` |

---

## Eigene Fixtures hinzufügen

1. App öffnen → Kamera → Foto aufnehmen
2. Im Debug-Panel: "↓ JSON speichern" klicken
3. Datei in diesen Ordner kopieren
4. Aussagekräftigen Namen wählen: `mur-<beschreibung>.json`
5. Zeile in der Tabelle oben ergänzen

---

## Namenskonvention

```
<währung>-<betrag-oder-beschreibung>[-<sonderfall>].json

mur-1250-clean.json
mur-1250-ocr-zero.json
mur-19-99-decimal.json
mur-large-5000.json
empty-no-text.json
```
