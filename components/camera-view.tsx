'use client';

import { useEffect, useCallback } from 'react';
import PhotoPreview from './photo-preview';
import { useCamera } from '@/hooks/use-camera';

interface CameraViewProps {
  onCapture: (blob: Blob) => void;
  disabled?: boolean;
}

export default function CameraView({ onCapture, disabled = false }: CameraViewProps) {
  const { videoRef, capturedPhoto, isStreaming, error, startCamera, capturePhoto } =
    useCamera();

  useEffect(() => {
    startCamera();
  }, [startCamera]);

  const handleCapture = useCallback(async () => {
    const blob = await capturePhoto();
    onCapture(blob);
  }, [capturePhoto, onCapture]);

  return (
    <div className="flex flex-col items-center gap-6 p-4 pb-12">
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
        <button
          type="button"
          onClick={handleCapture}
          disabled={disabled}
          aria-label="Foto aufnehmen"
          className="w-full max-w-lg py-6 bg-white text-black text-2xl font-bold rounded-2xl active:scale-95 transition-transform disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Foto aufnehmen
        </button>
      )}

      {capturedPhoto && <PhotoPreview src={capturedPhoto} />}
    </div>
  );
}
