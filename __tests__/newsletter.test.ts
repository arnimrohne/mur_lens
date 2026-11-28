import { describe, expect, it } from 'vitest';

import { VERSANDZEITEN_FUER, istHaeufigkeit, newsletterBereit } from '@/lib/newsletter/konfiguration';
import { baueMail, themenFuerMail } from '@/lib/newsletter/mail';
import { inhaltFuer, maskiere } from '@/lib/newsletter/mail-html';
import { SEITEN_URL, YOUTUBE_PLAYLISTS } from '@/lib/zeitung/seite';
import { einstellungsLink, einstellungsToken, emailAusLink, istEmail, tokenGueltig } from '@/lib/newsletter/token';
import { parseZeitungDaten } from '@/lib/zeitung/parse-daten';
import type { Thema, ZeitungDaten } from '@/lib/zeitung/types';

const GEHEIM = 'x'.repeat(40);
const JETZT = Date.parse('2026-11-27T07:00:00+04:00');
const STUNDE = 3_600_000;

function thema(id: string, stundenAlt: number, teil: Partial<Thema> = {}): Thema {
  const zeit = new Date(JETZT - stundenAlt * STUNDE).toISOString();
  return {
    id, rubrik: 'politik', titel: id, status: 'aktiv', erstellt: zeit, aktualisiert: zeit, top: false, warTop: false,
    updates: [{ zeit, nurDatum: false, titel: `Titel ${id}`, text: `Text ${id}`, quellen: [], i18n: { fr: { titel: `Titre ${id}`, text: `Texte ${id}` } } }],
    ...teil,
  };
}

function daten(themen: Thema[], einleitung?: ZeitungDaten['einleitung']): ZeitungDaten {
  return { stand: new Date(JETZT).toISOString(), themen, videos: [], einleitung };
}

describe('Newsletter: Häufigkeit', () => {
  it('ordnet Häufigkeiten den Versandzeiten zu', () => {
    expect(VERSANDZEITEN_FUER[1]).toEqual(['morgen']);
    expect(VERSANDZEITEN_FUER[2]).toEqual(['morgen', 'abend']);
    expect(VERSANDZEITEN_FUER[3]).toEqual(['morgen', 'mittag', 'abend']);
    expect(istHaeufigkeit(2)).toBe(true);
    expect(istHaeufigkeit(4)).toBe(false);
  });

  it('bleibt gesperrt, solange der Brevo-Schlüssel fehlt', () => {
    expect(newsletterBereit()).toBe(false);
  });
});

describe('Newsletter: signierte Links', () => {
  it('erkennt gültige und gefälschte Tokens', () => {
    const token = einstellungsToken('Leser@Example.org ', GEHEIM);
    expect(tokenGueltig('leser@example.org', token, GEHEIM)).toBe(true);
    expect(tokenGueltig('andere@example.org', token, GEHEIM)).toBe(false);
    expect(tokenGueltig('leser@example.org', 'falsch', GEHEIM)).toBe(false);
  });

  it('kodiert die Adresse im Link und liest sie wieder', () => {
    const link = new URL(einstellungsLink('leser@example.org', GEHEIM));
    expect(link.pathname).toBe('/newsletter/einstellungen');
    expect(emailAusLink(link.searchParams.get('e') ?? '')).toBe('leser@example.org');
    expect(emailAusLink('kaputt')).toBeUndefined();
  });

  it('prüft E-Mail-Adressen grob', () => {
    expect(istEmail('a@b.mu')).toBe(true);
    expect(istEmail('keine-mail')).toBe(false);
  });
});

describe('Newsletter: Mail', () => {
  it('nimmt morgens die letzten 24 Stunden, mittags nur Neues', () => {
    const d = daten([thema('frisch', 2), thema('gestern', 20), thema('alt', 30)]);
    expect(themenFuerMail(d, 'morgen', JETZT).neu.map((t) => t.id)).toEqual(['frisch', 'gestern']);
    expect(themenFuerMail(d, 'mittag', JETZT).neu.map((t) => t.id)).toEqual(['frisch']);
  });

  it('verschickt mittags nichts, wenn es nichts Neues gibt', () => {
    expect(baueMail(daten([thema('gestern', 20)]), undefined, 'mittag', JETZT)).toBeUndefined();
  });

  it('enthält alle Sprachen, Abmeldelink, Einstellungslink und Shop nur mit Einwilligung', () => {
    const d = daten([thema('a', 1, { top: true, warTop: true, topSeit: new Date(JETZT - STUNDE).toISOString() })], {
      zeit: new Date(JETZT - STUNDE).toISOString(),
      texte: { de: 'Kurz DE', fr: 'Bref FR', en: 'Brief EN' },
    });
    const mail = baueMail(d, undefined, 'morgen', JETZT);
    expect(mail).toBeDefined();
    const html = mail?.html ?? '';
    expect(html).toContain('{% if contact.SPRACHE == "fr" %}');
    expect(html).toContain('Titre a');
    expect(html).toContain('Kurz DE');
    expect(html).toContain('{{ unsubscribe }}');
    expect(html).toContain('{{ contact.EINSTELLUNGEN }}');
    expect(html).toContain('{% if contact.SHOP == "ja" %}');
    expect(mail?.betreff).toContain('Gazet Morisyen');
  });

  it('verlinkt ganz oben Zeitung und Playlist der jeweiligen Sprache', () => {
    const html = baueMail(daten([thema('a', 1)]), undefined, 'morgen', JETZT)?.html ?? '';
    for (const sprache of ['de', 'fr', 'en'] as const) {
      const block = inhaltFuer(sprache, { top: [], neu: [], jetzt: JETZT });
      const zeitung = block.indexOf(`href="${SEITEN_URL}"`);
      const playlist = block.indexOf(YOUTUBE_PLAYLISTS[sprache]);
      expect(zeitung).toBeGreaterThan(-1);
      expect(playlist).toBeGreaterThan(-1);
      expect(Math.max(zeitung, playlist)).toBeLessThan(block.indexOf('</tr>'));
      expect(html).toContain(YOUTUBE_PLAYLISTS[sprache]);
    }
  });

  it('maskiert HTML und Vorlagensyntax aus den Daten', () => {
    expect(maskiere('<b>{{ x }}</b> {% if %}')).toBe('&lt;b&gt;&#123;&#123; x &#125;&#125;&lt;/b&gt; &#123;% if %&#125;');
    const boese = thema('b', 1, {});
    boese.updates[0].titel = '{{ contact.EMAIL }}<script>';
    const html = baueMail(daten([boese]), undefined, 'morgen', JETZT)?.html ?? '';
    expect(html).not.toContain('{{ contact.EMAIL }}<script>');
  });

  it('liest die Einleitung aus den Zeitungsdaten', () => {
    const d = parseZeitungDaten({ einleitung: { zeit: '2026-11-27T06:00:00+04:00', de: 'Hallo', fr: 'Salut' }, topics: [] });
    expect(d.einleitung?.texte).toEqual({ de: 'Hallo', fr: 'Salut', en: 'Hallo' });
  });
});
