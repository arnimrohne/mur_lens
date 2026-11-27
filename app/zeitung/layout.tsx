import type { Metadata, Viewport } from 'next';
import { Bricolage_Grotesque, IBM_Plex_Mono, Source_Serif_4 } from 'next/font/google';

import { Analyse } from '@/components/zeitung/analyse';
import { impressumVollstaendig, SEITEN_BESCHREIBUNG, SEITEN_NAME, SEITEN_URL, SUCHBEGRIFFE } from '@/lib/zeitung/seite';

import './zeitung.css';

// Schriften werden beim Build heruntergeladen und von der eigenen Domain
// ausgeliefert: Besucher stellen keine Verbindung zu Google her.
const display = Bricolage_Grotesque({ subsets: ['latin'], weight: ['500', '700', '800'], variable: '--font-gz-display' });
const body = Source_Serif_4({ subsets: ['latin'], weight: ['400', '600'], variable: '--font-gz-body' });
const mono = IBM_Plex_Mono({ subsets: ['latin'], weight: ['400', '500'], variable: '--font-gz-mono' });

const indexierbar = impressumVollstaendig();

export const metadata: Metadata = {
  metadataBase: new URL(SEITEN_URL),
  title: {
    default: `${SEITEN_NAME} – Nachrichten aus Mauritius`,
    template: `%s – ${SEITEN_NAME}`,
  },
  description: SEITEN_BESCHREIBUNG,
  keywords: SUCHBEGRIFFE,
  applicationName: SEITEN_NAME,
  manifest: null,
  alternates: { canonical: '/' },
  openGraph: {
    type: 'website',
    siteName: SEITEN_NAME,
    title: `${SEITEN_NAME} – Nachrichten aus Mauritius`,
    description: SEITEN_BESCHREIBUNG,
    url: '/',
    locale: 'de_DE',
    alternateLocale: ['fr_FR', 'en_GB'],
  },
  twitter: {
    card: 'summary_large_image',
    title: `${SEITEN_NAME} – Nachrichten aus Mauritius`,
    description: SEITEN_BESCHREIBUNG,
  },
  appleWebApp: { capable: true, title: SEITEN_NAME, statusBarStyle: 'default' },
  robots: indexierbar
    ? { index: true, follow: true, googleBot: { index: true, follow: true, 'max-snippet': -1 } }
    : { index: false, follow: false },
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#fdfaf5' },
    { media: '(prefers-color-scheme: dark)', color: '#101418' },
  ],
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
  viewportFit: 'cover',
};

export default function ZeitungLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={`gazet ${display.variable} ${body.variable} ${mono.variable}`}>
      {children}
      <Analyse />
    </div>
  );
}
