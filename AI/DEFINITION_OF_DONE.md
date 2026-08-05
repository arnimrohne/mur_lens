# Definition of Done (DoD)

## Zweck

Diese Definition of Done beschreibt die Mindestanforderungen, die erfüllt sein müssen, bevor eine Aufgabe, ein Sprint oder ein Feature als abgeschlossen gilt.

Ein Feature ist erst "Done", wenn **alle** folgenden Punkte erfüllt sind.

---

# 1. Funktionalität

* Alle Anforderungen des Sprints wurden umgesetzt.
* Das Feature funktioniert wie beschrieben.
* Keine bekannten Blocker sind vorhanden.
* Offensichtliche Randfälle wurden berücksichtigt.
* Fehler werden sinnvoll behandelt.

---

# 2. Codequalität

* TypeScript enthält keine Fehler.
* Es wird kein `any` verwendet (außer mit dokumentierter Ausnahme).
* Keine ungenutzten Variablen.
* Keine ungenutzten Imports.
* Keine doppelten Implementierungen.
* Keine offensichtlichen Code-Smells.
* Keine Magic Numbers.
* Keine Magic Strings.
* Business-Logik befindet sich nicht in UI-Komponenten.

---

# 3. Architektur

* Die bestehende Architektur wurde eingehalten.
* Neue Komponenten haben eine klar definierte Verantwortung.
* Wiederverwendbare Logik wurde ausgelagert.
* Neue Konfigurationen sind zentral definiert.
* Bestehende Architektur wurde nicht unnötig verschlechtert.

---

# 4. Benutzeroberfläche

* Mobile Darstellung geprüft.
* Desktop-Darstellung funktioniert.
* Touch-Bedienung berücksichtigt.
* Buttons ausreichend groß.
* Gute Lesbarkeit.
* Keine offensichtlichen Layoutfehler.

---

# 5. Performance

* Keine unnötigen Re-Renders.
* Keine unnötigen API-Aufrufe.
* Keine unnötigen Bibliotheken eingebunden.
* Bilder und Assets werden sinnvoll geladen.
* Bundle-Größe wurde nicht unnötig vergrößert.

---

# 6. Sicherheit

* Keine Secrets im Repository.
* Keine API-Keys im Quellcode.
* Benutzereingaben werden validiert.
* Fehler enthalten keine sensiblen Informationen.

---

# 7. Build & Qualitätssicherung

Vor Abschluss sind folgende Befehle erfolgreich auszuführen:

```bash
npm run lint

npm run build
```

Falls Tests vorhanden sind:

```bash
npm test
```

Alle Befehle müssen erfolgreich abgeschlossen werden.

---

# 8. Dokumentation

Falls erforderlich wurden aktualisiert:

* README.md
* PROJECT.md
* CLAUDE.md
* ROADMAP.md
* relevante ADRs

Architekturentscheidungen werden als ADR dokumentiert.

---

# 9. Git

Vor Abschluss:

* Änderungen logisch gruppieren.
* Keine temporären Dateien committen.
* Keine Debug-Ausgaben hinterlassen.
* Aussagekräftige Commit-Message erstellen.

---

# 10. Abschlussbericht

Nach jedem Sprint wird ein kurzer Bericht erstellt:

## Umgesetzt

Welche Anforderungen wurden erfüllt?

## Geänderte Dateien

Welche Dateien wurden erstellt oder geändert?

## Qualitätsprüfung

Ergebnis von:

* TypeScript
* ESLint
* Build
* Tests (falls vorhanden)

## Bekannte Einschränkungen

Welche Punkte sind bewusst noch nicht umgesetzt?

## Empfehlungen

Welche Aufgaben eignen sich sinnvoll für den nächsten Sprint?

---

# Ausschlusskriterien

Ein Sprint gilt **nicht** als abgeschlossen, wenn einer der folgenden Punkte zutrifft:

* Build schlägt fehl.
* Linter schlägt fehl.
* TypeScript enthält Fehler.
* Offensichtliche Bugs sind bekannt.
* Anforderungen wurden nur teilweise umgesetzt.
* Dokumentation ist veraltet.
* Temporärer oder experimenteller Code wurde zurückgelassen.
* Neue technische Schulden wurden eingeführt, ohne sie zu dokumentieren.

---

# Qualitätsziel

Nicht die Anzahl der Features entscheidet über den Erfolg eines Sprints.

Ein Sprint ist erfolgreich, wenn eine stabile, verständliche und erweiterbare Grundlage entstanden ist, auf der die nächsten Funktionen sicher aufgebaut werden können.
