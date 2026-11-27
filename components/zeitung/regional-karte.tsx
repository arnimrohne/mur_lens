import { entfernungKm, kartenGeometrie } from '@/lib/zeitung/regionalkarte';
import type { DossierKarte, Sprache } from '@/lib/zeitung/types';

const QUELLE: Record<Sprache, string> = {
  de: 'Karte: Natural Earth (gemeinfrei)',
  fr: 'Carte : Natural Earth (domaine public)',
  en: 'Map: Natural Earth (public domain)',
};

function km(wert: number, sprache: Sprache): string {
  const gerundet = Math.round(wert / 50) * 50;
  return `≈ ${gerundet.toLocaleString(sprache === 'en' ? 'en-GB' : sprache === 'fr' ? 'fr-FR' : 'de-DE')} km`;
}

/** Regionalkarte mit markierten Orten; Namen stehen als Text an den Punkten. */
export function RegionalKarte({ karte, sprache }: { karte: DossierKarte; sprache: Sprache }) {
  const g = kartenGeometrie(karte);
  const beschreibung = karte.orte.map((o) => o.name[sprache]).join(', ');
  return (
    <figure className="gz-regionalkarte">
      {karte.titel && <figcaption className="gz-grafik-titel">{karte.titel[sprache]}</figcaption>}
      <svg viewBox={`0 0 ${g.breite} ${g.hoehe}`} role="img" aria-label={beschreibung}>
        <rect className="gz-rk-meer" width={g.breite} height={g.hoehe} />
        <path className="gz-rk-land" d={g.landPfad} />
        {karte.linien.map(({ von, nach }) => {
          const a = karte.orte[von];
          const b = karte.orte[nach];
          const pa = g.punkt(a.lon, a.lat);
          const pb = g.punkt(b.lon, b.lat);
          const mx = (pa.x + pb.x) / 2;
          const my = (pa.y + pb.y) / 2;
          return (
            <g key={`${von}-${nach}`} className="gz-rk-linie">
              <line x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y} />
              <text x={mx + 8} y={my} dominantBaseline="middle">{km(entfernungKm(a, b), sprache)}</text>
            </g>
          );
        })}
        {karte.orte.map((o) => {
          const p = g.punkt(o.lon, o.lat);
          const seite = o.seite ?? 'rechts';
          const dx = seite === 'rechts' ? 10 : seite === 'links' ? -10 : 0;
          const dy = seite === 'oben' ? -12 : seite === 'unten' ? 16 : 0;
          const anker = seite === 'rechts' ? 'start' : seite === 'links' ? 'end' : 'middle';
          return (
            <g key={o.name.de} className={o.hervor ? 'gz-rk-ort gz-rk-hervor' : 'gz-rk-ort'}>
              <circle cx={p.x} cy={p.y} r={o.hervor ? 6 : 4} />
              <text x={p.x + dx} y={p.y + dy} textAnchor={anker} dominantBaseline="middle">{o.name[sprache]}</text>
            </g>
          );
        })}
      </svg>
      <p className="gz-grafik-quelle">{QUELLE[sprache]}</p>
    </figure>
  );
}
