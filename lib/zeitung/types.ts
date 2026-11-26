/**
 * Domain-Typen der Gazet Moris.
 *
 * Das Datenformat entspricht der Datei `daten.json` auf dem Branch
 * `zeitung-daten`, die der automatische 4-Stunden-Lauf pflegt.
 */

export type Sprache = 'de' | 'fr' | 'en';

export const SPRACHEN: readonly Sprache[] = ['de', 'fr', 'en'];

export type RubrikId =
  | 'politik'
  | 'wirtschaft'
  | 'soziales'
  | 'umwelt'
  | 'justiz'
  | 'sport'
  | 'alltag';

export const RUBRIK_IDS: readonly RubrikId[] = [
  'politik',
  'wirtschaft',
  'soziales',
  'umwelt',
  'justiz',
  'sport',
  'alltag',
];

export interface Quelle {
  name: string;
  url: string;
}

export interface MeldungUebersetzung {
  titel?: string;
  text?: string;
  zeitText?: string;
}

/** Ein Stand (eine Meldung) innerhalb eines Themas. */
export interface Meldung {
  zeit: string;
  nurDatum: boolean;
  zeitText?: string;
  titel: string;
  text: string;
  quellen: Quelle[];
  i18n: Partial<Record<Exclude<Sprache, 'de'>, MeldungUebersetzung>>;
}

export type ThemaStatus = 'aktiv' | 'archiv';

/** Ein Thema bündelt alle Meldungen zu einer Geschichte. */
export interface Thema {
  id: string;
  rubrik: RubrikId;
  titel: string;
  status: ThemaStatus;
  erstellt: string;
  aktualisiert: string;
  top: boolean;
  /** War jemals Top-Thema; bleibt dauerhaft gekennzeichnet. */
  warTop: boolean;
  ort?: string;
  /** Neueste Meldung zuerst. */
  updates: Meldung[];
}

export interface VideoUebersetzung {
  titel?: string;
  beschreibung?: string;
  datumText?: string;
}

export interface Video {
  id: string;
  titel: string;
  beschreibung: string;
  url: string;
  quelle: string;
  reihenfolge: number;
  datum?: string;
  datumText?: string;
  i18n: Partial<Record<Exclude<Sprache, 'de'>, VideoUebersetzung>>;
}

export interface ZeitungDaten {
  stand: string;
  themen: Thema[];
  videos: Video[];
}
