/**
 * Baut die Newsletter-Mail aus der aktuellen Ausgabe.
 *
 * Eine Mail enthält alle drei Sprachen; Brevo wählt beim Versand per
 * Vorlagen-Bedingung den Block passend zum Kontakt-Attribut SPRACHE.
 * Alle Inhalte aus den Daten werden maskiert, auch gegen Brevo-Vorlagensyntax.
 */

import { FENSTER_STUNDEN } from './konfiguration';
import type { Versandzeit } from './konfiguration';
import { inhaltFuer, mailHtml } from './mail-html';
import { istAktiv, istImTopBereich } from '@/lib/zeitung/ausgabe';
import type { Thema, ZeitungDaten } from '@/lib/zeitung/types';
import type { Wetter } from '@/lib/zeitung/wetter';

const STUNDE_MS = 3_600_000;

export interface MailAusgabe {
  betreff: string;
  html: string;
  anzahlThemen: number;
}

/** Themen für eine Versandzeit: Top-Themen und alles, was im Zeitfenster neu oder aktualisiert ist. */
export function themenFuerMail(daten: ZeitungDaten, zeit: Versandzeit, jetzt: number): { top: Thema[]; neu: Thema[] } {
  const seit = jetzt - FENSTER_STUNDEN[zeit] * STUNDE_MS;
  const imFenster = (t: Thema) => Date.parse(t.aktualisiert) >= seit && Date.parse(t.aktualisiert) <= jetzt;
  const sortiert = [...daten.themen].sort((a, b) => Date.parse(b.aktualisiert) - Date.parse(a.aktualisiert));
  const top = sortiert.filter((t) => istImTopBereich(t, jetzt) && (zeit === 'morgen' || imFenster(t)));
  const neu = sortiert.filter((t) => !top.includes(t) && istAktiv(t, jetzt) && imFenster(t));
  return { top, neu };
}

const BETREFF_DATUM = new Intl.DateTimeFormat('de-DE', { timeZone: 'Indian/Mauritius', day: '2-digit', month: '2-digit' });
const BETREFF_ZEIT: Record<Versandzeit, string> = { morgen: 'Morgen · Matin · Morning', mittag: 'Mittag · Midi · Noon', abend: 'Abend · Soir · Evening' };

/**
 * Baut die Mail; gibt `undefined` zurück, wenn es mittags oder abends
 * nichts Neues gibt (dann wird nichts verschickt).
 */
export function baueMail(daten: ZeitungDaten, wetter: Wetter | undefined, zeit: Versandzeit, jetzt: number): MailAusgabe | undefined {
  const { top, neu } = themenFuerMail(daten, zeit, jetzt);
  const ticker = Boolean(daten.ticker);
  if (zeit !== 'morgen' && top.length === 0 && neu.length === 0 && !ticker) return undefined;
  if (top.length === 0 && neu.length === 0 && !ticker) return undefined;
  const einleitung =
    daten.einleitung && jetzt - Date.parse(daten.einleitung.zeit) < FENSTER_STUNDEN[zeit] * STUNDE_MS
      ? daten.einleitung
      : undefined;
  const html = mailHtml({
    de: inhaltFuer('de', { top, neu, wetter, einleitung, ticker: daten.ticker, jetzt }),
    fr: inhaltFuer('fr', { top, neu, wetter, einleitung, ticker: daten.ticker, jetzt }),
    en: inhaltFuer('en', { top, neu, wetter, einleitung, ticker: daten.ticker, jetzt }),
  });
  return {
    betreff: `Gazet Morisyen · ${BETREFF_DATUM.format(new Date(jetzt))} · ${BETREFF_ZEIT[zeit]}`,
    html,
    anzahlThemen: top.length + neu.length,
  };
}
