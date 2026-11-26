'use client';

import { useEffect, useState } from 'react';

import { STANDARD_ZEITZONE } from '@/lib/zeitung/ausgabe';

const MINUTE_MS = 60_000;

interface Uhr {
  jetzt: number;
  zeitzone: string;
}

/**
 * Aktuelle Zeit und Zeitzone des Lesers für zeitabhängige Anzeigen
 * (Neu, heute, Archiv). Beim ersten Rendern gelten Stand der Ausgabe und
 * Ortszeit Mauritius, damit Server und Browser dasselbe HTML erzeugen;
 * danach die echte Uhrzeit, minütlich aktualisiert.
 */
export function useJetzt(startZeit: number): Uhr {
  const [uhr, setzeUhr] = useState<Uhr>({ jetzt: startZeit, zeitzone: STANDARD_ZEITZONE });

  useEffect(() => {
    const zeitzone = Intl.DateTimeFormat().resolvedOptions().timeZone || STANDARD_ZEITZONE;
    const ticken = () => setzeUhr({ jetzt: Date.now(), zeitzone });
    ticken();
    const intervall = window.setInterval(ticken, MINUTE_MS);
    return () => window.clearInterval(intervall);
  }, []);

  return uhr;
}
