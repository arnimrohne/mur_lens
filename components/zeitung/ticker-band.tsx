import { uhrzeit } from '@/lib/zeitung/sprache';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';
import type { Sprache, Ticker, TickerEintrag } from '@/lib/zeitung/types';

interface TickerBandProps {
  ticker: Ticker;
  sprache: Sprache;
  texte: OberflaechenTexte;
}

function Eintrag({ eintrag, sprache }: { eintrag: TickerEintrag; sprache: Sprache }) {
  return (
    <li className="gz-ticker-eintrag">
      <time dateTime={eintrag.zeit}>{uhrzeit(eintrag.zeit, sprache)}</time>
      <p>
        {eintrag.text[sprache]}
        {eintrag.quelle && (
          <>
            {' '}
            <a href={eintrag.quelle.url} rel="noopener" target="_blank">
              {eintrag.quelle.name}
            </a>
          </>
        )}
      </p>
    </li>
  );
}

/** Live-Ticker ganz oben, solange eine Lage (z. B. Zyklonwarnung) läuft. */
export function TickerBand({ ticker, sprache, texte }: TickerBandProps) {
  const [neuester, ...aeltere] = ticker.eintraege;
  return (
    <section className="gz-ticker" aria-label={`${texte.ticker}: ${ticker.anlass[sprache]}`} aria-live="polite">
      <div className="gz-ticker-kopf">
        <span className="gz-ticker-live">
          <span className="gz-ticker-punkt" aria-hidden="true" />
          {texte.ticker}
        </span>
        <strong>{ticker.anlass[sprache]}</strong>
        {ticker.warnstufe && <span className="gz-ticker-stufe">{ticker.warnstufe[sprache]}</span>}
        <span className="gz-ticker-zone">{texte.tickerOrtszeit}</span>
      </div>
      <ol className="gz-ticker-liste">
        <Eintrag eintrag={neuester} sprache={sprache} />
      </ol>
      {aeltere.length > 0 && (
        <details className="gz-ticker-mehr">
          <summary>{texte.tickerAeltere(aeltere.length)}</summary>
          <ol className="gz-ticker-liste">
            {aeltere.map((eintrag) => (
              <Eintrag key={eintrag.zeit} eintrag={eintrag} sprache={sprache} />
            ))}
          </ol>
        </details>
      )}
    </section>
  );
}
