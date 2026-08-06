'use client';

import type { ConvertedPrice, Price } from '@/lib/domain/price';
import type { RecognitionResult } from '@/lib/recognition/types';
import { getTexts } from '@/lib/recognition/types';

interface Props {
  price: Price;
  conversion: ConvertedPrice;
  result: RecognitionResult;
}

export default function PriceResultView({ price, conversion, result }: Props) {
  const texts = getTexts(result);
  const avgConfidence =
    texts.length > 0
      ? texts.reduce((s, t) => s + t.confidence, 0) / texts.length
      : 0;
  const confidencePct = Math.round(avgConfidence * 100);

  const murFormatted = price.amount.toLocaleString('de-DE');
  const eurFormatted = conversion.target.amount.toLocaleString('de-DE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return (
    <div className="mx-4 mt-4 space-y-2">
      <div className="bg-gray-900 rounded-2xl p-6 text-center space-y-1">
        <p className="text-gray-400 text-sm uppercase tracking-widest">Erkannter Preis</p>
        <p className="text-white text-3xl font-bold tracking-tight">Rs {murFormatted}</p>
        <div className="h-px bg-gray-700 my-4" />
        <p className="text-gray-400 text-sm uppercase tracking-widest">Umgerechnet</p>
        <p className="text-green-400 text-5xl font-bold tracking-tight">€ {eurFormatted}</p>
      </div>

      {([
        ['Wechselkurs', `1 EUR = ${conversion.rate} MUR`],
        ['Konfidenz', `${confidencePct} %`],
        ['Verarbeitung', `${result.processingTimeMs} ms`],
      ] as const).map(([label, value]) => (
        <div
          key={label}
          className="bg-gray-900 rounded-xl px-4 py-3 flex justify-between text-sm"
        >
          <span className="text-gray-400">{label}</span>
          <span className="text-gray-200">{value}</span>
        </div>
      ))}
    </div>
  );
}
