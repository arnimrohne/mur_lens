/**
 * Lädt das Wetter für Port-Louis serverseitig von MET Norway.
 * Besucher stellen dadurch keine Verbindung zum Wetterdienst her.
 */

import { parseSonne, parseVorhersage } from './wetter';
import type { SonnenTag, Wetter } from './wetter';

const BREITE = -20.1609;
const LAENGE = 57.5012;
const BASIS = 'https://api.met.no/weatherapi';

/** MET Norway verlangt eine aussagekräftige Kennung der Anwendung. */
const KENNUNG = 'GazetMorisyen/1.0 (+https://gazet.morisyen.de)';

/** Wetter wird höchstens alle 30 Minuten neu geholt. */
export const WETTER_SEKUNDEN = 1800;

const MAURITIUS_DATUM = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Indian/Mauritius',
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
});

async function holeJson(url: string): Promise<unknown> {
  const antwort = await fetch(url, {
    headers: { 'User-Agent': KENNUNG, Accept: 'application/json' },
    next: { revalidate: WETTER_SEKUNDEN },
  });
  if (!antwort.ok) throw new Error(`HTTP ${antwort.status} für ${url}`);
  return antwort.json();
}

async function holeSonne(datum: string): Promise<SonnenTag | undefined> {
  return parseSonne(await holeJson(`${BASIS}/sunrise/3.0/sun?lat=${BREITE}&lon=${LAENGE}&date=${datum}&offset=+04:00`));
}

export async function ladeWetter(): Promise<Wetter | undefined> {
  const jetzt = Date.now();
  const heute = MAURITIUS_DATUM.format(new Date(jetzt));
  const morgen = MAURITIUS_DATUM.format(new Date(jetzt + 86_400_000));
  try {
    const [vorhersage, sonneHeute, sonneMorgen] = await Promise.all([
      holeJson(`${BASIS}/locationforecast/2.0/complete?lat=${BREITE}&lon=${LAENGE}`),
      holeSonne(heute),
      holeSonne(morgen),
    ]);
    const werte = parseVorhersage(vorhersage, jetzt);
    if (!werte) return undefined;
    return { ...werte, sonne: [sonneHeute, sonneMorgen].flatMap((tag) => tag ?? []) };
  } catch (fehler) {
    console.warn('Gazet Morisyen: Wetter nicht verfügbar.', fehler);
    return undefined;
  }
}
