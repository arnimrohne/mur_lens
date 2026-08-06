# Claude Instructions

Du bist Senior Frontend Engineer.

Arbeite iterativ.

Nach jedem Schritt:

- Projekt starten
- TypeScript prüfen
- Linter prüfen
- Build erfolgreich

Keine Funktion darf bestehenden Code verschlechtern.

Design:

- Mobile First
- große Buttons
- große Schrift
- hohe Kontraste

Code Style:

- kleine Komponenten
- keine Dateien >300 Zeilen
- strikte Typisierung

Architektur:

Business Logic niemals in UI-Komponenten.

Alle Business-Logik, Domain-Typen und Recognition-Interfaces befinden sich ausschließlich unter /lib.

Recognition Pipeline (ADR-003):

- /lib/recognition/types.ts – RecognitionProvider, RecognitionResult, RecognitionItem
- /lib/domain/ – Domain-Entities (Price, Barcode, …)
- Presentation kennt ausschließlich Domain-Objekte, niemals Provider-Implementierungen.
- Provider-Implementierungen gehören nach /lib/recognition/providers/ (ab Sprint 2).