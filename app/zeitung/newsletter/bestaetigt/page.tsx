import type { Metadata } from 'next';

import { NewsletterSeite } from '@/components/newsletter/newsletter-seite';

export const metadata: Metadata = { title: 'Anmeldung bestätigt', robots: { index: false, follow: false } };

export default function NewsletterBestaetigt() {
  return <NewsletterSeite art="bestaetigt" />;
}
