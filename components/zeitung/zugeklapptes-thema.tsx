'use client';

import { useDossiers } from './dossier-kontext';
import { ThemenKarte } from './themen-karte';
import { dossierFuerThema, dossierZiel } from '@/lib/zeitung/dossiers';
import { meldungText, meldungZeit } from '@/lib/zeitung/sprache';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';
import type { Sprache, Thema } from '@/lib/zeitung/types';

interface ZugeklapptesThemaProps {
  thema: Thema;
  sprache: Sprache;
  texte: OberflaechenTexte;
  jetzt: number;
}

/** Thema von einem Vortag: nur Datum und Schlagzeile, auf Antippen die ganze Karte. */
export function ZugeklapptesThema({ thema, sprache, texte, jetzt }: ZugeklapptesThemaProps) {
  const neueste = thema.updates[0];
  const anzahl = thema.updates.length;
  const dossier = dossierFuerThema(thema, useDossiers());
  const datum = meldungZeit(neueste, sprache) + (anzahl > 1 ? ` · ${texte.staende(anzahl)}` : '');

  return (
    <details className="gz-zu">
      <summary>
        <span className="gz-zu-datum">{datum}</span>
        <span className="gz-zu-titel">
          {thema.warTop && <span className="gz-marke gz-marke-top">{texte.aufmacher}</span>}
          {meldungText(neueste, 'titel', sprache)}
          {dossier && (
            <a
              className="gz-marke gz-marke-dossier"
              href={dossierZiel(dossier)}
              title={dossier.titel[sprache]}
              aria-label={`${dossier.video ? texte.hintergrundVideo : texte.hintergrund}: ${dossier.titel[sprache]}`}
            >
              {dossier.video && <span className="gz-play-mini" aria-hidden="true" />}
              {dossier.video ? texte.hintergrundVideo : texte.hintergrund}
            </a>
          )}
        </span>
      </summary>
      <ThemenKarte thema={thema} sprache={sprache} texte={texte} jetzt={jetzt} />
    </details>
  );
}
