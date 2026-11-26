import { NextResponse } from 'next/server';

import { BrevoFehler, starteAnmeldung } from '@/lib/newsletter/brevo';
import { istHaeufigkeit, newsletterBereit, newsletterGeheimnis } from '@/lib/newsletter/konfiguration';
import { einstellungsLink, istEmail } from '@/lib/newsletter/token';
import { SEITEN_URL } from '@/lib/zeitung/seite';
import { istSprache } from '@/lib/zeitung/sprache';

/** Newsletter-Anmeldung: startet das Double-Opt-in bei Brevo. */
export async function POST(anfrage: Request): Promise<NextResponse> {
  const geheimnis = newsletterGeheimnis();
  if (!newsletterBereit() || !geheimnis) return NextResponse.json({ fehler: 'nicht_bereit' }, { status: 503 });

  let roh: unknown;
  try {
    roh = await anfrage.json();
  } catch {
    return NextResponse.json({ fehler: 'ungueltig' }, { status: 400 });
  }
  if (typeof roh !== 'object' || roh === null) return NextResponse.json({ fehler: 'ungueltig' }, { status: 400 });
  const d = roh as Record<string, unknown>;

  // Verstecktes Feld: von Menschen leer gelassen, von Bots oft ausgefüllt.
  if (typeof d.website === 'string' && d.website !== '') return NextResponse.json({ ok: true });

  const haeufigkeit = Number(d.haeufigkeit);
  if (!istEmail(d.email) || !istHaeufigkeit(haeufigkeit) || !istSprache(d.sprache) || d.einwilligung !== true) {
    return NextResponse.json({ fehler: 'ungueltig' }, { status: 400 });
  }

  try {
    await starteAnmeldung({
      email: d.email,
      sprache: d.sprache,
      haeufigkeit,
      shop: d.shop === true,
      einstellungsLink: einstellungsLink(d.email, geheimnis),
      bestaetigtUrl: `${SEITEN_URL}/newsletter/bestaetigt`,
    });
    return NextResponse.json({ ok: true });
  } catch (fehler) {
    console.error('Newsletter-Anmeldung fehlgeschlagen', fehler instanceof BrevoFehler ? fehler.message : fehler);
    return NextResponse.json({ fehler: 'dienst' }, { status: 502 });
  }
}
