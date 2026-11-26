/**
 * Newsletter-Vorgänge bei Brevo: Anmeldung, Einstellungen, Versand.
 * Listen und Bestätigungsvorlage werden über ihre Namen gefunden (einrichtung.ts).
 */

import { brevo, BrevoFehler } from './brevo-api';
import { ladeBrevoKonfig } from './einrichtung';
import type { BrevoKonfig } from './einrichtung';
import { ABSENDER, ALLE_VERSANDZEITEN, VERSANDZEITEN_FUER } from './konfiguration';
import type { Haeufigkeit, Versandzeit } from './konfiguration';
import { normalisiereEmail } from './token';
import type { Sprache } from '@/lib/zeitung/types';

export { BrevoFehler };

async function konfig(): Promise<BrevoKonfig> {
  const k = await ladeBrevoKonfig();
  if (!k) throw new BrevoFehler(503, 'Brevo ist noch nicht eingerichtet (Listen oder Vorlage fehlen)');
  return k;
}

function listenFuer(k: BrevoKonfig, haeufigkeit: Haeufigkeit): { rein: number[]; raus: number[] } {
  const zeiten = VERSANDZEITEN_FUER[haeufigkeit];
  return {
    rein: zeiten.map((zeit) => k.listen[zeit]),
    raus: ALLE_VERSANDZEITEN.filter((zeit) => !zeiten.includes(zeit)).map((zeit) => k.listen[zeit]),
  };
}

export interface Anmeldung {
  email: string;
  sprache: Sprache;
  haeufigkeit: Haeufigkeit;
  shop: boolean;
  einstellungsLink: string;
  bestaetigtUrl: string;
}

/** Startet das Double-Opt-in: Brevo schickt die Bestätigungsmail. */
export async function starteAnmeldung(a: Anmeldung): Promise<void> {
  const k = await konfig();
  await brevo('/contacts/doubleOptinConfirmation', 'POST', {
    email: normalisiereEmail(a.email),
    includeListIds: listenFuer(k, a.haeufigkeit).rein,
    templateId: k.doiVorlage,
    redirectionUrl: a.bestaetigtUrl,
    attributes: {
      SPRACHE: a.sprache,
      HAEUFIGKEIT: String(a.haeufigkeit),
      SHOP: a.shop ? 'ja' : 'nein',
      EINSTELLUNGEN: a.einstellungsLink,
    },
  });
}

/** Ändert Häufigkeit, Sprache und Shop-Einwilligung eines bestätigten Kontakts. */
export async function aendereEinstellungen(
  email: string,
  e: { haeufigkeit: Haeufigkeit; sprache: Sprache; shop: boolean },
): Promise<void> {
  const { rein, raus } = listenFuer(await konfig(), e.haeufigkeit);
  await brevo(`/contacts/${encodeURIComponent(normalisiereEmail(email))}`, 'PUT', {
    attributes: { HAEUFIGKEIT: String(e.haeufigkeit), SPRACHE: e.sprache, SHOP: e.shop ? 'ja' : 'nein' },
    listIds: rein,
    unlinkListIds: raus,
  });
}

/** Legt eine Kampagne für die Liste einer Versandzeit an und verschickt sie sofort. */
export async function versendeKampagne(zeit: Versandzeit, betreff: string, html: string, name: string): Promise<number> {
  const k = await konfig();
  const ergebnis = await brevo('/emailCampaigns', 'POST', {
    name,
    subject: betreff,
    sender: ABSENDER,
    htmlContent: html,
    recipients: { listIds: [k.listen[zeit]] },
  });
  const id = typeof ergebnis === 'object' && ergebnis !== null && 'id' in ergebnis ? Number(ergebnis.id) : NaN;
  if (!Number.isFinite(id)) throw new BrevoFehler(502, 'Brevo lieferte keine Kampagnen-ID');
  await brevo(`/emailCampaigns/${id}/sendNow`, 'POST');
  return id;
}

/**
 * Schickt eine Ausgabe als einzelne Testmail an eine Adresse (ohne Liste).
 * Ohne Kontakt-Daten zeigt Brevo den deutschen Block; Abmelde- und
 * Einstellungslink sind in der Testmail leer.
 */
export async function versendeTestmail(adresse: string, betreff: string, html: string): Promise<void> {
  await brevo('/smtp/email', 'POST', {
    sender: ABSENDER,
    to: [{ email: normalisiereEmail(adresse) }],
    subject: betreff,
    htmlContent: html,
  });
}
