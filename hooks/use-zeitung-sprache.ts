'use client';

import { useCallback, useEffect, useState } from 'react';

import { istSprache, spracheAusBrowser } from '@/lib/zeitung/sprache';
import type { Sprache } from '@/lib/zeitung/types';

const SPEICHER_SCHLUESSEL = 'gazet-sprache';

function gespeicherteSprache(): Sprache | undefined {
  try {
    const wert = window.localStorage.getItem(SPEICHER_SCHLUESSEL);
    return istSprache(wert) ? wert : undefined;
  } catch {
    // Speicher gesperrt (z. B. privater Modus): Browsersprache verwenden.
    return undefined;
  }
}

/**
 * Sprache der Zeitung: eigene Wahl, sonst Browsersprache, sonst Englisch.
 * Der Server rendert Deutsch; die Umstellung erfolgt nach dem Laden.
 */
export function useZeitungSprache(): [Sprache, (sprache: Sprache) => void] {
  const [sprache, setzeSprache] = useState<Sprache>('de');

  useEffect(() => {
    const browser = navigator.languages?.length ? navigator.languages : [navigator.language];
    setzeSprache(gespeicherteSprache() ?? spracheAusBrowser(browser));
  }, []);

  useEffect(() => {
    document.documentElement.lang = sprache;
  }, [sprache]);

  const waehle = useCallback((neu: Sprache) => {
    setzeSprache(neu);
    try {
      window.localStorage.setItem(SPEICHER_SCHLUESSEL, neu);
    } catch {
      // Ohne Speicher gilt die Wahl nur bis zum Neuladen.
    }
  }, []);

  return [sprache, waehle];
}
