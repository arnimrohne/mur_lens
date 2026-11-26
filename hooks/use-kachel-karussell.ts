'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { KeyboardEvent, RefObject } from 'react';

interface KachelKarussell {
  spurRef: RefObject<HTMLDivElement | null>;
  position: number;
  /** true, wenn nicht alle Kacheln gleichzeitig sichtbar sind. */
  blaetterbar: boolean;
  blaettern: (richtung: -1 | 1) => void;
  beiTaste: (ereignis: KeyboardEvent<HTMLDivElement>) => void;
}

/** Breite einer Kachel samt Abstand, aus dem gerenderten Layout gelesen. */
function schrittweite(spur: HTMLDivElement): number {
  const erste = spur.children[0];
  const zweite = spur.children[1];
  if (!(erste instanceof HTMLElement)) return Math.max(1, spur.clientWidth);
  if (zweite instanceof HTMLElement) return Math.max(1, zweite.offsetLeft - erste.offsetLeft);
  return Math.max(1, erste.offsetWidth);
}

/** Horizontales Karussell aus Kacheln, beginnt links bei der ersten Kachel. */
export function useKachelKarussell(anzahl: number): KachelKarussell {
  const spurRef = useRef<HTMLDivElement | null>(null);
  const [position, setzePosition] = useState(0);
  const [blaetterbar, setzeBlaetterbar] = useState(anzahl > 1);

  useEffect(() => {
    const spur = spurRef.current;
    if (!spur) return undefined;
    const beiScroll = () => {
      // Am rechten Rand gilt die letzte Kachel als aktiv, auch wenn sie nicht ganz links steht.
      const amEnde = spur.scrollLeft + spur.clientWidth >= spur.scrollWidth - 2;
      const neu = amEnde ? anzahl - 1 : Math.round(spur.scrollLeft / schrittweite(spur));
      setzePosition(Math.min(anzahl - 1, Math.max(0, neu)));
    };
    const pruefeBreite = () => setzeBlaetterbar(spur.scrollWidth > spur.clientWidth + 2);
    const beobachter = new ResizeObserver(pruefeBreite);
    beobachter.observe(spur);
    pruefeBreite();
    spur.addEventListener('scroll', beiScroll, { passive: true });
    return () => {
      beobachter.disconnect();
      spur.removeEventListener('scroll', beiScroll);
    };
  }, [anzahl]);

  const blaettern = useCallback((richtung: -1 | 1) => {
    const spur = spurRef.current;
    if (!spur) return;
    const ruhig = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    spur.scrollBy({ left: richtung * schrittweite(spur), behavior: ruhig ? 'auto' : 'smooth' });
  }, []);

  const beiTaste = useCallback(
    (ereignis: KeyboardEvent<HTMLDivElement>) => {
      if (ereignis.key === 'ArrowLeft' || ereignis.key === 'ArrowRight') {
        blaettern(ereignis.key === 'ArrowLeft' ? -1 : 1);
        ereignis.preventDefault();
      }
    },
    [blaettern],
  );

  return { spurRef, position, blaetterbar, blaettern, beiTaste };
}
