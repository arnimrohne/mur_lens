import type { Sprache } from './types';

const LOCALE: Record<Sprache, string> = { de: 'de-DE', fr: 'fr-FR', en: 'en-GB' };

/** 55.2 → „55,2 %“ (de/fr) bzw. „55.2%“ (en); wie die Video-Sendung (sendung/erzeuge_sendung.py → zahl_text). */
export function zahlMitEinheit(wert: number, einheit: string, sprache: Sprache): string {
  const zahl = new Intl.NumberFormat(LOCALE[sprache], { maximumFractionDigits: 1 }).format(wert);
  if (!einheit) return zahl;
  return sprache === 'en' && einheit === '%' ? `${zahl}%` : `${zahl} ${einheit}`;
}
