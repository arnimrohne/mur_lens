import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

import { SEITEN_HOST } from '@/lib/zeitung/seite';

const ZEITUNG_PFAD = '/zeitung';

/**
 * Auf gazet.morisyen.de wird direkt die Zeitung ausgeliefert:
 *   /             → /zeitung
 *   /impressum    → /zeitung/impressum
 *   /robots.txt   → /zeitung/robots.txt
 * Aufrufe von /zeitung/… werden auf die kurze Adresse umgeleitet.
 * Alle anderen Hosts (MUR Lens) bleiben unverändert.
 */
export function middleware(anfrage: NextRequest): NextResponse {
  const host = (anfrage.headers.get('host') ?? '').split(':')[0].toLowerCase();
  if (host !== SEITEN_HOST) return NextResponse.next();

  const { pathname } = anfrage.nextUrl;

  // Icons der Zeitung (Dodo) direkt ausliefern, nicht auf die Wurzel umleiten.
  if (/^\/zeitung\/(icon|apple-icon)/.test(pathname)) return NextResponse.next();

  if (pathname === ZEITUNG_PFAD || pathname.startsWith(`${ZEITUNG_PFAD}/`)) {
    const ziel = anfrage.nextUrl.clone();
    ziel.pathname = pathname.slice(ZEITUNG_PFAD.length) || '/';
    return NextResponse.redirect(ziel, 308);
  }

  const ziel = anfrage.nextUrl.clone();
  ziel.pathname = pathname === '/' ? ZEITUNG_PFAD : `${ZEITUNG_PFAD}${pathname}`;
  return NextResponse.rewrite(ziel);
}

export const config = {
  // Next.js-Interna, API-Routen und App-Dateien auslassen.
  matcher: ['/((?!_next/|api/|favicon\\.ico|icon|apple-icon|manifest\\.json|icons/|bilder/).*)'],
};
