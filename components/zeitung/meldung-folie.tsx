import { fehltUebersetzung, meldungText, meldungZeit } from '@/lib/zeitung/sprache';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';
import type { Meldung, Sprache } from '@/lib/zeitung/types';

interface MeldungFolieProps {
  meldung: Meldung;
  sprache: Sprache;
  texte: OberflaechenTexte;
  /** Hinweis neben dem Datum, z. B. „Neu“ oder „Älterer Stand“. */
  marke?: { text: string; art: 'neu' | 'aktualisiert' | 'alt' };
}

export function MeldungFolie({ meldung, sprache, texte, marke }: MeldungFolieProps) {
  const absaetze = meldungText(meldung, 'text', sprache)
    .split(/\n\s*\n/)
    .map((absatz) => absatz.trim())
    .filter(Boolean);

  return (
    <div className={`gz-folie${marke?.art === 'alt' ? ' gz-folie-alt' : ''}`}>
      <div className="gz-stempel">
        {marke && <span className={`gz-marke gz-marke-${marke.art}`}>{marke.text}</span>}
        <time dateTime={meldung.zeit}>{meldungZeit(meldung, sprache)}</time>
        {fehltUebersetzung(meldung, sprache) && (
          <span className="gz-marke gz-marke-alt">{texte.nurDeutsch}</span>
        )}
      </div>
      <h3>{meldungText(meldung, 'titel', sprache)}</h3>
      {absaetze.map((absatz) => (
        <p key={absatz}>{absatz}</p>
      ))}
      {meldung.quellen.length > 0 && (
        <div className="gz-meta">
          <span>{texte.quellen}</span>
          {meldung.quellen.map((quelle) => (
            <a key={quelle.url} href={quelle.url} target="_blank" rel="noopener noreferrer">
              {quelle.name}
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
