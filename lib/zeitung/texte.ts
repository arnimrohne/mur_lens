/**
 * Feste Texte der Oberfläche in Deutsch, Französisch und Englisch.
 */

import type { RubrikId, Sprache } from './types';

export interface OberflaechenTexte {
  untertitel: string;
  rubrikenLabel: string;
  rubriken: Record<RubrikId, { lang: string; kurz: string }>;
  aufmacher: string;
  neu: string;
  aktualisiert: string;
  aelterStand: string;
  quellen: string;
  nurDeutsch: string;
  stapelLabel: (titel: string) => string;
  aeltere: string;
  neuere: string;
  hinweisEnde: (anzahl: number) => string;
  hinweisPosition: (position: number, anzahl: number) => string;
  staende: (anzahl: number) => string;
  themen: (anzahl: number) => string;
  vortage: string;
  videos: string;
  videosHinweis: string;
  datumUnbekannt: string;
  archiv: string;
  archivHinweis: (anzahl: number) => string;
  stand: (zeit: string) => string;
  keineAusgabe: string;
  leer: string;
  fussnoten: string[];
  impressum: string;
  datenschutz: string;
  teilen: string;
  linkKopiert: string;
  linkFehler: string;
  zurAusgabe: string;
  topThemen: string;
  weiterlesen: string;
  vorherigesTop: string;
  naechstesTop: string;
  shop: { kennzeichnung: string; titel: string; text: string; knopf: string };
}

const de: OberflaechenTexte = {
  untertitel: 'Die Tageszeitung für Mauritius',
  rubrikenLabel: 'Rubriken',
  rubriken: {
    politik: { lang: 'Politik & Diplomatie', kurz: 'Politik' },
    wirtschaft: { lang: 'Wirtschaft', kurz: 'Wirtschaft' },
    soziales: { lang: 'Arbeit & Soziales', kurz: 'Soziales' },
    umwelt: { lang: 'Wasser, Umwelt & Landwirtschaft', kurz: 'Umwelt' },
    justiz: { lang: 'Polizei & Justiz', kurz: 'Polizei & Justiz' },
    sport: { lang: 'Sport', kurz: 'Sport' },
    alltag: { lang: 'Alltag & Kultur', kurz: 'Kultur' },
  },
  aufmacher: 'Top-Thema',
  neu: 'Neu',
  aktualisiert: 'Aktualisiert',
  aelterStand: 'Älterer Stand',
  quellen: 'Quellen:',
  nurDeutsch: 'nur auf Deutsch',
  stapelLabel: (titel) => `Meldungen zu ${titel}, ältere links, neueste rechts`,
  aeltere: 'Ältere Meldung',
  neuere: 'Neuere Meldung',
  hinweisEnde: (n) => `← ${n} ${n === 1 ? 'älterer Stand' : 'ältere Stände'}`,
  hinweisPosition: (p, n) => `Stand ${p} von ${n} · neuester rechts`,
  staende: (n) => `${n} Stände`,
  themen: (n) => `${n} ${n === 1 ? 'Thema' : 'Themen'}`,
  vortage: 'Von den Vortagen · zum Aufklappen antippen',
  videos: 'Videos',
  videosHinweis: 'Öffnen im neuen Tab',
  datumUnbekannt: 'Datum unbekannt',
  archiv: 'Archiv',
  archivHinweis: (n) => `${n} ältere Themen · seit 3 Tagen ohne neue Meldung`,
  stand: (zeit) => `Stand ${zeit} Uhr (Ortszeit Mauritius)`,
  keineAusgabe: 'Noch keine Ausgabe',
  leer: 'Noch keine Meldungen. Die erste Ausgabe erscheint beim nächsten automatischen Lauf.',
  fussnoten: [
    'Gazet Morisyen wird etwa alle vier Stunden automatisch aktualisiert. Jede Karte ist ein Thema: Sie sehen zuerst die neueste Meldung, ältere Stände liegen links davon. Sie erreichen sie durch Wischen oder mit dem Pfeil ‹. Themen, deren letzte Meldung von einem Vortag stammt, sind zugeklappt.',
    'Die Texte sind automatisch erstellte, eigene Zusammenfassungen ohne Gewähr. Details stehen in den verlinkten Originalen. Themen ohne neue Meldung seit 3 Tagen wandern ins Archiv und werden nach 60 Tagen gelöscht.',
  ],
  impressum: 'Impressum',
  datenschutz: 'Datenschutz',
  teilen: 'Teilen',
  linkKopiert: 'Link kopiert',
  linkFehler: 'Kopieren nicht möglich',
  zurAusgabe: '← Zur aktuellen Ausgabe',
  topThemen: 'Top-Themen',
  weiterlesen: 'Weiterlesen →',
  vorherigesTop: 'Vorheriges Top-Thema',
  naechstesTop: 'Nächstes Top-Thema',
  shop: { kennzeichnung: 'Eigenwerbung', titel: 'Morisyen Shop', text: 'Made for Mauritius lovers: T-Shirts, Tassen und mehr mit Dodo, kreolischer Kultur und Inselflair.', knopf: 'Zum Shop →' },
};

