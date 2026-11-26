/**
 * Lädt die aktuelle Ausgabe.
 *
 * Quelle ist `daten.json` auf dem Branch `zeitung-daten`, den der
 * automatische 4-Stunden-Lauf pflegt. Ist sie nicht erreichbar, wird der
 * im Repository mitgelieferte Stand verwendet.
 */

import mitgeliefert from '@/data/zeitung/daten.json';

import { parseZeitungDaten } from './parse-daten';
import type { ZeitungDaten } from './types';

export const DATEN_URL =
  'https://raw.githubusercontent.com/arnimrohne/mur_lens/zeitung-daten/daten.json';

/** Wie oft die Seite höchstens neu erzeugt wird (Sekunden). */
export const AKTUALISIERUNG_SEKUNDEN = 600;

export async function ladeZeitung(): Promise<ZeitungDaten> {
  const ersatz = parseZeitungDaten(mitgeliefert);
  try {
    const antwort = await fetch(DATEN_URL, { next: { revalidate: AKTUALISIERUNG_SEKUNDEN } });
    if (!antwort.ok) {
      console.warn(`Gazet Morisyen: Daten nicht erreichbar (HTTP ${antwort.status}), nutze mitgelieferten Stand.`);
      return ersatz;
    }
    const daten = parseZeitungDaten(await antwort.json());
    return daten.themen.length > 0 ? daten : ersatz;
  } catch (fehler) {
    console.warn('Gazet Morisyen: Laden fehlgeschlagen, nutze mitgelieferten Stand.', fehler);
    return ersatz;
  }
}
