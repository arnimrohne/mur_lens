# Coding Standards

## Ziel

Diese Coding Standards definieren die Regeln für die Entwicklung dieses Projekts.

Ziel ist ein konsistenter, wartbarer und gut verständlicher Code, der auch nach Jahren problemlos erweitert werden kann.

Im Zweifel gilt:

> Lesbarkeit ist wichtiger als Cleverness.

---

# Allgemeine Prinzipien

* Bevorzuge einfache Lösungen.
* Vermeide unnötige Komplexität.
* Schreibe Code für Menschen, nicht für Compiler.
* Jede Datei hat eine klar definierte Verantwortung.
* Jede Funktion erfüllt möglichst genau eine Aufgabe.

---

# TypeScript

## Typisierung

Verwende immer eine explizite Typisierung.

`any` ist nicht erlaubt.

Falls eine Ausnahme notwendig ist, muss sie dokumentiert werden.

Bevorzuge:

* Interfaces für Datenstrukturen
* Type Aliases für Union Types
* Enums nur wenn sie echten Mehrwert bieten

---

# Benennung

Verwende sprechende Namen.

Nicht:

```ts
const d = ...
```

Sondern:

```ts
const exchangeRate = ...
```

---

# Dateinamen

Verwende ausschließlich:

kebab-case

Beispiele

```text
camera-preview.tsx
price-parser.ts
exchange-rate.ts
currency-config.ts
```

---

# React-Komponenten

Komponentennamen:

PascalCase

```tsx
CameraPreview
ExchangeRateCard
ResultScreen
```

Eine Komponente soll möglichst nur eine Aufgabe haben.

Wenn eine Komponente wächst, teile sie auf.

---

# Hooks

Alle Hooks beginnen mit:

```text
use...
```

Beispiele

```text
useCamera
useRecognition
useExchangeRate
useCurrency
```

Hooks enthalten ausschließlich wiederverwendbare Logik.

Keine Darstellung.

---

# Utilities

Alle Berechnungen gehören in:

```text
lib/
```

Zum Beispiel

```text
price-parser.ts
currency.ts
recognition/types.ts
recognition/providers/tesseract-provider.ts
```

Utilities dürfen keine React-Abhängigkeiten besitzen.

Sie sollen unabhängig testbar sein.

---

# Komponentenstruktur

Empfohlene Reihenfolge

```tsx
Imports

Typen

Konstanten

Komponente

Helper-Funktionen

Export
```

---

# Import-Reihenfolge

1. React
2. Next.js
3. Externe Bibliotheken
4. Eigene Komponenten
5. Hooks
6. Utilities
7. Typen
8. Styles

Keine ungenutzten Imports.

---

# Funktionen

Eine Funktion soll:

* kurz sein
* leicht verständlich sein
* möglichst nur eine Aufgabe haben

Richtwert:

maximal etwa 40 Zeilen.

Längere Funktionen sollten überprüft und gegebenenfalls aufgeteilt werden.

---

# Komponenten

Richtwert:

unter 250 Zeilen.

Wenn eine Komponente deutlich größer wird:

* Child Components extrahieren
* Custom Hooks erstellen
* Logik auslagern

---

# Fehlerbehandlung

Jeder Fehler wird bewusst behandelt.

Keine leeren

```ts
catch {}
```

Keine still ignorierten Exceptions.

Fehlermeldungen sollen verständlich sein.

---

# Logging

Nutze

```ts
console.error()
```

nur für echte Fehler.

Temporäre

```ts
console.log()
```

dürfen nicht im finalen Code verbleiben.

---

# Konfiguration

Alle Konfigurationen liegen zentral.

Beispiele

```text
config/

currency-config.ts

app-config.ts

feature-flags.ts
```

Keine Hardcodierung.

---

# Konstanten

Keine Magic Numbers.

Nicht:

```ts
if (price > 52.34)
```

Sondern:

```ts
const DEFAULT_EXCHANGE_RATE = 52.34
```

---

# Kommentare

Kommentiere nur das Warum.

Nicht das Offensichtliche.

Schlecht:

```ts
// Erhöhe i um eins
i++
```

Gut:

```ts
// Einige Recognition Provider liefern Leerzeichen in Zahlen.
// Diese werden vor dem Parsen entfernt.
```

---

# Styling

Verwende Tailwind Utilities.

Keine Inline-Styles.

Komplexe Varianten werden in eigene Komponenten ausgelagert.

---

# Performance

Vermeide:

* unnötige Re-Renders
* unnötige State-Updates
* doppelte Berechnungen
* unnötige Bibliotheken

Optimierungen erfolgen nur bei messbarem Nutzen.

---

# Accessibility

Alle interaktiven Elemente benötigen:

* sinnvolle Labels
* Tastaturbedienbarkeit
* ausreichenden Kontrast
* sichtbaren Fokus

Bilder benötigen Alt-Texte, sofern sie nicht rein dekorativ sind.

---

# Mobile First

Die Anwendung wird zuerst für Smartphones entwickelt.

Danach erfolgt die Optimierung für größere Bildschirme.

---

# Projektstruktur

Empfohlene Struktur

```text
app/
components/
hooks/
lib/
config/
types/
public/
docs/
```

Neue Dateien werden dort abgelegt, wo ihre Verantwortung liegt.

---

# Architekturentscheidungen

Wenn eine neue Architekturentscheidung getroffen wird, prüfe, ob ein ADR erstellt oder aktualisiert werden sollte.

---

# Refactoring

Wenn bestehender Code verbessert werden kann:

* kleine Refactorings sofort durchführen
* größere Refactorings dokumentieren und für einen späteren Sprint vorschlagen

---

# Goldene Regel

Jeder Commit soll den Code mindestens genauso gut hinterlassen, wie er vorgefunden wurde.

Im Idealfall ist der Code nach jeder Änderung ein kleines Stück besser.
