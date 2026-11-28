/**
 * HTML der Newsletter-Mail: tabellenbasiert mit Inline-Styles, damit sie
 * in gängigen Mailprogrammen gleich aussieht. Farben aus der Kreol-Farbwelt.
 */

import { IMPRESSUM, SEITEN_NAME, SEITEN_URL, YOUTUBE_PLAYLISTS } from '@/lib/zeitung/seite';
import { meldungText } from '@/lib/zeitung/sprache';
import { themaUrl } from '@/lib/zeitung/teilen';
import { TEXTE } from '@/lib/zeitung/texte';
import type { Einleitung, Sprache, Thema } from '@/lib/zeitung/types';
import type { Wetter } from '@/lib/zeitung/wetter';
import { MAIL_TEXTE } from './texte';

const FARBE = { bg: '#fdfaf5', papier: '#fffdf9', text: '#14181f', leise: '#6b6357', linie: '#ece3d7', gruen: '#0f6e5c', rot: '#c8323c' };
const SCHRIFT = "font-family:Georgia,'Times New Roman',serif;";
const SANS = "font-family:'Segoe UI',Helvetica,Arial,sans-serif;";
const SHOP_URL = 'https://shop.morisyen.de/en-eur';

/** Maskiert HTML und neutralisiert Brevo-Vorlagensyntax ({{ … }}, {% … %}). */
export function maskiere(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/\{/g, '&#123;')
    .replace(/\}/g, '&#125;');
}

interface InhaltDaten {
  top: Thema[];
  neu: Thema[];
  wetter?: Wetter;
  einleitung?: Einleitung;
  jetzt: number;
}

function themaBlock(thema: Thema, sprache: Sprache, istTop: boolean): string {
  const neueste = thema.updates[0];
  const titel = maskiere(meldungText(neueste, 'titel', sprache));
  const anriss = maskiere(meldungText(neueste, 'text', sprache).split(/\n\s*\n/)[0] ?? '');
  const rubrik = maskiere(TEXTE[sprache].rubriken[thema.rubrik].kurz);
  const marke = istTop ? `<span style="color:${FARBE.rot};">${maskiere(TEXTE[sprache].aufmacher)}</span> · ` : '';
  const url = maskiere(themaUrl(thema.id));
  return `<tr><td style="padding:14px 0;border-top:1px solid ${FARBE.linie};">
<div style="${SANS}font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:${FARBE.leise};">${marke}${rubrik}</div>
<a href="${url}" style="${SANS}font-size:${istTop ? 22 : 17}px;font-weight:700;line-height:1.25;color:${FARBE.text};text-decoration:none;display:block;margin:4px 0 6px;">${titel}</a>
<div style="${SCHRIFT}font-size:15px;line-height:1.5;color:${FARBE.text};">${anriss}</div>
<a href="${url}" style="${SANS}font-size:13px;font-weight:700;color:${FARBE.gruen};text-decoration:none;">${maskiere(TEXTE[sprache].weiterlesen)}</a>
</td></tr>`;
}

function wetterZeile(wetter: Wetter, sprache: Sprache): string {
  const t = TEXTE[sprache].wetter;
  const zeit = (iso: string) =>
    new Intl.DateTimeFormat(sprache === 'en' ? 'en-GB' : sprache, { timeZone: 'Indian/Mauritius', hour: '2-digit', minute: '2-digit' }).format(new Date(Date.parse(iso)));
  const sonne = wetter.sonne[0] ? ` · ↑ ${zeit(wetter.sonne[0].aufgang)} · ↓ ${zeit(wetter.sonne[0].untergang)}` : '';
  return `<tr><td style="padding:12px 16px;background:${FARBE.papier};border:1px solid ${FARBE.linie};border-radius:10px;${SANS}font-size:14px;color:${FARBE.text};">
<strong>${maskiere(t.titel)}:</strong> ${Math.round(wetter.aktuell.temperatur)}° · ${maskiere(t.arten[wetter.aktuell.art])}${maskiere(sonne)}
</td></tr><tr><td style="height:8px;"></td></tr>`;
}

/** Ganz oben: Knöpfe zur Zeitung und zur Playlist der Video-Sendung in der Sprache des Empfängers. */
function linkLeiste(sprache: Sprache): string {
  const m = MAIL_TEXTE[sprache];
  const knopf = (url: string, text: string, voll: boolean) =>
    `<a href="${maskiere(url)}" style="display:inline-block;margin:0 8px 8px 0;padding:9px 16px;border-radius:999px;${SANS}font-size:14px;font-weight:700;text-decoration:none;${
      voll ? `background:${FARBE.gruen};color:#ffffff;` : `background:${FARBE.papier};color:${FARBE.rot};border:1px solid ${FARBE.linie};`
    }">${maskiere(text)}</a>`;
  return `<tr><td style="padding:0 0 10px;">${knopf(SEITEN_URL, m.zurZeitung + ' →', true)}${knopf(YOUTUBE_PLAYLISTS[sprache], '▶ ' + m.zurSendung, false)}</td></tr>`;
}

