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

/**
 * Ein Thema ist „von heute“, wenn seine letzte Meldung am selben
 * Kalendertag erschienen ist – gemessen in der Zeitzone des Lesers.
 * So bleibt alles vom Tag sichtbar, egal wie viele Läufe dazwischen lagen.
 */
export function istVonHeute(thema: Thema, jetzt: number, zeitzone: string = STANDARD_ZEITZONE): boolean {
  return kalendertag(Date.parse(thema.aktualisiert), zeitzone) === kalendertag(jetzt, zeitzone);
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
        heute: themen.filter((t) => istVonHeute(t, jetzt, zeitzone)),
        vortage: themen.filter((t) => !istVonHeute(t, jetzt, zeitzone)),
      },
    ];
  });

  return { topThemen, rubriken, archiv };
}
