'use client';

import { useDossiers } from './dossier-kontext';
import { TeilenKnopf } from './teilen-knopf';
import { dossierFuerThema, dossierPfad } from '@/lib/zeitung/dossiers';
import { useKachelKarussell } from '@/hooks/use-kachel-karussell';
import { meldungText, meldungZeit } from '@/lib/zeitung/sprache';
import { themaPfad } from '@/lib/zeitung/teilen';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';
import type { Sprache, Thema } from '@/lib/zeitung/types';

interface TopKachelnProps {
  themen: Thema[];
  sprache: Sprache;
  texte: OberflaechenTexte;
}

/** Top-Themen der letzten 24 Stunden als wischbare Kacheln. */
export function TopKacheln({ themen, sprache, texte }: TopKachelnProps) {
  const { spurRef, position, blaetterbar, blaettern, beiTaste } = useKachelKarussell(themen.length);
  const mehrere = themen.length > 1;

  return (
    <section className="gz-top" aria-labelledby="h-top">
      <div className="gz-top-kopf">
        <h2 id="h-top">{texte.topThemen}</h2>
        {mehrere && blaetterbar && (
          <div className="gz-blaettern gz-top-pfeile">
            <button type="button" aria-label={texte.vorherigesTop} disabled={position <= 0} onClick={() => blaettern(-1)}>‹</button>
            <span className="gz-top-zaehler">{position + 1} / {themen.length}</span>
            <button type="button" aria-label={texte.naechstesTop} disabled={position >= themen.length - 1} onClick={() => blaettern(1)}>›</button>
          </div>
        )}
      </div>
      <div
        ref={spurRef}
        className={`gz-top-spur${mehrere ? '' : ' gz-top-einzeln'}`}
        tabIndex={mehrere ? 0 : -1}
        aria-label={texte.topThemen}
        onKeyDown={beiTaste}
      >
        {themen.map((thema, index) => (
          <TopKachel key={thema.id} thema={thema} sprache={sprache} texte={texte} aktuell={index === 0 && thema.top} />
        ))}
      </div>
    </section>
  );
}

interface TopKachelProps {
  thema: Thema;
  sprache: Sprache;
  texte: OberflaechenTexte;
  aktuell: boolean;
}

function TopKachel({ thema, sprache, texte, aktuell }: TopKachelProps) {
  const neueste = thema.updates[0];
  const titel = meldungText(neueste, 'titel', sprache);
  const anriss = meldungText(neueste, 'text', sprache).split(/\n\s*\n/)[0] ?? '';
  const anzahl = thema.updates.length;
  const dossier = dossierFuerThema(thema, useDossiers());

  return (
    <article className={`gz-kachel${aktuell ? ' gz-kachel-aktuell' : ''}`} id={`thema-${thema.id}`}>
      <div className="gz-oberzeile">
        {texte.aufmacher} · {thema.ort ?? texte.rubriken[thema.rubrik].kurz}
      </div>
      <div className="gz-stempel">
        <time dateTime={neueste.zeit}>{meldungZeit(neueste, sprache)}</time>
        {anzahl > 1 && <span>· {texte.staende(anzahl)}</span>}
      </div>
      <h3>
        <a href={`/zeitung${themaPfad(thema.id)}`}>{titel}</a>
      </h3>
      <p>{anriss}</p>
      {dossier && (
        <a className="gz-kachel-dossier" href={dossierPfad(dossier.id)}>
          <span className="gz-dossier-marke">{texte.hintergrund}</span> {dossier.titel[sprache]} →
        </a>
      )}
      <div className="gz-kachel-fuss">
        <a className="gz-weiter" href={`/zeitung${themaPfad(thema.id)}`}>{texte.weiterlesen}</a>
        <TeilenKnopf themaId={thema.id} titel={titel} texte={texte} />
      </div>
    </article>
  );
}
