'use client';

import { MeldungFolie } from './meldung-folie';
import { TeilenKnopf } from './teilen-knopf';
import { useWischStapel } from '@/hooks/use-wisch-stapel';
import { istFrischAktualisiert, istNeu } from '@/lib/zeitung/ausgabe';
import { meldungText } from '@/lib/zeitung/sprache';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';
import type { Meldung, Sprache, Thema } from '@/lib/zeitung/types';

interface ThemenKarteProps {
  thema: Thema;
  sprache: Sprache;
  texte: OberflaechenTexte;
  jetzt: number;
  oberzeile?: string;
}

export function ThemenKarte({ thema, sprache, texte, jetzt, oberzeile }: ThemenKarteProps) {
  const anzahl = thema.updates.length;
  const { spurRef, position, blaettern, beiTaste } = useWischStapel(anzahl);
  // Ältester Stand links, neuester rechts.
  const folien = [...thema.updates].reverse();
  const titel = meldungText(thema.updates[0], 'titel', sprache);

  return (
    <article className="gz-thema" id={`thema-${thema.id}`}>
      {oberzeile && <div className="gz-oberzeile">{oberzeile}</div>}
      <div
        ref={spurRef}
        className="gz-spur"
        tabIndex={0}
        aria-label={texte.stapelLabel(titel)}
        onKeyDown={beiTaste}
      >
        {folien.map((meldung, index) => (
          <MeldungFolie
            key={`${meldung.zeit}-${index}`}
            meldung={meldung}
            sprache={sprache}
            texte={texte}
            marke={marke(thema, meldung, jetzt, texte)}
            topMarke={!oberzeile && thema.warTop && meldung === thema.updates[0] ? texte.aufmacher : undefined}
          />
        ))}
      </div>
      {anzahl > 1 && (
        <div className="gz-blaettern">
          <button type="button" aria-label={texte.aeltere} disabled={position <= 0} onClick={() => blaettern(-1)}>
            ‹
          </button>
          <div className="gz-punkte" aria-hidden="true">
            {folien.map((meldung, index) => (
              <span key={`${meldung.zeit}-${index}`} className={index === position ? 'gz-an' : undefined} />
            ))}
          </div>
          <button type="button" aria-label={texte.neuere} disabled={position >= anzahl - 1} onClick={() => blaettern(1)}>
            ›
          </button>
          <span className="gz-hinweis">
            {position === anzahl - 1 ? texte.hinweisEnde(anzahl - 1) : texte.hinweisPosition(position + 1, anzahl)}
          </span>
        </div>
      )}
      <div className="gz-aktionen">
        <TeilenKnopf themaId={thema.id} titel={titel} texte={texte} />
      </div>
    </article>
  );
}

function marke(thema: Thema, meldung: Meldung, jetzt: number, texte: OberflaechenTexte) {
  if (meldung !== thema.updates[0]) return { text: texte.aelterStand, art: 'alt' as const };
  if (istNeu(thema, jetzt)) return { text: texte.neu, art: 'neu' as const };
  if (istFrischAktualisiert(thema, jetzt)) return { text: texte.aktualisiert, art: 'aktualisiert' as const };
  return undefined;
}
