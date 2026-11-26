import type { Metadata } from 'next';
import { notFound } from 'next/navigation';

import { ThemaAnsicht } from '@/components/zeitung/thema-ansicht';
import { ladeZeitung } from '@/lib/zeitung/lade-daten';
import { SEITEN_NAME } from '@/lib/zeitung/seite';
import { alsSkriptJson, artikelDaten } from '@/lib/zeitung/strukturierte-daten';
import { findeThema, themaPfad } from '@/lib/zeitung/teilen';
import { TEXTE } from '@/lib/zeitung/texte';

/** Themenseiten werden beim ersten Aufruf erzeugt und alle 10 Minuten erneuert. */
export const revalidate = 600;
export const dynamicParams = true;

/** Keine Vorab-Erzeugung beim Build; jede Themenseite entsteht beim ersten Aufruf (ISR). */
export function generateStaticParams(): { id: string }[] {
  return [];
}

interface ThemaSeiteProps {
  params: Promise<{ id: string }>;
}

const MAX_BESCHREIBUNG = 200;

export async function generateMetadata({ params }: ThemaSeiteProps): Promise<Metadata> {
  const { id } = await params;
  const thema = findeThema(await ladeZeitung(), decodeURIComponent(id));
  if (!thema) return { title: 'Thema nicht gefunden', robots: { index: false } };

  const neueste = thema.updates[0];
  const beschreibung = neueste.text.replace(/\s+/g, ' ').slice(0, MAX_BESCHREIBUNG);
  const pfad = themaPfad(thema.id);
  return {
    title: neueste.titel,
    description: beschreibung,
    alternates: { canonical: pfad },
    openGraph: {
      type: 'article',
      siteName: SEITEN_NAME,
      title: neueste.titel,
      description: beschreibung,
      url: pfad,
      locale: 'de_DE',
      publishedTime: thema.erstellt,
      modifiedTime: thema.aktualisiert,
      section: TEXTE.de.rubriken[thema.rubrik].lang,
    },
    twitter: { card: 'summary', title: neueste.titel, description: beschreibung },
  };
}

export default async function ThemaSeite({ params }: ThemaSeiteProps) {
  const { id } = await params;
  const daten = await ladeZeitung();
  const thema = findeThema(daten, decodeURIComponent(id));
  if (!thema) notFound();

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: alsSkriptJson(artikelDaten(thema)) }} />
      <ThemaAnsicht thema={thema} stand={daten.stand} />
    </>
  );
}
