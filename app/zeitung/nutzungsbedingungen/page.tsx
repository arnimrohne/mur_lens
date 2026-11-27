import type { Metadata } from 'next';

import { IMPRESSUM, SEITEN_NAME, SEITEN_URL } from '@/lib/zeitung/seite';

export const metadata: Metadata = {
  title: 'Nutzungsbedingungen',
  alternates: { canonical: '/nutzungsbedingungen' },
};

export default function NutzungsbedingungenSeite() {
  return (
    <main className="gz-rahmen gz-rechtstext">
      <p><a href="/zeitung">← {SEITEN_NAME}</a></p>
      <h1>Nutzungsbedingungen</h1>

      <h2>Angebot</h2>
      <p>
        {SEITEN_NAME} ({SEITEN_URL}) ist ein kostenloses Nachrichtenangebot über Mauritius, Rodrigues und die
        Region in deutscher, französischer und englischer Sprache. Dazu gehören die Website, der E-Mail-Newsletter
        und eine tägliche Nachrichtensendung auf unserem YouTube-Kanal. Anbieter ist {IMPRESSUM.name},{' '}
        {IMPRESSUM.anschrift} (siehe <a href="/zeitung/impressum">Impressum</a>).
      </p>

      <h2>Inhalte und Quellen</h2>
      <p>
        Unsere Texte sind eigene Zusammenfassungen von Meldungen öffentlich zugänglicher Quellen, die bei jeder
        Meldung verlinkt sind. Wir bemühen uns um Richtigkeit, übernehmen aber keine Gewähr für Vollständigkeit
        und Aktualität. Für die Inhalte verlinkter Seiten sind ausschließlich deren Betreiber verantwortlich.
      </p>

      <h2>Nutzung unserer Inhalte</h2>
      <p>
        Sie dürfen unsere Inhalte für private Zwecke lesen, ansehen und über die Teilen-Funktion oder einen Link
        weitergeben. Eine darüber hinausgehende Vervielfältigung oder Veröffentlichung, insbesondere zu
        gewerblichen Zwecken, bedarf unserer vorherigen Zustimmung.
      </p>

      <h2>YouTube</h2>
      <p>
        Unsere Nachrichtensendung wird über die YouTube API Services auf unserem YouTube-Kanal veröffentlicht.
        Wer die Videos auf YouTube ansieht, nutzt YouTube und stimmt damit den{' '}
        <a href="https://www.youtube.com/t/terms" rel="noopener">Nutzungsbedingungen von YouTube</a> zu. Für die
        Verarbeitung von Daten durch YouTube gilt die{' '}
        <a href="https://policies.google.com/privacy" rel="noopener">Datenschutzerklärung von Google</a>. Wie
        wir selbst die YouTube API Services nutzen, beschreibt unsere{' '}
        <a href="/zeitung/datenschutz#youtube">Datenschutzerklärung</a>.
      </p>

      <h2>Newsletter</h2>
      <p>
        Der Newsletter ist kostenlos und kann jederzeit über den Link in jeder Mail abbestellt werden.
      </p>

      <h2>Änderungen und Kontakt</h2>
      <p>
        Wir können diese Bedingungen anpassen; es gilt die jeweils hier veröffentlichte Fassung. Fragen richten
        Sie bitte an {IMPRESSUM.email}. Es gilt deutsches Recht.
      </p>

      <section lang="en" aria-labelledby="terms-en">
        <h2 id="terms-en">Terms of use (English)</h2>
        <p>
          {SEITEN_NAME} ({SEITEN_URL}) is a free news service about Mauritius, Rodrigues and the region in German,
          French and English, consisting of the website, an email newsletter and a daily news bulletin on our
          YouTube channel. It is provided by {IMPRESSUM.name}, {IMPRESSUM.anschrift}.
        </p>
        <p>
          Our texts are original summaries of publicly available sources, which are linked with every story. We
          aim for accuracy but give no warranty as to completeness or timeliness. Operators of linked sites are
          solely responsible for their content. You may read, watch and share our content for personal use; any
          other reproduction, in particular for commercial purposes, requires our prior consent.
        </p>
        <p>
          Our news bulletin is published on our YouTube channel using the YouTube API Services. By watching our
          videos on YouTube you agree to be bound by the{' '}
          <a href="https://www.youtube.com/t/terms" rel="noopener">YouTube Terms of Service</a>; the{' '}
          <a href="https://policies.google.com/privacy" rel="noopener">Google Privacy Policy</a> applies to data
          processed by YouTube. How we use the YouTube API Services is described in our{' '}
          <a href="/zeitung/datenschutz#youtube-en">privacy policy</a>.
        </p>
        <p>
          We may update these terms; the version published here applies. Contact: {IMPRESSUM.email}. German law
          applies.
        </p>
      </section>
    </main>
  );
}
