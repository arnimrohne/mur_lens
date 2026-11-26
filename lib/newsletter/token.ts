/**
 * Signierte Kennung je E-Mail-Adresse für den Link „Einstellungen ändern“.
 * Wird bei der Anmeldung in Brevo gespeichert und im Link mitgeschickt.
 */

import { createHmac, timingSafeEqual } from 'node:crypto';

import { SEITEN_URL } from '@/lib/zeitung/seite';

export function normalisiereEmail(email: string): string {
  return email.trim().toLowerCase();
}

export function einstellungsToken(email: string, geheimnis: string): string {
  return createHmac('sha256', geheimnis).update(normalisiereEmail(email)).digest('base64url').slice(0, 32);
}

export function tokenGueltig(email: string, token: string, geheimnis: string): boolean {
  const erwartet = Buffer.from(einstellungsToken(email, geheimnis));
  const erhalten = Buffer.from(token);
  return erwartet.length === erhalten.length && timingSafeEqual(erwartet, erhalten);
}

/** Einfache, bewusst großzügige Prüfung; die eigentliche Prüfung ist die Bestätigungsmail. */
export function istEmail(wert: unknown): wert is string {
  return typeof wert === 'string' && wert.length <= 254 && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(wert.trim());
}

/** Vollständiger, signierter Link zur Einstellungsseite; wird in Brevo als Attribut gespeichert. */
export function einstellungsLink(email: string, geheimnis: string): string {
  const e = Buffer.from(normalisiereEmail(email)).toString('base64url');
  return `${SEITEN_URL}/newsletter/einstellungen?e=${e}&t=${einstellungsToken(email, geheimnis)}`;
}

/** Liest die E-Mail-Adresse aus dem Link-Parameter `e`. */
export function emailAusLink(e: string): string | undefined {
  try {
    const email = Buffer.from(e, 'base64url').toString('utf8');
    return istEmail(email) ? email : undefined;
  } catch {
    return undefined;
  }
}
