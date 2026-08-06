'use client';

import { useEffect, useCallback } from 'react';
import { useCamera } from '@/hooks/use-camera';

interface CameraViewProps {
  onCapture: (blob: Blob, photoUrl: string) => void;
  disabled?: boolean;
  buttonLabel?: string;
}

export default function CameraView({
  onCapture,
  disabled = false,
  buttonLabel = 'Foto aufnehmen',
}: CameraViewProps) {
  const { videoRef, isStreaming, error, startCamera, capturePhoto } = useCamera();

  useEffect(() => {
    startCamera();
  }, [startCamera]);

  const handleCapture = useCallback(async () => {
    try {
      const { blob, photoUrl } = await capturePhoto();
      onCapture(blob, photoUrl);
    } catch {
      // Camera not ready – the user can retry
    }
  }, [capturePhoto, onCapture]);

  return (
    <div className="flex flex-col items-center gap-4 p-4 pb-12">
      {error && (
        <div className="w-full max-w-lg bg-red-950 border border-red-700 text-red-200 rounded-xl p-4 text-center text-lg">
          {error}
        </div>
      )}

      <div className="w-full max-w-lg bg-gray-900 rounded-2xl overflow-hidden aspect-[3/4] relative">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover"
        />
        {!isStreaming && !error && (
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-white text-lg">Kamera wird gestartet…</p>
          </div>
        )}
      </div>

      {isStreaming && (
        <div className="w-full max-w-lg space-y-3">
          <button
            type="button"
            onClick={handleCapture}
            disabled={disabled}
            aria-label="Foto aufnehmen"
            className="w-full py-6 bg-white text-black text-2xl font-bold rounded-2xl active:scale-95 transition-transform disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {buttonLabel}
          </button>
          {disabled && (
            <div className="h-1 w-full rounded-full overflow-hidden bg-gray-800">
              <div className="h-full bg-green-400 animate-pulse rounded-full" />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
