import { NextResponse } from 'next/server';

import { BrevoFehler, aendereEinstellungen } from '@/lib/newsletter/brevo';
import { istHaeufigkeit, newsletterBereit, newsletterGeheimnis } from '@/lib/newsletter/konfiguration';
import { emailAusLink, tokenGueltig } from '@/lib/newsletter/token';
import { istSprache } from '@/lib/zeitung/sprache';

/** Ändert Häufigkeit, Sprache und Shop-Einwilligung über den signierten Link aus der Mail. */
export async function POST(anfrage: Request): Promise<NextResponse> {
  const geheimnis = newsletterGeheimnis();
  if (!newsletterBereit() || !geheimnis) return NextResponse.json({ fehler: 'nicht_bereit' }, { status: 503 });

  let d: Record<string, unknown>;
  try {
    const roh: unknown = await anfrage.json();
    if (typeof roh !== 'object' || roh === null) throw new Error('kein Objekt');
    d = roh as Record<string, unknown>;
  } catch {
    return NextResponse.json({ fehler: 'ungueltig' }, { status: 400 });
  }

  const email = typeof d.e === 'string' ? emailAusLink(d.e) : undefined;
  if (!email || typeof d.t !== 'string' || !tokenGueltig(email, d.t, geheimnis)) {
    return NextResponse.json({ fehler: 'link' }, { status: 403 });
  }
  const haeufigkeit = Number(d.haeufigkeit);
  if (!istHaeufigkeit(haeufigkeit) || !istSprache(d.sprache)) {
    return NextResponse.json({ fehler: 'ungueltig' }, { status: 400 });
  }

  try {
    await aendereEinstellungen(email, { haeufigkeit, sprache: d.sprache, shop: d.shop === true });
    return NextResponse.json({ ok: true });
  } catch (fehler) {
    const status = fehler instanceof BrevoFehler && fehler.status === 404 ? 404 : 502;
    console.error('Newsletter-Einstellungen fehlgeschlagen', fehler instanceof Error ? fehler.message : fehler);
    return NextResponse.json({ fehler: status === 404 ? 'unbekannt' : 'dienst' }, { status });
  }
}
