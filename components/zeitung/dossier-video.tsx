'use client';

import Image from 'next/image';
import { useState } from 'react';

import type { OberflaechenTexte } from '@/lib/zeitung/texte';
import type { DossierVideo, Sprache } from '@/lib/zeitung/types';

const REIHENFOLGE: Sprache[] = ['de', 'en', 'fr'];

/**
 * Lernvideo im Dossier, in der gewählten Sprache. Zwei Klicks: zuerst nur das eigene Vorschaubild,
 * YouTube (youtube-nocookie.com) wird erst nach dem Klick auf „Abspielen“ geladen.
 */
export function DossierVideoBlock({ video, sprache, texte }: { video: DossierVideo; sprache: Sprache; texte: OberflaechenTexte }) {
  const [laeuft, setLaeuft] = useState<string | null>(null);
  const eigene = video.youtube[sprache];
  const id = eigene ?? REIHENFOLGE.map((s) => video.youtube[s]).find(Boolean);
  if (!id) return null;
  const vorschau = (eigene ? video.vorschau[sprache] : undefined) ?? REIHENFOLGE.map((s) => video.vorschau[s]).find(Boolean);
  const abspielen = laeuft === id;

  return (
    <section id="video" className="gz-dossier-abschnitt gz-dossier-video" aria-labelledby="h-dossier-video">
      <h2 id="h-dossier-video">{texte.dossierVideo}</h2>
      <div className="gz-dossier-video-flaeche">
        {abspielen ? (
          <iframe
            src={`https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0&hl=${sprache}&cc_lang_pref=${sprache}`}
            title={texte.dossierVideo}
            allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
            allowFullScreen
            referrerPolicy="strict-origin-when-cross-origin"
          />
        ) : (
          <button type="button" className="gz-dossier-video-start" onClick={() => setLaeuft(id)}>
            {vorschau && <Image src={vorschau} alt="" fill sizes="(max-width: 800px) 100vw, 760px" />}
            <span className="gz-dossier-video-play" aria-hidden="true" />
            <span className="gz-dossier-video-label">{texte.dossierVideoStart}</span>
          </button>
        )}
      </div>
      <p className="gz-dossier-video-hinweis">
        {!eigene && <strong>{texte.dossierVideoAndereSprache}. </strong>}
        {texte.dossierVideoHinweis} <a href="/zeitung/datenschutz#youtube">{texte.dossierVideoDatenschutz}</a>
      </p>
    </section>
  );
}
