import type { Metadata } from 'next';

import { NewsletterSeite } from '@/components/newsletter/newsletter-seite';
import { newsletterBereit } from '@/lib/newsletter/konfiguration';

export const metadata: Metadata = {
  title: 'Newsletter',
  description: 'Gazet Morisyen per E-Mail: die wichtigsten Nachrichten aus Mauritius, ein- bis dreimal täglich.',
  alternates: { canonical: '/newsletter' },
};

export const dynamic = 'force-dynamic';

export default function NewsletterAnmeldung() {
  return <NewsletterSeite art="anmelden" bereit={newsletterBereit()} />;
}
