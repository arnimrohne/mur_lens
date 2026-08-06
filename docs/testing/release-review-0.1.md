# Release Review 0.1

**Stand:** Sprint 4 (Commit 129e4e3)  
**Reviewer:** Claude Sonnet 4.6  
**Datum:** 2026-08-06

---

## Zusammenfassung

Der Code ist strukturell solide – saubere Schichtenarchitektur, klare Verantwortlichkeiten, gut getestete Kernlogik. Für ein internes Entwicklungs-Tool oder einen Beta-Test wäre der Stand akzeptabel. Für einen öffentlichen Release gibt es fünf Probleme, die ich als Release-blockierend einstufe.

---

## Must Fix – blockiert Release

### M1 · RecognitionDebugView ist im Produktions-Flow sichtbar

**Wo:** `app/scan/page.tsx` Zeilen 64 und 76  
**Was:** Im Erfolgsfall und im „kein Preis"-Fall wird `RecognitionDebugView` für jeden Benutzer angezeigt: Wortliste mit Confidence-Balken, JSON-Download-Button, aufklappbares Raw-JSON-Panel.

Das ist ein Entwickler-Werkzeug. Für einen Endnutzer, der Rs 1,250 in Euro umrechnen will, ist dieser Output bedeutungslos und verwirrend. Der JSON-Download-Button auf einem Produktions-Screen ist ein Zeichen, dass der Debug-Modus irrtümlich nicht entfernt wurde.

**Risiko:** Vertrauensverlust. Benutzer fragen sich, ob etwas schiefgelaufen ist.  
**Fix:** `RecognitionDebugView` aus dem Produktions-Flow entfernen. Optional: hinter einem versteckten Tap (z.B. 5× schnell tippen auf die Versionsangabe) für Felddiagnose zugänglich halten.

---

### M2 · Tesseract-Kaltstart ist für den Benutzer unsichtbar

**Wo:** `lib/recognition/providers/tesseract-provider.ts` Zeile 13, `app/scan/page.tsx` Zeile 13  
**Was:** Der Tesseract-Worker wird beim ersten `recognize()`-Aufruf initialisiert (Lazy-Loading). Auf einem Mittelklasse-Smartphone dauert die Worker-Initialisierung 3–8 Sekunden – zusätzlich zur eigentlichen OCR-Zeit.

Der Benutzer tippt auf „Foto aufnehmen", die App wechselt auf `{ kind: 'scanning' }` und zeigt „Erkenne…" – aber die nächsten 5–8 Sekunden passiert nichts sichtbares. Auf einem langsamen Gerät sieht das aus wie ein Absturz.

**Risiko:** Der erste Eindruck der App ist ein gefrorener Bildschirm.  
**Fix:** Worker-Initialisierung beim Laden der Scan-Seite starten (nicht beim ersten Capture). Während der Initialisierung eine eigene Ladeanzeige zeigen: „Wird vorbereitet…" mit Ladeanimation.

---

### M3 · Keine Ladeanimation für 2–4 Sekunden OCR-Wartezeit

**Wo:** `app/scan/page.tsx` Zeile 48–50  
**Was:** `{phase.kind === 'scanning' && <p>Erkenne…</p>}` – ein statischer Text ohne jede Animation für eine Operation, die mehrere Sekunden dauert.

Statischer Text signalisiert dem Benutzer nicht, dass die App aktiv arbeitet. Bei 2–4 Sekunden Wartezeit ist eine pulsierende Animation oder ein Spinner notwendig, damit der Benutzer weiß, dass die App nicht hängt.

**Risiko:** Fehlgeleitete Tipp-Wiederholungen, Frustration.  
**Fix:** Animierter Spinner oder pulsierendes Element während `scanning`.

---

### M4 · PWA-Manifest hat keine Icons

**Wo:** `public/manifest.json`  
**Was:** Das Manifest hat kein `icons`-Feld. Ohne Icons:
- iOS: kein Homescreen-Icon beim „Zum Home-Bildschirm" hinzufügen
- Android Chrome: PWA-Installationsprompt erscheint nicht
- Kein Splash-Screen

Die App ist als PWA deklariert (`manifest.json`, `appleWebApp`-Metadata), verhält sich aber nicht wie eine.

**Risiko:** Die primäre Verteilungsstrategie (PWA-Installation) funktioniert nicht.  
**Fix:** Mindestens `192×192` und `512×512` PNG-Icons erstellen und in `manifest.json` eintragen. Apple benötigt zusätzlich `apple-touch-icon` im `<head>`.

---

### M5 · PhotoPreview verursacht UI-Verwirrung nach Capture

