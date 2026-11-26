import type { Metadata } from 'next';

import { IMPRESSUM, SEITEN_NAME } from '@/lib/zeitung/seite';

export const metadata: Metadata = {
  title: 'Impressum',
  alternates: { canonical: '/impressum' },
};

function Angabe({ wert }: { wert: string }) {
  return wert.trim() ? <>{wert}</> : <span className="gz-offen">noch nicht ausgefüllt</span>;
}

export default function ImpressumSeite() {
  return (
    <main className="gz-rahmen gz-rechtstext">
      <p><a href="/zeitung">← {SEITEN_NAME}</a></p>
      <h1>Impressum</h1>
      <h2>Angaben gemäß § 5 DDG</h2>
      <p>
        <Angabe wert={IMPRESSUM.name} />
        <br />
        <Angabe wert={IMPRESSUM.anschrift} />
      </p>
      <h2>Kontakt</h2>
      <p>E-Mail: <Angabe wert={IMPRESSUM.email} /></p>
      <h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2>
      <p><Angabe wert={IMPRESSUM.verantwortlich} /></p>
      <h2>Hinweis zu den Inhalten</h2>
      <p>
        Die Meldungen werden automatisch aus öffentlich zugänglichen Nachrichtenquellen zusammengestellt
        und in eigenen Worten zusammengefasst. Jede Meldung verlinkt ihre Quellen. Für die Richtigkeit,
        Vollständigkeit und Aktualität wird keine Gewähr übernommen.
      </p>
      <h2>Haftung für Links</h2>
      <p>
        Für die Inhalte verlinkter externer Seiten sind ausschließlich deren Betreiber verantwortlich.
        Bei Bekanntwerden von Rechtsverletzungen werden entsprechende Links umgehend entfernt.
      </p>
    </main>
  );
}
