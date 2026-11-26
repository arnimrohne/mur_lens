'use client';

import { useMemo } from 'react';

import { RubrikAbschnitt } from './rubrik-abschnitt';
import { ShopBanner } from './shop-banner';
import { TopKacheln } from './top-kacheln';
import { WetterLeiste } from './wetter-leiste';
import { VideoAbschnitt } from './video-abschnitt';
import { ZeitungKopf } from './zeitung-kopf';
import { ZugeklapptesThema } from './zugeklapptes-thema';
import { useJetzt } from '@/hooks/use-jetzt';
import { useZeitungSprache } from '@/hooks/use-zeitung-sprache';
import { baueAusgabe } from '@/lib/zeitung/ausgabe';
import { TEXTE } from '@/lib/zeitung/texte';
import type { ZeitungDaten } from '@/lib/zeitung/types';
import type { Wetter } from '@/lib/zeitung/wetter';

interface ZeitungAnsichtProps {
  daten: ZeitungDaten;
  /** Fehlt, wenn der Wetterdienst nicht erreichbar war. */
  wetter?: Wetter;
}

export function ZeitungAnsicht({ daten, wetter }: ZeitungAnsichtProps) {
  const [sprache, waehleSprache] = useZeitungSprache();
  const { jetzt, zeitzone } = useJetzt(Date.parse(daten.stand) || 0);
  const ausgabe = useMemo(() => baueAusgabe(daten, jetzt, zeitzone), [daten, jetzt, zeitzone]);
  const texte = TEXTE[sprache];
  const { topThemen } = ausgabe;

  return (
    <>
      <div className="gz-flagge" aria-hidden="true">
        <span /><span /><span /><span />
      </div>
      <div className="gz-rahmen">
        <ZeitungKopf stand={daten.stand} sprache={sprache} texte={texte} waehleSprache={waehleSprache} />
      </div>

      <nav className="gz-nav" aria-label={texte.rubrikenLabel}>
        <div className="gz-rahmen gz-nav-liste">
          {ausgabe.rubriken.map((block) => (
            <a key={block.rubrik} href={`#${block.rubrik}`}>{texte.rubriken[block.rubrik].kurz}</a>
          ))}
          {daten.videos.length > 0 && <a href="#videos">{texte.videos}</a>}
          {ausgabe.archiv.length > 0 && <a href="#archiv">{texte.archiv}</a>}
        </div>
      </nav>

      <main className="gz-rahmen">
        {topThemen.length === 0 && ausgabe.archiv.length === 0 && <p className="gz-notiz">{texte.leer}</p>}
        {topThemen.length > 0 && <TopKacheln themen={topThemen} sprache={sprache} texte={texte} />}
        {wetter && <WetterLeiste wetter={wetter} sprache={sprache} texte={texte} jetzt={jetzt} />}
        {ausgabe.rubriken.map((block) => (
          <RubrikAbschnitt key={block.rubrik} block={block} sprache={sprache} texte={texte} jetzt={jetzt} />
        ))}
        <VideoAbschnitt videos={daten.videos} sprache={sprache} texte={texte} />
        {ausgabe.archiv.length > 0 && (
          <section className="gz-archiv" id="archiv">
            <details>
              <summary>
                <span>{texte.archiv}</span>
                <span className="gz-anzahl">{texte.archivHinweis(ausgabe.archiv.length)}</span>
              </summary>
              <div className="gz-zuliste">
                {ausgabe.archiv.map((thema) => (
                  <ZugeklapptesThema key={thema.id} thema={thema} sprache={sprache} texte={texte} jetzt={jetzt} />
                ))}
              </div>
            </details>
          </section>
        )}
      </main>

      <ShopBanner texte={texte} />

      <footer className="gz-rahmen gz-fuss">
        {texte.fussnoten.map((absatz) => (
          <p key={absatz}>{absatz}</p>
        ))}
        <p className="gz-fuss-links">
          <a href="/zeitung/impressum">{texte.impressum}</a>
          <a href="/zeitung/datenschutz">{texte.datenschutz}</a>
        </p>
      </footer>
    </>
  );
}
