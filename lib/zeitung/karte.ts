/**
 * Insel-Piktogramm: Umriss (Natural Earth, gemeinfrei) und Lage des Orts.
 * Dieselben Daten nutzt die Video-Sendung (sendung/erzeuge_sendung.py).
 */

import inselDaten from './inseln.json';
import ortDaten from './orte.json';
import type { InselId, Thema } from './types';

export interface Kartenort {
  insel: InselId;
  /** Lage der Nadel im Piktogramm (0–100), fehlt bei „nur Insel“. */
  nadel?: { x: number; y: number };
  name?: string;
}

export interface InselForm {
  pfad: string;
  breite: number;
  hoehe: number;
}

const INSELN = inselDaten.inseln as Record<InselId, { name: string; umriss: number[][] }>;
const ORTE = ortDaten.orte as unknown as Record<string, [InselId, number, number]>;
const NUR_INSEL = ortDaten.inseln as Record<string, InselId>;

const RAND = 4;
const KANTE = 100;

function projektion(insel: InselId) {
  const ring = INSELN[insel].umriss;
  const xs = ring.map(([x]) => x);
  const ys = ring.map(([, y]) => y);
  const k = Math.cos((ys.reduce((a, b) => a + b, 0) / ys.length) * (Math.PI / 180));
  const minx = Math.min(...xs);
  const maxx = Math.max(...xs);
  const miny = Math.min(...ys);
  const maxy = Math.max(...ys);
  const m = (KANTE - 2 * RAND) / Math.max((maxx - minx) * k, maxy - miny);
  const breite = (maxx - minx) * k * m + 2 * RAND;
  const hoehe = (maxy - miny) * m + 2 * RAND;
  const punkt = (lon: number, lat: number) => ({ x: RAND + (lon - minx) * k * m, y: RAND + (maxy - lat) * m });
  return { ring, breite, hoehe, punkt };
}

function chaikin(punkte: { x: number; y: number }[], runden: number) {
  let p = punkte;
  for (let r = 0; r < runden; r += 1) {
    const neu: { x: number; y: number }[] = [];
    p.forEach((a, i) => {
      const b = p[(i + 1) % p.length];
      neu.push({ x: 0.75 * a.x + 0.25 * b.x, y: 0.75 * a.y + 0.25 * b.y });
      neu.push({ x: 0.25 * a.x + 0.75 * b.x, y: 0.25 * a.y + 0.75 * b.y });
    });
    p = neu;
  }
  return p;
}

const formCache = new Map<InselId, InselForm>();

export function inselForm(insel: InselId): InselForm {
  const vorhanden = formCache.get(insel);
  if (vorhanden) return vorhanden;
  const { ring, breite, hoehe, punkt } = projektion(insel);
  const pts = chaikin(ring.map(([lon, lat]) => punkt(lon, lat)), 2);
  const pfad = `M${pts.map((q) => `${q.x.toFixed(1)} ${q.y.toFixed(1)}`).join('L')}Z`;
  const form = { pfad, breite, hoehe };
  formCache.set(insel, form);
  return form;
}

/** Ort eines Themas für die Karte: thema.koordinaten, sonst die Ortsliste; ohne bekannten Ort undefined. */
export function kartenort(thema: Thema): Kartenort | undefined {
  if (thema.koordinaten) {
    const { insel, lat, lon } = thema.koordinaten;
    return { insel, nadel: projektion(insel).punkt(lon, lat), name: thema.ort };
  }
  const ort = thema.ort?.trim();
  if (!ort) return undefined;
  const eintrag = ORTE[ort];
  if (eintrag) {
    const [insel, lat, lon] = eintrag;
    return { insel, nadel: projektion(insel).punkt(lon, lat), name: ort };
  }
  const insel = NUR_INSEL[ort];
  return insel ? { insel } : undefined;
}
