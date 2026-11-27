import { videoDatum, videoText } from '@/lib/zeitung/sprache';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';
import type { Sprache, Video } from '@/lib/zeitung/types';

const PLAYLISTEN: Record<Sprache, string> = {
  de: 'https://www.youtube.com/playlist?list=PLeLup6StD61s',
  fr: 'https://www.youtube.com/playlist?list=PLR-uk753xli4',
  en: 'https://www.youtube.com/playlist?list=PLPQaMoOwBNx8',
};

interface VideoAbschnittProps {
  videos: Video[];
  sprache: Sprache;
  texte: OberflaechenTexte;
}

export function VideoAbschnitt({ videos, sprache, texte }: VideoAbschnittProps) {
  if (videos.length === 0) return null;

  return (
    <section className="gz-videos" id="videos" aria-labelledby="h-videos">
      <div className="gz-rubrik-kopf">
        <span className="gz-farbe gz-farbe-wirtschaft" aria-hidden="true" />
        <h2 id="h-videos">{texte.videos}</h2>
        <span className="gz-anzahl">{texte.videosHinweis}</span>
      </div>
      <p className="gz-kanal-abo">
        <a href={PLAYLISTEN[sprache]} target="_blank" rel="noopener noreferrer">
          ▶ {texte.kanalAbo}
        </a>
      </p>
      <div className="gz-video-raster">
        {videos.map((video, index) => (
          <a
            key={video.id}
            className="gz-video"
            href={video.url}
            target="_blank"
            rel="noopener noreferrer"
          >
            <div className={`gz-video-flaeche gz-verlauf-${index % 6}`}>
              <span className="gz-play" aria-hidden="true" />
              <span className="gz-video-quelle">{video.quelle}</span>
            </div>
            <div className="gz-video-text">
              <span className="gz-video-datum">{videoDatum(video, sprache, texte.datumUnbekannt)}</span>
              <strong>{videoText(video, 'titel', sprache)}</strong>
              <span>{videoText(video, 'beschreibung', sprache)}</span>
            </div>
          </a>
        ))}
      </div>
    </section>
  );
}
