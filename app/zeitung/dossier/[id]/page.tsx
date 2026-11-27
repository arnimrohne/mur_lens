import type { Metadata } from 'next';
import { notFound } from 'next/navigation';

import { DossierAnsicht } from '@/components/zeitung/dossier-ansicht';
import { dossierPfad, findeDossier, themenZuDossier } from '@/lib/zeitung/dossiers';
import { ladeDossiers, ladeZeitung } from '@/lib/zeitung/lade-daten';
import { SEITEN_NAME, SEITEN_URL } from '@/lib/zeitung/seite';
import { alsSkriptJson } from '@/lib/zeitung/strukturierte-daten';

export const revalidate = 600;
export const dynamicParams = true;

export function generateStaticParams(): { id: string }[] {
  return [];
}

interface DossierSeiteProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: DossierSeiteProps): Promise<Metadata> {
  const { id } = await params;
  const dossier = findeDossier(await ladeDossiers(), decodeURIComponent(id));
  if (!dossier) return { title: 'Dossier nicht gefunden', robots: { index: false } };
  return {
    title: dossier.titel.de,
    description: dossier.kurz.de.slice(0, 200),
    alternates: { canonical: dossierPfad(dossier.id) },
    openGraph: {
      type: 'article',
      siteName: SEITEN_NAME,
      title: dossier.titel.de,
      description: dossier.kurz.de.slice(0, 200),
      url: dossierPfad(dossier.id),
      locale: 'de_DE',
      modifiedTime: dossier.stand,
    },
  };
}

export default async function DossierSeite({ params }: DossierSeiteProps) {
  const { id } = await params;
  const [daten, dossiers] = await Promise.all([ladeZeitung(), ladeDossiers()]);
  const dossier = findeDossier(dossiers, decodeURIComponent(id));
  if (!dossier) notFound();
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: dossier.titel.de,
    description: dossier.kurz.de,
    dateModified: dossier.stand,
    inLanguage: 'de',
    url: `${SEITEN_URL}${dossierPfad(dossier.id)}`,
    publisher: { '@type': 'Organization', name: SEITEN_NAME, url: SEITEN_URL },
  };
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: alsSkriptJson(jsonLd) }} />
      <DossierAnsicht dossier={dossier} themen={themenZuDossier(daten, dossier)} stand={daten.stand} />
    </>
  );
}
