'use client';

import Image from 'next/image';

import { FussLinks } from './fuss-links';
import { GrafikBalken } from './grafik-balken';
import { RegionalKarte } from './regional-karte';
import { ShopBanner } from './shop-banner';
import { ZeitungKopf } from './zeitung-kopf';
import { useZeitungSprache } from '@/hooks/use-zeitung-sprache';
import { dossierPfad, DOSSIERS_PFAD } from '@/lib/zeitung/dossiers';
import { meldungText, tagLang } from '@/lib/zeitung/sprache';
import { themaPfad } from '@/lib/zeitung/teilen';
import { TEXTE } from '@/lib/zeitung/texte';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';
import type { Dossier, DossierBild, Mehrsprachig, Sprache, Thema } from '@/lib/zeitung/types';

function Absaetze({ text, sprache }: { text?: Mehrsprachig; sprache: Sprache }) {
  if (!text) return null;
  return (
    <>
      {text[sprache].split(/\n\s*\n/).map((absatz) => (
        <p key={absatz.slice(0, 40)}>{absatz.trim()}</p>
      ))}
    </>
  );
}

function QuellenVerweis({ url, texte }: { url?: string; texte: OberflaechenTexte }) {
  if (!url) return null;
  return (
    <a className="gz-dossier-quelle" href={url} target="_blank" rel="noopener noreferrer">
      {texte.quelleLink}
    </a>
  );
}

const FOTO: Record<Sprache, string> = { de: 'Foto', fr: 'Photo', en: 'Photo' };

/** Namensnennung nach Lizenz: Urheber (Link zur Dateiseite), Lizenz (Link), Quelle. */
function BildNachweis({ bild, sprache }: { bild: DossierBild; sprache: Sprache }) {
  return (
    <>
      {FOTO[sprache]}: <a href={bild.seite} target="_blank" rel="noopener noreferrer">{bild.urheber}</a>
      {' · '}
      {bild.lizenzUrl ? (
        <a href={bild.lizenzUrl} target="_blank" rel="noopener noreferrer license">{bild.lizenz}</a>
      ) : (
        bild.lizenz
      )}
      {' · Wikimedia Commons'}
    </>
  );
}

function Rahmen({ stand, children }: { stand: string; children: (s: Sprache, t: OberflaechenTexte) => React.ReactNode }) {
  const [sprache, waehleSprache] = useZeitungSprache();
  const texte = TEXTE[sprache];
  return (
    <>
      <div className="gz-flagge" aria-hidden="true">
        <span /><span /><span /><span />
      </div>
      <div className="gz-rahmen">
        <ZeitungKopf stand={stand} sprache={sprache} texte={texte} waehleSprache={waehleSprache} />
      </div>
      <main className="gz-rahmen gz-dossier-seite">{children(sprache, texte)}</main>
      <ShopBanner texte={texte} />
      <footer className="gz-rahmen gz-fuss">
        <FussLinks texte={texte} />
      </footer>
    </>
  );
}

/** Übersicht aller Dossiers („Lexikon“), nach Rubrik. */
export function DossierUebersicht({ dossiers, stand }: { dossiers: Dossier[]; stand: string }) {
  return (
    <Rahmen stand={stand}>
      {(sprache, texte) => (
        <>
          <p className="gz-zurueck"><a href="/zeitung">{texte.zurAusgabe}</a></p>
          <h1 className="gz-dossier-h1">{texte.dossiers}</h1>
          <p className="gz-dossier-unter">{texte.dossiersUntertitel}</p>
          {dossiers.length === 0 && <p className="gz-notiz">{texte.keineDossiers}</p>}
          <div className="gz-dossier-liste">
            {dossiers.map((d) => (
              <div key={d.id} className="gz-dossier-karte">
                <span className={`gz-farbe gz-farbe-${d.rubrik}`} aria-hidden="true" />
                {d.bild && (
                  <figure className="gz-dossier-karte-bild">
                    <Image src={d.bild.src} alt={d.bild.alt[sprache]} width={d.bild.breite} height={d.bild.hoehe} sizes="(max-width: 600px) 100vw, 400px" />
                    <figcaption><BildNachweis bild={d.bild} sprache={sprache} /></figcaption>
                  </figure>
                )}
                <span className="gz-dossier-rubrik">{texte.rubriken[d.rubrik].kurz}</span>
                <a className="gz-dossier-karte-link" href={dossierPfad(d.id)}>
                  <strong>{d.titel[sprache]}</strong>
                </a>
                <span className="gz-dossier-kurz">{d.kurz[sprache]}</span>
                <span className="gz-dossier-stand">{texte.dossierStand(tagLang(Date.parse(d.stand), sprache))}</span>
              </div>
            ))}
          </div>
        </>
      )}
    </Rahmen>
  );
}

