'use client';

import { ThemenKarte } from './themen-karte';
import { ZugeklapptesThema } from './zugeklapptes-thema';
import type { RubrikBlock } from '@/lib/zeitung/ausgabe';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';
import type { Sprache } from '@/lib/zeitung/types';

interface RubrikAbschnittProps {
  block: RubrikBlock;
  sprache: Sprache;
  texte: OberflaechenTexte;
  jetzt: number;
}

export function RubrikAbschnitt({ block, sprache, texte, jetzt }: RubrikAbschnittProps) {
  const anzahl = block.heute.length + block.vortage.length;

  return (
    <section className="gz-rubrik" id={block.rubrik} aria-labelledby={`h-${block.rubrik}`}>
      <div className="gz-rubrik-kopf">
        <span className={`gz-farbe gz-farbe-${block.rubrik}`} aria-hidden="true" />
        <h2 id={`h-${block.rubrik}`}>{texte.rubriken[block.rubrik].lang}</h2>
        <span className="gz-anzahl">{texte.themen(anzahl)}</span>
      </div>
      {block.heute.length > 0 && (
        <div className="gz-raster">
          {block.heute.map((thema) => (
            <ThemenKarte key={thema.id} thema={thema} sprache={sprache} texte={texte} jetzt={jetzt} />
          ))}
        </div>
      )}
      {block.vortage.length > 0 && (
        <div className="gz-zuliste">
          <div className="gz-zuliste-kopf">{texte.vortage}</div>
          {block.vortage.map((thema) => (
            <ZugeklapptesThema key={thema.id} thema={thema} sprache={sprache} texte={texte} jetzt={jetzt} />
          ))}
        </div>
      )}
    </section>
  );
}
