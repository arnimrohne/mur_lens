/**
 * Stammdaten der Website Gazet Morisyen.
 */

export const SEITEN_NAME = 'Gazet Morisyen';
export const SEITEN_URL = 'https://gazet.morisyen.de';
export const SEITEN_HOST = 'gazet.morisyen.de';

/** YouTube-Kanal mit der täglichen Sendung (leer = Link wird nicht angezeigt). */
export const YOUTUBE_KANAL = 'https://www.youtube.com/channel/UCzsMl1rAgzyy3y2eb04BZPg';

export const SEITEN_BESCHREIBUNG =
  'Nachrichten aus Mauritius auf Deutsch, Französisch und Englisch: Politik, Wirtschaft, Gesellschaft, Umwelt, Sport und Kultur, nach Themen gebündelt und alle vier Stunden aktualisiert.';

export const SUCHBEGRIFFE = [
  'Mauritius Nachrichten',
  'Mauritius News',
  'Actualités Maurice',
  'Île Maurice',
  'Rodrigues',
  'Port-Louis',
  'Mauritius Zeitung',
];

/**
 * Angaben für das Impressum (§ 5 DDG, § 18 MStV).
 * Solange hier etwas fehlt, bleibt die Seite für Suchmaschinen gesperrt
 * (noindex), damit kein öffentliches Angebot ohne Impressum entsteht.
 */
export const IMPRESSUM = {
  name: 'Arnim Rohne',
  anschrift: 'Heinrich-von-Stein-Str. 118, 92342 Freystadt',
  email: 'gazet@morisyen.de',
  verantwortlich: 'Arnim Rohne, Heinrich-von-Stein-Str. 118, 92342 Freystadt',
} as const;

export function impressumVollstaendig(): boolean {
  return Object.values(IMPRESSUM).every((wert) => wert.trim() !== '');
}
