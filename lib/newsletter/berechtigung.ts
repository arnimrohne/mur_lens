import { timingSafeEqual } from 'node:crypto';

/** Prüft den Kopf `Authorization: Bearer <NEWSLETTER_GEHEIMNIS>` zeitkonstant. */
export function mitGeheimnisBerechtigt(anfrage: Request, geheimnis: string): boolean {
  const kopf = anfrage.headers.get('authorization') ?? '';
  const erhalten = Buffer.from(kopf.replace(/^Bearer\s+/i, ''));
  const erwartet = Buffer.from(geheimnis);
  return erhalten.length === erwartet.length && timingSafeEqual(erhalten, erwartet);
}
