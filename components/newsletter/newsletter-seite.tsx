'use client';

import { AnmeldeFormular } from './anmelde-formular';
import { EinstellungenFormular } from './einstellungen-formular';
import { useZeitungSprache } from '@/hooks/use-zeitung-sprache';
import { MAIL_TEXTE } from '@/lib/newsletter/texte';
import { SEITEN_NAME } from '@/lib/zeitung/seite';
import { TEXTE } from '@/lib/zeitung/texte';

type NewsletterSeiteProps =
  | { art: 'anmelden'; bereit: boolean }
  | { art: 'einstellungen'; e?: string; t?: string }
  | { art: 'bestaetigt' };

/** Rahmen der Newsletter-Unterseiten, in der Sprache des Lesers. */
export function NewsletterSeite(props: NewsletterSeiteProps) {
  const [sprache] = useZeitungSprache();
  const t = MAIL_TEXTE[sprache];
  const titel = props.art === 'einstellungen' ? t.einstellungenTitel : props.art === 'bestaetigt' ? t.bestaetigtTitel : t.titel;

  return (
    <>
      <div className="gz-flagge" aria-hidden="true">
        <span /><span /><span /><span />
      </div>
      <main className="gz-rahmen gz-rechtstext">
        <p><a href="/zeitung">← {SEITEN_NAME}</a></p>
        <h1>{titel}</h1>
        {props.art === 'anmelden' && <AnmeldeFormular sprache={sprache} bereit={props.bereit} ohneTitel />}
        {props.art === 'einstellungen' &&
          (props.e && props.t ? <EinstellungenFormular e={props.e} t={props.t} /> : <p className="gz-nl-fehler">{t.linkUngueltig}</p>)}
        {props.art === 'bestaetigt' && <p className="gz-nl-erfolg">{t.bestaetigtText}</p>}
        <p className="gz-fuss-links">
          <a href="/zeitung/impressum">{TEXTE[sprache].impressum}</a>
          <a href="/zeitung/datenschutz">{TEXTE[sprache].datenschutz}</a>
        </p>
      </main>
    </>
  );
}
