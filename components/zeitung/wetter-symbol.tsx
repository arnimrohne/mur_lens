import type { WetterArt } from '@/lib/zeitung/wetter';

interface WetterSymbolProps {
  art: WetterArt;
  nacht: boolean;
  groesse?: number;
  label?: string;
}

const SONNE = (
  <g className="gz-ws-sonne">
    <circle cx="12" cy="12" r="4.2" />
    <path d="M12 2.5v2.4M12 19.1v2.4M2.5 12h2.4M19.1 12h2.4M5.3 5.3l1.7 1.7M17 17l1.7 1.7M5.3 18.7 7 17M17 7l1.7-1.7" />
  </g>
);
const MOND = <path className="gz-ws-mond" d="M15.5 3.6a8.5 8.5 0 1 0 4.9 13.6 7 7 0 0 1-4.9-13.6Z" />;
const KLEINE_SONNE = (
  <g className="gz-ws-sonne">
    <circle cx="8" cy="8" r="3.2" />
    <path d="M8 1.6v1.6M1.6 8h1.6M3.5 3.5l1.1 1.1M12.5 3.5l-1.1 1.1" />
  </g>
);
const KLEINER_MOND = <path className="gz-ws-mond" d="M10 2.4a5.6 5.6 0 1 0 3.3 9 4.6 4.6 0 0 1-3.3-9Z" />;
const WOLKE = <path className="gz-ws-wolke" d="M7.5 19h10a4 4 0 0 0 .3-8 5.5 5.5 0 0 0-10.6 1.3A3.4 3.4 0 0 0 7.5 19Z" />;
const TROPFEN = <path className="gz-ws-regen" d="M9 21.2l-.8 1.6M13 21.2l-.8 1.6M17 21.2l-.8 1.6" />;
const BLITZ = <path className="gz-ws-blitz" d="M13 18.5l-2 3h2.4l-1.4 2.6" />;
const NEBEL = <path className="gz-ws-wolke" d="M4 9h16M3 13h18M5 17h14" />;

/** Schlichte Wettersymbole als SVG; Farben kommen aus dem Stylesheet. */
export function WetterSymbol({ art, nacht, groesse = 28, label }: WetterSymbolProps) {
  const inhalt = (() => {
    switch (art) {
      case 'klar':
        return nacht ? MOND : SONNE;
      case 'heiter':
      case 'wolkig':
        return (
          <>
            {nacht ? KLEINER_MOND : KLEINE_SONNE}
            {WOLKE}
          </>
        );
      case 'bedeckt':
        return WOLKE;
      case 'nebel':
        return NEBEL;
      case 'gewitter':
        return (
          <>
            {WOLKE}
            {BLITZ}
          </>
        );
      default:
        return (
          <>
            {art === 'schauer' && (nacht ? KLEINER_MOND : KLEINE_SONNE)}
            {WOLKE}
            {TROPFEN}
          </>
        );
    }
  })();

  return (
    <svg
      className="gz-ws"
      viewBox="0 0 24 24"
      width={groesse}
      height={groesse}
      role={label ? 'img' : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
    >
      {inhalt}
    </svg>
  );
}
