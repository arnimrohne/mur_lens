'use client';

import { DossierKontext } from './dossier-kontext';
import { FussLinks } from './fuss-links';
import { ShopBanner } from './shop-banner';
import { ThemenKarte } from './themen-karte';
import { ZeitungKopf } from './zeitung-kopf';
import { useJetzt } from '@/hooks/use-jetzt';
import { useZeitungSprache } from '@/hooks/use-zeitung-sprache';
import { TEXTE } from '@/lib/zeitung/texte';
import type { Dossier, Thema } from '@/lib/zeitung/types';

interface ThemaAnsichtProps {
  thema: Thema;
  stand: string;
  dossiers?: Dossier[];
}

/** Einzelnes Thema, z. B. aus einem geteilten Link. */
export function ThemaAnsicht({ thema, stand, dossiers = [] }: ThemaAnsichtProps) {
  const [sprache, waehleSprache] = useZeitungSprache();
  const { jetzt } = useJetzt(Date.parse(stand) || 0);
  const texte = TEXTE[sprache];

  return (
    <DossierKontext.Provider value={dossiers}>
      <div className="gz-flagge" aria-hidden="true">
        <span /><span /><span /><span />
      </div>
      <div className="gz-rahmen">
        <ZeitungKopf stand={stand} sprache={sprache} texte={texte} waehleSprache={waehleSprache} />
      </div>
      <main className="gz-rahmen gz-einzel">
        <p className="gz-zurueck">
          <a href="/zeitung">{texte.zurAusgabe}</a>
        </p>
        <section className="gz-aufmacher">
          <ThemenKarte
            thema={thema}
            sprache={sprache}
            texte={texte}
            jetzt={jetzt}
            oberzeile={texte.rubriken[thema.rubrik].lang + (thema.ort ? ` · ${thema.ort}` : '')}
          />
        </section>
      </main>
      <ShopBanner texte={texte} />
      <footer className="gz-rahmen gz-fuss">
        <p>{texte.fussnoten[1]}</p>
        <FussLinks texte={texte} />
      </footer>
    </DossierKontext.Provider>
  );
}
