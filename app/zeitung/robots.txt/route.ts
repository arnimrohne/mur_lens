import { impressumVollstaendig, SEITEN_URL } from '@/lib/zeitung/seite';

/**
 * robots.txt für gazet.morisyen.de (per Middleware unter /robots.txt erreichbar).
 * Solange das Impressum unvollständig ist, bleiben Suchmaschinen ausgesperrt.
 */
export function GET(): Response {
  const regeln = impressumVollstaendig()
    ? ['User-agent: *', 'Allow: /', '', `Sitemap: ${SEITEN_URL}/sitemap.xml`]
    : ['User-agent: *', 'Disallow: /'];
  return new Response(`${regeln.join('\n')}\n`, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
}
