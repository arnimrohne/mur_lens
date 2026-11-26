'use client';

import { useMemo } from 'react';

import { RubrikAbschnitt } from './rubrik-abschnitt';
import { ThemenKarte } from './themen-karte';
import { VideoAbschnitt } from './video-abschnitt';
import { ZeitungKopf } from './zeitung-kopf';
import { ZugeklapptesThema } from './zugeklapptes-thema';
import { useJetzt } from '@/hooks/use-jetzt';
import { useZeitungSprache } from '@/hooks/use-zeitung-sprache';
import { baueAusgabe } from '@/lib/zeitung/ausgabe';
import { TEXTE } from '@/lib/zeitung/texte';
import type { ZeitungDaten } from '@/lib/zeitung/types';

interface ZeitungAnsichtProps {
  daten: ZeitungDaten;
}

export function ZeitungAnsicht({ daten }: ZeitungAnsichtProps) {
  const [sprache, waehleSprache] = useZeitungSprache();
  const { jetzt, zeitzone } = useJetzt(Date.parse(daten.stand) || 0);
  const ausgabe = useMemo(() => baueAusgabe(daten, jetzt, zeitzone), [daten, jetzt, zeitzone]);
  const texte = TEXTE[sprache];
  const { aufmacher } = ausgabe;

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
        {!aufmacher && ausgabe.archiv.length === 0 && <p className="gz-notiz">{texte.leer}</p>}
        {aufmacher && (
          <section className="gz-aufmacher">
            <ThemenKarte
              thema={aufmacher}
              sprache={sprache}
              texte={texte}
              jetzt={jetzt}
              oberzeile={`${texte.aufmacher} · ${aufmacher.ort ?? texte.rubriken[aufmacher.rubrik].kurz}`}
            />
          </section>
        )}
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
