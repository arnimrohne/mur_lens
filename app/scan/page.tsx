'use client';

import { useCallback, useState } from 'react';
import CameraView from '@/components/camera-view';
import PriceResultView from '@/components/price-result-view';
import RecognitionDebugView from '@/components/recognition-debug-view';
import { TesseractProvider } from '@/lib/recognition/providers/tesseract-provider';
import { extractPrice } from '@/lib/recognition/extractors/price-extractor';
import { currencyService } from '@/lib/services/currency-service';
import type { RecognitionProvider, RecognitionResult } from '@/lib/recognition/types';
import type { ConvertedPrice, Price } from '@/lib/domain/price';

const provider: RecognitionProvider = new TesseractProvider();

type ScanPhase =
  | { kind: 'idle' }
  | { kind: 'scanning' }
  | { kind: 'error'; message: string }
  | { kind: 'no-price'; result: RecognitionResult }
  | { kind: 'done'; result: RecognitionResult; price: Price; conversion: ConvertedPrice };

export default function ScanPage() {
  const [phase, setPhase] = useState<ScanPhase>({ kind: 'idle' });

  const handleCapture = useCallback(async (blob: Blob) => {
    setPhase({ kind: 'scanning' });
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
      setPhase({
        kind: 'error',
        message: 'Erkennung fehlgeschlagen – bitte erneut versuchen.',
      });
    }
  }, []);

  return (
    <main className="min-h-screen bg-black pb-12">
      <CameraView onCapture={handleCapture} disabled={phase.kind === 'scanning'} />

      {phase.kind === 'scanning' && (
        <p className="text-white text-lg text-center px-4 -mt-2">Erkenne…</p>
      )}

      {phase.kind === 'error' && (
        <div className="mx-4 mt-2 bg-red-950 border border-red-700 text-red-200 rounded-xl p-4 text-lg">
          {phase.message}
        </div>
      )}

      {phase.kind === 'no-price' && (
        <>
          <div className="mx-4 mt-2 bg-yellow-950 border border-yellow-700 text-yellow-200 rounded-xl p-4 text-lg">
            Kein Preis erkannt – bitte erneut versuchen.
          </div>
          <div className="mt-4">
            <RecognitionDebugView result={phase.result} />
          </div>
        </>
      )}

      {phase.kind === 'done' && (
        <>
          <PriceResultView
            price={phase.price}
            conversion={phase.conversion}
            result={phase.result}
          />
          <div className="mt-4">
            <RecognitionDebugView result={phase.result} />
          </div>
        </>
      )}
    </main>
  );
}
