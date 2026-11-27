import { describe, expect, it } from 'vitest';

import { parseGrafik } from '@/lib/zeitung/parse-daten';
import { zahlMitEinheit } from '@/lib/zeitung/zahlen';

const beispiel = {
  art: 'balken',
  einheit: '%',
  titel: { de: 'Füllstand der Reservoirs', en: 'Reservoir levels' },
  kennzahl: { wert: { de: '44 %', en: '44%' }, text: { de: '40,6 von 92,2 Mio. m³' } },
  werte: [
    { wert: 44, hervor: true, label: { de: '26.11.2026', fr: '26/11/2026', en: '26 Nov 2026' } },
    { wert: 55.2, label: { de: 'Saisonaler Schnitt' } },
    { wert: 69.7, label: 'Vor einem Jahr' },
  ],
  quelle: 'CWA',
};

describe('Grafik', () => {
  it('übernimmt ein gültiges Balkendiagramm und ergänzt fehlende Sprachen', () => {
    const g = parseGrafik(beispiel);
    expect(g?.werte.map((w) => w.wert)).toEqual([44, 55.2, 69.7]);
    expect(g?.werte[0].hervor).toBe(true);
    expect(g?.werte[1].label.fr).toBe('Saisonaler Schnitt');
    expect(g?.titel?.fr).toBe('Füllstand der Reservoirs');
    expect(g?.kennzahl?.text?.en).toBe('40,6 von 92,2 Mio. m³');
    expect(g?.einheit).toEqual({ de: '%', fr: '%', en: '%' });
  });

  it('verwirft unvollständige oder unsinnige Grafiken', () => {
    expect(parseGrafik({ ...beispiel, werte: [beispiel.werte[0]] })).toBeUndefined();
    expect(parseGrafik({ ...beispiel, werte: [...beispiel.werte, { wert: -3, label: 'x' }] })).toBeUndefined();
    expect(parseGrafik({ ...beispiel, werte: [{ wert: 1, label: '' }, { wert: 2, label: 'b' }] })).toBeUndefined();
    expect(parseGrafik({ ...beispiel, art: 'torte' })).toBeUndefined();
    expect(parseGrafik('44 %')).toBeUndefined();
  });

  it('schreibt Zahlen je Sprache wie die Sendung', () => {
    expect(zahlMitEinheit(55.2, '%', 'de')).toBe('55,2 %');
    expect(zahlMitEinheit(55.2, '%', 'en')).toBe('55.2%');
    expect(zahlMitEinheit(1200, 'Rs', 'de')).toBe('1.200 Rs');
    expect(zahlMitEinheit(1200, 'Rs', 'en')).toBe('1,200 Rs');
    expect(zahlMitEinheit(1200, 'Rs', 'fr')).toMatch(/^1\s200 Rs$/u);
  });
});