/** Inhalt einer Sprache (ohne Rahmen, Kopf und Fuß). */
export function inhaltFuer(sprache: Sprache, d: InhaltDaten): string {
  const m = MAIL_TEXTE[sprache];
  const teile: string[] = [linkLeiste(sprache)];
  if (d.einleitung) {
    teile.push(`<tr><td style="padding:4px 0 14px;${SCHRIFT}font-size:16px;line-height:1.55;color:${FARBE.text};">
<div style="${SANS}font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:${FARBE.gruen};margin-bottom:4px;">${maskiere(m.kurz)}</div>
${maskiere(d.einleitung.texte[sprache])}</td></tr>`);
  }
  if (d.wetter) teile.push(wetterZeile(d.wetter, sprache));
  d.top.forEach((t) => teile.push(themaBlock(t, sprache, true)));
  if (d.neu.length > 0) {
    teile.push(`<tr><td style="padding:18px 0 4px;${SANS}font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:${FARBE.leise};">${maskiere(m.weitere)}</td></tr>`);
    d.neu.forEach((t) => teile.push(themaBlock(t, sprache, false)));
  }
  teile.push(`<tr><td style="padding:18px 0;"><a href="${SEITEN_URL}" style="${SANS}font-size:14px;font-weight:700;color:${FARBE.gruen};">${maskiere(m.alles)}</a></td></tr>`);
  return teile.join('\n');
}

function fuss(sprache: Sprache): string {
  const m = MAIL_TEXTE[sprache];
  const impressum = [IMPRESSUM.name, IMPRESSUM.anschrift, IMPRESSUM.email].filter((s) => s.trim()).map(maskiere).join(' · ');
  // {{ unsubscribe }} und {{ contact.EINSTELLUNGEN }} sind Brevo-Platzhalter; der Link wird bei der Anmeldung signiert gespeichert.
  const einstellungen = '{{ contact.EINSTELLUNGEN }}';
  return `<p style="margin:0 0 8px;">${maskiere(m.grund)}</p>
<p style="margin:0 0 8px;"><a href="${einstellungen}" style="color:${FARBE.leise};">${maskiere(m.einstellungen)}</a> · <a href="{{ unsubscribe }}" style="color:${FARBE.leise};">${maskiere(m.abmelden)}</a></p>
<p style="margin:0;">${[maskiere(SEITEN_NAME), impressum, `<a href="${SEITEN_URL}/impressum" style="color:${FARBE.leise};">${maskiere(TEXTE[sprache].impressum)}</a>`].filter(Boolean).join(' · ')}</p>`;
}

function shopBlock(sprache: Sprache): string {
  const s = TEXTE[sprache].shop;
  return `<tr><td style="padding:16px;background:${FARBE.gruen};border-radius:10px;${SANS}color:#ffffff;">
<div style="font-size:10px;letter-spacing:.1em;text-transform:uppercase;opacity:.75;">${maskiere(s.kennzeichnung)}</div>
<div style="font-size:18px;font-weight:700;margin:4px 0;">${maskiere(s.titel)}</div>
<div style="font-size:14px;margin-bottom:10px;">${maskiere(s.text)}</div>
<a href="${SHOP_URL}" style="display:inline-block;background:#fdfaf5;color:${FARBE.gruen};font-weight:700;padding:8px 16px;border-radius:999px;text-decoration:none;">${maskiere(s.knopf)}</a>
</td></tr>`;
}

function sprachBlock(sprache: Sprache, inhalt: string): string {
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0">${inhalt}
{% if contact.SHOP == "ja" %}${shopBlock(sprache)}{% endif %}
<tr><td style="padding:20px 0 0;${SANS}font-size:12px;line-height:1.5;color:${FARBE.leise};">${fuss(sprache)}</td></tr></table>`;
}

/** Komplettes Mail-HTML mit allen drei Sprachen, gesteuert über contact.SPRACHE. */
export function mailHtml(inhalte: Record<Sprache, string>): string {
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${SEITEN_NAME}</title></head>
<body style="margin:0;padding:0;background:${FARBE.bg};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:${FARBE.bg};"><tr><td align="center" style="padding:20px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;">
<tr><td style="height:5px;background:linear-gradient(90deg,#c8323c 0 25%,#1f4fa3 25% 50%,#a87c08 50% 75%,#1f8a4c 75%);"></td></tr>
<tr><td style="padding:18px 0 10px;${SANS}font-size:30px;font-weight:800;color:${FARBE.text};">${SEITEN_NAME}</td></tr>
<tr><td>
{% if contact.SPRACHE == "fr" %}${sprachBlock('fr', inhalte.fr)}{% elif contact.SPRACHE == "en" %}${sprachBlock('en', inhalte.en)}{% else %}${sprachBlock('de', inhalte.de)}{% endif %}
</td></tr></table></td></tr></table></body></html>`;
}
