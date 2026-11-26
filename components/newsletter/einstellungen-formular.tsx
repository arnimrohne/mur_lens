'use client';

import { useState } from 'react';
import type { FormEvent } from 'react';

import { useZeitungSprache } from '@/hooks/use-zeitung-sprache';
import { MAIL_TEXTE } from '@/lib/newsletter/texte';
import { SPRACHEN } from '@/lib/zeitung/types';

interface EinstellungenFormularProps {
  e: string;
  t: string;
}

type Zustand = 'offen' | 'sendet' | 'gespeichert' | 'link' | 'fehler';

const SPRACH_NAMEN = { de: 'Deutsch', fr: 'Français', en: 'English' } as const;

/** Ändert Häufigkeit, Sprache und Shop-Einwilligung über den signierten Link aus der Mail. */
export function EinstellungenFormular({ e, t: token }: EinstellungenFormularProps) {
  const [sprache] = useZeitungSprache();
  const t = MAIL_TEXTE[sprache];
  const [zustand, setzeZustand] = useState<Zustand>('offen');

  async function speichern(ereignis: FormEvent<HTMLFormElement>) {
    ereignis.preventDefault();
    const form = new FormData(ereignis.currentTarget);
    setzeZustand('sendet');
    try {
      const antwort = await fetch('/api/newsletter/einstellungen', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          e,
          t: token,
          haeufigkeit: Number(form.get('haeufigkeit')),
          sprache: String(form.get('sprache')),
          shop: form.get('shop') === 'on',
        }),
      });
      setzeZustand(antwort.ok ? 'gespeichert' : antwort.status === 403 ? 'link' : 'fehler');
    } catch {
      setzeZustand('fehler');
    }
  }

  if (zustand === 'link') return <p className="gz-nl-fehler" role="alert">{t.linkUngueltig}</p>;
  if (zustand === 'gespeichert') return <p className="gz-nl-erfolg" role="status">{t.gespeichert}</p>;

  return (
    <form className="gz-nl-form" onSubmit={speichern}>
      <div className="gz-nl-zeile">
        <label className="gz-nl-feld">
          <span>{t.haeufigkeit}</span>
          <select id="ne-haeufigkeit" name="haeufigkeit" defaultValue="1">
            <option value="1">{t.optionen['1']}</option>
            <option value="2">{t.optionen['2']}</option>
            <option value="3">{t.optionen['3']}</option>
          </select>
        </label>
        <label className="gz-nl-feld">
          <span>Sprache · Langue · Language</span>
          <select id="ne-sprache" name="sprache" defaultValue={sprache} key={sprache}>
            {SPRACHEN.map((k) => (
              <option key={k} value={k}>{SPRACH_NAMEN[k]}</option>
            ))}
          </select>
        </label>
      </div>
      <label className="gz-nl-check">
        <input id="ne-shop" name="shop" type="checkbox" />
        <span>{t.shop}</span>
      </label>
      <button type="submit" className="gz-nl-knopf" disabled={zustand === 'sendet'}>
        {zustand === 'sendet' ? t.sendet : t.speichern}
      </button>
      {zustand === 'fehler' && <p className="gz-nl-fehler" role="alert">{t.fehler}</p>}
    </form>
  );
}
