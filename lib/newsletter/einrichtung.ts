/**
 * Einrichtung in Brevo: Kontaktfelder, drei Listen und die Vorlage der
 * Bestätigungsmail. Alles wird über feste Namen gefunden oder angelegt,
 * sodass keine Kennungen im Code stehen müssen. Mehrfaches Ausführen ist unschädlich.
 */

import { brevo, BrevoFehler } from './brevo-api';
import { ABSENDER, ALLE_VERSANDZEITEN } from './konfiguration';
import type { Versandzeit } from './konfiguration';

export const LISTEN_NAMEN: Record<Versandzeit, string> = {
  morgen: 'Gazet Morisyen – Morgen (7 Uhr)',
  mittag: 'Gazet Morisyen – Mittag (12 Uhr)',
  abend: 'Gazet Morisyen – Abend (18 Uhr)',
};
export const ORDNER_NAME = 'Gazet Morisyen';
export const DOI_VORLAGE_NAME = 'Gazet Morisyen – Bestätigung (Double-Opt-in)';
const ATTRIBUTE = ['SPRACHE', 'HAEUFIGKEIT', 'SHOP', 'EINSTELLUNGEN'] as const;

export interface BrevoKonfig {
  listen: Record<Versandzeit, number>;
  doiVorlage: number;
}

type Roh = Record<string, unknown>;

function eintraege(antwort: unknown, feld: string): Roh[] {
  const liste = typeof antwort === 'object' && antwort !== null ? (antwort as Roh)[feld] : undefined;
  return Array.isArray(liste) ? liste.filter((e): e is Roh => typeof e === 'object' && e !== null) : [];
}

async function findeListen(): Promise<Partial<Record<Versandzeit, number>>> {
  const listen = eintraege(await brevo('/contacts/lists?limit=50&offset=0', 'GET'), 'lists');
  const ergebnis: Partial<Record<Versandzeit, number>> = {};
  for (const zeit of ALLE_VERSANDZEITEN) {
    const treffer = listen.find((l) => l.name === LISTEN_NAMEN[zeit]);
    if (treffer && typeof treffer.id === 'number') ergebnis[zeit] = treffer.id;
  }
  return ergebnis;
}

async function findeDoiVorlage(): Promise<number | undefined> {
  const vorlagen = eintraege(await brevo('/smtp/templates?templateStatus=true&limit=100&offset=0', 'GET'), 'templates');
  const treffer = vorlagen.find((v) => v.name === DOI_VORLAGE_NAME);
  return treffer && typeof treffer.id === 'number' ? treffer.id : undefined;
}

let zwischenspeicher: { konfig: BrevoKonfig; zeit: number } | undefined;
const GUELTIG_MS = 10 * 60_000;

/** Liest Listen und Vorlage aus Brevo (10 Minuten zwischengespeichert). */
export async function ladeBrevoKonfig(): Promise<BrevoKonfig | undefined> {
  if (zwischenspeicher && Date.now() - zwischenspeicher.zeit < GUELTIG_MS) return zwischenspeicher.konfig;
  const [listen, doiVorlage] = await Promise.all([findeListen(), findeDoiVorlage()]);
  if (!doiVorlage || ALLE_VERSANDZEITEN.some((z) => !listen[z])) return undefined;
  const konfig: BrevoKonfig = { listen: listen as Record<Versandzeit, number>, doiVorlage };
  zwischenspeicher = { konfig, zeit: Date.now() };
  return konfig;
}

async function legeAttributeAn(): Promise<void> {
  for (const name of ATTRIBUTE) {
    try {
      await brevo(`/contacts/attributes/normal/${name}`, 'POST', { type: 'text' });
    } catch (fehler) {
      // 400 = Feld existiert bereits
      if (!(fehler instanceof BrevoFehler && fehler.status === 400)) throw fehler;
    }
  }
}

async function ordnerId(): Promise<number> {
  const ordner = eintraege(await brevo('/contacts/folders?limit=50&offset=0', 'GET'), 'folders');
  const treffer = ordner.find((o) => o.name === ORDNER_NAME);
  if (treffer && typeof treffer.id === 'number') return treffer.id;
  const neu = await brevo('/contacts/folders', 'POST', { name: ORDNER_NAME });
  return Number((neu as Roh).id);
}

function doiHtml(): string {
  const absatz = (text: string) => `<p style="margin:0 0 12px;font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:1.5;color:#14181f;">${text}</p>`;
  const knopf = (text: string) =>
    `<p style="margin:0 0 24px;"><a href="{{ doubleoptin }}" style="display:inline-block;background:#0f6e5c;color:#ffffff;font-family:Helvetica,Arial,sans-serif;font-weight:700;padding:10px 20px;border-radius:999px;text-decoration:none;">${text}</a></p>`;
  return `<!doctype html><html><body style="margin:0;padding:24px;background:#fdfaf5;">
<div style="max-width:560px;margin:0 auto;">
<h1 style="font-family:Helvetica,Arial,sans-serif;font-size:26px;color:#14181f;">Gazet Morisyen</h1>
${absatz('Bitte bestätigen Sie Ihre Anmeldung zum Newsletter von Gazet Morisyen.')}${knopf('Anmeldung bestätigen')}
${absatz("Veuillez confirmer votre inscription à la newsletter de Gazet Morisyen.")}${knopf("Confirmer l'inscription")}
${absatz('Please confirm your subscription to the Gazet Morisyen newsletter.')}${knopf('Confirm subscription')}
${absatz('<span style="color:#6b6357;font-size:13px;">Wenn Sie sich nicht angemeldet haben, ignorieren Sie diese Mail. · Si vous ne vous êtes pas inscrit(e), ignorez cet e-mail. · If you did not sign up, please ignore this email.</span>')}
</div></body></html>`;
}

/** Legt fehlende Felder, Listen und die Bestätigungsvorlage an und gibt die Kennungen zurück. */
export async function richteBrevoEin(): Promise<BrevoKonfig> {
  await legeAttributeAn();
  const vorhanden = await findeListen();
  const fehlend = ALLE_VERSANDZEITEN.filter((z) => !vorhanden[z]);
  if (fehlend.length > 0) {
    const ordner = await ordnerId();
    for (const zeit of fehlend) {
      const neu = await brevo('/contacts/lists', 'POST', { name: LISTEN_NAMEN[zeit], folderId: ordner });
      vorhanden[zeit] = Number((neu as Roh).id);
    }
  }
  let doiVorlage = await findeDoiVorlage();
  if (!doiVorlage) {
    const neu = await brevo('/smtp/templates', 'POST', {
      templateName: DOI_VORLAGE_NAME,
      subject: 'Gazet Morisyen: Bitte bestätigen · Veuillez confirmer · Please confirm',
      sender: ABSENDER,
      htmlContent: doiHtml(),
      isActive: true,
      tag: 'optin',
    });
    doiVorlage = Number((neu as Roh).id);
  }
  zwischenspeicher = undefined;
  return { listen: vorhanden as Record<Versandzeit, number>, doiVorlage };
}