**Wo:** `hooks/use-camera.ts` Zeile 56, `components/camera-view.tsx` Zeile 60  
**Was:** Nach jedem Capture wird `capturedPhoto` (Data-URL) gesetzt und `<PhotoPreview>` unterhalb des Live-Kamera-Feeds gerendert. Das Ergebnis:

```
[Live-Kamerabild – streaming]
[Foto aufnehmen Button – noch aktiv]
[Standbild der Aufnahme – PhotoPreview]
[... Scroll erforderlich ...]
[Preis-Ergebnis – PriceResultView]
```

Der Benutzer sieht zwei Bilder gleichzeitig, der wichtige Inhalt (EUR-Betrag) ist out-of-viewport. Die Live-Kamera läuft weiter, obwohl der Benutzer gerade ein Foto auswertet.

**Risiko:** Benutzer sehen ihr Ergebnis nicht, weil es unterhalb des Folds liegt.  
**Fix:** Nach Capture entweder (a) zur Ergebnis-Ansicht scrollen/navigieren, oder (b) `CameraView` im Scanning-/Done-Zustand ausblenden und durch Ergebnis ersetzen. `PhotoPreview` sollte für den Endnutzer entweder entfernt oder deutlich weniger prominent sein.

---

## Should Fix – verbessert Qualität deutlich

### S1 · Kamerafehler erzeugt irreführende Fehlermeldung

**Wo:** `app/scan/page.tsx` Zeile 37–40, `components/camera-view.tsx` Zeile 20–23  
**Was:** `handleCapture` in `CameraView` hat kein eigenes Error-Handling. Wenn `capturePhoto()` wirft (z.B. `"Camera not ready"`), fängt `ScanPage.handleCapture` den Fehler – und zeigt „Erkennung fehlgeschlagen – bitte erneut versuchen." Das ist eine OCR-Fehlermeldung für einen Kamerafehler.

Außerdem: `use-camera.ts` Zeile 34 enthält `console.error('Camera access failed:', err)` – ein Debug-Log im Produktionscode.

**Fix:** `capturePhoto()` in `CameraView.handleCapture` in ein try-catch wrappen, einen kamerabezogenen Fehler-Callback hinzufügen oder den Fehlertyp im `ScanPage`-Catch unterscheiden.

---

### S2 · Kein React Error Boundary

**Wo:** gesamte App  
**Was:** Kein Error Boundary. Ein unbehandelter React-Fehler (z.B. ein Rendering-Fehler in `PriceResultView` durch einen unerwarteten Wert) führt zu einem komplett weißen Bildschirm ohne Meldung. Bei einer PWA ist das kritisch, weil kein Browser-Navigationselement sichtbar ist.

**Fix:** Ein einfaches `ErrorBoundary`-Component um `<ScanPage>` und/oder den Root-Layout wrappen. Zeigt „Etwas ist schiefgelaufen – bitte neu laden" statt leerer Seite.

---

### S3 · Confidence-Metrik in PriceResultView ist falsch berechnet

**Wo:** `components/price-result-view.tsx` Zeilen 14–19  
**Was:** `avgConfidence` ist der Durchschnitt **aller** TextItems im RecognitionResult – also einschließlich Noise-Wörter wie „PRICE", „TOTAL" usw. die möglicherweise hohe Confidence haben. Das Ergebnis hat keine Beziehung zur tatsächlichen Erkennungsqualität des Preises.

Außerdem ist `RecognitionResult` in `PriceResultView` als Prop vorhanden ausschließlich für diese Berechnung. Das ist ein Layer-Durchbruch: die Presentation-Schicht referenziert direkt das Recognition-Domain-Objekt, nur um eine Metrik zu berechnen.

**Fix:** Entweder (a) die Confidence aus `extractPrice` zurückgeben (z.B. als `{ price: Price, confidence: number } | null`), oder (b) die Metrik aus der UI entfernen, bis sie korrekt berechnet werden kann.

---

### S4 · Tesseract-Worker wird nie terminiert (Memory-Leak)

**Wo:** `lib/recognition/providers/tesseract-provider.ts` Zeile 13  
**Was:** `workerPromise` wird beim Initialisieren gesetzt und nie `worker.terminate()` aufgerufen. Tesseract-Worker verbrauchen signifikanten Speicher (~50–100 MB). In einer langen Session akkumuliert sich das.

**Fix:** Entweder ein `dispose()`-Methode auf `TesseractProvider` implementieren, oder den Worker-Lifecycle an den Page-Unmount binden (via `useEffect`-Cleanup in der Scan-Seite).

---

### S5 · Bildauflösung wird nicht reduziert vor OCR

**Wo:** `hooks/use-camera.ts` Zeilen 53–61  
**Was:** `capturePhoto` erstellt ein Canvas in voller Videauflösung. Aktuelle Smartphones liefern 1920×1080 bis 4032×3024. Tesseract performt auf großen Bildern erheblich langsamer, ohne proportionalen Qualitätsgewinn für Texterkennung (Texte auf Preisetiketten sind typischerweise 30–80px hoch).

