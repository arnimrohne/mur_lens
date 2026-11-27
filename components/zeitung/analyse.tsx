'use client';

import { useEffect, useState } from 'react';

import { useZeitungSprache } from '@/hooks/use-zeitung-sprache';
import {
  GA_ID,
  istGaId,
  leseZustimmung,
  loescheGaCookies,
  speichereZustimmung,
  ZUSTIMMUNG_OEFFNEN,
} from '@/lib/zeitung/zustimmung';
import type { Zustimmung } from '@/lib/zeitung/zustimmung';
import type { Sprache } from '@/lib/zeitung/types';

const TEXTE: Record<Sprache, { titel: string; text: string; ja: string; nein: string; mehr: string }> = {
  de: {
    titel: 'Reichweitenmessung',
    text: 'Dürfen wir mit Google Analytics zählen, welche Seiten gelesen werden? Dafür setzt Google Cookies und verarbeitet Nutzungsdaten, auch in den USA. Sie können die Wahl jederzeit unten auf der Seite ändern.',
    ja: 'Zustimmen',
    nein: 'Ablehnen',
    mehr: 'Datenschutz',
  },
  fr: {
    titel: 'Mesure d’audience',
    text: 'Pouvons-nous compter avec Google Analytics les pages lues ? Google dépose pour cela des cookies et traite des données d’utilisation, y compris aux États-Unis. Vous pouvez modifier ce choix à tout moment en bas de page.',
    ja: 'Accepter',
    nein: 'Refuser',
    mehr: 'Confidentialité',
  },
  en: {
    titel: 'Audience measurement',
    text: 'May we use Google Analytics to count which pages are read? Google sets cookies for this and processes usage data, including in the USA. You can change your choice at any time at the bottom of the page.',
    ja: 'Accept',
    nein: 'Decline',
    mehr: 'Privacy',
  },
};

declare global {
  interface Window {
    dataLayer?: unknown[];
    gtag?: (...args: unknown[]) => void;
  }
}

let geladen = false;

function ladeGoogleAnalytics(id: string): void {
  if (geladen) return;
  geladen = true;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag() {
    // gtag erwartet das arguments-Objekt, kein Array.
    // eslint-disable-next-line prefer-rest-params
    window.dataLayer!.push(arguments);
  };
  window.gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'granted',
  });
  window.gtag('js', new Date());
  window.gtag('config', id, { allow_google_signals: false, allow_ad_personalization_signals: false });
  const skript = document.createElement('script');
  skript.async = true;
  skript.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`;
  document.head.appendChild(skript);
}

/** Zustimmungs-Banner; lädt Google Analytics erst nach „Zustimmen“. */
export function Analyse() {
  const [sprache] = useZeitungSprache();
  const [wahl, setzeWahl] = useState<Zustimmung | undefined>();
  const [offen, setzeOffen] = useState(false);
  const aktiv = istGaId(GA_ID);

  useEffect(() => {
    if (!aktiv) return;
    const gespeichert = leseZustimmung();
    setzeWahl(gespeichert);
    setzeOffen(!gespeichert);
    if (gespeichert === 'ja') ladeGoogleAnalytics(GA_ID);
    const oeffnen = () => setzeOffen(true);
    window.addEventListener(ZUSTIMMUNG_OEFFNEN, oeffnen);
    return () => window.removeEventListener(ZUSTIMMUNG_OEFFNEN, oeffnen);
  }, [aktiv]);

  if (!aktiv || !offen) return null;
  const t = TEXTE[sprache];

  const entscheide = (neu: Zustimmung) => {
    speichereZustimmung(neu);
    setzeOffen(false);
    if (neu === 'ja') {
      setzeWahl(neu);
      ladeGoogleAnalytics(GA_ID);
      return;
    }
    if (wahl === 'ja') {
      // Widerruf: Cookies löschen und neu laden, damit das Skript nicht weiterläuft.
      loescheGaCookies();
      window.location.reload();
      return;
    }
    setzeWahl(neu);
  };

  return (
    <div className="gz-zustimmung" role="dialog" aria-labelledby="gz-zustimmung-titel" aria-live="polite">
      <div className="gz-zustimmung-inhalt">
        <p className="gz-zustimmung-titel" id="gz-zustimmung-titel">{t.titel}</p>
        <p className="gz-zustimmung-text">
          {t.text} <a href="/zeitung/datenschutz#analytics">{t.mehr}</a>
        </p>
        <div className="gz-zustimmung-knoepfe">
          <button type="button" onClick={() => entscheide('nein')}>{t.nein}</button>
          <button type="button" onClick={() => entscheide('ja')}>{t.ja}</button>
        </div>
      </div>
    </div>
  );
}

/** Fußzeilen-Link, der das Banner wieder öffnet. */
export function ZustimmungLink({ text }: { text: string }) {
  if (!istGaId(GA_ID)) return null;
  return (
    <button type="button" className="gz-link-knopf" onClick={() => window.dispatchEvent(new Event(ZUSTIMMUNG_OEFFNEN))}>
      {text}
    </button>
  );
}
