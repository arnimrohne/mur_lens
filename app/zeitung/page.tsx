import { ZeitungAnsicht } from '@/components/zeitung/zeitung-ansicht';
import { newsletterBereit } from '@/lib/newsletter/konfiguration';
import { ladeZeitung } from '@/lib/zeitung/lade-daten';
import { ladeWetter } from '@/lib/zeitung/lade-wetter';
import { alsSkriptJson, strukturierteDaten } from '@/lib/zeitung/strukturierte-daten';

/** Seite wird höchstens alle 10 Minuten mit neuen Daten erzeugt. */
export const revalidate = 600;

export default async function ZeitungSeite() {
  const [daten, wetter] = await Promise.all([ladeZeitung(), ladeWetter()]);
  const jsonLd = strukturierteDaten(daten, Date.parse(daten.stand) || Date.now());

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: alsSkriptJson(jsonLd) }} />
      <ZeitungAnsicht daten={daten} wetter={wetter} newsletterBereit={newsletterBereit()} />
    </>
  );
}
