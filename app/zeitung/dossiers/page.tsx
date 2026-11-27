import type { Metadata } from 'next';

import { DossierUebersicht } from '@/components/zeitung/dossier-ansicht';
import { ladeDossiers, ladeZeitung } from '@/lib/zeitung/lade-daten';
import { TEXTE } from '@/lib/zeitung/texte';

export const revalidate = 600;

export const metadata: Metadata = {
  title: 'Dossiers',
  description: TEXTE.de.dossiersUntertitel,
  alternates: { canonical: '/dossiers' },
};

export default async function DossiersSeite() {
  const [daten, dossiers] = await Promise.all([ladeZeitung(), ladeDossiers()]);
  const sortiert = [...dossiers].sort((a, b) => a.titel.de.localeCompare(b.titel.de, 'de'));
  return <DossierUebersicht dossiers={sortiert} stand={daten.stand} />;
}
