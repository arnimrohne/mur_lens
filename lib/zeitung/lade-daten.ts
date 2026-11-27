/**
 * Lädt die aktuelle Ausgabe.
 *
 * Quelle ist `daten.json` auf dem Branch `zeitung-daten`, den der
 * automatische 4-Stunden-Lauf pflegt. Ist sie nicht erreichbar, wird der
 * im Repository mitgelieferte Stand verwendet.
 */

import mitgeliefert from '@/data/zeitung/daten.json';
import dossiersMitgeliefert from '@/data/zeitung/dossiers.json';

import { parseDossiers, parseZeitungDaten } from './parse-daten';
import type { Dossier, ZeitungDaten } from './types';

export const DATEN_URL =
  'https://raw.githubusercontent.com/arnimrohne/mur_lens/zeitung-daten/daten.json';

/** Wie oft die Seite höchstens neu erzeugt wird (Sekunden). */
export const AKTUALISIERUNG_SEKUNDEN = 600;

export async function ladeZeitung(): Promise<ZeitungDaten> {
  const ersatz = parseZeitungDaten(mitgeliefert);
  // Für lokale Vorschauen: GAZET_DATEN_LOKAL=1 nutzt nur data/zeitung/daten.json.
  if (process.env.GAZET_DATEN_LOKAL === '1') return ersatz;
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

export const DOSSIERS_URL =
  'https://raw.githubusercontent.com/arnimrohne/mur_lens/zeitung-daten/dossiers.json';

/** Dossiers vom Daten-Branch; fehlt die Datei dort noch, gilt der mitgelieferte Stand. */
export async function ladeDossiers(): Promise<Dossier[]> {
  const ersatz = parseDossiers(dossiersMitgeliefert);
  if (process.env.GAZET_DATEN_LOKAL === '1') return ersatz;
  try {
    const antwort = await fetch(DOSSIERS_URL, { next: { revalidate: AKTUALISIERUNG_SEKUNDEN } });
    if (!antwort.ok) return ersatz;
    const dossiers = parseDossiers(await antwort.json());
    return dossiers.length > 0 ? dossiers : ersatz;
  } catch {
    return ersatz;
  }
}
