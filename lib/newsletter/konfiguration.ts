/**
 * Einstellungen des Newsletters.
 *
 * Geheimnisse (API-Schlüssel, Versand-Geheimnis) kommen ausschließlich aus
 * Umgebungsvariablen in Vercel, nie aus dem Code:
 *   BREVO_API_KEY         API-Schlüssel von Brevo
 *   NEWSLETTER_GEHEIMNIS  langes Zufallswort; schützt den Versand-Aufruf und
 *                         signiert die Links zum Ändern der Einstellungen
 */

import { impressumVollstaendig } from '@/lib/zeitung/seite';

export type Haeufigkeit = 1 | 2 | 3;
export type Versandzeit = 'morgen' | 'mittag' | 'abend';

/** Versandzeiten je gewählter Häufigkeit (Ortszeit Mauritius: 7, 12, 18 Uhr). */
export const VERSANDZEITEN_FUER: Record<Haeufigkeit, Versandzeit[]> = {
  1: ['morgen'],
  2: ['morgen', 'abend'],
  3: ['morgen', 'mittag', 'abend'],
};

export const ALLE_VERSANDZEITEN: readonly Versandzeit[] = ['morgen', 'mittag', 'abend'];

/** Zeitraum, den eine Ausgabe abdeckt (Stunden zurück). Morgens: Tagesüberblick. */
export const FENSTER_STUNDEN: Record<Versandzeit, number> = { morgen: 24, mittag: 6, abend: 7 };

export const ABSENDER = { name: 'Gazet Morisyen', email: 'gazet@morisyen.de' };

export function istHaeufigkeit(wert: unknown): wert is Haeufigkeit {
  return wert === 1 || wert === 2 || wert === 3;
}

export function istVersandzeit(wert: unknown): wert is Versandzeit {
  return typeof wert === 'string' && (ALLE_VERSANDZEITEN as readonly string[]).includes(wert);
}

export function brevoSchluessel(): string | undefined {
  return process.env.BREVO_API_KEY?.trim() || undefined;
}

export function newsletterGeheimnis(): string | undefined {
  const geheimnis = process.env.NEWSLETTER_GEHEIMNIS?.trim();
  return geheimnis && geheimnis.length >= 32 ? geheimnis : undefined;
}

/** Brevo-Schlüssel und Versand-Geheimnis sind in Vercel hinterlegt. */
export function brevoVerbunden(): boolean {
  return Boolean(brevoSchluessel()) && Boolean(newsletterGeheimnis());
}

/**
 * Anmeldung und regulärer Versand sind erst möglich, wenn Brevo verbunden
 * und das Impressum vollständig ist (Pflichtangaben in jeder Mail).
 * Ob Listen und Vorlage in Brevo existieren, wird beim Aufruf geprüft.
 */
export function newsletterBereit(): boolean {
  return brevoVerbunden() && impressumVollstaendig();
}
