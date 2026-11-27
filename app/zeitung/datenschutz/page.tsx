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

      <h2 id="analytics">Reichweitenmessung mit Google Analytics (nur mit Einwilligung)</h2>
      <p>
        Wenn Sie im Hinweisfenster „Zustimmen“ wählen, nutzen wir Google Analytics 4, einen Dienst der
        Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland. Wir sehen damit, welche Seiten
        wie oft gelesen werden, aus welchen Ländern und mit welchen Gerätetypen. Dafür setzt Google Cookies
        (_ga, _ga_…, Speicherdauer bis zu 2 Jahre) und verarbeitet Nutzungsdaten wie gekürzte IP-Adresse,
        aufgerufene Seiten, Verweildauer, Browser und Gerät. Google kürzt IP-Adressen in der EU; eine Übermittlung
        an Google LLC in den USA ist möglich und erfolgt auf Grundlage des EU-US Data Privacy Framework.
        Google-Signale und Werbefunktionen sind abgeschaltet; die Daten werden nicht mit einem Google-Konto
        verknüpft und von uns nach 14 Monaten gelöscht.
      </p>
      <p>
        Rechtsgrundlage ist Ihre Einwilligung (§ 25 Abs. 1 TDDDG, Art. 6 Abs. 1 lit. a DSGVO). Ohne Zustimmung
        wird Google Analytics nicht geladen. Sie können Ihre Einwilligung jederzeit mit Wirkung für die Zukunft
        über „Cookie-Einstellungen“ unten auf jeder Seite widerrufen; die Analytics-Cookies werden dann gelöscht.
        Weitere Informationen:{' '}
        <a href="https://policies.google.com/privacy" rel="noopener">Datenschutzerklärung von Google</a>.
      </p>
      <p>
        Darüber hinaus setzt diese Website keine Cookies und verwendet keine Werbedienste. Schriftarten werden
        von unserem eigenen Server geladen, nicht von Google.
      </p>

      <h2>Wetterdaten</h2>
      <p>
        Die Wetteranzeige wird von unserem Server beim Norwegischen Meteorologischen Institut
        (MET Norway, api.met.no) abgerufen. Dabei werden keine Daten der Besucherinnen und Besucher
        übermittelt; Ihr Browser verbindet sich nicht mit dem Wetterdienst.
      </p>

      <h2>Newsletter</h2>
      <p>
        Für den Newsletter verarbeiten wir Ihre E-Mail-Adresse sowie Ihre gewählte Sprache, Häufigkeit und,
        falls angekreuzt, Ihre Einwilligung zu Hinweisen auf den Morisyen-Shop (Art. 6 Abs. 1 lit. a DSGVO).
        Die Anmeldung erfolgt im Double-Opt-in-Verfahren: Erst nach Klick auf den Link in der Bestätigungsmail
        sind Sie angemeldet. Versand und Verwaltung der Adressen übernimmt Sendinblue GmbH (Brevo),
        Köpenicker Straße 126, 10179 Berlin, als Auftragsverarbeiter. Brevo protokolliert die Anmeldung und
        Bestätigung (Zeitpunkt, IP-Adresse) als Nachweis der Einwilligung und kann Öffnungen und Klicks
        statistisch auswerten. Sie können sich jederzeit über den Link in jeder Mail abmelden; Ihre Daten werden
        dann aus der Empfängerliste gelöscht bzw. gesperrt, soweit keine Nachweispflichten entgegenstehen.
      </p>

      <h2>Spracheinstellung</h2>
      <p>
        Wenn Sie eine Sprache wählen oder über Google Analytics entscheiden, wird diese Wahl ausschließlich in Ihrem Browser gespeichert
        (localStorage), damit die Seite beim nächsten Besuch in Ihrer Sprache erscheint. Diese Angabe
        wird nicht an uns übertragen und lässt sich über die Browser-Einstellungen löschen.
      </p>

      <h2>Externe Links und Videos</h2>
      <p>
        Quellen und Videos sind als einfache Links eingebunden. Erst wenn Sie einen Link anklicken,
        stellt Ihr Browser eine Verbindung zum jeweiligen Anbieter her (z. B. YouTube, Nachrichtenseiten);
        dort gelten deren Datenschutzbestimmungen.
      </p>

      <h2 id="youtube">YouTube-Kanal und YouTube API Services</h2>
      <p>
        Wir veröffentlichen eine tägliche Nachrichtensendung auf unserem YouTube-Kanal. Die Videos werden von
        unserem Server automatisch über die YouTube API Services (ein Dienst von Google) hochgeladen und in
        Playlists sortiert. Dabei verwenden wir ausschließlich den Zugang zu unserem eigenen Kanal. Daten von
        Besucherinnen und Besuchern dieser Website oder von anderen YouTube-Nutzern werden über die API weder
        abgerufen noch gespeichert oder weitergegeben. Gelesen wird nur die Liste unserer eigenen Uploads und
        Playlists, um doppelte Uploads zu vermeiden; diese Angaben werden nach dem jeweiligen Lauf nicht
        aufbewahrt.
      </p>
      <p>
        Wer unsere Videos auf YouTube ansieht, nutzt YouTube. Es gelten die{' '}
        <a href="https://www.youtube.com/t/terms" rel="noopener">Nutzungsbedingungen von YouTube</a> und die{' '}
        <a href="https://policies.google.com/privacy" rel="noopener">Datenschutzerklärung von Google</a>.
      </p>
      <p>
        <strong>Widerruf und Löschung:</strong> Der Zugriff unserer Anwendung auf ein Google-Konto lässt sich
        jederzeit unter{' '}
        <a href="https://security.google.com/settings/security/permissions" rel="noopener">
          security.google.com/settings/security/permissions
        </a>{' '}
        widerrufen. Da wir über die API keine personenbezogenen Daten speichern, fallen keine Daten zur Löschung an;
        Anfragen dazu beantworten wir unter {IMPRESSUM.email} innerhalb von 30 Tagen.
      </p>

      <section lang="en" aria-labelledby="youtube-en">
        <h2 id="youtube-en">YouTube channel and YouTube API Services (English)</h2>
        <p>
          We publish a daily news bulletin on our YouTube channel. The videos are uploaded automatically by our
          server using the YouTube API Services (a Google service) and added to playlists. We only use access to
          our own channel. No data of visitors to this website or of other YouTube users is accessed, stored or
          shared through the API. We only read the list of our own uploads and playlists to avoid duplicate
          uploads; this information is not kept after each run.
        </p>
        <p>
          By watching our videos on YouTube you use YouTube and agree to the{' '}
          <a href="https://www.youtube.com/t/terms" rel="noopener">YouTube Terms of Service</a>; see also the{' '}
          <a href="https://policies.google.com/privacy" rel="noopener">Google Privacy Policy</a>.
        </p>
        <p>
          <strong>Revocation and deletion:</strong> Access granted to our application can be revoked at any time at{' '}
          <a href="https://security.google.com/settings/security/permissions" rel="noopener">
            security.google.com/settings/security/permissions
          </a>
          . As we store no personal data obtained through the API, there is no such data to delete; requests are
          answered at {IMPRESSUM.email} within 30 days.
        </p>
      </section>

      <h2>Ihre Rechte</h2>
      <p>
        Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung,
        Widerspruch sowie auf Beschwerde bei einer Datenschutz-Aufsichtsbehörde.
      </p>
    </main>
  );
}