Eine Reduktion auf 800–1000px Breite reduziert die OCR-Zeit auf mobilen Geräten um 50–70 % bei gleicher oder besserer Erkennungsrate (Tesseract intern skaliert ohnehin).

**Fix:** Vor `canvas.toBlob()` auf eine Maximalbreite von 1000px skalieren.

---

### S6 · MUR-Betragsformatierung kann Benutzer verwirren

**Wo:** `components/price-result-view.tsx` Zeile 21  
**Was:** `price.amount.toLocaleString('de-DE')` gibt `1.250` aus (Punkt als Tausendertrenner, deutsches Format). Das physische Etikett zeigt `1,250` (Komma als Tausendertrenner, englisches Format). Ein Benutzer, der das Preisschild mit dem App-Display vergleicht, sieht zwei verschiedene Zahlendarstellungen für denselben Betrag.

**Fix:** Entweder Intl-Format explizit auf Mauritius-Standard setzen (`en-MU`) oder Tausendertrenner konsistent verwenden: `Rs 1 250` (Leerzeichen – international neutral und klar).

---

## Nice to Have – kann nach Release erfolgen

### N1 · Worker-Pre-warming mit sichtbarer Initialisierungsphase

Derzeit wird der Worker lazy initialisiert. Als vollständige Lösung für M2 wäre ein dedizierter `init()`-Aufruf auf dem ScanPage-Mount wünschenswert – mit einer kurzen Initialisierungs-Animation (z.B. 3 Sekunden „Kamera-OCR wird geladen…"), die nach Init automatisch verschwindet.

---

### N2 · Cross-Line Currency Association

**Wo:** `lib/recognition/extractors/price-extractor.ts`  
**Was:** `extractFromLine` findet nur Preise, wenn Currency-Token und Number-Token auf **derselben** Bildzeile sind. Der Fall „Rs" (Zeile N) + „1250" ohne MUR-Suffix (Zeile N+1) wird nicht erkannt. Der aktuelle `mur-currency-separate-line`-Fixture funktioniert nur, weil „MUR" und „1,250" auf derselben Zeile sind.

In der Praxis kommen Labels vor, die nur „Rs" oben und die Zahl darunter zeigen, ohne MUR-Suffix.

---

### N3 · `looksLikeNumber`-zweite Bedingung hat keine Testabdeckung

**Wo:** `lib/recognition/extractors/price-extractor.ts` Zeile 67  
**Was:** `/^[,.\d\s]*[\d]$/` würde Strings wie `",5"` oder `"  5"` als Zahl klassifizieren. Kein Fixture oder Inline-Test deckt diesen Fall ab. Entweder testen oder entfernen.

---

### N4 · Content-Security-Policy fehlt

**Wo:** `next.config.ts`  
**Was:** Security-Headers vorhanden (X-Frame-Options, Referrer-Policy usw.), aber kein CSP. Für eine App, die Kamera-Zugriff nutzt und externen Code (Tesseract WASM) lädt, wäre ein CSP mit `worker-src blob:` und `wasm-unsafe-eval` korrekt.

---

### N5 · `console.error` im Produktionscode

**Wo:** `hooks/use-camera.ts` Zeile 34  
**Was:** `console.error('Camera access failed:', err)` – sollte entfernt oder hinter `process.env.NODE_ENV === 'development'` gestellt werden. Kein sicherheitskritisches Problem, aber kein prodder Code.

---

### N6 · `key={i}` in RecognitionDebugView

**Wo:** `components/recognition-debug-view.tsx` Zeile 47  
**Was:** Index als React-Key. Kein funktionales Problem solange die Liste nicht reordert, aber technisch schlechte Praxis. Da `TextItem` kein stabiles `id`-Feld hat, wäre `key={item.value + item.boundingBox?.x}` eine robustere Option.

---

## Gesamtbewertung

| Bereich | Status | Kritischster Punkt |
|---|---|---|
| Architektur | ✅ Gut | – |
| Codequalität | ✅ Gut | S3 (falsche Confidence-Berechnung) |
| UX | ❌ Nicht release-bereit | M2, M3, M5 |
| Performance | ⚠️ Bedingt | M2 (Kaltstart), S5 (Bildgröße) |
| Wartbarkeit | ✅ Gut | S4 (Worker-Leak) |
| Release-Risiko | ❌ Blockiert | M1, M4 |

**Empfehlung:** M1–M5 beheben, dann erneut reviewen. S1–S2 können parallel oder unmittelbar danach erfolgen. S3–S6 gehören in den nächsten Sprint nach Release.
