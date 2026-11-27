/**
 * Prüft die Rohdaten aus `daten.json` und wandelt sie in Domain-Objekte um.
 *
 * Die Datei wird automatisch erzeugt. Ungültige Einträge werden deshalb
 * verworfen statt die ganze Seite zu blockieren.
 */

import { RUBRIK_IDS } from './types';
import type {
  Einleitung,
  Grafik,
  GrafikWert,
  Mehrsprachig,
  Meldung,
  MeldungUebersetzung,
  Quelle,
  RubrikId,
  Thema,
  Video,
  VideoUebersetzung,
  ZeitungDaten,
} from './types';

type Roh = Record<string, unknown>;

function istObjekt(wert: unknown): wert is Roh {
  return typeof wert === 'object' && wert !== null && !Array.isArray(wert);
}

function text(wert: unknown): string | undefined {
  return typeof wert === 'string' && wert.trim() !== '' ? wert : undefined;
}

function istGueltigeZeit(wert: unknown): wert is string {
  return typeof wert === 'string' && !Number.isNaN(Date.parse(wert));
}

/** Nur https-Links werden übernommen. */
export function sichereUrl(wert: unknown): string | undefined {
  return typeof wert === 'string' && wert.startsWith('https://') ? wert : undefined;
}

function parseQuellen(wert: unknown): Quelle[] {
  if (!Array.isArray(wert)) return [];
  return wert.flatMap((eintrag): Quelle[] => {
    if (!istObjekt(eintrag)) return [];
    const url = sichereUrl(eintrag.url);
    return url ? [{ name: text(eintrag.name) ?? 'Quelle', url }] : [];
  });
}

function parseMeldungI18n(wert: unknown): Meldung['i18n'] {
  if (!istObjekt(wert)) return {};
  const ergebnis: Meldung['i18n'] = {};
  for (const sprache of ['fr', 'en'] as const) {
    const roh = wert[sprache];
    if (!istObjekt(roh)) continue;
    const uebersetzung: MeldungUebersetzung = {
      titel: text(roh.titel),
      text: text(roh.text),
      zeitText: text(roh.zeitText),
    };
    ergebnis[sprache] = uebersetzung;
  }
  return ergebnis;
}

/** Text oder {de, fr, en}; fehlende Sprachen übernehmen den deutschen bzw. ersten vorhandenen Wert. */
function mehrsprachig(wert: unknown): Mehrsprachig | undefined {
  if (typeof wert === 'string') return text(wert) ? { de: wert, fr: wert, en: wert } : undefined;
  if (!istObjekt(wert)) return undefined;
  const basis = text(wert.de) ?? text(wert.fr) ?? text(wert.en);
  if (!basis) return undefined;
  return { de: text(wert.de) ?? basis, fr: text(wert.fr) ?? basis, en: text(wert.en) ?? basis };
}

/** Balkendiagramm: 2–5 Werte ≥ 0, jeder mit Beschriftung; sonst wird die Grafik verworfen. */
export function parseGrafik(wert: unknown): Grafik | undefined {
  if (!istObjekt(wert) || (wert.art !== undefined && wert.art !== 'balken')) return undefined;
  if (!Array.isArray(wert.werte) || wert.werte.length < 2 || wert.werte.length > 5) return undefined;
  const werte: GrafikWert[] = [];
  for (const roh of wert.werte) {
    if (!istObjekt(roh) || typeof roh.wert !== 'number' || !Number.isFinite(roh.wert) || roh.wert < 0) return undefined;
    const label = mehrsprachig(roh.label);
    if (!label) return undefined;
    werte.push({ wert: roh.wert, label, hervor: roh.hervor === true });
  }
  const kz = istObjekt(wert.kennzahl) ? mehrsprachig(wert.kennzahl.wert) : undefined;
  const max = typeof wert.max === 'number' && Number.isFinite(wert.max) && wert.max > 0 ? wert.max : undefined;
  return {
    art: 'balken',
    einheit: mehrsprachig(wert.einheit) ?? { de: '', fr: '', en: '' },
    max,
    titel: mehrsprachig(wert.titel),
    kennzahl: kz && istObjekt(wert.kennzahl) ? { wert: kz, text: mehrsprachig(wert.kennzahl.text) } : undefined,
    werte,
    quelle: text(wert.quelle),
  };
}

