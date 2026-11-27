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
  /** Zugehöriges Dossier (Hintergrund zu wiederkehrenden Themen). */
  dossier?: string;
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

export interface DossierEreignis {
  /** Anzeige, z. B. „2009“ oder „Nov. 2026“; je Sprache. */
  datum: Mehrsprachig;
  text: Mehrsprachig;
  quelle?: string;
}

export interface DossierAkteur {
  name: Mehrsprachig;
  position: Mehrsprachig;
  quelle?: string;
}

export interface DossierZahl {
  wert: Mehrsprachig;
  text: Mehrsprachig;
  quelle?: string;
}

/** Hintergrund zu einem wiederkehrenden Thema (z. B. Wasserversorgung). */
/** Frei lizenziertes Bild (Wikimedia Commons), selbst ausgeliefert, mit Namensnennung. */
export interface DossierBild {
  /** /bilder/<datei> (mitgeliefert) oder raw.githubusercontent.com/…/zeitung-daten/bilder/<datei>. */
  src: string;
  breite: number;
  hoehe: number;
  alt: Mehrsprachig;
  urheber: string;
  /** Dateiseite auf Wikimedia Commons. */
  seite: string;
  lizenz: string;
  lizenzUrl?: string;
}

/** Regionalkarte (westlicher Indischer Ozean) mit markierten Orten. */
export interface DossierKartenOrt {
  name: Mehrsprachig;
  lat: number;
  lon: number;
  hervor?: boolean;
  /** Lage der Beschriftung zum Punkt. */
  seite?: 'links' | 'rechts' | 'oben' | 'unten';
}

export interface DossierKarte {
  titel?: Mehrsprachig;
  /** [West, Süd, Ost, Nord] in Grad. */
  ausschnitt: [number, number, number, number];
  orte: DossierKartenOrt[];
  /** Verbindungslinien zwischen Orten (Indizes in orte); die Entfernung wird berechnet. */
  linien: { von: number; nach: number }[];
}

export interface Dossier {
  id: string;
  rubrik: RubrikId;
  stand: string;
  titel: Mehrsprachig;
  kurz: Mehrsprachig;
  bild?: DossierBild;
  karte?: DossierKarte;
  warum?: Mehrsprachig;
  entwicklung?: Mehrsprachig;
  chronik: DossierEreignis[];
  akteure: DossierAkteur[];
  zahlen: DossierZahl[];
  grafiken: Grafik[];
  offen: Mehrsprachig[];
  /** Ausdrücklich zugeordnete Themen-IDs (zusätzlich zu thema.dossier). */
  themen: string[];
  quellen: Quelle[];
}
