/**
 * Regionalkarte für Dossiers: Küsten des westlichen Indischen Ozeans (Natural Earth 1:10m, gemeinfrei),
 * flächentreu genug für kleine Ausschnitte (Plattkarte mit Breitenkorrektur).
 */

import region from './region-indischer-ozean.json';
import type { DossierKarte } from './types';

const LAND = region.land as number[][][];
const BREITE = 640;

export interface KartenGeometrie {
  breite: number;
  hoehe: number;
  landPfad: string;
  punkt: (lon: number, lat: number) => { x: number; y: number };
}

export function kartenGeometrie(karte: DossierKarte): KartenGeometrie {
  const [w, s, o, n] = karte.ausschnitt;
  const k = Math.cos((((s + n) / 2) * Math.PI) / 180);
  const m = BREITE / ((o - w) * k);
  const hoehe = Math.round((n - s) * m);
  const punkt = (lon: number, lat: number) => ({ x: (lon - w) * k * m, y: (n - lat) * m });
  const rand = 1;
  const teile: string[] = [];
  for (const ring of LAND) {
    const xs = ring.map(([lon]) => lon);
    const ys = ring.map(([, lat]) => lat);
    if (Math.max(...xs) < w - rand || Math.min(...xs) > o + rand || Math.max(...ys) < s - rand || Math.min(...ys) > n + rand) continue;
    teile.push(`M${ring.map(([lon, lat]) => {
      const p = punkt(lon, lat);
      return `${p.x.toFixed(1)} ${p.y.toFixed(1)}`;
    }).join('L')}Z`);
  }
  return { breite: BREITE, hoehe, landPfad: teile.join(''), punkt };
}

/** Großkreis-Entfernung in Kilometern. */
export function entfernungKm(a: { lat: number; lon: number }, b: { lat: number; lon: number }): number {
  const r = Math.PI / 180;
  const dLat = (b.lat - a.lat) * r;
  const dLon = (b.lon - a.lon) * r;
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(dLon / 2) ** 2;
  return 6371 * 2 * Math.asin(Math.sqrt(h));
}
