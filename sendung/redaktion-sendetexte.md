# Zusatz zum Auftrag der Redaktion: Sende-Texte

Diesen Abschnitt im Auftrag der geplanten Aufgabe „Gazet Morisyen – Aktualisierung (Redaktion)“
vor „Stil:“ einfügen. Außerdem in SCHRITT 5 die Prüfung um „jedes neue Update hat sendung.de/fr/en
mit sprechtext und stichpunkte (2–4 Punkte, je ≤ 70 Zeichen)“ ergänzen.

SENDE-TEXTE (für die tägliche Video-Sendung, die ein Sprecher vorliest)
Jedes Update, das in diesem Lauf neu angelegt wird, bekommt zusätzlich das Feld
"sendung": { "de": {"sprechtext", "stichpunkte"}, "fr": {"sprechtext", "stichpunkte"}, "en": {"sprechtext", "stichpunkte"} }:
- "sprechtext": 3–5 kurze Sätze zum Vorlesen, in gesprochener Sprache, in eigenen Worten (gleiche RECHTLICHE REGELN). Die Schlagzeile wird nicht vorgelesen. Der erste Satz muss ihren Inhalt deshalb sinngemäß enthalten (Wer? Was? Wo?). Gibt es im Thema schon frühere Updates, endet der Text mit 1–2 Sätzen Rückblick, eingeleitet mit „Zuvor …“, „Bisher …“ oder „Bereits am …“ (fr: « Auparavant… », « Jusqu'ici… », « Déjà le… »; en: "Earlier…", "Previously…", "Already on…"). Zahlen, Beträge und Uhrzeiten so schreiben, wie man sie spricht: de „19 Uhr 15“, „400.000 Rupien“, „6,4 Prozent“; fr « 19 heures 15 », « 400 000 roupies », « 6,4 pour cent »; en "7.15 pm", "400,000 rupees", "6.4 per cent". Jahreszahlen immer als Ziffern ohne Tausenderpunkt schreiben (1971, 2026), Beträge und Mengen mit Tausenderpunkt (1.971 Rupien). Keine URLs, keine Klammern, keine Abkürzungen mit Punkt (statt „z. B.“ → „zum Beispiel“).
- "stichpunkte": Liste mit 2–4 Stichpunkten für die Folie, die den GANZEN Text zusammenfassen. Je höchstens 70 Zeichen, ohne Punkt am Ende, Ziffern statt ausgeschriebener Zahlen (z. B. "Rs 400.000 Drogen in Quatre-Bornes sichergestellt"). Kein Rückblick, der steht separat auf der Folie.
Ältere Updates behalten ihr "sendung"-Feld unverändert. Fehlt es dort, wird es nicht nachgetragen.

ORT FÜR DIE KARTE (Sendung und Website zeigen ein Insel-Piktogramm mit Nadel)
- Setze beim Thema "ort", wenn die Meldung an einem bestimmten Ort spielt. Verwende dafür die Schreibweise aus lib/zeitung/orte.json (z. B. "Port-Louis", "Quatre-Bornes", "Port Mathurin", "Saint-Denis"), bei Meldungen zu einer ganzen Insel nur "Mauritius", "Rodrigues" oder "La Réunion".
- Ist der Ort nicht in dieser Liste, setze zusätzlich "koordinaten": {"insel": "mauritius" | "rodrigues" | "reunion", "lat": …, "lon": …} – nur wenn du die Lage sicher kennst, sonst weglassen.
- Landesweite Themen ohne bestimmten Ort bekommen kein "ort".

GRAFIK (Diagramm in Sendung und Website)
Enthält eine Meldung vergleichbare Zahlen (z. B. Füllstand heute, vor einem Jahr, Durchschnitt; Preise vorher/nachher; Ergebnisse mehrerer Wahlkreise), bekommt das NEUE Update zusätzlich "grafik":
{ "art": "balken",
  "einheit": "%" oder {"de": "Mio. m³", "fr": "millions de m³", "en": "million m³"},
  "titel": {"de", "fr", "en"},                         // kurz, z. B. „Füllstand der Reservoirs“
  "kennzahl": {"wert": {"de": "44 %", "fr": "44 %", "en": "44%"}, "text": {"de", "fr", "en"}},   // optional, die wichtigste Zahl
  "werte": [ {"wert": 44, "hervor": true, "label": {"de", "fr", "en"}}, {"wert": 55.2, "label": {…}}, … ],   // 2–5 Balken, Zahlen ohne Einheit
  "max": 100,                                         // optional, Skalenende
  "quelle": "CWA" }                                   // wer die Zahlen veröffentlicht hat
Regeln: Nur Zahlen, die so in der Quelle stehen – nichts schätzen, umrechnen oder ergänzen. Alle Balken in derselben Einheit. Genau ein Balken "hervor": true (der aktuelle bzw. wichtigste Wert). Keine Grafik, wenn weniger als zwei vergleichbare Werte vorliegen. Die Stichpunkte wiederholen die Zahlen der Grafik nicht, sondern ergänzen sie.
