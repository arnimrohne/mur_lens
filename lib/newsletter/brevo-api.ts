/**
 * Schlanker Zugriff auf die Brevo-REST-API (https://developers.brevo.com).
 * Nur serverseitig verwenden; der API-Schlüssel kommt aus BREVO_API_KEY.
 */

import { brevoSchluessel } from './konfiguration';

const BASIS = 'https://api.brevo.com/v3';

export class BrevoFehler extends Error {
  constructor(
    public readonly status: number,
    nachricht: string,
  ) {
    super(nachricht);
  }
}

export async function brevo(pfad: string, methode: 'GET' | 'POST' | 'PUT', koerper?: unknown): Promise<unknown> {
  const schluessel = brevoSchluessel();
  if (!schluessel) throw new BrevoFehler(503, 'BREVO_API_KEY fehlt');
  const antwort = await fetch(`${BASIS}${pfad}`, {
    method: methode,
    headers: { 'api-key': schluessel, 'content-type': 'application/json', accept: 'application/json' },
    body: koerper === undefined ? undefined : JSON.stringify(koerper),
    cache: 'no-store',
  });
  const text = await antwort.text();
  if (!antwort.ok) {
    throw new BrevoFehler(antwort.status, `Brevo ${methode} ${pfad}: HTTP ${antwort.status} ${text.slice(0, 300)}`);
  }
  return text ? (JSON.parse(text) as unknown) : undefined;
}
