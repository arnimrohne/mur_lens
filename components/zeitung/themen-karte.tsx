'use client';

import { useDossiers } from './dossier-kontext';
import { InselKarte } from './insel-karte';
import { MeldungFolie } from './meldung-folie';
import { TeilenKnopf } from './teilen-knopf';
import { useWischStapel } from '@/hooks/use-wisch-stapel';
import { istFrischAktualisiert, istNeu } from '@/lib/zeitung/ausgabe';
import { dossierFuerThema, dossierZiel } from '@/lib/zeitung/dossiers';
import { kartenort } from '@/lib/zeitung/karte';
import { meldungText } from '@/lib/zeitung/sprache';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';
import type { Meldung, Sprache, Thema } from '@/lib/zeitung/types';

interface ThemenKarteProps {
  thema: Thema;
  sprache: Sprache;
  texte: OberflaechenTexte;
  jetzt: number;
  oberzeile?: string;
  /** Alle Stände untereinander statt zum Wischen (Themenseite). */
  liste?: boolean;
}

export function ThemenKarte({ thema, sprache, texte, jetzt, oberzeile, liste = false }: ThemenKarteProps) {
  const anzahl = thema.updates.length;
  const { spurRef, position, blaettern, beiTaste } = useWischStapel(anzahl);
  // Ältester Stand links, neuester rechts.
  const folien = [...thema.updates].reverse();
  const titel = meldungText(thema.updates[0], 'titel', sprache);
  const ort = kartenort(thema);
  const dossier = dossierFuerThema(thema, useDossiers());
  const inselName = ort ? texte.inseln[ort.insel] : '';
  const ortText = ort ? (ort.name && ort.name !== inselName ? `${ort.name} · ${inselName}` : inselName) : '';

  return (
    <article className="gz-thema" id={`thema-${thema.id}`}>
      {oberzeile && <div className="gz-oberzeile">{oberzeile}</div>}
      {ort && (
        <div className="gz-ortzeile">
          <InselKarte ort={ort} label={ortText} />
          <span aria-hidden="true">{ortText}</span>
        </div>
      )}
      {liste ? (
        <div className="gz-verlauf">
          <MeldungFolie
            meldung={thema.updates[0]}
            sprache={sprache}
            texte={texte}
            marke={marke(thema, thema.updates[0], jetzt, texte)}
            topMarke={!oberzeile && thema.warTop ? texte.aufmacher : undefined}
          />
          {anzahl > 1 && (
            <>
              <h2 className="gz-verlauf-kopf">{texte.bisherigeMeldungen(anzahl - 1)}</h2>
              <ol className="gz-verlauf-liste">
                {thema.updates.slice(1).map((meldung, index) => (
                  <li key={`${meldung.zeit}-${index}`}>
                    <MeldungFolie meldung={meldung} sprache={sprache} texte={texte} />
                  </li>
                ))}
              </ol>
            </>
          )}
        </div>
      ) : (
        <>
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
        </>
      )}
      {dossier && (
        <a className={dossier.video ? 'gz-dossier-link gz-mit-video' : 'gz-dossier-link'} href={dossierZiel(dossier)}>
          {dossier.video && <span className="gz-play-knopf" aria-hidden="true" />}
          <span className="gz-dossier-text">
            <span className="gz-dossier-marke">{dossier.video ? texte.hintergrundVideo : texte.hintergrund}</span>
            <span className="gz-dossier-titel">{dossier.titel[sprache]}</span>
          </span>
          <span aria-hidden="true">→</span>
        </a>
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
