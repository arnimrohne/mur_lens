/**
 * Texte für Newsletter-Anmeldung und Mail in Deutsch, Französisch und Englisch.
 */

import type { Sprache } from '@/lib/zeitung/types';

export interface NewsletterTexte {
  titel: string;
  beschreibung: string;
  email: string;
  haeufigkeit: string;
  optionen: Record<'1' | '2' | '3', string>;
  shop: string;
  einwilligung: string;
  datenschutzLink: string;
  anmelden: string;
  sendet: string;
  erfolg: string;
  fehler: string;
  ungueltig: string;
  baldVerfuegbar: string;
  // Mail
  kurz: string;
  weitere: string;
  alles: string;
  grund: string;
  einstellungen: string;
  abmelden: string;
  // Einstellungen / Bestätigung
  einstellungenTitel: string;
  speichern: string;
  gespeichert: string;
  linkUngueltig: string;
  bestaetigtTitel: string;
  bestaetigtText: string;
}

const de: NewsletterTexte = {
  titel: 'Gazet Morisyen per E-Mail',
  beschreibung: 'Die wichtigsten Nachrichten aus Mauritius, kurz zusammengefasst – so oft Sie möchten.',
  email: 'E-Mail-Adresse',
  haeufigkeit: 'Wie oft?',
  optionen: { '1': '1× täglich (7 Uhr)', '2': '2× täglich (7 und 18 Uhr)', '3': '3× täglich (7, 12 und 18 Uhr)' },
  shop: 'Ich möchte auch gelegentlich Hinweise auf den Morisyen-Shop erhalten (freiwillig).',
  einwilligung: 'Ich möchte den Newsletter erhalten. Die Einwilligung kann ich jederzeit über den Link in jeder Mail widerrufen.',
  datenschutzLink: 'Datenschutz',
  anmelden: 'Anmelden',
  sendet: 'Wird gesendet …',
  erfolg: 'Fast geschafft: Bitte bestätigen Sie die Anmeldung über den Link in der E-Mail, die wir Ihnen gerade geschickt haben.',
  fehler: 'Die Anmeldung hat nicht geklappt. Bitte versuchen Sie es später noch einmal.',
  ungueltig: 'Bitte geben Sie eine gültige E-Mail-Adresse an und bestätigen Sie die Einwilligung.',
  baldVerfuegbar: 'Der Newsletter startet in Kürze.',
  kurz: 'Das Wichtigste in Kürze',
  weitere: 'Weitere Meldungen',
  alles: 'Alle Meldungen auf gazet.morisyen.de →',
  grund: 'Sie erhalten diese Mail, weil Sie den Newsletter von Gazet Morisyen bestellt haben. Uhrzeiten: Ortszeit Mauritius.',
  einstellungen: 'Häufigkeit oder Sprache ändern',
  abmelden: 'Abmelden',
  einstellungenTitel: 'Newsletter-Einstellungen',
  speichern: 'Speichern',
  gespeichert: 'Gespeichert. Ihre Einstellungen gelten ab der nächsten Ausgabe.',
  linkUngueltig: 'Dieser Link ist ungültig oder abgelaufen. Bitte nutzen Sie den Link aus einer aktuellen Newsletter-Mail.',
  bestaetigtTitel: 'Anmeldung bestätigt',
  bestaetigtText: 'Vielen Dank! Sie erhalten Gazet Morisyen ab der nächsten Ausgabe per E-Mail.',
};

const fr: NewsletterTexte = {
  titel: 'Gazet Morisyen par e-mail',
  beschreibung: "L'essentiel de l'actualité mauricienne, en bref – aussi souvent que vous le souhaitez.",
  email: 'Adresse e-mail',
  haeufigkeit: 'À quelle fréquence ?',
  optionen: { '1': '1× par jour (7 h)', '2': '2× par jour (7 h et 18 h)', '3': '3× par jour (7 h, 12 h et 18 h)' },
  shop: "Je souhaite aussi recevoir de temps en temps des nouvelles de la boutique Morisyen (facultatif).",
  einwilligung: 'Je souhaite recevoir la newsletter. Je peux retirer mon consentement à tout moment via le lien présent dans chaque e-mail.',
  datenschutzLink: 'Confidentialité',
  anmelden: "S'inscrire",
  sendet: 'Envoi …',
  erfolg: "Presque terminé : veuillez confirmer votre inscription via le lien de l'e-mail que nous venons de vous envoyer.",
  fehler: "L'inscription n'a pas fonctionné. Veuillez réessayer plus tard.",
  ungueltig: 'Veuillez saisir une adresse e-mail valide et confirmer votre consentement.',
  baldVerfuegbar: 'La newsletter démarre prochainement.',
  kurz: "L'essentiel en bref",
  weitere: 'Autres articles',
  alles: 'Tous les articles sur gazet.morisyen.de →',
  grund: "Vous recevez cet e-mail car vous êtes inscrit(e) à la newsletter de Gazet Morisyen. Heures : heure de Maurice.",
  einstellungen: 'Modifier la fréquence ou la langue',
  abmelden: 'Se désinscrire',
  einstellungenTitel: 'Paramètres de la newsletter',
  speichern: 'Enregistrer',
  gespeichert: 'Enregistré. Vos paramètres s’appliquent dès la prochaine édition.',
  linkUngueltig: "Ce lien n'est pas valide. Veuillez utiliser le lien d'une newsletter récente.",
  bestaetigtTitel: 'Inscription confirmée',
  bestaetigtText: 'Merci ! Vous recevrez Gazet Morisyen par e-mail dès la prochaine édition.',
};

const en: NewsletterTexte = {
  titel: 'Gazet Morisyen by email',
  beschreibung: 'The most important news from Mauritius, in brief – as often as you like.',
  email: 'Email address',
  haeufigkeit: 'How often?',
  optionen: { '1': 'Once a day (7 am)', '2': 'Twice a day (7 am and 6 pm)', '3': 'Three times a day (7 am, noon and 6 pm)' },
  shop: 'I would also like occasional news about the Morisyen shop (optional).',
  einwilligung: 'I want to receive the newsletter. I can withdraw my consent at any time via the link in every email.',
  datenschutzLink: 'Privacy',
  anmelden: 'Subscribe',
  sendet: 'Sending …',
  erfolg: 'Almost done: please confirm your subscription via the link in the email we have just sent you.',
  fehler: 'Subscription did not work. Please try again later.',
  ungueltig: 'Please enter a valid email address and confirm your consent.',
  baldVerfuegbar: 'The newsletter is starting soon.',
  kurz: 'In brief',
  weitere: 'More stories',
  alles: 'All stories on gazet.morisyen.de →',
  grund: 'You are receiving this email because you subscribed to the Gazet Morisyen newsletter. Times: Mauritius time.',
  einstellungen: 'Change frequency or language',
  abmelden: 'Unsubscribe',
  einstellungenTitel: 'Newsletter settings',
  speichern: 'Save',
  gespeichert: 'Saved. Your settings apply from the next edition.',
  linkUngueltig: 'This link is invalid. Please use the link from a recent newsletter email.',
  bestaetigtTitel: 'Subscription confirmed',
  bestaetigtText: 'Thank you! You will receive Gazet Morisyen by email from the next edition.',
};

export const MAIL_TEXTE: Record<Sprache, NewsletterTexte> = { de, fr, en };
