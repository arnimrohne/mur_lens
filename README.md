# MUR Lens

Mauritius-Preise sofort in Euro umrechnen.

Die App öffnet die Rückkamera, erkennt Preisschilder per OCR und zeigt den Eurobetrag in Echtzeit — vollständig lokal im Browser, ohne Cloud, ohne Backend.

## Tech Stack

- Next.js 15 · React 19 · TypeScript (strict)
- Tailwind CSS · PWA
- Tesseract.js (OCR, ab Sprint 2)

## Entwicklung

```bash
npm install
npm run dev
```

## Qualitätsprüfung

```bash
npm run lint
npm run build
```

## Architekturprinzipien

- Mobile First · Offline First · Privacy First
- Business-Logik ausschließlich in `lib/` und `hooks/`
- Keine Bilder verlassen das Gerät
