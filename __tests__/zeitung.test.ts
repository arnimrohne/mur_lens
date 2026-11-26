import { describe, expect, it } from 'vitest';

import mitgeliefert from './fixtures/zeitung/ausgabe-2026-11-26.json';
import aktuellerStand from '@/data/zeitung/daten.json';
import { baueAusgabe, istAktiv, istVonHeute } from '@/lib/zeitung/ausgabe';
import { parseZeitungDaten, sichereUrl } from '@/lib/zeitung/parse-daten';
import { meldungText, meldungZeit, spracheAusBrowser } from '@/lib/zeitung/sprache';
import { alsSkriptJson, strukturierteDaten } from '@/lib/zeitung/strukturierte-daten';
import { findeThema, themaPfad, themaUrlFuerHost } from '@/lib/zeitung/teilen';
import type { Thema } from '@/lib/zeitung/types';

const STUNDE = 3_600_000;

function thema(teil: Partial<Thema> & { id: string; aktualisiert: string }): Thema {
  return {
    rubrik: 'politik',
    titel: 'Titel',
    status: 'aktiv',
    erstellt: teil.aktualisiert,
    top: false,
    warTop: false,
    updates: [
      { zeit: teil.aktualisiert, nurDatum: false, titel: 'Titel', text: 'Text', quellen: [], i18n: {} },
    ],
    ...teil,
  };
}

describe('parseZeitungDaten', () => {
  it('liest die mitgelieferte Ausgabe vollständig', () => {
    const daten = parseZeitungDaten(mitgeliefert);
    expect(daten.themen.length).toBe(26);
    expect(daten.videos.length).toBe(8);
    expect(daten.stand).toBe('2026-11-26T22:00:00+04:00');
  });

  it('liest den mitgelieferten Ersatzstand ohne Verluste', () => {
    const daten = parseZeitungDaten(aktuellerStand);
    expect(daten.themen.length).toBe(aktuellerStand.topics.length);
    expect(daten.videos.length).toBe(aktuellerStand.videos.length);
  });

  it('verwirft ungültige Themen, Videos und unsichere Links', () => {
    const daten = parseZeitungDaten({
      stand: 'kein Datum',
      topics: [
        { id: 'ok', rubrik: 'sport', updates: [{ zeit: '2026-11-26T10:00:00+04:00', titel: 'A', quellen: [{ name: 'X', url: 'http://unsicher' }] }] },
        { id: 'falsche-rubrik', rubrik: 'mode', updates: [{ zeit: '2026-11-26T10:00:00+04:00', titel: 'B' }] },
        { id: 'ohne-updates', rubrik: 'sport', updates: [] },
      ],
      videos: [{ id: 'v', titel: 'V', url: 'javascript:alert(1)' }],
    });
    expect(daten.stand).toBe('');
    expect(daten.themen.map((t) => t.id)).toEqual(['ok']);
    expect(daten.themen[0].updates[0].quellen).toEqual([]);
    expect(daten.videos).toEqual([]);
  });

  it('sortiert Meldungen eines Themas neueste zuerst', () => {
    const daten = parseZeitungDaten({
      topics: [
        {
          id: 't',
          rubrik: 'umwelt',
          updates: [
            { zeit: '2026-11-20T10:00:00+04:00', titel: 'alt' },
            { zeit: '2026-11-24T10:00:00+04:00', titel: 'neu' },
          ],
        },
      ],
    });
    expect(daten.themen[0].updates.map((u) => u.titel)).toEqual(['neu', 'alt']);
    expect(daten.themen[0].aktualisiert).toBe('2026-11-24T10:00:00+04:00');
  });

  it('akzeptiert nur https-Links', () => {
    expect(sichereUrl('https://defimedia.info/x')).toBe('https://defimedia.info/x');
    expect(sichereUrl('http://defimedia.info/x')).toBeUndefined();
  });
});

