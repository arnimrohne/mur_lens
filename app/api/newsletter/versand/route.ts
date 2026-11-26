import { NextResponse } from 'next/server';

import { mitGeheimnisBerechtigt } from '@/lib/newsletter/berechtigung';
import { versendeKampagne, versendeTestmail } from '@/lib/newsletter/brevo';
import { brevoVerbunden, istVersandzeit, newsletterBereit, newsletterGeheimnis } from '@/lib/newsletter/konfiguration';
import { baueMail } from '@/lib/newsletter/mail';
import { istEmail } from '@/lib/newsletter/token';
import { ladeZeitung } from '@/lib/zeitung/lade-daten';
import { ladeWetter } from '@/lib/zeitung/lade-wetter';

export const dynamic = 'force-dynamic';

/**
 * Verschickt die Ausgabe einer Versandzeit (?zeit=morgen|mittag|abend).
 * Mit ?test=adresse geht sie nur als Test an diese Adresse (auch vor dem Start).
 * Aufruf über .github/workflows/newsletter.yml bzw. newsletter-einrichten.yml.
 */
export async function POST(anfrage: Request): Promise<NextResponse> {
  const geheimnis = newsletterGeheimnis();
  if (!geheimnis || !mitGeheimnisBerechtigt(anfrage, geheimnis)) {
    return NextResponse.json({ fehler: 'nicht_berechtigt' }, { status: 401 });
  }
  const parameter = new URL(anfrage.url).searchParams;
  const zeit = parameter.get('zeit') ?? 'morgen';
  const test = parameter.get('test') ?? undefined;
  if (!istVersandzeit(zeit)) return NextResponse.json({ fehler: 'zeit' }, { status: 400 });
  if (test !== undefined && !istEmail(test)) return NextResponse.json({ fehler: 'testadresse' }, { status: 400 });
  if (test ? !brevoVerbunden() : !newsletterBereit()) {
    return NextResponse.json({ fehler: 'nicht_bereit (Brevo-Schlüssel, Geheimnis oder Impressum fehlt)' }, { status: 503 });
  }

  const jetzt = Date.now();
  const [daten, wetter] = await Promise.all([ladeZeitung(), ladeWetter()]);
  const mail = baueMail(daten, wetter, test ? 'morgen' : zeit, jetzt);
  if (!mail) return NextResponse.json({ verschickt: false, grund: 'keine neuen Meldungen' });

  try {
    if (test) {
      await versendeTestmail(test, `[Test] ${mail.betreff}`, mail.html);
      return NextResponse.json({ verschickt: true, test: true, themen: mail.anzahlThemen });
    }
    const name = `Gazet Morisyen ${new Date(jetzt).toISOString().slice(0, 16)} ${zeit}`;
    const kampagne = await versendeKampagne(zeit, mail.betreff, mail.html, name);
    return NextResponse.json({ verschickt: true, kampagne, themen: mail.anzahlThemen });
  } catch (fehler) {
    const nachricht = fehler instanceof Error ? fehler.message : String(fehler);
    console.error('Newsletter-Versand fehlgeschlagen', nachricht);
    return NextResponse.json({ fehler: nachricht }, { status: 502 });
  }
}
