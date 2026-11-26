/**
 * Adressen einzelner Themen zum Teilen.
 */

import { SEITEN_HOST, SEITEN_URL } from './seite';
import type { Thema, ZeitungDaten } from './types';

/** Pfad eines Themas auf gazet.morisyen.de. */
export function themaPfad(id: string): string {
  return `/thema/${encodeURIComponent(id)}`;
}

/** Kanonische, öffentliche Adresse eines Themas. */
export function themaUrl(id: string): string {
  return `${SEITEN_URL}${themaPfad(id)}`;
}

/**
 * Adresse zum Teilen aus Sicht des aktuellen Browsers: auf gazet.morisyen.de
 * die kurze Adresse, auf anderen Hosts (z. B. Vercel-Vorschau) /zeitung/thema/….
 */
export function themaUrlFuerHost(id: string, host: string, herkunft: string): string {
  return host === SEITEN_HOST ? themaUrl(id) : `${herkunft}/zeitung${themaPfad(id)}`;
}

export function findeThema(daten: ZeitungDaten, id: string): Thema | undefined {
  return daten.themen.find((thema) => thema.id === id);
}
