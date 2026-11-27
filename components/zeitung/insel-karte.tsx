import { inselForm } from '@/lib/zeitung/karte';
import type { Kartenort } from '@/lib/zeitung/karte';

interface InselKarteProps {
  ort: Kartenort;
  /** Barrierefreie Beschreibung, z. B. „Quatre-Bornes, Mauritius“. */
  label: string;
  className?: string;
}

/** Kleines Insel-Piktogramm mit Nadel am Ort (Umriss: Natural Earth, gemeinfrei). */
export function InselKarte({ ort, label, className }: InselKarteProps) {
  const form = inselForm(ort.insel);
  return (
    <svg
      className={className ?? 'gz-inselkarte'}
      viewBox={`0 0 ${form.breite.toFixed(1)} ${form.hoehe.toFixed(1)}`}
      role="img"
      aria-label={label}
    >
      <path className="gz-insel" d={form.pfad} />
      {ort.nadel && (
        <g className="gz-nadel" transform={`translate(${ort.nadel.x.toFixed(1)} ${ort.nadel.y.toFixed(1)})`}>
          <path d="M0 0 L-5.5 -11 A7 7 0 1 1 5.5 -11 Z" />
          <circle cx="0" cy="-14" r="2.6" />
        </g>
      )}
    </svg>
  );
}
