import type { Dossier, Thema, ZeitungDaten } from './types';

export function dossierPfad(id: string): string {
  return `/dossier/${encodeURIComponent(id)}`;
}

export const DOSSIERS_PFAD = '/dossiers';

/** Dossier eines Themas: thema.dossier, sonst ein Dossier, das das Thema ausdrücklich führt. */
export function dossierFuerThema(thema: Thema, dossiers: Dossier[]): Dossier | undefined {
  if (thema.dossier) {
    const treffer = dossiers.find((d) => d.id === thema.dossier);
    if (treffer) return treffer;
  }
  return dossiers.find((d) => d.themen.includes(thema.id));
}

/** Meldungen zu einem Dossier, neueste zuerst. */
export function themenZuDossier(daten: ZeitungDaten, dossier: Dossier): Thema[] {
  return daten.themen
    .filter((t) => t.dossier === dossier.id || dossier.themen.includes(t.id))
    .sort((a, b) => Date.parse(b.aktualisiert) - Date.parse(a.aktualisiert));
}

export function findeDossier(dossiers: Dossier[], id: string): Dossier | undefined {
  return dossiers.find((d) => d.id === id);
}
