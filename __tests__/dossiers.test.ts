import { describe, expect, it } from 'vitest';

import dossierDatei from '../data/zeitung/dossiers.json';
import { dossierFuerThema, dossierPfad, themenZuDossier } from '../lib/zeitung/dossiers';
import { istFreieLizenz, parseDossierBild, parseDossiers } from '../lib/zeitung/parse-daten';

const t = (s: string) => ({ de: s, fr: s, en: s });
const minimal = {
  id: 'test-dossier',
  rubrik: 'umwelt',
  stand: '2026-11-27T00:00:00Z',
  titel: t('Titel'),
  kurz: t('Kurz'),
};

describe('parseDossiers', () => {
  it('liest das mitgelieferte Dossier', () => {
    const dossiers = parseDossiers(dossierDatei);
    expect(dossiers.length).toBeGreaterThan(0);
    const wasser = dossiers.find((d) => d.id === 'wasserversorgung');
    expect(wasser?.chronik.length).toBeGreaterThan(3);
    expect(wasser?.grafiken.length).toBeGreaterThan(0);
    for (const q of wasser?.quellen ?? []) expect(q.url).toMatch(/^https:\/\//);
  });

  it('übernimmt ein minimales Dossier mit leeren Listen', () => {
    const [d] = parseDossiers({ dossiers: [minimal] });
    expect(d.chronik).toEqual([]);
    expect(d.offen).toEqual([]);
    expect(d.grafiken).toEqual([]);
  });

  it('verwirft ungültige IDs, Rubriken, fehlende Titel und Dubletten', () => {
    const dossiers = parseDossiers({
      dossiers: [
        minimal,
        { ...minimal },
        { ...minimal, id: 'Gross Buchstaben' },
        { ...minimal, id: 'x2', rubrik: 'unbekannt' },
        { ...minimal, id: 'x3', titel: {} },
      ],
    });
    expect(dossiers.map((d) => d.id)).toEqual(['test-dossier']);
  });

  it('liefert bei Unsinn eine leere Liste', () => {
    expect(parseDossiers(null)).toEqual([]);
    expect(parseDossiers({ dossiers: 'nein' })).toEqual([]);
  });
});

describe('Dossier-Zuordnung', () => {
  it('baut den Pfad', () => {
    expect(dossierPfad('wasserversorgung')).toBe('/dossier/wasserversorgung');
  });

  it('findet das Dossier zu einem Thema', () => {
    const dossiers = parseDossiers({ dossiers: [{ ...minimal, themen: ['wasserkrise'] }] });
    expect(dossierFuerThema({ id: 'wasserkrise' } as never, dossiers)?.id).toBe('test-dossier');
    expect(dossierFuerThema({ id: 'x', dossier: 'test-dossier' } as never, dossiers)?.id).toBe('test-dossier');
    expect(dossierFuerThema({ id: 'x' } as never, dossiers)).toBeUndefined();
  });

  it('sammelt Themen zum Dossier', () => {
    const [d] = parseDossiers({ dossiers: [{ ...minimal, themen: ['a'] }] });
    const daten = { themen: [{ id: 'a', aktualisiert: '2026-11-01' }, { id: 'b', dossier: 'test-dossier', aktualisiert: '2026-11-02' }, { id: 'c' }] };
    expect(themenZuDossier(daten as never, d).map((x) => x.id).sort()).toEqual(['a', 'b']);
  });
});

describe('Dossier-Bilder', () => {
  const bild = {
    src: '/bilder/test.jpg',
    breite: 1920,
    hoehe: 625,
    alt: t('Ein See'),
    urheber: 'Jemand',
    seite: 'https://commons.wikimedia.org/wiki/File:Test.jpg',
    lizenz: 'CC BY-SA 4.0',
    lizenzUrl: 'https://creativecommons.org/licenses/by-sa/4.0/',
  };

  it('nimmt nur freie Lizenzen', () => {
    for (const l of ['CC0', 'CC0 1.0', 'Public domain', 'CC BY 4.0', 'CC BY-SA 3.0', 'CC BY-SA 2.0 de']) expect(istFreieLizenz(l)).toBe(true);
    for (const l of ['CC BY-NC 4.0', 'CC BY-ND 4.0', 'CC BY-NC-SA 4.0', 'All rights reserved', 'GFDL']) expect(istFreieLizenz(l)).toBe(false);
  });

  it('übernimmt ein gültiges Bild', () => {
    expect(parseDossierBild(bild)?.urheber).toBe('Jemand');
    expect(parseDossierBild({ ...bild, src: 'https://raw.githubusercontent.com/arnimrohne/mur_lens/zeitung-daten/bilder/x-1.jpg' })).toBeDefined();
  });

  it('verwirft fremde Hosts, unfreie Lizenzen und fehlende Angaben', () => {
    expect(parseDossierBild({ ...bild, src: 'https://upload.wikimedia.org/x.jpg' })).toBeUndefined();
    expect(parseDossierBild({ ...bild, seite: 'https://example.com/x' })).toBeUndefined();
    expect(parseDossierBild({ ...bild, lizenz: 'CC BY-NC 4.0' })).toBeUndefined();
    expect(parseDossierBild({ ...bild, urheber: '' })).toBeUndefined();
    expect(parseDossierBild({ ...bild, alt: undefined })).toBeUndefined();
  });

  it('das mitgelieferte Dossier hat ein Bild', () => {
    expect(parseDossiers(dossierDatei)[0].bild?.lizenz).toBe('CC BY-SA 4.0');
  });
});
