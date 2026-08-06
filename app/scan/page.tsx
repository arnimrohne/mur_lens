'use client';

import { useCallback, useState } from 'react';
import CameraView from '@/components/camera-view';
import RecognitionDebugView from '@/components/recognition-debug-view';
import { TesseractProvider } from '@/lib/recognition/providers/tesseract-provider';
import type { RecognitionProvider, RecognitionResult } from '@/lib/recognition/types';

const provider: RecognitionProvider = new TesseractProvider();

export default function ScanPage() {
  const [result, setResult] = useState<RecognitionResult | null>(null);
  const [isRecognizing, setIsRecognizing] = useState(false);
  const [recognitionError, setRecognitionError] = useState<string | null>(null);

  const handleCapture = useCallback(async (blob: Blob) => {
    setIsRecognizing(true);
    setRecognitionError(null);
    try {
      const r = await provider.recognize(blob);
      setResult(r);
    } catch (err) {
      setRecognitionError(err instanceof Error ? err.message : 'Erkennung fehlgeschlagen.');
    } finally {
      setIsRecognizing(false);
    }
  }, []);

  return (
    <main className="min-h-screen bg-black pb-12">
      <CameraView onCapture={handleCapture} disabled={isRecognizing} />

      {isRecognizing && (
        <p className="text-white text-lg text-center px-4 -mt-2">
          Erkenne…
        </p>
      )}

      {recognitionError && (
        <div className="mx-4 mt-2 bg-red-950 border border-red-700 text-red-200 rounded-xl p-4 text-lg">
          {recognitionError}
        </div>
      )}

      {result && !isRecognizing && (
        <RecognitionDebugView result={result} />
      )}
    </main>
  );
}
