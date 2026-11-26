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

/** Brevo-Listen je Versandzeit. 0 = noch nicht eingerichtet. */
export const BREVO_LISTEN: Record<Versandzeit, number> = { morgen: 0, mittag: 0, abend: 0 };

/** Brevo-Vorlage für die Bestätigungsmail (Double-Opt-in). 0 = noch nicht eingerichtet. */
export const BREVO_DOI_VORLAGE = 0;

export const ABSENDER = { name: 'Gazet Morisyen', email: 'zeitung@morisyen.de' };

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

/**
 * Anmeldung und Versand sind erst möglich, wenn Brevo eingerichtet ist
 * und das Impressum vollständig ist (Pflichtangaben in jeder Mail).
 */
export function newsletterBereit(): boolean {
  return (
    Boolean(brevoSchluessel()) &&
    Boolean(newsletterGeheimnis()) &&
    Object.values(BREVO_LISTEN).every((id) => id > 0) &&
    BREVO_DOI_VORLAGE > 0 &&
    impressumVollstaendig()
  );
}
