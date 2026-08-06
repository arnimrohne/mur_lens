'use client';

import type { ConvertedPrice, Price } from '@/lib/domain/price';

interface Props {
  price: Price;
  conversion: ConvertedPrice;
  processingTimeMs: number;
  onReset: () => void;
}

export default function PriceResultView({ price, conversion, processingTimeMs, onReset }: Props) {
  // en-US matches Mauritius label format: 1,250 (comma as thousands separator)
  const murFormatted = price.amount.toLocaleString('en-US');
  const eurFormatted = conversion.target.amount.toLocaleString('de-DE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return (
    <div className="mx-4 mt-4 space-y-3">
      <div className="bg-gray-900 rounded-2xl p-6 text-center space-y-1">
        <p className="text-gray-400 text-sm uppercase tracking-widest">Erkannter Preis</p>
        <p className="text-white text-3xl font-bold tracking-tight">Rs {murFormatted}</p>
        <div className="h-px bg-gray-700 my-4" />
        <p className="text-gray-400 text-sm uppercase tracking-widest">Umgerechnet</p>
        <p className="text-green-400 text-5xl font-bold tracking-tight">€ {eurFormatted}</p>
      </div>

      {([
        ['Wechselkurs', `1 EUR = ${conversion.rate} MUR`],
        ['Verarbeitung', `${processingTimeMs} ms`],
      ] as const).map(([label, value]) => (
        <div
          key={label}
          className="bg-gray-900 rounded-xl px-4 py-3 flex justify-between text-sm"
        >
          <span className="text-gray-400">{label}</span>
          <span className="text-gray-200">{value}</span>
        </div>
      ))}

      <button
        type="button"
        onClick={onReset}
        className="w-full py-5 bg-gray-900 border border-gray-700 text-white text-xl font-semibold rounded-2xl active:scale-95 transition-transform"
      >
        Erneut scannen
      </button>
    </div>
  );
}
