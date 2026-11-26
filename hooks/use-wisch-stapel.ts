'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { KeyboardEvent, RefObject } from 'react';

const ABSTAND_PX = 24;

interface WischStapel {
  spurRef: RefObject<HTMLDivElement | null>;
  position: number;
  blaettern: (richtung: -1 | 1) => void;
  beiTaste: (ereignis: KeyboardEvent<HTMLDivElement>) => void;
}

/**
 * Horizontaler Stapel von Meldungen: ältere links, neueste rechts.
 * Startet beim neuesten Stand, auch wenn der Stapel erst später sichtbar
 * wird (z. B. in einem zugeklappten Thema).
 */
export function useWischStapel(anzahl: number): WischStapel {
  const spurRef = useRef<HTMLDivElement | null>(null);
  const [position, setzePosition] = useState(anzahl - 1);
  const angefasst = useRef(false);

  useEffect(() => {
    const spur = spurRef.current;
    if (!spur) return undefined;

    const aktuellePosition = () => {
      const breite = Math.max(1, spur.clientWidth + ABSTAND_PX);
      return Math.min(anzahl - 1, Math.max(0, Math.round(spur.scrollLeft / breite)));
    };
    // Höhe folgt der sichtbaren Meldung, damit unter kurzen Meldungen keine Lücke bleibt.
    const passeHoeheAn = (index: number) => {
      const folie = spur.children[index];
      if (folie instanceof HTMLElement && folie.offsetHeight > 0) {
        spur.style.height = `${folie.offsetHeight}px`;
      }
    };
    const zumNeuesten = () => {
      if (spur.clientWidth === 0) return;
      if (!angefasst.current) spur.scrollLeft = spur.scrollWidth;
      passeHoeheAn(aktuellePosition());
    };
    const beiScroll = () => {
      const neu = aktuellePosition();
      setzePosition(neu);
      passeHoeheAn(neu);
      if (neu !== anzahl - 1) angefasst.current = true;
    };

    const beobachter = new ResizeObserver(zumNeuesten);
    beobachter.observe(spur);
    spur.addEventListener('scroll', beiScroll, { passive: true });
    zumNeuesten();
    return () => {
      beobachter.disconnect();
      spur.removeEventListener('scroll', beiScroll);
    };
  }, [anzahl]);

  const blaettern = useCallback((richtung: -1 | 1) => {
    const spur = spurRef.current;
    if (!spur) return;
    angefasst.current = true;
    const ruhig = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    spur.scrollBy({ left: richtung * (spur.clientWidth + ABSTAND_PX), behavior: ruhig ? 'auto' : 'smooth' });
  }, []);

  const beiTaste = useCallback(
    (ereignis: KeyboardEvent<HTMLDivElement>) => {
      if (ereignis.key === 'ArrowLeft') {
        blaettern(-1);
        ereignis.preventDefault();
      } else if (ereignis.key === 'ArrowRight') {
        blaettern(1);
        ereignis.preventDefault();
      }
    },
    [blaettern],
  );

  return { spurRef, position, blaettern, beiTaste };
}
