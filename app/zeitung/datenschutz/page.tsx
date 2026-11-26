import type { Metadata } from 'next';

import { IMPRESSUM, SEITEN_NAME } from '@/lib/zeitung/seite';

export const metadata: Metadata = {
  title: 'Datenschutz',
  alternates: { canonical: '/datenschutz' },
};

export default function DatenschutzSeite() {
  const verantwortlich = [IMPRESSUM.name, IMPRESSUM.anschrift, IMPRESSUM.email].filter((s) => s.trim());

  return (
    <main className="gz-rahmen gz-rechtstext">
      <p><a href="/zeitung">← {SEITEN_NAME}</a></p>
      <h1>Datenschutzerklärung</h1>

      <h2>Verantwortlicher</h2>
      <p>
        {verantwortlich.length > 0 ? verantwortlich.join(', ') : <span className="gz-offen">noch nicht ausgefüllt</span>}
      </p>

      <h2>Hosting und Server-Protokolle</h2>
      <p>
        Diese Website wird bei Vercel Inc., 440 N Barranca Ave #4133, Covina, CA 91723, USA, gehostet.
        Beim Aufruf verarbeitet Vercel technisch notwendige Daten wie IP-Adresse, Zeitpunkt, aufgerufene
        Seite und Browserkennung, um die Seite auszuliefern und vor Missbrauch zu schützen
        (Art. 6 Abs. 1 lit. f DSGVO). Die Übermittlung in die USA erfolgt auf Grundlage des
        EU-US Data Privacy Framework bzw. von Standardvertragsklauseln.
      </p>

      <h2>Keine Cookies, kein Tracking</h2>
      <p>
        Diese Website setzt keine Cookies und verwendet keine Analyse- oder Werbedienste.
        Schriftarten werden von unserem eigenen Server geladen, nicht von Google.
      </p>

      <h2>Spracheinstellung</h2>
      <p>
        Wenn Sie eine Sprache wählen, wird diese Wahl ausschließlich in Ihrem Browser gespeichert
        (localStorage), damit die Seite beim nächsten Besuch in Ihrer Sprache erscheint. Diese Angabe
        wird nicht an uns übertragen und lässt sich über die Browser-Einstellungen löschen.
      </p>

      <h2>Externe Links und Videos</h2>
      <p>
        Quellen und Videos sind als einfache Links eingebunden. Erst wenn Sie einen Link anklicken,
        stellt Ihr Browser eine Verbindung zum jeweiligen Anbieter her (z. B. YouTube, Nachrichtenseiten);
        dort gelten deren Datenschutzbestimmungen.
      </p>

      <h2>Ihre Rechte</h2>
      <p>
        Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung,
        Widerspruch sowie auf Beschwerde bei einer Datenschutz-Aufsichtsbehörde.
      </p>
    </main>
  );
}
