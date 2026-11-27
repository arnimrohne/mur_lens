import { ImageResponse } from 'next/og';

import { DODO_PFAD } from '@/lib/zeitung/dodo';

export const size = { width: 180, height: 180 };
export const contentType = 'image/png';

/** Icon für den Startbildschirm (iOS): weißer Dodo auf Tannengrün. */
export default function ZeitungAppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          background: '#0f6e5c',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <svg width="132" height="132" viewBox="0 0 64 64">
          <path d={DODO_PFAD} fill="#ffffff" fillRule="evenodd" />
        </svg>
      </div>
    ),
    size,
  );
}