const fr: OberflaechenTexte = {
  untertitel: 'Le quotidien de Maurice',
  rubrikenLabel: 'Rubriques',
  rubriken: {
    politik: { lang: 'Politique & diplomatie', kurz: 'Politique' },
    wirtschaft: { lang: 'Économie', kurz: 'Économie' },
    soziales: { lang: 'Travail & société', kurz: 'Société' },
    umwelt: { lang: 'Eau, environnement & agriculture', kurz: 'Environnement' },
    justiz: { lang: 'Police & justice', kurz: 'Police & justice' },
    sport: { lang: 'Sport', kurz: 'Sport' },
    alltag: { lang: 'Vie quotidienne & culture', kurz: 'Culture' },
  },
  aufmacher: 'À la une',
  neu: 'Nouveau',
  aktualisiert: 'Mis à jour',
  aelterStand: 'Version précédente',
  quellen: 'Sources :',
  nurDeutsch: 'en allemand uniquement',
  stapelLabel: (titel) => `Articles sur ${titel}, anciens à gauche, le plus récent à droite`,
  aeltere: 'Article précédent',
  neuere: 'Article suivant',
  hinweisEnde: (n) => `← ${n} ${n === 1 ? 'version précédente' : 'versions précédentes'}`,
  hinweisPosition: (p, n) => `Version ${p} sur ${n} · la plus récente à droite`,
  staende: (n) => `${n} versions`,
  themen: (n) => `${n} ${n === 1 ? 'sujet' : 'sujets'}`,
  vortage: 'Des jours précédents · touchez pour déplier',
  videos: 'Vidéos',
  videosHinweis: "S'ouvre dans un nouvel onglet",
  datumUnbekannt: 'date inconnue',
  archiv: 'Archives',
  archivHinweis: (n) => `${n} sujets plus anciens · sans nouvelle depuis 3 jours`,
  stand: (zeit) => `Mis à jour le ${zeit} (heure de Maurice)`,
  keineAusgabe: "Pas encore d'édition",
  leer: "Pas encore d'articles. La première édition paraîtra lors de la prochaine mise à jour automatique.",
  fussnoten: [
    "Gazet Morisyen est mise à jour automatiquement toutes les quatre heures environ. Chaque carte est un sujet : vous voyez d'abord l'article le plus récent, les versions précédentes se trouvent à gauche. Faites glisser ou utilisez la flèche ‹. Les sujets dont le dernier article date d'un jour précédent sont repliés.",
    'Les textes sont des résumés propres, générés automatiquement et sans garantie. Les détails figurent dans les originaux en lien. Les sujets sans nouvel article depuis 3 jours passent aux archives et sont supprimés après 60 jours.',
  ],
  impressum: 'Mentions légales',
  datenschutz: 'Confidentialité',
  teilen: 'Partager',
  linkKopiert: 'Lien copié',
  linkFehler: 'Copie impossible',
  zurAusgabe: "← Vers l'édition du jour",
  topThemen: 'À la une',
  weiterlesen: 'Lire la suite →',
  vorherigesTop: 'Sujet précédent',
  naechstesTop: 'Sujet suivant',
  shop: { kennzeichnung: 'Publicité', titel: 'Morisyen Shop', text: "Made for Mauritius lovers : t-shirts, mugs et plus encore, avec le dodo, la culture créole et l'esprit de l'île.", knopf: 'Vers la boutique →' },
};

const en: OberflaechenTexte = {
  untertitel: 'The daily paper for Mauritius',
  rubrikenLabel: 'Sections',
  rubriken: {
    politik: { lang: 'Politics & diplomacy', kurz: 'Politics' },
    wirtschaft: { lang: 'Economy', kurz: 'Economy' },
    soziales: { lang: 'Work & society', kurz: 'Society' },
    umwelt: { lang: 'Water, environment & farming', kurz: 'Environment' },
    justiz: { lang: 'Police & courts', kurz: 'Police & courts' },
    sport: { lang: 'Sport', kurz: 'Sport' },
    alltag: { lang: 'Daily life & culture', kurz: 'Culture' },
  },
  aufmacher: 'Top story',
  neu: 'New',
  aktualisiert: 'Updated',
  aelterStand: 'Earlier update',
  quellen: 'Sources:',
  nurDeutsch: 'German only',
  stapelLabel: (titel) => `Reports on ${titel}, older on the left, newest on the right`,
  aeltere: 'Earlier report',
  neuere: 'Newer report',
  hinweisEnde: (n) => `← ${n} ${n === 1 ? 'earlier update' : 'earlier updates'}`,
  hinweisPosition: (p, n) => `Update ${p} of ${n} · newest on the right`,
  staende: (n) => `${n} updates`,
  themen: (n) => `${n} ${n === 1 ? 'story' : 'stories'}`,
  vortage: 'From previous days · tap to expand',
  videos: 'Videos',
  videosHinweis: 'Opens in a new tab',
  datumUnbekannt: 'date unknown',
  archiv: 'Archive',
  archivHinweis: (n) => `${n} older stories · no news for 3 days`,
  stand: (zeit) => `Updated ${zeit} (Mauritius time)`,
  keineAusgabe: 'No edition yet',
  leer: 'No reports yet. The first edition will appear at the next automatic update.',
  fussnoten: [
    'Gazet Morisyen updates automatically about every four hours. Each card is a story: you see the newest report first, earlier updates sit to its left. Swipe or use the ‹ arrow to reach them. Stories whose latest report is from a previous day are collapsed.',
    'The texts are our own automatically generated summaries, without guarantee. Details are in the linked originals. Stories with no new report for 3 days move to the archive and are deleted after 60 days.',
  ],
  impressum: 'Legal notice',
  datenschutz: 'Privacy',
  teilen: 'Share',
  linkKopiert: 'Link copied',
  linkFehler: 'Could not copy',
  zurAusgabe: '← To the current edition',
  topThemen: 'Top stories',
  weiterlesen: 'Read more →',
  vorherigesTop: 'Previous top story',
  naechstesTop: 'Next top story',
  shop: { kennzeichnung: 'Advertisement', titel: 'Morisyen Shop', text: 'Made for Mauritius lovers: T-shirts, mugs and more celebrating the Dodo, Mauritian culture and island life.', knopf: 'Visit the shop →' },
};

export const TEXTE: Record<Sprache, OberflaechenTexte> = { de, fr, en };
