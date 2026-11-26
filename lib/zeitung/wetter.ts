/**
 * Wetter für Port-Louis aus MET Norway (api.met.no):
 * Umwandlung der Rohdaten und Aufbau des 24-Stunden-Bands.
 */

export type WetterArt = 'klar' | 'heiter' | 'wolkig' | 'bedeckt' | 'nebel' | 'schauer' | 'regen' | 'gewitter';

export interface WetterStunde {
  zeit: string;
  temperatur: number;
  art: WetterArt;
  nacht: boolean;
  /** Erwarteter Niederschlag in der Stunde, mm. */
  niederschlag: number;
}

export interface WetterAktuell extends WetterStunde {
  gefuehlt?: number;
  feuchte?: number;
  /** km/h */
  wind?: number;
}

export interface SonnenTag {
  aufgang: string;
  untergang: string;
}

export interface Wetter {
  aktuell: WetterAktuell;
  stunden: WetterStunde[];
  sonne: SonnenTag[];
}

export type BandEintrag =
  | ({ typ: 'stunde' } & WetterStunde)
  | { typ: 'aufgang' | 'untergang'; zeit: string };

type Roh = Record<string, unknown>;

function objekt(wert: unknown): Roh | undefined {
  return typeof wert === 'object' && wert !== null && !Array.isArray(wert) ? (wert as Roh) : undefined;
}

function zahl(wert: unknown): number | undefined {
  return typeof wert === 'number' && Number.isFinite(wert) ? wert : undefined;
}

/** Ordnet ein MET-Norway-Symbol (z. B. "lightrainshowers_day") einer Wetterart zu. */
export function symbolZuArt(symbol: string): { art: WetterArt; nacht: boolean } {
  const [name, tageszeit] = symbol.split('_');
  const nacht = tageszeit === 'night' || tageszeit === 'polartwilight';
  if (name.includes('thunder')) return { art: 'gewitter', nacht };
  if (name.includes('showers')) return { art: 'schauer', nacht };
  if (name.includes('rain') || name.includes('sleet') || name.includes('snow')) return { art: 'regen', nacht };
  if (name === 'fog') return { art: 'nebel', nacht };
  if (name === 'cloudy') return { art: 'bedeckt', nacht };
  if (name === 'partlycloudy') return { art: 'wolkig', nacht };
  if (name === 'fair') return { art: 'heiter', nacht };
  return { art: 'klar', nacht };
}

interface Messpunkt {
  zeitMs: number;
  aktuell: WetterAktuell;
}

function eintragZuMesspunkt(eintrag: unknown): Messpunkt | undefined {
  const e = objekt(eintrag);
  const daten = objekt(e?.data);
  const details = objekt(objekt(daten?.instant)?.details);
  const naechste = objekt(daten?.next_1_hours);
  const symbol = objekt(naechste?.summary)?.symbol_code;
  const temperatur = zahl(details?.air_temperature);
  if (typeof e?.time !== 'string' || temperatur === undefined || typeof symbol !== 'string') return undefined;
  const zeitMs = Date.parse(e.time);
  if (Number.isNaN(zeitMs)) return undefined;
  const wind = zahl(details?.wind_speed);
  return {
    zeitMs,
    aktuell: {
      zeit: e.time,
      temperatur,
      ...symbolZuArt(symbol),
      niederschlag: zahl(objekt(naechste?.details)?.precipitation_amount) ?? 0,
      gefuehlt: zahl(details?.apparent_air_temperature),
      feuchte: zahl(details?.relative_humidity),
      wind: wind === undefined ? undefined : Math.round(wind * 3.6),
    },
  };
}

function nurStunde(werte: WetterAktuell): WetterStunde {
  return {
    zeit: werte.zeit,
    temperatur: werte.temperatur,
    art: werte.art,
    nacht: werte.nacht,
    niederschlag: werte.niederschlag,
  };
}

/** Wandelt die Antwort von locationforecast/2.0 in Stundenwerte um. */
export function parseVorhersage(roh: unknown, jetzt: number): Pick<Wetter, 'aktuell' | 'stunden'> | undefined {
  const reihe = objekt(objekt(roh)?.properties)?.timeseries;
  if (!Array.isArray(reihe)) return undefined;
  const punkte = reihe.flatMap((e) => eintragZuMesspunkt(e) ?? []);
  if (punkte.length === 0) return undefined;
  // Aktuell = letzter Wert, der nicht in der Zukunft liegt (sonst der erste).
  const aktuell = [...punkte].reverse().find((p) => p.zeitMs <= jetzt) ?? punkte[0];
  return { aktuell: aktuell.aktuell, stunden: punkte.map((p) => nurStunde(p.aktuell)) };
}

/** Wandelt die Antwort von sunrise/3.0/sun in Auf- und Untergang um. */
export function parseSonne(roh: unknown): SonnenTag | undefined {
  const eigenschaften = objekt(objekt(roh)?.properties);
  const aufgang = objekt(eigenschaften?.sunrise)?.time;
  const untergang = objekt(eigenschaften?.sunset)?.time;
  if (typeof aufgang !== 'string' || typeof untergang !== 'string') return undefined;
  if (Number.isNaN(Date.parse(aufgang)) || Number.isNaN(Date.parse(untergang))) return undefined;
  return { aufgang, untergang };
}

const STUNDE_MS = 3_600_000;

/**
 * 24-Stunden-Band ab der laufenden Stunde, mit Sonnenauf- und -untergang
 * an der richtigen Stelle einsortiert.
 */
export function baueBand(wetter: Wetter, jetzt: number, stunden = 24): BandEintrag[] {
  const beginn = Math.floor(jetzt / STUNDE_MS) * STUNDE_MS;
  const ende = beginn + stunden * STUNDE_MS;
  const stundenEintraege: BandEintrag[] = wetter.stunden
    .filter((s) => Date.parse(s.zeit) >= beginn && Date.parse(s.zeit) < ende)
    .map((s) => ({ typ: 'stunde', ...s }));
  const sonnenEintraege: BandEintrag[] = wetter.sonne.flatMap((tag): BandEintrag[] => [
    { typ: 'aufgang', zeit: tag.aufgang },
    { typ: 'untergang', zeit: tag.untergang },
  ]);
  return [...stundenEintraege, ...sonnenEintraege.filter((e) => Date.parse(e.zeit) > jetzt && Date.parse(e.zeit) < ende)]
    .sort((a, b) => Date.parse(a.zeit) - Date.parse(b.zeit));
}

/** Nächster Sonnenauf- und -untergang ab jetzt. */
export function naechsteSonne(wetter: Wetter, jetzt: number): { aufgang?: string; untergang?: string } {
  const aufgang = wetter.sonne.map((t) => t.aufgang).find((z) => Date.parse(z) > jetzt);
  const untergang = wetter.sonne.map((t) => t.untergang).find((z) => Date.parse(z) > jetzt);
  return { aufgang, untergang };
}
