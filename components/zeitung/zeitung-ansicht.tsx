'use client';

import Image from 'next/image';
import { useEffect, useMemo, useRef, useState } from 'react';

import { RubrikAbschnitt } from './rubrik-abschnitt';
import { AnmeldeFormular } from '@/components/newsletter/anmelde-formular';
import { ShopBanner } from './shop-banner';
import { TickerBand } from './ticker-band';
import { TopKacheln } from './top-kacheln';
import { WetterLeiste } from './wetter-leiste';
import { VideoAbschnitt } from './video-abschnitt';
import { DossierKontext } from './dossier-kontext';
import { FussLinks } from './fuss-links';
import { LOGO_PFAD, ZeitungKopf } from './zeitung-kopf';
import { ZugeklapptesThema } from './zugeklapptes-thema';
import { useJetzt } from '@/hooks/use-jetzt';
import { useZeitungSprache } from '@/hooks/use-zeitung-sprache';
import { baueAusgabe } from '@/lib/zeitung/ausgabe';
import { DOSSIERS_PFAD } from '@/lib/zeitung/dossiers';
import { SEITEN_NAME } from '@/lib/zeitung/seite';
import { TEXTE } from '@/lib/zeitung/texte';
import type { Dossier, ZeitungDaten } from '@/lib/zeitung/types';
import type { Wetter } from '@/lib/zeitung/wetter';

interface ZeitungAnsichtProps {
  daten: ZeitungDaten;
  /** Fehlt, wenn der Wetterdienst nicht erreichbar war. */
  wetter?: Wetter;
  /** Newsletter-Anmeldung freigeschaltet (Brevo und Impressum eingerichtet). */
  newsletterBereit?: boolean;
  dossiers?: Dossier[];
}

export function ZeitungAnsicht({ daten, wetter, newsletterBereit = false, dossiers = [] }: ZeitungAnsichtProps) {
  const [sprache, waehleSprache] = useZeitungSprache();
  const { jetzt, zeitzone } = useJetzt(Date.parse(daten.stand) || 0);
  const ausgabe = useMemo(() => baueAusgabe(daten, jetzt, zeitzone), [daten, jetzt, zeitzone]);
  const texte = TEXTE[sprache];
  const { topThemen } = ausgabe;

  // Sobald der Kopf aus dem Bild ist, erscheint das Logo klein in der Rubrikleiste.
  const kopfRef = useRef<HTMLDivElement>(null);
  const [kopfWeg, setKopfWeg] = useState(false);
  useEffect(() => {
    const kopf = kopfRef.current;
    if (!kopf || typeof IntersectionObserver === 'undefined') return;
    const beobachter = new IntersectionObserver(([eintrag]) => setKopfWeg(!eintrag.isIntersecting));
    beobachter.observe(kopf);
    return () => beobachter.disconnect();
  }, []);

  return (
    <DossierKontext.Provider value={dossiers}>
      <div className="gz-flagge" aria-hidden="true">
        <span /><span /><span /><span />
      </div>
      <div className="gz-rahmen" ref={kopfRef}>
        <ZeitungKopf stand={daten.stand} sprache={sprache} texte={texte} waehleSprache={waehleSprache} />
      </div>

      <nav className={kopfWeg ? 'gz-nav gz-nav-mit-logo' : 'gz-nav'} aria-label={texte.rubrikenLabel}>
        <div className="gz-rahmen gz-nav-liste">
          <a className="gz-nav-logo" href="#" aria-label={SEITEN_NAME} tabIndex={kopfWeg ? 0 : -1} aria-hidden={!kopfWeg}>
            <Image className="gz-logo" src={LOGO_PFAD} alt="" width={64} height={64} />
          </a>
          {ausgabe.rubriken.map((block) => (
            <a key={block.rubrik} href={`#${block.rubrik}`}>{texte.rubriken[block.rubrik].kurz}</a>
          ))}
          {daten.videos.length > 0 && <a href="#videos">{texte.videos}</a>}
          {ausgabe.archiv.length > 0 && <a href="#archiv">{texte.archiv}</a>}
          {dossiers.length > 0 && <a className="gz-nav-dossiers" href={DOSSIERS_PFAD}>{texte.dossiers}</a>}
        </div>
      </nav>

      <main className="gz-rahmen">
        {daten.ticker && <TickerBand ticker={daten.ticker} sprache={sprache} texte={texte} />}
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

      {newsletterBereit && (
        <div className="gz-rahmen">
          <AnmeldeFormular sprache={sprache} bereit />
        </div>
      )}

      <ShopBanner texte={texte} />

      <footer className="gz-rahmen gz-fuss">
        {texte.fussnoten.map((absatz) => (
          <p key={absatz}>{absatz}</p>
        ))}
        <FussLinks texte={texte} newsletter={newsletterBereit} />
      </footer>
    </DossierKontext.Provider>
  );
}
