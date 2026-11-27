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
/** Text in den drei Sprachen; fehlende Sprachen fallen auf Deutsch zurück. */
export type Mehrsprachig = Record<Sprache, string>;

export interface GrafikWert {
  wert: number;
  label: Mehrsprachig;
  /** Hervorgehobener Balken, z. B. der aktuelle Wert. */
  hervor: boolean;
}

/** Balkendiagramm zu einer Meldung (vom Redaktions-Agenten aus Zahlen der Quelle erstellt). */
export interface Grafik {
  art: 'balken';
  einheit: Mehrsprachig;
  /** Skalenende; ohne Angabe 100 bei Prozent, sonst der größte Wert. */
  max?: number;
  titel?: Mehrsprachig;
  kennzahl?: { wert: Mehrsprachig; text?: Mehrsprachig };
  werte: GrafikWert[];
  quelle?: string;
}

export interface Meldung {
  zeit: string;
  nurDatum: boolean;
  zeitText?: string;
  titel: string;
  text: string;
  quellen: Quelle[];
  i18n: Partial<Record<Exclude<Sprache, 'de'>, MeldungUebersetzung>>;
  grafik?: Grafik;
}

export type ThemaStatus = 'aktiv' | 'archiv';

/** Ein Thema bündelt alle Meldungen zu einer Geschichte. */
export type InselId = 'mauritius' | 'rodrigues' | 'reunion';

export interface Koordinaten {
  insel: InselId;
  lat: number;
  lon: number;
}

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
  /** Zeitpunkt, an dem das Thema (zuletzt) Top-Thema wurde. */
  topSeit?: string;
  ort?: string;
  /** Lage für die Inselkarte, falls der Ort nicht in lib/zeitung/orte.json steht. */
  koordinaten?: Koordinaten;
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

/** Kurze Einleitung „Das Wichtigste in Kürze“, vom automatischen Lauf geschrieben. */
export interface Einleitung {
  zeit: string;
  texte: Record<Sprache, string>;
}

export interface ZeitungDaten {
  stand: string;
  einleitung?: Einleitung;
  themen: Thema[];
  videos: Video[];
}
