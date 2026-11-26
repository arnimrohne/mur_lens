import { timingSafeEqual } from 'node:crypto';

import { NextResponse } from 'next/server';

import { versendeKampagne } from '@/lib/newsletter/brevo';
import { istVersandzeit, newsletterBereit, newsletterGeheimnis } from '@/lib/newsletter/konfiguration';
import { baueMail } from '@/lib/newsletter/mail';
import { ladeZeitung } from '@/lib/zeitung/lade-daten';
import { ladeWetter } from '@/lib/zeitung/lade-wetter';

export const dynamic = 'force-dynamic';

function berechtigt(anfrage: Request, geheimnis: string): boolean {
  const kopf = anfrage.headers.get('authorization') ?? '';
  const erhalten = Buffer.from(kopf.replace(/^Bearer\s+/i, ''));
  const erwartet = Buffer.from(geheimnis);
  return erhalten.length === erwartet.length && timingSafeEqual(erhalten, erwartet);
}

/**
 * Verschickt die Ausgabe einer Versandzeit (?zeit=morgen|mittag|abend).
 * Wird vom Zeitplan in .github/workflows/newsletter.yml aufgerufen.
 */
export async function POST(anfrage: Request): Promise<NextResponse> {
  const geheimnis = newsletterGeheimnis();
  if (!geheimnis || !berechtigt(anfrage, geheimnis)) return NextResponse.json({ fehler: 'nicht_berechtigt' }, { status: 401 });
  if (!newsletterBereit()) return NextResponse.json({ fehler: 'nicht_bereit' }, { status: 503 });

  const zeit = new URL(anfrage.url).searchParams.get('zeit');
  if (!istVersandzeit(zeit)) return NextResponse.json({ fehler: 'zeit' }, { status: 400 });

  const jetzt = Date.now();
  const [daten, wetter] = await Promise.all([ladeZeitung(), ladeWetter()]);
  const mail = baueMail(daten, wetter, zeit, jetzt);
  if (!mail) return NextResponse.json({ verschickt: false, grund: 'keine neuen Meldungen' });

  try {
    const name = `Gazet Morisyen ${new Date(jetzt).toISOString().slice(0, 16)} ${zeit}`;
    const kampagne = await versendeKampagne(zeit, mail.betreff, mail.html, name);
    return NextResponse.json({ verschickt: true, kampagne, themen: mail.anzahlThemen });
  } catch (fehler) {
    console.error('Newsletter-Versand fehlgeschlagen', fehler instanceof Error ? fehler.message : fehler);
    return NextResponse.json({ fehler: 'dienst' }, { status: 502 });
  }
}
