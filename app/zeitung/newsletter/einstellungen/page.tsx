import type { Metadata } from 'next';

import { NewsletterSeite } from '@/components/newsletter/newsletter-seite';

export const metadata: Metadata = { title: 'Newsletter-Einstellungen', robots: { index: false, follow: false } };

interface Props {
  searchParams: Promise<{ e?: string; t?: string }>;
}

export default async function NewsletterEinstellungen({ searchParams }: Props) {
  const { e, t } = await searchParams;
  return <NewsletterSeite art="einstellungen" e={e} t={t} />;
}