function parseMeldung(wert: unknown): Meldung | undefined {
  if (!istObjekt(wert) || !istGueltigeZeit(wert.zeit)) return undefined;
  const titel = text(wert.titel);
  if (!titel) return undefined;
  return {
    zeit: wert.zeit,
    nurDatum: wert.nurDatum === true,
    zeitText: text(wert.zeitText),
    titel,
    text: text(wert.text) ?? '',
    quellen: parseQuellen(wert.quellen),
    i18n: parseMeldungI18n(wert.i18n),
    grafik: parseGrafik(wert.grafik),
  };
}

function istRubrik(wert: unknown): wert is RubrikId {
  return typeof wert === 'string' && (RUBRIK_IDS as readonly string[]).includes(wert);
}

function parseThema(wert: unknown): Thema | undefined {
  if (!istObjekt(wert) || !istRubrik(wert.rubrik)) return undefined;
  const id = text(wert.id);
  const updates = Array.isArray(wert.updates)
    ? wert.updates.flatMap((u) => parseMeldung(u) ?? [])
    : [];
  if (!id || updates.length === 0) return undefined;
  updates.sort((a, b) => Date.parse(b.zeit) - Date.parse(a.zeit));
  const neueste = updates[0];
  return {
    id,
    rubrik: wert.rubrik,
    titel: text(wert.titel) ?? neueste.titel,
    status: wert.status === 'archiv' ? 'archiv' : 'aktiv',
    erstellt: istGueltigeZeit(wert.erstellt) ? wert.erstellt : updates[updates.length - 1].zeit,
    aktualisiert: istGueltigeZeit(wert.aktualisiert) ? wert.aktualisiert : neueste.zeit,
    top: wert.top === true,
    warTop: wert.warTop === true || wert.top === true,
    topSeit: istGueltigeZeit(wert.topSeit) ? wert.topSeit : undefined,
    ort: text(wert.ort),
    koordinaten: parseKoordinaten(wert.koordinaten),
    updates,
  };
}

function parseKoordinaten(wert: unknown): Thema['koordinaten'] {
  if (!istObjekt(wert)) return undefined;
  const { insel, lat, lon } = wert;
  if (insel !== 'mauritius' && insel !== 'rodrigues' && insel !== 'reunion') return undefined;
  if (typeof lat !== 'number' || typeof lon !== 'number' || !Number.isFinite(lat) || !Number.isFinite(lon)) return undefined;
  return { insel, lat, lon };
}

function parseVideoI18n(wert: unknown): Video['i18n'] {
  if (!istObjekt(wert)) return {};
  const ergebnis: Video['i18n'] = {};
  for (const sprache of ['fr', 'en'] as const) {
    const roh = wert[sprache];
    if (!istObjekt(roh)) continue;
    const uebersetzung: VideoUebersetzung = {
      titel: text(roh.titel),
      beschreibung: text(roh.beschreibung),
      datumText: text(roh.datumText),
    };
    ergebnis[sprache] = uebersetzung;
  }
  return ergebnis;
}

function parseVideo(wert: unknown): Video | undefined {
  if (!istObjekt(wert)) return undefined;
  const id = text(wert.id);
  const url = sichereUrl(wert.url);
  const titel = text(wert.titel);
  if (!id || !url || !titel) return undefined;
  return {
    id,
    titel,
    beschreibung: text(wert.beschreibung) ?? '',
    url,
    quelle: text(wert.quelle) ?? 'Video',
    reihenfolge: typeof wert.reihenfolge === 'number' ? wert.reihenfolge : 99,
    datum: istGueltigeZeit(wert.datum) ? wert.datum : undefined,
    datumText: text(wert.datumText),
    i18n: parseVideoI18n(wert.i18n),
  };
}

function parseEinleitung(wert: unknown): Einleitung | undefined {
  if (!istObjekt(wert) || !istGueltigeZeit(wert.zeit)) return undefined;
  const de = text(wert.de);
  if (!de) return undefined;
  return { zeit: wert.zeit, texte: { de, fr: text(wert.fr) ?? de, en: text(wert.en) ?? de } };
}

/** Wandelt beliebige JSON-Daten in gültige Zeitungsdaten um. */
export function parseZeitungDaten(roh: unknown): ZeitungDaten {
  if (!istObjekt(roh)) return { stand: '', themen: [], videos: [] };
  const themen = Array.isArray(roh.topics) ? roh.topics.flatMap((t) => parseThema(t) ?? []) : [];
  const videos = Array.isArray(roh.videos) ? roh.videos.flatMap((v) => parseVideo(v) ?? []) : [];
  videos.sort((a, b) => a.reihenfolge - b.reihenfolge);
  return {
    stand: istGueltigeZeit(roh.stand) ? roh.stand : '',
    einleitung: parseEinleitung(roh.einleitung),
    themen,
    videos,
  };
}
