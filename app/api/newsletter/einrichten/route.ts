import { NextResponse } from 'next/server';

import { mitGeheimnisBerechtigt } from '@/lib/newsletter/berechtigung';
import { richteBrevoEin } from '@/lib/newsletter/einrichtung';
import { brevoVerbunden, newsletterGeheimnis } from '@/lib/newsletter/konfiguration';

export const dynamic = 'force-dynamic';

/**
 * Legt in Brevo Kontaktfelder, Listen und die Bestätigungsvorlage an (idempotent).
 * Aufruf über den GitHub-Workflow „Newsletter einrichten“.
 */
export async function POST(anfrage: Request): Promise<NextResponse> {
  const geheimnis = newsletterGeheimnis();
  if (!geheimnis || !mitGeheimnisBerechtigt(anfrage, geheimnis)) {
    return NextResponse.json({ fehler: 'nicht_berechtigt' }, { status: 401 });
  }
  if (!brevoVerbunden()) return NextResponse.json({ fehler: 'BREVO_API_KEY fehlt in Vercel' }, { status: 503 });
  try {
    const konfig = await richteBrevoEin();
    return NextResponse.json({ ok: true, ...konfig });
  } catch (fehler) {
    const nachricht = fehler instanceof Error ? fehler.message : String(fehler);
    console.error('Brevo-Einrichtung fehlgeschlagen', nachricht);
    return NextResponse.json({ fehler: nachricht }, { status: 502 });
  }
}
