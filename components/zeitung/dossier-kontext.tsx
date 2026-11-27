'use client';

import { createContext, useContext } from 'react';

import type { Dossier } from '@/lib/zeitung/types';

/** Dossiers für die Hintergrund-Links an den Themenkarten. */
export const DossierKontext = createContext<Dossier[]>([]);

export function useDossiers(): Dossier[] {
  return useContext(DossierKontext);
}
