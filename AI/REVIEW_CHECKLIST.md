# Review Checklist

## Zweck

Diese Checkliste wird vor jedem Abschluss eines Features, eines Sprints oder eines Pull Requests durchgeführt.

Ziel ist es, typische Fehler frühzeitig zu erkennen und eine gleichbleibend hohe Codequalität sicherzustellen.

Alle Punkte sollten aktiv geprüft werden.

---

# 1. Anforderungen

* Stimmen alle umgesetzten Funktionen mit den Anforderungen des Sprints überein?
* Wurden keine zusätzlichen, nicht angeforderten Features eingebaut?
* Wurden alle Akzeptanzkriterien erfüllt?
* Wurden offensichtliche Randfälle berücksichtigt?

---

# 2. Architektur

* Passt die Lösung zur bestehenden Architektur?
* Wurde Business-Logik von der UI getrennt?
* Liegt neue Logik an der richtigen Stelle?
* Wurden bestehende Komponenten sinnvoll wiederverwendet?
* Ist die Lösung erweiterbar?

---

# 3. Codequalität

* Ist der Code leicht verständlich?
* Sind Variablen und Funktionen sinnvoll benannt?
* Gibt es unnötige Verschachtelungen?
* Gibt es doppelten Code?
* Sind Funktionen klein und fokussiert?
* Enthält der Code keine offensichtlichen Code-Smells?

---

# 4. TypeScript

* Keine Verwendung von `any`
* Typen sind vollständig
* Keine TypeScript-Warnungen
* Keine unnötigen Type Assertions (`as`)
* Nullable-Werte werden korrekt behandelt

---

# 5. React

* Komponenten besitzen nur eine Verantwortung
* Props sind sauber typisiert
* State wird minimal gehalten
* Keine unnötigen Re-Renders
* Hooks werden korrekt verwendet
* Keine Logik direkt im JSX

---

# 6. Fehlerbehandlung

* Alle asynchronen Aufrufe behandeln Fehler
* Fehler werden dem Benutzer verständlich angezeigt
* Keine leeren `catch`-Blöcke
* Keine still ignorierten Exceptions

---

# 7. Performance

* Keine unnötigen Berechnungen
* Keine unnötigen API-Aufrufe
* Keine unnötigen Bibliotheken
* Keine unnötigen Re-Renders
* Bundle-Größe wurde nicht unnötig erhöht

---

# 8. Mobile & UX

* Smartphone getestet
* Touch-Bedienung angenehm
* Buttons ausreichend groß
* Gute Lesbarkeit
* Layout auf kleinen Displays geprüft
* Keine überlappenden Elemente
* Fokus- und Tastaturbedienung funktionieren

---

# 9. Accessibility

* Sinnvolle `aria`-Attribute
* Formulare korrekt beschriftet
* Kontraste ausreichend
* Fokus sichtbar
* Bilder besitzen Alt-Texte (sofern erforderlich)

---

# 10. Sicherheit

* Keine Secrets im Code
* Keine API-Keys im Repository
* Eingaben validiert
* Keine sensiblen Daten im Client
* Fehlermeldungen enthalten keine vertraulichen Informationen

---

# 11. Projektstruktur

* Neue Dateien befinden sich am richtigen Ort
* Keine temporären Dateien
* Keine ungenutzten Dateien
* Keine ungenutzten Imports
* Keine Debug-Ausgaben (`console.log`)

---

# 12. Dokumentation

Falls erforderlich wurden aktualisiert:

* README.md
* PROJECT.md
* CLAUDE.md
* ROADMAP.md
* ADRs

Neue Architekturentscheidungen wurden dokumentiert.

---

# 13. Qualitätssicherung

Vor Abschluss erfolgreich ausgeführt:

```bash
npm run lint
```

```bash
npm run build
```

Falls vorhanden:

```bash
npm test
```

Alle Befehle müssen erfolgreich abgeschlossen werden.

---

# 14. Git

* Commit enthält nur zusammengehörige Änderungen
* Keine temporären Dateien
* Aussagekräftige Commit-Message
* Keine versehentlich eingecheckten Artefakte

---

# 15. Abschlussbericht

Vor Abschluss kurz dokumentieren:

## Umgesetzt

Welche Anforderungen wurden erfüllt?

## Qualitätsstatus

* TypeScript
* ESLint
* Build
* Tests

## Bekannte Einschränkungen

Welche Punkte sind bewusst offen geblieben?

## Nächster sinnvoller Schritt

Empfehlung für den folgenden Sprint.

---

# Stop-Kriterien

Die Arbeit darf **nicht** abgeschlossen werden, wenn einer der folgenden Punkte zutrifft:

* Build schlägt fehl.
* Linter schlägt fehl.
* TypeScript enthält Fehler.
* Bekannte Bugs wurden nicht dokumentiert.
* Anforderungen sind unvollständig umgesetzt.
* Temporärer Code oder Debug-Ausgaben befinden sich im Repository.
* Dokumentation ist offensichtlich veraltet.

---

# Ziel

Nicht möglichst schnell fertig werden.

Sondern jede Änderung in einem Zustand hinterlassen, den ein anderer Entwickler sofort verstehen, testen und sicher erweitern kann.
