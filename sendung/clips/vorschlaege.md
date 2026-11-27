# Vorschläge: Sprecher und Hintergründe für die Moderations-Clips

Für jede Sprache gibt es eine Person, passend zur Stimme der Sendung:
- **DE:** männlich (Thorsten)
- **FR:** weiblich (SIWIS)
- **EN:** weiblich (Cori)

Die drei Personen spiegeln die Vielfalt von Mauritius wider. Sie sind KI-generiert, keine realen Personen. Jede Person bekommt zwei Szenen, **Begrüßung** und **Abschied**, im selben Look. In Higgsfield sollte die Person dafür als feste Figur gespeichert werden (Character/Soul-ID), damit sie in beiden Szenen gleich aussieht.

## Hausfarben (für Kleidung und Licht)
- Navy `#0D203E` (Grundfarbe der Folien)
- Lagunengrün `#0F6E5C`
- Rot `#C8323C`
- Sandbeige `#FDFAF5`

## Bildaufbau (gilt für alle Szenen)
- 16:9, 1920×1080, Kamera auf Augenhöhe, ruhige Kamera ohne Zoom.
- Die Person steht leicht rechts der Mitte. **Unten links bleibt Platz** für die Bauchbinde (ca. 40 % Breite, untere 25 %), **oben rechts** für den Hinweis „KI-Moderation“.
- Kein Text, keine Logos und keine Bildschirme mit lesbarer Schrift im Bild; die Einblendungen kommen von der Sendung.
- Vor und nach dem Sprechen jeweils ca. 0,5 s ruhiger Blick in die Kamera.

## Die drei Personen

| | DE | FR | EN |
|---|---|---|---|
| Typ | Mann, ca. 40, indo-mauritisch | Frau, ca. 35, kreolisch-mauritisch | Frau, ca. 30, sino-mauritisch |
| Haare | kurz, dunkel, gepflegter kurzer Bart | natürliche Locken, locker zurückgebunden | schulterlang, glatt, dunkel |
| Kleidung | navyblaues Sakko, hellblaues Hemd, ohne Krawatte | Bluse in Lagunengrün, kleine Ohrringe | cremefarbener Blazer, schlichtes Shirt |
| Ausstrahlung | ruhig, seriös, freundlich | warm, zugewandt | klar, sachlich, offen |

Prompts (Englisch, für Higgsfield):

- **DE:** `Photorealistic male news presenter, around 40, Indo-Mauritian, short dark hair, neatly trimmed short beard, navy blue blazer over light blue open-collar shirt, calm and friendly expression, looking directly into the camera, natural skin texture`
- **FR:** `Photorealistic female news presenter, around 35, Mauritian Creole, natural curly hair loosely tied back, teal-green blouse, small earrings, warm and approachable expression, looking directly into the camera, natural skin texture`
- **EN:** `Photorealistic female news presenter, around 30, Sino-Mauritian, shoulder-length straight dark hair, cream blazer over simple top, clear and open expression, looking directly into the camera, natural skin texture`

## Hintergründe: drei Richtungen zur Auswahl

### A „Studio Port-Louis“ (seriös, klassisch)
Modernes Nachrichtenstudio in Navy und Holz. Durch ein großes Fenster sieht man unscharf die Skyline von Port-Louis und den Hafen.
- **Begrüßung:** Halbnah, hinten Abendlicht mit Hafenlichtern.
- **Abschied:** Etwas weiter, die Person nickt leicht und lächelt, das Licht ist eine Spur wärmer.
- Prompt-Zusatz: `modern TV news studio, navy blue and warm wood tones, large window behind with softly blurred Port Louis harbour skyline at dusk, shallow depth of field, soft key light, 16:9, medium shot, presenter slightly right of centre, empty space lower left`

### B „Terrasse über der Stadt“ (nahbar, Tageslicht)
Die Person steht auf einer Dachterrasse. Hinten unscharf die Stadt mit den Bergen der Moka-Kette (Le Pouce), dazu Tageslicht mit leichter Brise.
- **Begrüßung:** Morgenlicht, klarer Himmel.
- **Abschied:** Später Nachmittag, goldenes Licht.
- Prompt-Zusatz: `rooftop terrace, softly blurred view of Port Louis and the Moka mountain range with Le Pouce peak, natural daylight, light breeze, shallow depth of field, 16:9, medium shot, presenter slightly right of centre, empty space lower left`

### C „Lagune“ (magazinig, Inselgefühl)
Die Person steht im Schatten unter Filao-Bäumen. Hinten unscharf die türkise Lagune, das Riff und am Horizont Le Morne.
- **Begrüßung:** Vormittag.
- **Abschied:** Sonnenuntergang.
- Wirkt weniger nach Nachrichten und eher touristisch.
- Prompt-Zusatz: `shaded beach under casuarina trees, softly blurred turquoise lagoon and reef, Le Morne mountain on the horizon, soft natural light, shallow depth of field, 16:9, medium shot, presenter slightly right of centre, empty space lower left`

**Empfehlung:** A für alle drei Sprachen. Es passt am besten zum Nachrichten-Look der Folien (Navy) und wirkt glaubwürdig. B wäre die freundlichere Alternative. Wichtig ist, dass alle drei Sprachen dieselbe Richtung bekommen.

## Ablauf in Higgsfield
1. Pro Sprache ein Porträt mit Person-Prompt und Hintergrund-Zusatz erzeugen, 2–3 Varianten.
2. Die gewählte Variante als feste Figur speichern.
3. Szene „Begrüßung“ und Szene „Abschied“ mit Lippensync und der passenden Ton-Datei aus `ton/` erzeugen (`ton/de-begruessung.wav` usw., gesprochen mit den Sendungsstimmen).
4. Exportieren als `de-begruessung.mp4`, `de-abschied.mp4` usw. in diesen Ordner. Ohne Wasserzeichen; die Lizenz für kommerzielle Nutzung muss geklärt sein.
