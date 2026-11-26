import { ladeZeitung } from '@/lib/zeitung/lade-daten';
import { SEITEN_URL } from '@/lib/zeitung/seite';
import { themaPfad } from '@/lib/zeitung/teilen';

export const revalidate = 600;

/** Sitemap für gazet.morisyen.de (per Middleware unter /sitemap.xml erreichbar). */
export async function GET(): Promise<Response> {
  const daten = await ladeZeitung();
  const stand = daten.stand || new Date().toISOString();
  const eintraege = [
    { pfad: '/', geaendert: stand, haeufigkeit: 'hourly', prioritaet: '1.0' },
    { pfad: '/impressum', geaendert: stand, haeufigkeit: 'yearly', prioritaet: '0.1' },
    { pfad: '/datenschutz', geaendert: stand, haeufigkeit: 'yearly', prioritaet: '0.1' },
    ...daten.themen.map((thema) => ({
      pfad: themaPfad(thema.id),
      geaendert: thema.aktualisiert,
      haeufigkeit: 'daily',
      prioritaet: thema.status === 'archiv' ? '0.4' : '0.7',
    })),
  ];
  const xml = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ...eintraege.map(
      (e) =>
        `  <url><loc>${SEITEN_URL}${e.pfad}</loc><lastmod>${new Date(e.geaendert).toISOString()}</lastmod>` +
        `<changefreq>${e.haeufigkeit}</changefreq><priority>${e.prioritaet}</priority></url>`,
    ),
    '</urlset>',
  ].join('\n');
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
