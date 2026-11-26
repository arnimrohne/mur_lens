'use client';

import { useState } from 'react';

import { themaUrlFuerHost } from '@/lib/zeitung/teilen';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';

interface TeilenKnopfProps {
  themaId: string;
  titel: string;
  texte: OberflaechenTexte;
}

type Zustand = 'bereit' | 'kopiert' | 'fehler';

const ANZEIGE_MS = 2500;

/**
 * Teilt ein Thema: auf Geräten mit Teilen-Menü (Handy) über das System,
 * sonst wird der Link in die Zwischenablage kopiert.
 */
export function TeilenKnopf({ themaId, titel, texte }: TeilenKnopfProps) {
  const [zustand, setzeZustand] = useState<Zustand>('bereit');

  async function teilen() {
    const url = themaUrlFuerHost(themaId, window.location.hostname, window.location.origin);
    if (typeof navigator.share === 'function') {
      try {
        await navigator.share({ title: titel, url });
        return;
      } catch (fehler) {
        // Abbruch durch den Nutzer ist kein Fehler; sonst auf Kopieren ausweichen.
        if (fehler instanceof DOMException && fehler.name === 'AbortError') return;
      }
    }
    try {
      await navigator.clipboard.writeText(url);
      setzeZustand('kopiert');
    } catch {
      setzeZustand('fehler');
    }
    window.setTimeout(() => setzeZustand('bereit'), ANZEIGE_MS);
  }

  return (
    <button type="button" className="gz-teilen" onClick={teilen} aria-live="polite">
      <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
        <path
          d="M12 3v12M7 8l5-5 5 5M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      {zustand === 'kopiert' ? texte.linkKopiert : zustand === 'fehler' ? texte.linkFehler : texte.teilen}
    </button>
  );
}
