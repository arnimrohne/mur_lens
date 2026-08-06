# MUR Lens

Mauritius-Preise sofort in Euro umrechnen.

Die App öffnet die Rückkamera, erkennt Preisschilder und zeigt den Eurobetrag in Echtzeit — vollständig lokal im Browser, ohne Cloud, ohne Backend.

## Tech Stack

- Next.js 15 · React 19 · TypeScript (strict)
- Tailwind CSS · PWA
- Tesseract.js (Texterkennung, ab Sprint 2)

---

## Lokale Entwicklung

**Voraussetzung:** Node.js 20 oder neuer

```bash
# Abhängigkeiten installieren
npm install

# Entwicklungsserver starten
npm run dev
# → http://localhost:3000
```

> **Kamerazugriff auf `localhost`:** Moderne Browser erlauben `getUserMedia` auf
> `localhost` ohne HTTPS. Für Tests auf einem anderen Gerät im lokalen Netz
> (z. B. Smartphone):
>
> ```bash
> npm run dev -- --experimental-https
> ```

### Qualitätsprüfung

```bash
npm run lint    # ESLint
npm run build   # TypeScript + Produktions-Build
```

Beide Befehle müssen fehlerfrei durchlaufen, bevor ein Commit erstellt wird.

---

## Deployment

Das Projekt ist ohne zusätzliche Konfiguration auf Vercel deploybar.
Vercel stellt automatisch HTTPS bereit — Voraussetzung für den Kamerazugriff auf Mobilgeräten.

### Erstmalig über GitHub → Vercel

1. Repository auf GitHub pushen (z. B. `main`-Branch)
2. [vercel.com/new](https://vercel.com/new) aufrufen und einloggen
3. GitHub-Repository auswählen
4. Vercel erkennt Next.js automatisch — **keine weitere Konfiguration nötig**
5. „Deploy" klicken

### Automatisches Deployment (nach dem ersten Setup)

| Ereignis | Ergebnis |
|---|---|
| Push auf `main` | Produktions-Deployment |
| Push auf anderen Branch | Preview-Deployment mit eigener URL |
| Pull Request geöffnet | Preview-Deployment, URL erscheint im PR |

### Umgebungsvariablen

Keine — die App läuft vollständig im Browser ohne Backend oder externe APIs.

### Build-Einstellungen auf Vercel

Vercel erkennt Next.js automatisch. Die Standardeinstellungen sind korrekt:

| Einstellung | Wert |
|---|---|
| Framework | Next.js (auto-detect) |
| Build Command | `npm run build` |
| Output Directory | `.next` (auto) |
| Node.js Version | 20.x (via `.nvmrc`) |

---

## Architekturprinzipien

- Mobile First · Offline First · Privacy First
- Business-Logik und Recognition-Foundation ausschließlich in `lib/`
- Keine Bilder verlassen das Gerät
- Kein Backend · Keine Datenbank · Keine Cloud
