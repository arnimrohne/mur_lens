/**
 * Regeln für den Aufbau einer Ausgabe: was aktiv ist, was ins Archiv gehört,
 * welche Themen von heute sind und welches Thema oben steht.
 */

import { RUBRIK_IDS } from './types';
import type { RubrikId, Thema, ZeitungDaten } from './types';

/** Ohne neue Meldung seit dieser Zeit wandert ein Thema ins Archiv. */
export const AKTIV_STUNDEN = 72;

const STUNDE_MS = 3_600_000;

/** Themen gelten in den ersten Stunden nach dem ersten Bericht als neu. */
const NEU_STUNDEN = 6;

/** Zeitzone für „heute“, bis der Browser seine eigene meldet. */
export const STANDARD_ZEITZONE = 'Indian/Mauritius';

function kalendertag(zeitpunkt: number, zeitzone: string): string {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: zeitzone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(zeitpunkt));
}

export function istAktiv(thema: Thema, jetzt: number): boolean {
  if (thema.status === 'archiv') return false;
  return jetzt - Date.parse(thema.aktualisiert) < AKTIV_STUNDEN * STUNDE_MS;
}

/** Wie viele Kalendertage zwischen zwei Zeitpunkten liegen (in der Zeitzone des Lesers). */
function tageZurueck(zeitpunkt: number, jetzt: number, zeitzone: string): number {
  const alsUtc = (tag: string): number => {
    const [j, m, t] = tag.split('-').map(Number);
    return Date.UTC(j, m - 1, t);
  };
  return Math.round((alsUtc(kalendertag(jetzt, zeitzone)) - alsUtc(kalendertag(zeitpunkt, zeitzone))) / (24 * STUNDE_MS));
}

/**
 * Ein Thema ist „aktuell“ (aufgeklappt), wenn seine letzte Meldung heute oder
 * gestern erschienen ist – gemessen am Kalendertag in der Zeitzone des Lesers.
 * Wie in einer Tageszeitung: Vortag und heutiger Tag stehen offen,
 * erst ab vorgestern wird zugeklappt.
 */
export function istAktuell(thema: Thema, jetzt: number, zeitzone: string = STANDARD_ZEITZONE): boolean {
  return tageZurueck(Date.parse(thema.aktualisiert), jetzt, zeitzone) <= 1;
}

export function istNeu(thema: Thema, jetzt: number): boolean {
  return jetzt - Date.parse(thema.erstellt) < NEU_STUNDEN * STUNDE_MS;
}

export function istFrischAktualisiert(thema: Thema, jetzt: number): boolean {
  return thema.updates.length > 1 && jetzt - Date.parse(thema.updates[0].zeit) < 24 * STUNDE_MS;
}

export interface RubrikBlock {
  rubrik: RubrikId;
  heute: Thema[];
  vortage: Thema[];
}

export interface Ausgabe {
  /** Top-Themen der letzten 24 Stunden, aktuelles Top-Thema zuerst. */
  topThemen: Thema[];
  rubriken: RubrikBlock[];
  archiv: Thema[];
}

/** So lange bleibt ein Thema im Top-Bereich, nachdem es Top-Thema wurde. */
export const TOP_STUNDEN = 24;

export function istImTopBereich(thema: Thema, jetzt: number): boolean {
  if (thema.top) return true;
  return thema.topSeit !== undefined && jetzt - Date.parse(thema.topSeit) < TOP_STUNDEN * STUNDE_MS;
}

function topReihenfolge(a: Thema, b: Thema): number {
  if (a.top !== b.top) return Number(b.top) - Number(a.top);
  return Date.parse(b.topSeit ?? b.aktualisiert) - Date.parse(a.topSeit ?? a.aktualisiert);
}

/** Ordnet alle Themen der Ausgabe zu. Neueste zuerst. */
export function baueAusgabe(
  daten: ZeitungDaten,
  jetzt: number,
  zeitzone: string = STANDARD_ZEITZONE,
): Ausgabe {
  const sortiert = [...daten.themen].sort(
    (a, b) => Date.parse(b.aktualisiert) - Date.parse(a.aktualisiert),
  );
  let topThemen = sortiert.filter((t) => istImTopBereich(t, jetzt)).sort(topReihenfolge);
  const uebrige = sortiert.filter((t) => !topThemen.includes(t));
  const aktiv = uebrige.filter((t) => istAktiv(t, jetzt));
  // Ohne markiertes Top-Thema rückt das neueste aktive Thema nach oben.
  if (topThemen.length === 0 && aktiv.length > 0) topThemen = [aktiv[0]];
  const archiv = uebrige.filter((t) => !istAktiv(t, jetzt));

  const rubriken = RUBRIK_IDS.flatMap((rubrik): RubrikBlock[] => {
    // Ehemalige Top-Themen zuerst, sonst neueste zuerst (stabile Sortierung).
    const themen = aktiv
      .filter((t) => t.rubrik === rubrik && !topThemen.includes(t))
      .sort((a, b) => Number(b.warTop) - Number(a.warTop));
    if (themen.length === 0) return [];
    return [
      {
        rubrik,
        heute: themen.filter((t) => istAktuell(t, jetzt, zeitzone)),
        vortage: themen.filter((t) => !istAktuell(t, jetzt, zeitzone)),
      },
    ];
  });

  return { topThemen, rubriken, archiv };
}
