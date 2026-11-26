import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { DOI_VORLAGE_NAME, LISTEN_NAMEN, richteBrevoEin } from '@/lib/newsletter/einrichtung';

type Aufruf = { methode: string; pfad: string; koerper?: unknown };

/** Einfache Nachbildung der Brevo-API mit Speicher für Listen, Ordner und Vorlagen. */
function brevoAttrappe() {
  const aufrufe: Aufruf[] = [];
  const listen: { id: number; name: string }[] = [];
  const ordner: { id: number; name: string }[] = [];
  const vorlagen: { id: number; name: string }[] = [];
  const attribute = new Set<string>();
  let naechste = 10;
  const antwort = (status: number, daten?: unknown) =>
    new Response(daten === undefined ? '' : JSON.stringify(daten), { status });
  const fetchAttrappe = vi.fn(async (url: string, init: RequestInit) => {
    const pfad = url.replace('https://api.brevo.com/v3', '');
    const methode = init.method ?? 'GET';
    const koerper = init.body ? JSON.parse(String(init.body)) : undefined;
    aufrufe.push({ methode, pfad, koerper });
    if (pfad.startsWith('/contacts/attributes/normal/')) {
      const name = pfad.split('/').pop() ?? '';
      if (attribute.has(name)) return antwort(400, { code: 'invalid_parameter' });
      attribute.add(name);
      return antwort(201);
    }
    if (pfad.startsWith('/contacts/lists') && methode === 'GET') return antwort(200, { lists: listen });
    if (pfad === '/contacts/lists') { const l = { id: naechste++, name: koerper.name }; listen.push(l); return antwort(201, { id: l.id }); }
    if (pfad.startsWith('/contacts/folders') && methode === 'GET') return antwort(200, { folders: ordner });
    if (pfad === '/contacts/folders') { const o = { id: naechste++, name: koerper.name }; ordner.push(o); return antwort(201, { id: o.id }); }
    if (pfad.startsWith('/smtp/templates') && methode === 'GET') return antwort(200, { templates: vorlagen });
    if (pfad === '/smtp/templates') { const v = { id: naechste++, name: koerper.templateName }; vorlagen.push(v); return antwort(201, { id: v.id }); }
    return antwort(404);
  });
  return { fetchAttrappe, aufrufe };
}

describe('Brevo-Einrichtung', () => {
  beforeEach(() => vi.stubEnv('BREVO_API_KEY', 'test-schluessel'));
  afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

  it('legt Felder, drei Listen und die Bestätigungsvorlage an – und beim zweiten Mal nichts doppelt', async () => {
    const { fetchAttrappe, aufrufe } = brevoAttrappe();
    vi.stubGlobal('fetch', fetchAttrappe);

    const erstes = await richteBrevoEin();
    const zweites = await richteBrevoEin();

    expect(Object.keys(erstes.listen)).toEqual(['morgen', 'mittag', 'abend']);
    expect(zweites).toEqual(erstes);
    const angelegteListen = aufrufe.filter((a) => a.methode === 'POST' && a.pfad === '/contacts/lists');
    expect(angelegteListen.map((a) => (a.koerper as { name: string }).name)).toEqual(Object.values(LISTEN_NAMEN));
    const vorlage = aufrufe.filter((a) => a.methode === 'POST' && a.pfad === '/smtp/templates');
    expect(vorlage).toHaveLength(1);
    const v = vorlage[0].koerper as { templateName: string; tag: string; htmlContent: string };
    expect(v.templateName).toBe(DOI_VORLAGE_NAME);
    expect(v.tag).toBe('optin');
    expect(v.htmlContent).toContain('{{ doubleoptin }}');
    expect(aufrufe.every((a) => a.pfad.startsWith('/'))).toBe(true);
  });
});
