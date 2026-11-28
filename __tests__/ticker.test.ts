import { describe, expect, it } from 'vitest';
import { baueMail } from '@/lib/newsletter/mail';
import { parseTicker, parseZeitungDaten } from '@/lib/zeitung/parse-daten';

const roh = {
  aktiv: true,
  anlass: { de: 'Zyklon Belal', fr: 'Cyclone Belal', en: 'Cyclone Belal' },
  warnstufe: { de: 'Warnstufe II', fr: 'Avis de classe II', en: 'Class II warning' },
  seit: '2026-01-14T18:00:00+04:00',
  eintraege: [
    { zeit: '2026-01-15T05:30:00+04:00', text: { de: 'Ältere Meldung', fr: 'Ancien', en: 'Older' } },
    {
      zeit: '2026-01-15T06:00:00+04:00',
      text: { de: 'Warnstufe II gilt weiter.', fr: "L'avis de classe II reste en vigueur.", en: 'Class II remains in force.' },
      quelle: { name: 'MMS', url: 'https://metservice.intnet.mu/' },
    },
    { zeit: 'kaputt', text: 'ohne Zeit' },
    { zeit: '2026-01-15T04:00:00+04:00' },
  ],
};

describe('Live-Ticker', () => {
  it('übernimmt nur einen aktiven Ticker mit gültigen Einträgen, neueste zuerst', () => {
    const t = parseTicker(roh);
    expect(t?.eintraege.map((e) => e.text.de)).toEqual(['Warnstufe II gilt weiter.', 'Ältere Meldung']);
    expect(t?.eintraege[0].quelle?.url).toBe('https://metservice.intnet.mu/');
    expect(t?.warnstufe?.en).toBe('Class II warning');
  });

  it('verwirft inaktive, leere oder unvollständige Ticker', () => {
    expect(parseTicker({ ...roh, aktiv: false })).toBeUndefined();
    expect(parseTicker({ ...roh, eintraege: [] })).toBeUndefined();
    expect(parseTicker({ ...roh, anlass: undefined })).toBeUndefined();
    expect(parseTicker(undefined)).toBeUndefined();
  });

  it('nimmt nur https-Quellen', () => {
    const t = parseTicker({ ...roh, eintraege: [{ ...roh.eintraege[1], quelle: { name: 'X', url: 'http://x' } }] });
    expect(t?.eintraege[0].quelle).toBeUndefined();
  });

  it('erscheint im Newsletter, auch ohne neue Themen', () => {
    const daten = parseZeitungDaten({ stand: '2026-01-15T06:05:00+04:00', topics: [], videos: [], ticker: roh });
    const mail = baueMail(daten, undefined, 'mittag', Date.parse('2026-01-15T08:00:00Z'));
    expect(mail?.html).toContain('Warnstufe II gilt weiter.');
    expect(mail?.html).toContain('Cyclone Belal');
    const html = mail?.html ?? '';
    expect(html.indexOf('Zyklon Belal')).toBeLessThan(html.lastIndexOf('{{ unsubscribe }}'));
    expect(html.indexOf('Zyklon Belal')).toBeGreaterThan(html.lastIndexOf('{% else %}'));
  });
});
