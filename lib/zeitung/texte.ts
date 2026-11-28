/**
 * Feste Texte der Oberfläche in Deutsch, Französisch und Englisch.
 */

import type { InselId, RubrikId, Sprache } from './types';
import type { WetterArt } from './wetter';

export interface OberflaechenTexte {
  untertitel: string;
  rubrikenLabel: string;
  rubriken: Record<RubrikId, { lang: string; kurz: string }>;
  aufmacher: string;
  neu: string;
  aktualisiert: string;
  aelterStand: string;
  bisherigeMeldungen: (anzahl: number) => string;
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
  sendungAbo: string;
  inseln: Record<InselId, string>;
  sendungAboHinweis: string;
  datumUnbekannt: string;
  archiv: string;
  archivHinweis: (anzahl: number) => string;
  stand: (zeit: string) => string;
  keineAusgabe: string;
  leer: string;
  fussnoten: string[];
  impressum: string;
  datenschutz: string;
  nutzungsbedingungen: string;
  youtube: string;
  analyseEinstellungen: string;
  teilen: string;
  linkKopiert: string;
  linkFehler: string;
  zurAusgabe: string;
  dossiers: string;
  dossiersUntertitel: string;
  ticker: string;
  tickerOrtszeit: string;
  tickerAeltere: (anzahl: number) => string;
  hintergrund: string;
  dossierAbschnitte: { kurz: string; warum: string; chronik: string; entwicklung: string; akteure: string; zahlen: string; offen: string; aktuell: string; quellen: string };
  dossierStand: (datum: string) => string;
  dossierVideo: string;
  hintergrundVideo: string;
  dossierVideoStart: string;
  dossierVideoHinweis: string;
  dossierVideoDatenschutz: string;
  dossierVideoAndereSprache: string;
  alleDossiers: string;
  quelleLink: string;
  keineDossiers: string;
  wetter: {
    titel: string;
    gefuehlt: (grad: number) => string;
    wind: (kmh: number) => string;
    feuchte: (prozent: number) => string;
    aufgang: string;
    untergang: string;
    band: string;
    quelle: string;
    ortszeit: string;
    arten: Record<WetterArt, string>;
  };
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
  bisherigeMeldungen: (n) => (n === 1 ? 'Vorherige Meldung' : `Bisherige Meldungen (${n})`),
  quellen: 'Quellen:',
  nurDeutsch: 'nur auf Deutsch',
  stapelLabel: (titel) => `Meldungen zu ${titel}, ältere links, neueste rechts`,
  aeltere: 'Ältere Meldung',
  neuere: 'Neuere Meldung',
  hinweisEnde: (n) => `← ${n} ${n === 1 ? 'älterer Stand' : 'ältere Stände'}`,
  hinweisPosition: (p, n) => `Stand ${p} von ${n} · neuester rechts`,
  staende: (n) => `${n} Stände`,
  themen: (n) => `${n} ${n === 1 ? 'Thema' : 'Themen'}`,
  vortage: 'Ältere Meldungen · zum Aufklappen antippen',
  videos: 'Videos',
  videosHinweis: 'Öffnen im neuen Tab',
  inseln: { mauritius: 'Mauritius', rodrigues: 'Rodrigues', reunion: 'La Réunion' },
  sendungAbo: 'Abonnieren Sie unsere tägliche Nachrichtensendung auf YouTube',
  sendungAboHinweis: 'Jeden Morgen die wichtigsten Meldungen auf Deutsch',
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
  nutzungsbedingungen: 'Nutzungsbedingungen',
  youtube: 'Gazet Morisyen auf YouTube',
  analyseEinstellungen: 'Cookie-Einstellungen',
  teilen: 'Teilen',
  linkKopiert: 'Link kopiert',
  linkFehler: 'Kopieren nicht möglich',
  zurAusgabe: '← Zur aktuellen Ausgabe',
  dossiers: 'Dossiers',
  dossiersUntertitel: 'Hintergründe zu Themen, die Mauritius immer wieder beschäftigen',
  ticker: 'Live-Ticker',
  tickerOrtszeit: 'Ortszeit Mauritius',
  tickerAeltere: (n) => (n === 1 ? '1 ältere Meldung' : `${n} ältere Meldungen`),
  hintergrund: 'Hintergrund',
  dossierAbschnitte: { kurz: 'Kurz erklärt', warum: 'Warum es wichtig ist', chronik: 'Chronik', entwicklung: 'Entwicklung und Ursachen', akteure: 'Wer will was', zahlen: 'Zahlen und Fakten', offen: 'Offene Fragen', aktuell: 'Aktuelle Meldungen', quellen: 'Quellen' },
  dossierStand: (datum) => `Stand: ${datum}`,
  dossierVideo: 'Im Video erklärt',
  hintergrundVideo: 'Video & Hintergrund',
  dossierVideoStart: 'Video abspielen',
  dossierVideoHinweis: 'Beim Abspielen wird das Video von YouTube geladen. Dabei werden Daten an YouTube übertragen.',
  dossierVideoDatenschutz: 'Datenschutz',
  dossierVideoAndereSprache: 'Video auf Deutsch',
  alleDossiers: '← Alle Dossiers',
  quelleLink: 'Quelle',
  keineDossiers: 'Noch keine Dossiers.',
  wetter: {
    titel: 'Wetter in Port-Louis',
    gefuehlt: (g) => `gefühlt ${g}°`,
    wind: (v) => `Wind ${v} km/h`,
    feuchte: (p) => `Luftfeuchte ${p} %`,
    aufgang: 'Sonnenaufgang',
    untergang: 'Sonnenuntergang',
    band: 'Die nächsten 24 Stunden',
    quelle: 'Wetterdaten: MET Norway',
    ortszeit: 'Ortszeit Mauritius',
    arten: { klar: 'Klar', heiter: 'Heiter', wolkig: 'Teils bewölkt', bedeckt: 'Bedeckt', nebel: 'Nebel', schauer: 'Schauer', regen: 'Regen', gewitter: 'Gewitter' },
  },
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
  bisherigeMeldungen: (n) => (n === 1 ? 'Article précédent' : `Articles précédents (${n})`),
  quellen: 'Sources :',
  nurDeutsch: 'en allemand uniquement',
  stapelLabel: (titel) => `Articles sur ${titel}, anciens à gauche, le plus récent à droite`,
  aeltere: 'Article précédent',
  neuere: 'Article suivant',
  hinweisEnde: (n) => `← ${n} ${n === 1 ? 'version précédente' : 'versions précédentes'}`,
  hinweisPosition: (p, n) => `Version ${p} sur ${n} · la plus récente à droite`,
  staende: (n) => `${n} versions`,
  themen: (n) => `${n} ${n === 1 ? 'sujet' : 'sujets'}`,
  vortage: 'Plus anciennes · touchez pour déplier',
  videos: 'Vidéos',
  videosHinweis: "S'ouvre dans un nouvel onglet",
  inseln: { mauritius: 'Maurice', rodrigues: 'Rodrigues', reunion: 'La Réunion' },
  sendungAbo: 'Abonnez-vous à notre journal quotidien sur YouTube',
  sendungAboHinweis: "L'essentiel de l'actualité chaque matin, en français",
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
  nutzungsbedingungen: "Conditions d'utilisation",
  youtube: 'Gazet Morisyen sur YouTube',
  analyseEinstellungen: 'Paramètres des cookies',
  teilen: 'Partager',
  linkKopiert: 'Lien copié',
  linkFehler: 'Copie impossible',
  zurAusgabe: "← Vers l'édition du jour",
  dossiers: 'Dossiers',
  dossiersUntertitel: 'Le contexte des sujets qui reviennent sans cesse à Maurice',
  ticker: 'En direct',
  tickerOrtszeit: 'heure de Maurice',
  tickerAeltere: (n) => (n === 1 ? '1 message précédent' : `${n} messages précédents`),
  hintergrund: 'Contexte',
  dossierAbschnitte: { kurz: 'En bref', warum: 'Pourquoi c\'est important', chronik: 'Chronologie', entwicklung: 'Évolution et causes', akteure: 'Qui veut quoi', zahlen: 'Chiffres clés', offen: 'Questions ouvertes', aktuell: 'Actualités', quellen: 'Sources' },
  dossierStand: (datum) => `Mis à jour : ${datum}`,
  dossierVideo: 'En vidéo',
  hintergrundVideo: 'Vidéo et contexte',
  dossierVideoStart: 'Lire la vidéo',
  dossierVideoHinweis: 'En lançant la lecture, la vidéo est chargée depuis YouTube. Des données sont alors transmises à YouTube.',
  dossierVideoDatenschutz: 'Confidentialité',
  dossierVideoAndereSprache: 'Vidéo en allemand',
  alleDossiers: '← Tous les dossiers',
  quelleLink: 'Source',
  keineDossiers: 'Pas encore de dossiers.',
  wetter: {
    titel: 'Météo à Port-Louis',
    gefuehlt: (g) => `ressenti ${g}°`,
    wind: (v) => `Vent ${v} km/h`,
    feuchte: (p) => `Humidité ${p} %`,
    aufgang: 'Lever du soleil',
    untergang: 'Coucher du soleil',
    band: 'Les prochaines 24 heures',
    quelle: 'Données météo : MET Norway',
    ortszeit: 'heure de Maurice',
    arten: { klar: 'Dégagé', heiter: 'Beau temps', wolkig: 'Partiellement nuageux', bedeckt: 'Couvert', nebel: 'Brouillard', schauer: 'Averses', regen: 'Pluie', gewitter: 'Orage' },
  },
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
  bisherigeMeldungen: (n) => (n === 1 ? 'Previous update' : `Earlier updates (${n})`),
  quellen: 'Sources:',
  nurDeutsch: 'German only',
  stapelLabel: (titel) => `Reports on ${titel}, older on the left, newest on the right`,
  aeltere: 'Earlier report',
  neuere: 'Newer report',
  hinweisEnde: (n) => `← ${n} ${n === 1 ? 'earlier update' : 'earlier updates'}`,
  hinweisPosition: (p, n) => `Update ${p} of ${n} · newest on the right`,
  staende: (n) => `${n} updates`,
  themen: (n) => `${n} ${n === 1 ? 'story' : 'stories'}`,
  vortage: 'Older stories · tap to expand',
  videos: 'Videos',
  videosHinweis: 'Opens in a new tab',
  inseln: { mauritius: 'Mauritius', rodrigues: 'Rodrigues', reunion: 'Réunion' },
  sendungAbo: 'Subscribe to our daily news bulletin on YouTube',
  sendungAboHinweis: 'The main stories every morning, in English',
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
  nutzungsbedingungen: 'Terms of use',
  youtube: 'Gazet Morisyen on YouTube',
  analyseEinstellungen: 'Cookie settings',
  teilen: 'Share',
  linkKopiert: 'Link copied',
  linkFehler: 'Could not copy',
  zurAusgabe: '← To the current edition',
  dossiers: 'Explainers',
  dossiersUntertitel: 'Background on the issues that keep coming back in Mauritius',
  ticker: 'Live updates',
  tickerOrtszeit: 'Mauritius time',
  tickerAeltere: (n) => (n === 1 ? '1 earlier update' : `${n} earlier updates`),
  hintergrund: 'Background',
  dossierAbschnitte: { kurz: 'In short', warum: 'Why it matters', chronik: 'Timeline', entwicklung: 'Trends and causes', akteure: 'Who wants what', zahlen: 'Facts and figures', offen: 'Open questions', aktuell: 'Latest news', quellen: 'Sources' },
  dossierStand: (datum) => `Updated: ${datum}`,
  dossierVideo: 'Explained in a video',
  hintergrundVideo: 'Video & background',
  dossierVideoStart: 'Play video',
  dossierVideoHinweis: 'When you press play, the video is loaded from YouTube and data is sent to YouTube.',
  dossierVideoDatenschutz: 'Privacy',
  dossierVideoAndereSprache: 'Video in German',
  alleDossiers: '← All explainers',
  quelleLink: 'Source',
  keineDossiers: 'No explainers yet.',
  wetter: {
    titel: 'Weather in Port Louis',
    gefuehlt: (g) => `feels like ${g}°`,
    wind: (v) => `Wind ${v} km/h`,
    feuchte: (p) => `Humidity ${p}%`,
    aufgang: 'Sunrise',
    untergang: 'Sunset',
    band: 'Next 24 hours',
    quelle: 'Weather data: MET Norway',
    ortszeit: 'Mauritius time',
    arten: { klar: 'Clear', heiter: 'Fair', wolkig: 'Partly cloudy', bedeckt: 'Overcast', nebel: 'Fog', schauer: 'Showers', regen: 'Rain', gewitter: 'Thunderstorm' },
  },
  topThemen: 'Top stories',
  weiterlesen: 'Read more →',
  vorherigesTop: 'Previous top story',
  naechstesTop: 'Next top story',
  shop: { kennzeichnung: 'Advertisement', titel: 'Morisyen Shop', text: 'Made for Mauritius lovers: T-shirts, mugs and more celebrating the Dodo, Mauritian culture and island life.', knopf: 'Visit the shop →' },
};

export const TEXTE: Record<Sprache, OberflaechenTexte> = { de, fr, en };
