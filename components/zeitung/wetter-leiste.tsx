'use client';

import { WetterSymbol } from './wetter-symbol';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';
import type { Sprache } from '@/lib/zeitung/types';
import { baueBand, naechsteSonne } from '@/lib/zeitung/wetter';
import type { BandEintrag, Wetter } from '@/lib/zeitung/wetter';

interface WetterLeisteProps {
  wetter: Wetter;
  sprache: Sprache;
  texte: OberflaechenTexte;
  jetzt: number;
}

const LOCALE: Record<Sprache, string> = { de: 'de-DE', fr: 'fr-FR', en: 'en-GB' };

function uhrzeit(zeit: string, sprache: Sprache): string {
  return new Intl.DateTimeFormat(LOCALE[sprache], {
    timeZone: 'Indian/Mauritius',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(Date.parse(zeit)));
}

/** Aktuelles Wetter und 24-Stunden-Band mit Sonnenauf- und -untergang. */
export function WetterLeiste({ wetter, sprache, texte, jetzt }: WetterLeisteProps) {
  const t = texte.wetter;
  const { aktuell } = wetter;
  const band = baueBand(wetter, jetzt);
  const sonne = naechsteSonne(wetter, jetzt);
  const details = [
    aktuell.gefuehlt !== undefined ? t.gefuehlt(Math.round(aktuell.gefuehlt)) : undefined,
    aktuell.wind !== undefined ? t.wind(aktuell.wind) : undefined,
    aktuell.feuchte !== undefined ? t.feuchte(Math.round(aktuell.feuchte)) : undefined,
  ].filter(Boolean);

  return (
    <section className="gz-wetter" aria-labelledby="h-wetter">
      <div className="gz-wetter-jetzt">
        <h2 id="h-wetter">{t.titel}</h2>
        <div className="gz-wetter-haupt">
          <WetterSymbol art={aktuell.art} nacht={aktuell.nacht} groesse={52} label={t.arten[aktuell.art]} />
          <span className="gz-wetter-temp">{Math.round(aktuell.temperatur)}°</span>
          <div className="gz-wetter-lage">
            <strong>{t.arten[aktuell.art]}</strong>
            <span>{details.join(' · ')}</span>
          </div>
        </div>
        <div className="gz-wetter-sonne">
          {sonne.aufgang && <span>↑ {t.aufgang} {uhrzeit(sonne.aufgang, sprache)}</span>}
          {sonne.untergang && <span>↓ {t.untergang} {uhrzeit(sonne.untergang, sprache)}</span>}
        </div>
      </div>
      {band.length > 0 && (
        <div className="gz-wetter-band-rahmen">
          <div className="gz-wetter-band-kopf">
            <span>{t.band}</span>
            <span>{t.ortszeit}</span>
          </div>
          <ol className="gz-wetter-band" aria-label={t.band}>
            {band.map((eintrag) => (
              <BandZelle key={`${eintrag.typ}-${eintrag.zeit}`} eintrag={eintrag} sprache={sprache} texte={texte} />
            ))}
          </ol>
          <p className="gz-wetter-quelle">
            <a href="https://www.met.no/en" target="_blank" rel="noopener noreferrer">{t.quelle}</a> (CC BY 4.0)
          </p>
        </div>
      )}
    </section>
  );
}

function BandZelle({ eintrag, sprache, texte }: { eintrag: BandEintrag; sprache: Sprache; texte: OberflaechenTexte }) {
  const t = texte.wetter;
  if (eintrag.typ !== 'stunde') {
    const auf = eintrag.typ === 'aufgang';
    return (
      <li className={`gz-band-sonne ${auf ? 'gz-band-auf' : 'gz-band-unter'}`}>
        <time dateTime={eintrag.zeit}>{uhrzeit(eintrag.zeit, sprache)}</time>
        <span className="gz-band-sonne-symbol" aria-hidden="true">{auf ? '↑' : '↓'}</span>
        <span className="gz-band-sonne-text">{auf ? t.aufgang : t.untergang}</span>
      </li>
    );
  }
  return (
    <li className={`gz-band-stunde${eintrag.nacht ? ' gz-band-nacht' : ''}`}>
      <time dateTime={eintrag.zeit}>{uhrzeit(eintrag.zeit, sprache).slice(0, 2)}</time>
      <WetterSymbol art={eintrag.art} nacht={eintrag.nacht} label={t.arten[eintrag.art]} />
      <span className="gz-band-temp">{Math.round(eintrag.temperatur)}°</span>
      <span className="gz-band-regen">{eintrag.niederschlag > 0 ? `${eintrag.niederschlag.toLocaleString(LOCALE[sprache])} mm` : ' '}</span>
    </li>
  );
}
