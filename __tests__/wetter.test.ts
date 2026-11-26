import { describe, expect, it } from 'vitest';

import sonneHeute from './fixtures/zeitung/sonne-metno-1.json';
import sonneMorgen from './fixtures/zeitung/sonne-metno-2.json';
import vorhersage from './fixtures/zeitung/wetter-metno.json';
import { baueBand, naechsteSonne, parseSonne, parseVorhersage, symbolZuArt } from '@/lib/zeitung/wetter';
import type { SonnenTag, Wetter } from '@/lib/zeitung/wetter';

const JETZT = Date.parse('2026-11-26T21:30:00Z');

function wetter(): Wetter {
  const werte = parseVorhersage(vorhersage, JETZT);
  if (!werte) throw new Error('Testdaten ungültig');
  const sonne = [parseSonne(sonneHeute), parseSonne(sonneMorgen)].filter((t): t is SonnenTag => t !== undefined);
  return { ...werte, sonne };
}

describe('Wetter', () => {
  it('ordnet MET-Norway-Symbole Wetterarten zu', () => {
    expect(symbolZuArt('clearsky_night')).toEqual({ art: 'klar', nacht: true });
    expect(symbolZuArt('lightrainshowers_day')).toEqual({ art: 'schauer', nacht: false });
    expect(symbolZuArt('heavyrainandthunder')).toEqual({ art: 'gewitter', nacht: false });
    expect(symbolZuArt('partlycloudy_day').art).toBe('wolkig');
    expect(symbolZuArt('cloudy').art).toBe('bedeckt');
  });

  it('liest aktuelle Werte und Stunden aus der Vorhersage', () => {
    const w = wetter();
    expect(w.aktuell.zeit).toBe('2026-11-26T21:00:00Z');
    expect(w.aktuell.temperatur).toBe(22.5);
    expect(w.aktuell.wind).toBe(17); // 4,6 m/s ≈ 17 km/h
    expect(w.stunden.length).toBe(30);
  });

  it('liest Sonnenauf- und -untergang', () => {
    expect(parseSonne(sonneHeute)).toEqual({ aufgang: '2026-11-27T05:21+04:00', untergang: '2026-11-27T18:34+04:00' });
    expect(parseSonne({ properties: {} })).toBeUndefined();
  });

  it('baut ein 24-Stunden-Band mit einsortierter Sonne', () => {
    const band = baueBand(wetter(), JETZT);
    expect(band.filter((e) => e.typ === 'stunde').length).toBe(24);
    const typen = band.map((e) => e.typ);
    expect(typen).toContain('aufgang');
    expect(typen).toContain('untergang');
    const zeiten = band.map((e) => Date.parse(e.zeit));
    expect([...zeiten].sort((a, b) => a - b)).toEqual(zeiten);
    expect(naechsteSonne(wetter(), JETZT).aufgang).toBe('2026-11-27T05:21+04:00');
  });

  it('verwirft unbrauchbare Antworten', () => {
    expect(parseVorhersage({ error: true }, JETZT)).toBeUndefined();
  });
});
