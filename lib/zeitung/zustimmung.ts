/**
 * Einwilligung in Google Analytics (TTDSG § 25, DSGVO Art. 6 Abs. 1 lit. a).
 * Die Wahl liegt nur im Browser (localStorage); ohne „ja“ wird nichts geladen.
 */

export type Zustimmung = 'ja' | 'nein';

export const ZUSTIMMUNG_SCHLUESSEL = 'gazet-analyse';
/** Ereignis, mit dem z. B. der Fußzeilen-Link das Banner erneut öffnet. */
export const ZUSTIMMUNG_OEFFNEN = 'gazet-zustimmung-oeffnen';

/**
 * Google-Tag-Manager-Container (GTM-…) oder GA4-Mess-ID (G-…).
 * Überschreibbar mit NEXT_PUBLIC_GA_ID; leer = Analytics und Banner sind abgeschaltet.
 */
export const GA_ID = (process.env.NEXT_PUBLIC_GA_ID ?? 'GTM-KNGPKGPW').trim();

export function istGaId(id: string): boolean {
  return /^(G|GT|GTM)-[A-Z0-9]{4,12}$/.test(id);
}

export function istTagManager(id: string): boolean {
  return id.startsWith('GTM-');
}

export function leseZustimmung(): Zustimmung | undefined {
  try {
    const wert = window.localStorage.getItem(ZUSTIMMUNG_SCHLUESSEL);
    return wert === 'ja' || wert === 'nein' ? wert : undefined;
  } catch {
    return undefined;
  }
}

export function speichereZustimmung(wert: Zustimmung): void {
  try {
    window.localStorage.setItem(ZUSTIMMUNG_SCHLUESSEL, wert);
  } catch {
    // Speicher gesperrt: Wahl gilt nur für diesen Seitenaufruf.
  }
}

/** Entfernt die Google-Analytics-Cookies (_ga, _ga_<ID>) nach einem Widerruf. */
export function loescheGaCookies(): void {
  const namen = document.cookie
    .split(';')
    .map((c) => c.split('=')[0].trim())
    .filter((n) => n === '_ga' || n.startsWith('_ga_') || n === '_gid');
  const host = window.location.hostname;
  const domains = ['', host, `.${host}`, `.${host.split('.').slice(-2).join('.')}`];
  for (const name of namen) {
    for (const domain of domains) {
      document.cookie = `${name}=; Max-Age=0; path=/${domain ? `; domain=${domain}` : ''}`;
    }
  }
}
