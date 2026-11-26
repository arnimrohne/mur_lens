'use client';

import { useState } from 'react';
import type { FormEvent } from 'react';

import { MAIL_TEXTE } from '@/lib/newsletter/texte';
import type { Sprache } from '@/lib/zeitung/types';

interface AnmeldeFormularProps {
  sprache: Sprache;
  /** false, solange Brevo oder das Impressum noch nicht eingerichtet sind. */
  bereit: boolean;
  /** Überschrift weglassen, wenn die Seite selbst eine hat. */
  ohneTitel?: boolean;
}

type Zustand = 'offen' | 'sendet' | 'erfolg' | 'fehler' | 'ungueltig';

/** Newsletter-Anmeldung mit Häufigkeit, freiwilliger Shop-Einwilligung und Double-Opt-in. */
export function AnmeldeFormular({ sprache, bereit, ohneTitel = false }: AnmeldeFormularProps) {
  const t = MAIL_TEXTE[sprache];
  const [zustand, setzeZustand] = useState<Zustand>('offen');

  async function absenden(ereignis: FormEvent<HTMLFormElement>) {
    ereignis.preventDefault();
    const form = new FormData(ereignis.currentTarget);
    const email = String(form.get('email') ?? '').trim();
    if (!email || form.get('einwilligung') !== 'on') {
      setzeZustand('ungueltig');
      return;
    }
    setzeZustand('sendet');
    try {
      const antwort = await fetch('/api/newsletter/anmelden', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          email,
          sprache,
          haeufigkeit: Number(form.get('haeufigkeit')),
          shop: form.get('shop') === 'on',
          einwilligung: true,
          website: String(form.get('website') ?? ''),
        }),
      });
      setzeZustand(antwort.ok ? 'erfolg' : antwort.status === 400 ? 'ungueltig' : 'fehler');
    } catch {
      setzeZustand('fehler');
    }
  }

  return (
    <section className="gz-newsletter" id="newsletter" aria-label={t.titel}>
      {!ohneTitel && <h2>{t.titel}</h2>}
      <p>{t.beschreibung}</p>
      {!bereit ? (
        <p className="gz-nl-hinweis">{t.baldVerfuegbar}</p>
      ) : zustand === 'erfolg' ? (
        <p className="gz-nl-erfolg" role="status">{t.erfolg}</p>
      ) : (
        <form className="gz-nl-form" onSubmit={absenden} noValidate>
          <div className="gz-nl-zeile">
            <label className="gz-nl-feld">
              <span>{t.email}</span>
              <input id="nl-email" name="email" type="email" autoComplete="email" required inputMode="email" />
            </label>
            <label className="gz-nl-feld">
              <span>{t.haeufigkeit}</span>
              <select id="nl-haeufigkeit" name="haeufigkeit" defaultValue="1">
                <option value="1">{t.optionen['1']}</option>
                <option value="2">{t.optionen['2']}</option>
                <option value="3">{t.optionen['3']}</option>
              </select>
            </label>
          </div>
          <label className="gz-nl-check">
            <input id="nl-einwilligung" name="einwilligung" type="checkbox" required />
            <span>
              {t.einwilligung} <a href="/zeitung/datenschutz">{t.datenschutzLink}</a>
            </span>
          </label>
          <label className="gz-nl-check">
            <input id="nl-shop" name="shop" type="checkbox" />
            <span>{t.shop}</span>
          </label>
          <input className="gz-nl-falle" name="website" tabIndex={-1} autoComplete="off" aria-hidden="true" />
          <button type="submit" className="gz-nl-knopf" disabled={zustand === 'sendet'}>
            {zustand === 'sendet' ? t.sendet : t.anmelden}
          </button>
          {(zustand === 'fehler' || zustand === 'ungueltig') && (
            <p className="gz-nl-fehler" role="alert">{zustand === 'fehler' ? t.fehler : t.ungueltig}</p>
          )}
        </form>
      )}
    </section>
  );
}
