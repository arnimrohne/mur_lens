# Ergänzung für die Redaktion: Dossiers

Dossiers sind Hintergrund-Seiten zu Themen, die immer wiederkehren
(`dossiers.json` auf dem Branch `zeitung-daten`). Die Redaktion schreibt sie
**nicht** selbst. Sie macht zwei Dinge:

## 1. Meldungen einem Dossier zuordnen

Gehört ein Thema in `daten.json` zu einem bestehenden Dossier, setzt die Redaktion
`"dossier": "<dossier-id>"` am Thema. Die vorhandenen IDs stehen in `dossiers.json`.
Ohne passendes Dossier bleibt das Feld weg. Die Website zeigt dann unter der
Meldung den Link „Hintergrund: …“.

## 2. Neue Dossiers vorschlagen

Ein Dossier lohnt sich, wenn mindestens eines davon zutrifft:

- **Häufung:** Das Thema war in den letzten 30 Tagen mindestens dreimal in der
  Zeitung oder bleibt absehbar länger aktuell (Wasser, Energie, Preise, Drogen, Chagos).
- **Wiederkehr:** Das Thema kommt jedes Jahr oder alle zwei Jahre wieder. Ein
  Beispiel ist der Haushalt mit Budget-Rede, Lohnausgleich (Salary Compensation)
  und Mindestlohn. Weitere sind der PRB-Bericht, die Zyklon-Saison, Dürre und
  Wasserrationierung, die Zuckerrohrernte, Prüfungsergebnisse (SC/HSC, Laureates),
  Kommunal- und Dorfratswahlen sowie Fest- und Feiertage mit großer
  Bedeutung (Maha Shivaratri, Nationalfeiertag). Hier genügt **eine** Meldung,
  wenn aus der Quelle oder aus Allgemeinwissen klar ist, dass das Thema regelmäßig
  wiederkehrt. Im `grund` steht dann der Rhythmus, z. B. „jährlich im Juni (Budget)“.

Ein einmaliges Ereignis ohne Vorgeschichte und ohne Wiederkehr bekommt kein
Dossier. Für einen passenden Fall trägt die Redaktion in `dossiers.json` unter
`vorschlaege` ein:

```json
{ "id": "energie-ceb", "titel": "Strom und CEB", "rubrik": "wirtschaft",
  "grund": "Stromausfälle und Tarifdebatte, 4 Meldungen seit 2.11.",
  "themen": ["ceb-tarif", "stromausfall-port-louis"],
  "rhythmus": null, "vorgeschlagen": "2026-11-27T08:00:00Z" }
```

`rhythmus` ist `"jaehrlich"`, `"zweijaehrlich"` oder `null`. Schon vorhandene IDs werden nicht erneut vorgeschlagen. Pro Lauf gibt es höchstens
einen Vorschlag. Die Ausarbeitung übernimmt der Dossier-Recherche-Lauf; er nimmt
den Vorschlag danach aus der Liste.

Startliste (bei passender Meldung vorschlagen, sofern noch nicht vorhanden):
`wasserversorgung` (vorhanden), `lohnausgleich`, `tourismus`, `strassenbau-verkehr`,
`inflation-rupie`, `energie-ceb`, `jugendkriminalitaet-drogen`, `chagos`.
