import { YouTubeSymbol } from './fuss-links';
import { YOUTUBE_PLAYLISTS } from '@/lib/zeitung/seite';
import { videoDatum, videoText } from '@/lib/zeitung/sprache';
import type { OberflaechenTexte } from '@/lib/zeitung/texte';
import type { Sprache, Video } from '@/lib/zeitung/types';

interface VideoAbschnittProps {
  videos: Video[];
  sprache: Sprache;
  texte: OberflaechenTexte;
}

export function VideoAbschnitt({ videos, sprache, texte }: VideoAbschnittProps) {
  const playlist = YOUTUBE_PLAYLISTS[sprache];
  if (videos.length === 0 && !playlist) return null;

  return (
    <section className="gz-videos" id="videos" aria-labelledby="h-videos">
      <div className="gz-rubrik-kopf">
        <span className="gz-farbe gz-farbe-wirtschaft" aria-hidden="true" />
        <h2 id="h-videos">{texte.videos}</h2>
        <span className="gz-anzahl">{texte.videosHinweis}</span>
      </div>
      {playlist && (
        <a className="gz-sendung-abo" href={playlist} target="_blank" rel="noopener noreferrer">
          <YouTubeSymbol />
          <span>
            <strong>{texte.sendungAbo}</strong>
            <small>{texte.sendungAboHinweis}</small>
          </span>
          <span className="gz-sendung-abo-pfeil" aria-hidden="true">→</span>
        </a>
      )}
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
