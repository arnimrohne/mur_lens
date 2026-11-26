/**
 * Strukturierte Daten (schema.org, JSON-LD) für Suchmaschinen.
 */

import { baueAusgabe } from './ausgabe';
import { SEITEN_BESCHREIBUNG, SEITEN_NAME, SEITEN_URL } from './seite';
import { themaUrl } from './teilen';
import type { Thema, ZeitungDaten } from './types';

const MAX_ARTIKEL = 30;

function artikel(thema: Thema) {
  const neueste = thema.updates[0];
  return {
    '@type': 'NewsArticle',
    headline: neueste.titel.slice(0, 110),
    description: neueste.text.slice(0, 300),
    datePublished: thema.erstellt,
    dateModified: thema.aktualisiert,
    inLanguage: 'de',
    url: themaUrl(thema.id),
    mainEntityOfPage: themaUrl(thema.id),
    isBasedOn: neueste.quellen.map((quelle) => quelle.url),
    publisher: { '@type': 'Organization', name: SEITEN_NAME, url: SEITEN_URL },
    contentLocation: { '@type': 'Place', name: thema.ort ?? 'Mauritius' },
  };
}

/** NewsArticle für die Seite eines einzelnen Themas. */
export function artikelDaten(thema: Thema) {
  return { '@context': 'https://schema.org', ...artikel(thema) };
}

export function strukturierteDaten(daten: ZeitungDaten, jetzt: number) {
  const ausgabe = baueAusgabe(daten, jetzt);
  const aktuell = [
    ...ausgabe.topThemen,
    ...ausgabe.rubriken.flatMap((block) => [...block.heute, ...block.vortage]),
  ].slice(0, MAX_ARTIKEL);

  return {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'WebSite',
        '@id': `${SEITEN_URL}/#website`,
        name: SEITEN_NAME,
        url: SEITEN_URL,
        description: SEITEN_BESCHREIBUNG,
        inLanguage: ['de', 'fr', 'en'],
      },
      {
        '@type': 'CollectionPage',
        '@id': `${SEITEN_URL}/#ausgabe`,
        url: SEITEN_URL,
        name: `${SEITEN_NAME} – Nachrichten aus Mauritius`,
        isPartOf: { '@id': `${SEITEN_URL}/#website` },
        dateModified: daten.stand || undefined,
        about: { '@type': 'Country', name: 'Mauritius' },
        mainEntity: {
          '@type': 'ItemList',
          itemListElement: aktuell.map((thema, index) => ({
            '@type': 'ListItem',
            position: index + 1,
            item: artikel(thema),
          })),
        },
      },
    ],
  };
}

/** JSON für ein <script>-Tag: `<` wird maskiert, damit nichts das Tag beendet. */
export function alsSkriptJson(wert: unknown): string {
  return JSON.stringify(wert).replace(/</g, '\\u003c');
}
