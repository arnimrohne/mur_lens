import { describe, expect, it } from 'vitest';

import dossierDatei from '../data/zeitung/dossiers.json';
import { dossierFuerThema, dossierPfad, themenZuDossier } from '../lib/zeitung/dossiers';
import { parseDossiers } from '../lib/zeitung/parse-daten';

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
