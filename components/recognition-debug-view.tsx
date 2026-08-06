'use client';

import type { RecognitionResult, TextItem } from '@/lib/recognition/types';
import { getTexts } from '@/lib/recognition/types';

interface Props {
  result: RecognitionResult;
}

export default function RecognitionDebugView({ result }: Props) {
  const texts = getTexts(result);

  const handleDownload = () => {
    const json = JSON.stringify(result, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `recognition-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="mx-4 mt-2 space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-gray-400 text-sm">
          {result.provider} · {result.processingTimeMs} ms · {texts.length} Wörter
        </p>
        <button
          type="button"
          onClick={handleDownload}
          className="text-sm bg-gray-800 text-gray-300 px-3 py-1.5 rounded-lg active:scale-95 transition-transform"
        >
          ↓ JSON speichern
        </button>
      </div>

      {texts.length === 0 ? (
        <p className="text-gray-500 text-center py-6 text-lg">
          Kein Text erkannt.
        </p>
      ) : (
        <div className="space-y-2">
          {texts.map((item, i) => (
            <WordRow key={i} item={item} />
          ))}
        </div>
      )}

      <details className="bg-gray-900 rounded-xl overflow-hidden">
        <summary className="text-gray-400 text-sm px-4 py-3 cursor-pointer select-none">
          Raw JSON
        </summary>
        <pre className="text-green-400 text-xs px-4 pb-4 overflow-x-auto leading-relaxed">
          {JSON.stringify(result, null, 2)}
        </pre>
      </details>
    </div>
  );
}

function WordRow({ item }: { item: TextItem }) {
  const pct = Math.round(item.confidence * 100);
  const barColor =
    pct >= 80 ? 'bg-green-500' : pct >= 50 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div className="bg-gray-900 rounded-xl px-4 py-3 flex items-center gap-3">
      <span className="text-white text-xl font-mono flex-1 truncate">{item.value}</span>
      <div className="flex items-center gap-2 shrink-0">
        <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <div className={`h-full rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
        </div>
        <span className="text-gray-400 text-xs w-8 text-right">{pct}%</span>
      </div>
    </div>
  );
}
