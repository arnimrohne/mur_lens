import { YOUTUBE_KANAL } from '@/lib/zeitung/seite';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';

interface FussLinksProps {
  texte: OberflaechenTexte;
  newsletter?: boolean;
}

/** YouTube-Symbol (rotes Abspielfeld) nach den Markenrichtlinien, nur als Link zum eigenen Kanal. */
export function YouTubeSymbol() {
  return (
    <svg className="gz-yt-symbol" viewBox="0 0 28 20" width="28" height="20" aria-hidden="true">
      <rect width="28" height="20" rx="5" fill="#FF0000" />
      <path d="M11 5.5v9l8-4.5z" fill="#FFFFFF" />
    </svg>
  );
}

/** Fußzeilen-Links: Impressum, Datenschutz, Nutzungsbedingungen, YouTube-Kanal, Newsletter. */
export function FussLinks({ texte, newsletter = false }: FussLinksProps) {
  return (
    <p className="gz-fuss-links">
      <a href="/zeitung/impressum">{texte.impressum}</a>
      <a href="/zeitung/datenschutz">{texte.datenschutz}</a>
      <a href="/zeitung/nutzungsbedingungen">{texte.nutzungsbedingungen}</a>
      {newsletter && <a href="/zeitung/newsletter">Newsletter</a>}
      {YOUTUBE_KANAL && (
        <a className="gz-yt-link" href={YOUTUBE_KANAL} rel="noopener">
          <YouTubeSymbol />
          {texte.youtube}
        </a>
      )}
    </p>
  );
}
