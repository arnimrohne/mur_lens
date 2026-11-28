/**
 * Sprachauswahl und Zugriff auf übersetzte Felder.
 */

import { SPRACHEN } from './types';
import type { Meldung, Sprache, Video } from './types';

const LOCALE: Record<Sprache, string> = { de: 'de-DE', fr: 'fr-FR', en: 'en-GB' };
const ZEITZONE = 'Indian/Mauritius';

export function istSprache(wert: unknown): wert is Sprache {
  return typeof wert === 'string' && (SPRACHEN as readonly string[]).includes(wert);
}

/**
 * Erste angebotene Sprache aus der Browserliste, sonst Englisch.
 */
export function spracheAusBrowser(browserSprachen: readonly string[]): Sprache {
  for (const eintrag of browserSprachen) {
    const kuerzel = eintrag.toLowerCase().slice(0, 2);
    if (istSprache(kuerzel)) return kuerzel;
  }
  return 'en';
}

type MeldungFeld = 'titel' | 'text' | 'zeitText';

export function meldungText(meldung: Meldung, feld: MeldungFeld, sprache: Sprache): string {
  if (sprache !== 'de') {
    const uebersetzt = meldung.i18n[sprache]?.[feld];
    if (uebersetzt) return uebersetzt;
  }
  return meldung[feld] ?? '';
}

export function fehltUebersetzung(meldung: Meldung, sprache: Sprache): boolean {
  return sprache !== 'de' && !meldung.i18n[sprache]?.titel;
}

type VideoFeld = 'titel' | 'beschreibung' | 'datumText';

export function videoText(video: Video, feld: VideoFeld, sprache: Sprache): string {
  if (sprache !== 'de') {
    const uebersetzt = video.i18n[sprache]?.[feld];
    if (uebersetzt) return uebersetzt;
  }
  return video[feld] ?? '';
}

function format(sprache: Sprache, optionen: Intl.DateTimeFormatOptions): Intl.DateTimeFormat {
  return new Intl.DateTimeFormat(LOCALE[sprache], { timeZone: ZEITZONE, ...optionen });
}

/** Zeitangabe einer Meldung: Freitext, nur Datum oder Datum mit Uhrzeit. */
export function meldungZeit(meldung: Meldung, sprache: Sprache): string {
  if (meldung.zeitText) return meldungText(meldung, 'zeitText', sprache);
  const datum = new Date(Date.parse(meldung.zeit));
  return meldung.nurDatum
    ? format(sprache, { day: '2-digit', month: '2-digit' }).format(datum)
    : format(sprache, { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }).format(datum);
}

export function videoDatum(video: Video, sprache: Sprache, unbekannt: string): string {
  if (video.datumText) return videoText(video, 'datumText', sprache);
  if (video.datum) {
    return format(sprache, { day: '2-digit', month: '2-digit', year: 'numeric' }).format(
      new Date(Date.parse(video.datum)),
    );
  }
  return unbekannt;
}

export function tagLang(zeitpunkt: number, sprache: Sprache): string {
  return format(sprache, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }).format(
    new Date(zeitpunkt),
  );
}

/** Uhrzeit (HH:MM) in Ortszeit Mauritius. */
export function uhrzeit(iso: string, sprache: Sprache): string {
  return format(sprache, { hour: '2-digit', minute: '2-digit' }).format(new Date(Date.parse(iso)));
}

export function zeitKurz(zeitpunkt: number, sprache: Sprache): string {
  return format(sprache, { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }).format(
    new Date(zeitpunkt),
  );
}
