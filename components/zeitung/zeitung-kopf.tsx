'use client';

import { tagLang, zeitKurz } from '@/lib/zeitung/sprache';
import { SEITEN_NAME } from '@/lib/zeitung/seite';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';
import { SPRACHEN } from '@/lib/zeitung/types';
import type { Sprache } from '@/lib/zeitung/types';

interface ZeitungKopfProps {
  stand: string;
  sprache: Sprache;
  texte: OberflaechenTexte;
  waehleSprache: (sprache: Sprache) => void;
}

export function ZeitungKopf({ stand, sprache, texte, waehleSprache }: ZeitungKopfProps) {
  const standZeit = Date.parse(stand);

  return (
    <header className="gz-kopf">
      <h1>
        {SEITEN_NAME}
        <small>{texte.untertitel}</small>
      </h1>
      <div className="gz-kopf-rechts">
        <div className="gz-sprachen" role="group" aria-label="Sprache / Langue / Language">
          {SPRACHEN.map((kuerzel) => (
            <button
              key={kuerzel}
              type="button"
              lang={kuerzel}
              aria-pressed={kuerzel === sprache}
              onClick={() => waehleSprache(kuerzel)}
            >
              {kuerzel.toUpperCase()}
            </button>
          ))}
        </div>
        <div className="gz-datumszeile">
          {Number.isNaN(standZeit) ? (
            texte.keineAusgabe
          ) : (
            <>
              <b>{tagLang(standZeit, sprache)}</b>
              <br />
              <time dateTime={stand}>{texte.stand(zeitKurz(standZeit, sprache))}</time>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
