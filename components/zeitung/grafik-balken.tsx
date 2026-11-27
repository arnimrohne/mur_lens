import { zahlMitEinheit } from '@/lib/zeitung/zahlen';
import type { Grafik, Sprache } from '@/lib/zeitung/types';

const quelleText: Record<Sprache, string> = { de: 'Daten:', fr: 'Données :', en: 'Data:' };

interface GrafikBalkenProps {
  grafik: Grafik;
  sprache: Sprache;
}

/** Balkendiagramm mit optionaler Kennzahl; Werte stehen als Text am Balken (kein Farbcode allein). */
export function GrafikBalken({ grafik, sprache }: GrafikBalkenProps) {
  const einheit = grafik.einheit[sprache];
  const groesst = Math.max(...grafik.werte.map((w) => w.wert));
  const skala = grafik.max ?? (einheit === '%' && groesst <= 100 ? 100 : groesst);

  return (
    <figure className="gz-grafik">
      {grafik.titel && <figcaption className="gz-grafik-titel">{grafik.titel[sprache]}</figcaption>}
      {grafik.kennzahl && (
        <p className="gz-grafik-kennzahl">
          <strong>{grafik.kennzahl.wert[sprache]}</strong>
          {grafik.kennzahl.text && <span>{grafik.kennzahl.text[sprache]}</span>}
        </p>
      )}
      <ul className="gz-grafik-balken">
        {grafik.werte.map((w) => {
          const anteil = Math.max(2, Math.min(100, (w.wert / skala) * 100));
          const wertText = zahlMitEinheit(w.wert, einheit, sprache);
          return (
            <li key={w.label.de} className={w.hervor ? 'gz-hervor' : undefined} title={`${w.label[sprache]}: ${wertText}`}>
              <span className="gz-grafik-label">{w.label[sprache]}</span>
              <span className="gz-grafik-spur" aria-hidden="true">
                <span style={{ width: `${anteil}%` }} />
              </span>
              <span className="gz-grafik-wert">{wertText}</span>
            </li>
          );
        })}
      </ul>
      {grafik.quelle && <p className="gz-grafik-quelle">{quelleText[sprache]} {grafik.quelle}</p>}
    </figure>
  );
}