describe('Ausgabe', () => {
  const jetzt = Date.parse('2026-11-26T22:00:00+04:00');

  it('archiviert Themen ohne Meldung seit 72 Stunden', () => {
    expect(istAktiv(thema({ id: 'a', aktualisiert: new Date(jetzt - 71 * STUNDE).toISOString() }), jetzt)).toBe(true);
    expect(istAktiv(thema({ id: 'b', aktualisiert: new Date(jetzt - 73 * STUNDE).toISOString() }), jetzt)).toBe(false);
    expect(istAktiv(thema({ id: 'c', aktualisiert: new Date(jetzt).toISOString(), status: 'archiv' }), jetzt)).toBe(false);
  });

  it('bestimmt "heute" nach dem Kalendertag des Lesers', () => {
    // 00:30 Uhr auf Mauritius ist 21:30 Uhr in Berlin, noch der 26.11.
    const zeitpunkt = Date.parse('2026-11-27T00:30:00+04:00');
    const vomVormittag = thema({ id: 'a', aktualisiert: '2026-11-26T09:00:00+04:00' });
    expect(istVonHeute(vomVormittag, zeitpunkt, 'Europe/Berlin')).toBe(true);
    expect(istVonHeute(vomVormittag, zeitpunkt, 'Indian/Mauritius')).toBe(false);
    const vomVortag = thema({ id: 'b', aktualisiert: '2026-11-25T20:00:00+04:00' });
    expect(istVonHeute(vomVortag, zeitpunkt, 'Europe/Berlin')).toBe(false);
  });

  it('stellt das Top-Thema voran und verteilt den Rest auf Rubriken', () => {
    const ausgabe = baueAusgabe(parseZeitungDaten(mitgeliefert), jetzt);
    expect(ausgabe.topThemen[0]?.id).toBe('rodrigues-seebeben');
    const ids = ausgabe.rubriken.flatMap((b) => [...b.heute, ...b.vortage].map((t) => t.id));
    expect(ids).not.toContain('rodrigues-seebeben');
    expect(ausgabe.archiv.map((t) => t.id)).toContain('wasserkrise');
  });

  it('stellt ehemalige Top-Themen in ihrer Rubrik nach vorn', () => {
    const t = (id: string, stunden: number, warTop = false) =>
      thema({ id, rubrik: 'umwelt', warTop, aktualisiert: new Date(jetzt - stunden * STUNDE).toISOString() });
    const daten = { stand: '', videos: [], themen: [t('neu', 1), t('ehemals-top', 30, true), t('alt', 40)] };
    const ausgabe = baueAusgabe(daten, jetzt, 'Indian/Mauritius');
    // Aufmacher ist das neueste Thema, danach führt das ehemalige Top-Thema die Rubrik an.
    expect(ausgabe.topThemen.map((x) => x.id)).toEqual(['neu']);
    expect(ausgabe.rubriken[0].vortage.map((x) => x.id)).toEqual(['ehemals-top', 'alt']);
  });

  it('markiert das aktuelle Top-Thema auch als warTop', () => {
    const daten = parseZeitungDaten({
      topics: [{ id: 'x', rubrik: 'politik', top: true, updates: [{ zeit: '2026-11-26T10:00:00+04:00', titel: 'X' }] }],
    });
    expect(daten.themen[0].warTop).toBe(true);
  });
});

describe('Sprache', () => {
  it('nimmt die erste angebotene Browsersprache, sonst Englisch', () => {
    expect(spracheAusBrowser(['fr-CH', 'de-DE'])).toBe('fr');
    expect(spracheAusBrowser(['mfe', 'hi-IN'])).toBe('en');
    expect(spracheAusBrowser([])).toBe('en');
  });

  it('fällt bei fehlender Übersetzung auf Deutsch zurück', () => {
    const meldung = {
      zeit: '2026-11-24T19:15:00+04:00',
      nurDatum: false,
      titel: 'Deutsch',
      text: 'Text',
      quellen: [],
      i18n: { fr: { titel: 'Français' } },
    };
    expect(meldungText(meldung, 'titel', 'fr')).toBe('Français');
    expect(meldungText(meldung, 'titel', 'en')).toBe('Deutsch');
    expect(meldungZeit(meldung, 'de')).toBe('24.11., 19:15');
  });
});

describe('Strukturierte Daten', () => {
  it('erzeugt NewsArticle-Einträge und maskiert spitze Klammern', () => {
    const daten = parseZeitungDaten(mitgeliefert);
    const ld = strukturierteDaten(daten, Date.parse(daten.stand));
    const json = alsSkriptJson(ld);
    expect(json).toContain('"@type":"NewsArticle"');
    expect(alsSkriptJson({ x: '</script>' })).not.toContain('</script>');
  });
});

describe('Teilen', () => {
  it('baut kurze Adressen auf gazet.morisyen.de und /zeitung-Adressen anderswo', () => {
    expect(themaPfad('rodrigues-seebeben')).toBe('/thema/rodrigues-seebeben');
    expect(themaUrlFuerHost('wasserkrise', 'gazet.morisyen.de', 'https://gazet.morisyen.de')).toBe(
      'https://gazet.morisyen.de/thema/wasserkrise',
    );
    expect(themaUrlFuerHost('wasserkrise', 'mur-lens.vercel.app', 'https://mur-lens.vercel.app')).toBe(
      'https://mur-lens.vercel.app/zeitung/thema/wasserkrise',
    );
  });

  it('findet Themen über ihre Kennung', () => {
    const daten = parseZeitungDaten(mitgeliefert);
    expect(findeThema(daten, 'world-knits')?.rubrik).toBe('soziales');
    expect(findeThema(daten, 'gibt-es-nicht')).toBeUndefined();
  });
});

describe('Top-Bereich', () => {
  const jetzt = Date.parse('2026-11-27T12:00:00+04:00');
  const t = (id: string, teil: Partial<Thema>) =>
    thema({ id, aktualisiert: '2026-11-27T08:00:00+04:00', ...teil });

  it('zeigt Top-Themen 24 Stunden lang, aktuelles zuerst', () => {
    const daten = {
      stand: '',
      videos: [],
      themen: [
        t('frueher-top', { warTop: true, topSeit: '2026-11-26T20:00:00+04:00' }),
        t('aktuell', { top: true, warTop: true, topSeit: '2026-11-27T10:00:00+04:00' }),
        t('abgelaufen', { warTop: true, topSeit: '2026-11-26T08:00:00+04:00' }),
        t('normal', {}),
      ],
    };
    const ausgabe = baueAusgabe(daten, jetzt, 'Indian/Mauritius');
    expect(ausgabe.topThemen.map((x) => x.id)).toEqual(['aktuell', 'frueher-top']);
    const inRubriken = ausgabe.rubriken.flatMap((b) => [...b.heute, ...b.vortage].map((x) => x.id));
    // Nach 24 Stunden zurück in der Rubrik, ehemalige Top-Themen zuerst.
    expect(inRubriken).toEqual(['abgelaufen', 'normal']);
  });
});