/** Ein Dossier mit allen Abschnitten und den aktuellen Meldungen dazu. */
export function DossierAnsicht({ dossier, themen, stand }: { dossier: Dossier; themen: Thema[]; stand: string }) {
  return (
    <Rahmen stand={stand}>
      {(sprache, texte) => {
        const a = texte.dossierAbschnitte;
        return (
          <article className="gz-dossier">
            <p className="gz-zurueck"><a href={DOSSIERS_PFAD}>{texte.alleDossiers}</a></p>
            <div className="gz-oberzeile">{texte.dossiers} · {texte.rubriken[dossier.rubrik].lang}</div>
            <h1 className="gz-dossier-h1">{dossier.titel[sprache]}</h1>
            <p className="gz-dossier-stand">{texte.dossierStand(tagLang(Date.parse(dossier.stand), sprache))}</p>
            {dossier.bild && (
              <figure className="gz-dossier-bild">
                <Image
                  src={dossier.bild.src}
                  alt={dossier.bild.alt[sprache]}
                  width={dossier.bild.breite}
                  height={dossier.bild.hoehe}
                  sizes="(max-width: 800px) 100vw, 760px"
                  priority
                />
                <figcaption><BildNachweis bild={dossier.bild} sprache={sprache} /></figcaption>
              </figure>
            )}

            <section className="gz-dossier-abschnitt gz-dossier-kurz-block">
              <h2>{a.kurz}</h2>
              <p>{dossier.kurz[sprache]}</p>
              {dossier.karte && <RegionalKarte karte={dossier.karte} sprache={sprache} />}
            </section>

            {dossier.zahlen.length > 0 && (
              <section className="gz-dossier-abschnitt">
                <h2>{a.zahlen}</h2>
                <ul className="gz-dossier-zahlen">
                  {dossier.zahlen.map((z) => (
                    <li key={z.text.de}>
                      <strong>{z.wert[sprache]}</strong>
                      <span>{z.text[sprache]}</span>
                      <QuellenVerweis url={z.quelle} texte={texte} />
                    </li>
                  ))}
                </ul>
                <div className="gz-dossier-grafiken">
                  {dossier.grafiken.map((g, i) => (
                    <GrafikBalken key={i} grafik={g} sprache={sprache} />
                  ))}
                </div>
              </section>
            )}

            {dossier.warum && (
              <section className="gz-dossier-abschnitt">
                <h2>{a.warum}</h2>
                <Absaetze text={dossier.warum} sprache={sprache} />
              </section>
            )}

            {dossier.chronik.length > 0 && (
              <section className="gz-dossier-abschnitt">
                <h2>{a.chronik}</h2>
                <ol className="gz-chronik">
                  {dossier.chronik.map((e) => (
                    <li key={e.datum.de + e.text.de.slice(0, 20)}>
                      <span className="gz-chronik-datum">{e.datum[sprache]}</span>
                      <span className="gz-chronik-text">
                        {e.text[sprache]} <QuellenVerweis url={e.quelle} texte={texte} />
                      </span>
                    </li>
                  ))}
                </ol>
              </section>
            )}

            {dossier.entwicklung && (
              <section className="gz-dossier-abschnitt">
                <h2>{a.entwicklung}</h2>
                <Absaetze text={dossier.entwicklung} sprache={sprache} />
              </section>
            )}

            {dossier.akteure.length > 0 && (
              <section className="gz-dossier-abschnitt">
                <h2>{a.akteure}</h2>
                <dl className="gz-akteure">
                  {dossier.akteure.map((ak) => (
                    <div key={ak.name.de}>
                      <dt>{ak.name[sprache]}</dt>
                      <dd>
                        {ak.position[sprache]} <QuellenVerweis url={ak.quelle} texte={texte} />
                      </dd>
                    </div>
                  ))}
                </dl>
              </section>
            )}

            {dossier.offen.length > 0 && (
              <section className="gz-dossier-abschnitt">
                <h2>{a.offen}</h2>
                <ul className="gz-dossier-offen">
                  {dossier.offen.map((f) => (
                    <li key={f.de}>{f[sprache]}</li>
                  ))}
                </ul>
              </section>
            )}

            {themen.length > 0 && (
              <section className="gz-dossier-abschnitt">
                <h2>{a.aktuell}</h2>
                <ul className="gz-dossier-meldungen">
                  {themen.slice(0, 8).map((t) => (
                    <li key={t.id}>
                      <time dateTime={t.aktualisiert}>{tagLang(Date.parse(t.aktualisiert), sprache)}</time>
                      <a href={themaPfad(t.id)}>{meldungText(t.updates[0], 'titel', sprache)}</a>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {dossier.quellen.length > 0 && (
              <section className="gz-dossier-abschnitt">
                <h2>{a.quellen}</h2>
                <ul className="gz-dossier-quellenliste">
                  {dossier.quellen.map((q) => (
                    <li key={q.url}>
                      <a href={q.url} target="_blank" rel="noopener noreferrer">{q.name}</a>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </article>
        );
      }}
    </Rahmen>
  );
}
