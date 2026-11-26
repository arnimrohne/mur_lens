/**
 * Zugriff auf die Brevo-API (https://developers.brevo.com).
 * Nur serverseitig verwenden; der API-Schlüssel kommt aus BREVO_API_KEY.
 */

import {
  ABSENDER,
  ALLE_VERSANDZEITEN,
  BREVO_DOI_VORLAGE,
  BREVO_LISTEN,
  VERSANDZEITEN_FUER,
  brevoSchluessel,
} from './konfiguration';
import type { Haeufigkeit, Versandzeit } from './konfiguration';
import { normalisiereEmail } from './token';
import type { Sprache } from '@/lib/zeitung/types';

const BASIS = 'https://api.brevo.com/v3';

export class BrevoFehler extends Error {
  constructor(public readonly status: number, nachricht: string) {
    super(nachricht);
  }
}

async function brevo(pfad: string, methode: 'GET' | 'POST' | 'PUT', koerper?: unknown): Promise<unknown> {
  const schluessel = brevoSchluessel();
  if (!schluessel) throw new BrevoFehler(503, 'BREVO_API_KEY fehlt');
  const antwort = await fetch(`${BASIS}${pfad}`, {
    method: methode,
    headers: { 'api-key': schluessel, 'content-type': 'application/json', accept: 'application/json' },
    body: koerper === undefined ? undefined : JSON.stringify(koerper),
    cache: 'no-store',
  });
  const text = await antwort.text();
  if (!antwort.ok) throw new BrevoFehler(antwort.status, `Brevo ${methode} ${pfad}: HTTP ${antwort.status} ${text.slice(0, 300)}`);
  return text ? (JSON.parse(text) as unknown) : undefined;
}

function listenFuer(haeufigkeit: Haeufigkeit): { rein: number[]; raus: number[] } {
  const zeiten = VERSANDZEITEN_FUER[haeufigkeit];
  return {
    rein: zeiten.map((zeit) => BREVO_LISTEN[zeit]),
    raus: ALLE_VERSANDZEITEN.filter((zeit) => !zeiten.includes(zeit)).map((zeit) => BREVO_LISTEN[zeit]),
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
  await brevo('/contacts/doubleOptinConfirmation', 'POST', {
    email: normalisiereEmail(a.email),
    includeListIds: listenFuer(a.haeufigkeit).rein,
    templateId: BREVO_DOI_VORLAGE,
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
  const { rein, raus } = listenFuer(e.haeufigkeit);
  await brevo(`/contacts/${encodeURIComponent(normalisiereEmail(email))}`, 'PUT', {
    attributes: { HAEUFIGKEIT: String(e.haeufigkeit), SPRACHE: e.sprache, SHOP: e.shop ? 'ja' : 'nein' },
    listIds: rein,
    unlinkListIds: raus,
  });
}

/** Legt eine Kampagne für die Liste einer Versandzeit an und verschickt sie sofort. */
export async function versendeKampagne(zeit: Versandzeit, betreff: string, html: string, name: string): Promise<number> {
  const ergebnis = await brevo('/emailCampaigns', 'POST', {
    name,
    subject: betreff,
    sender: ABSENDER,
    htmlContent: html,
    recipients: { listIds: [BREVO_LISTEN[zeit]] },
  });
  const id = typeof ergebnis === 'object' && ergebnis !== null && 'id' in ergebnis ? Number(ergebnis.id) : NaN;
  if (!Number.isFinite(id)) throw new BrevoFehler(502, 'Brevo lieferte keine Kampagnen-ID');
  await brevo(`/emailCampaigns/${id}/sendNow`, 'POST');
  return id;
}
