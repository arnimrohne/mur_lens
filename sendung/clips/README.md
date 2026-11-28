# Moderations-Clips (Begrüßung und Abschied)

Liegen hier Clips, ersetzen sie in der Sendung die Begrüßungs- und die Abschiedsfolie.
Fehlt ein Clip, bleibt es bei der Folie. Jeder Clip wird bei allen Sendungen wiederverwendet.

| Datei | Inhalt |
|---|---|
| `de-begruessung.mp4`, `de-abschied.mp4` | Deutsch (Stimme Thorsten, männlich) |
| `fr-begruessung.mp4`, `fr-abschied.mp4` | Französisch (Stimme SIWIS, weiblich) |
| `en-begruessung.mp4`, `en-abschied.mp4` | Englisch (Stimme Cori, weiblich) |

- **Format:** Querformat 16:9, bevorzugt 1920×1080, sonst wird zugeschnitten und skaliert. `.mov` und `.webm` gehen auch.
- **Ton:** Die Tonspur des Clips wird übernommen. Hat der Clip keinen Ton, wird der Text der Begrüßung bzw. Verabschiedung mit Piper gesprochen.
- **Einblendungen:** Darüber legt die Sendung automatisch die Bauchbinde (Sendung und Datum bzw. Adresse) und oben rechts den Hinweis „KI-Moderation“.
- **Beschreibung:** In der YouTube-Beschreibung steht automatisch, dass die Moderation KI-generiert ist.
- **Ohne Wasserzeichen und Fremdlogos:** Die Clips müssen frei davon sein, und es braucht das Recht zur kommerziellen Nutzung.

## So sind die aktuellen Clips entstanden (28.11.2026, Kling)
- **Porträts:** RealVisXL V4.0 (SDXL, Lizenz OpenRAIL++) mit den Prompts aus `vorschlaege.md`, Richtung A (Studio), jeweils Variante 1. Die französische und die englische Sprecherin sind per SDXL-Inpainting (Maske nur um die Person) in das deutsche Studiobild `de-A-1` gesetzt, damit alle drei Sprachen denselben Hintergrund haben. Die Standbilder liegen als `<sprache>-sprecher.jpg` hier im Ordner und werden auch für das YouTube-Vorschaubild genutzt.
- **Animation:** Kling AI, Modell Kling 4.0 „Omni-Ref“ (1080p, 16:9, mit Ton), Eingaben: Standbild als `图片1` und die Tonspur als `音频1`. Kosten: 15 Credits pro Sekunde.
- **Wichtig beim Prompt:** Der genaue Wortlaut der Tonspur muss im Prompt stehen, dazu „Use 音频1 unchanged as the soundtrack … no other words“ und „exactly the framing of 图片1 (no desk …)“. Ohne Wortlaut erfindet Kling eigene Sätze und ignoriert die Tonspur; ohne Bildausschnitt setzt es die Person auch mal an ein Pult. Jeden Clip danach per Transkription mit der Tonspur vergleichen.
- **Ton:** `ton/<sprache>-<art>.wav`, gesprochen mit den Piper-Stimmen der Sendung. Vor dem Sprechen ist 0,6–0,8 s Ruhe eingefügt, danach 1,0–1,4 s.
- **Lizenz:** Die Clips sind mit einer bezahlten Kling-Mitgliedschaft erzeugt, die kommerzielle Nutzung erlaubt. Die frühere SadTalker-Fassung (Basel-Face-Model-Grauzone) ist damit ersetzt. Wer die Clips wieder entfernen will, löscht die `*.mp4` in diesem Ordner, dann erscheinen wieder die Folien.
