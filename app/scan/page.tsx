'use client';

import { useCallback, useEffect, useState } from 'react';
import CameraView from '@/components/camera-view';
import ScanningView from '@/components/scanning-view';
import PriceResultView from '@/components/price-result-view';
import RecognitionDebugView from '@/components/recognition-debug-view';
import { TesseractProvider } from '@/lib/recognition/providers/tesseract-provider';
import { extractPrice } from '@/lib/recognition/extractors/price-extractor';
import { currencyService } from '@/lib/services/currency-service';
import type { RecognitionResult } from '@/lib/recognition/types';
import type { ConvertedPrice, Price } from '@/lib/domain/price';

const provider = new TesseractProvider();
const debugMode = process.env.NEXT_PUBLIC_DEBUG_RECOGNITION === 'true';

type ScanPhase =
  | { kind: 'camera' }
  | { kind: 'scanning'; photoUrl: string }
  | { kind: 'error'; message: string }
  | { kind: 'no-price'; result: RecognitionResult }
  | { kind: 'done'; result: RecognitionResult; price: Price; conversion: ConvertedPrice };

function DebugPanel({ result }: { result: RecognitionResult }) {
  return (
    <div className="w-full max-w-lg mt-4">
      <RecognitionDebugView result={result} />
    </div>
  );
}

export default function ScanPage() {
  const [phase, setPhase] = useState<ScanPhase>({ kind: 'camera' });
  const [isProviderReady, setIsProviderReady] = useState(false);

  useEffect(() => {
    provider.warmUp().then(() => setIsProviderReady(true));
  }, []);

  const handleCapture = useCallback(async (blob: Blob, photoUrl: string) => {
    setPhase({ kind: 'scanning', photoUrl });
    try {
      const result = await provider.recognize(blob);
      const price = extractPrice(result);
      if (!price) {
        setPhase({ kind: 'no-price', result });
        return;
      }
      const conversion = currencyService.convert(price, 'EUR');
      setPhase({ kind: 'done', result, price, conversion });
    } catch {
      setPhase({ kind: 'error', message: 'Erkennung fehlgeschlagen – bitte erneut versuchen.' });
    }
  }, []);

  const reset = useCallback(() => setPhase({ kind: 'camera' }), []);

  return (
    <main className="min-h-screen bg-black pb-12">
      {phase.kind === 'camera' && (
        <CameraView
          onCapture={handleCapture}
          disabled={!isProviderReady}
          buttonLabel={isProviderReady ? 'Foto aufnehmen' : 'Wird vorbereitet…'}
        />
      )}

      {phase.kind === 'scanning' && <ScanningView photoUrl={phase.photoUrl} />}

      {phase.kind === 'error' && (
        <div className="flex flex-col items-center gap-4 p-4 pb-12">
          <div className="w-full max-w-lg bg-red-950 border border-red-700 text-red-200 rounded-xl p-6 text-center text-lg">
            {phase.message}
          </div>
          <button
            type="button"
            onClick={reset}
            className="w-full max-w-lg py-5 bg-gray-900 border border-gray-700 text-white text-xl font-semibold rounded-2xl active:scale-95 transition-transform"
          >
            Erneut scannen
          </button>
        </div>
      )}

      {phase.kind === 'no-price' && (
        <div className="flex flex-col items-center gap-4 p-4 pb-12">
          <div className="w-full max-w-lg bg-yellow-950 border border-yellow-700 text-yellow-200 rounded-xl p-6 text-center text-lg">
            Kein Preis erkannt – bitte erneut versuchen.
          </div>
          <button
            type="button"
            onClick={reset}
            className="w-full max-w-lg py-5 bg-gray-900 border border-gray-700 text-white text-xl font-semibold rounded-2xl active:scale-95 transition-transform"
          >
            Erneut scannen
          </button>
          {debugMode && <DebugPanel result={phase.result} />}
        </div>
      )}

      {phase.kind === 'done' && (
        <>
          <PriceResultView
            price={phase.price}
            conversion={phase.conversion}
            processingTimeMs={phase.result.processingTimeMs}
            onReset={reset}
          />
          {debugMode && <DebugPanel result={phase.result} />}
        </>
      )}
    </main>
  );
}
