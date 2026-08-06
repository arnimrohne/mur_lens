import { describe, it, expect } from 'vitest';
import type { RecognitionResult } from '@/lib/recognition/types';
import { getTexts } from '@/lib/recognition/types';
import { extractPrice } from '@/lib/recognition/extractors/price-extractor';

import cleanResult from './fixtures/recognition/mur-1250-clean.json';
import ocrZeroResult from './fixtures/recognition/mur-ocr-zero.json';
import spacedNumberResult from './fixtures/recognition/mur-spaced-number.json';
import periodSepResult from './fixtures/recognition/mur-period-sep.json';
import currencySeparateResult from './fixtures/recognition/mur-currency-separate-line.json';
import lowConfidenceResult from './fixtures/recognition/mur-low-confidence.json';
import emptyResult from './fixtures/recognition/empty-no-text.json';

// ─── Fixture validation ───────────────────────────────────────────────────────

describe('Fixtures', () => {
  const allFixtures: [string, unknown][] = [
    ['mur-1250-clean', cleanResult],
    ['mur-ocr-zero', ocrZeroResult],
    ['mur-spaced-number', spacedNumberResult],
    ['mur-period-sep', periodSepResult],
    ['mur-currency-separate-line', currencySeparateResult],
    ['mur-low-confidence', lowConfidenceResult],
    ['empty-no-text', emptyResult],
  ];

  it.each(allFixtures)('%s has valid RecognitionResult shape', (_name, raw) => {
    const result = raw as RecognitionResult;
    expect(typeof result.provider).toBe('string');
    expect(typeof result.processingTimeMs).toBe('number');
    expect(result.processingTimeMs).toBeGreaterThan(0);
    expect(Array.isArray(result.items)).toBe(true);
  });

  it.each(allFixtures)('%s items have valid TextItem shape', (_name, raw) => {
    const result = raw as RecognitionResult;
    for (const item of getTexts(result)) {
      expect(item.type).toBe('text');
      expect(typeof item.value).toBe('string');
      expect(item.confidence).toBeGreaterThanOrEqual(0);
      expect(item.confidence).toBeLessThanOrEqual(1);
    }
  });

  it('clean fixture contains "Rs" and "1,250"', () => {
    const result = cleanResult as RecognitionResult;
    const values = getTexts(result).map((t) => t.value);
    expect(values).toContain('Rs');
    expect(values).toContain('1,250');
  });

  it('ocr-zero fixture contains ambiguous "O" in number', () => {
    const result = ocrZeroResult as RecognitionResult;
    const values = getTexts(result).map((t) => t.value);
    expect(values.some((v) => v.includes('O'))).toBe(true);
  });

  it('empty fixture has no items', () => {
    const result = emptyResult as RecognitionResult;
    expect(result.items).toHaveLength(0);
  });

  it('low-confidence fixture has all items below 0.5', () => {
    const result = lowConfidenceResult as RecognitionResult;
    const allLow = getTexts(result).every((t) => t.confidence < 0.5);
    expect(allLow).toBe(true);
  });
});

// ─── Helpers ──────────────────────────────────────────────────────────────────

function makeResult(
  tokens: { value: string; confidence: number; x?: number; y?: number }[],
): RecognitionResult {
  return {
    provider: 'test',
    processingTimeMs: 100,
    items: tokens.map(({ value, confidence, x, y = 0 }, i) => ({
      type: 'text' as const,
      value,
      confidence,
      boundingBox: { x: x ?? i * 80, y, width: 50, height: 20 },
    })),
  };
}

// ─── PriceExtractor – Fixtures ────────────────────────────────────────────────

describe('PriceExtractor – Fixtures', () => {
  it('mur-1250-clean → { amount: 1250, currency: "MUR" }', () => {
    expect(extractPrice(cleanResult as RecognitionResult)).toEqual({
      amount: 1250,
      currency: 'MUR',
    });
  });

  it('mur-ocr-zero: O→0 korrigiert → { amount: 1250, currency: "MUR" }', () => {
    expect(extractPrice(ocrZeroResult as RecognitionResult)).toEqual({
      amount: 1250,
      currency: 'MUR',
    });
  });

  it('mur-spaced-number: "Rs" + "1" + "250" gemergt → { amount: 1250, currency: "MUR" }', () => {
    expect(extractPrice(spacedNumberResult as RecognitionResult)).toEqual({
      amount: 1250,
      currency: 'MUR',
    });
  });

  it('mur-period-sep: Punkt als Tausendertrenner → { amount: 1250, currency: "MUR" }', () => {
    expect(extractPrice(periodSepResult as RecognitionResult)).toEqual({
      amount: 1250,
      currency: 'MUR',
    });
  });

  it('mur-currency-separate-line: "MUR" auf gleicher Zeile wie Zahl → { amount: 1250, currency: "MUR" }', () => {
    expect(extractPrice(currencySeparateResult as RecognitionResult)).toEqual({
      amount: 1250,
      currency: 'MUR',
    });
  });

  it('mur-low-confidence: alle Items unter Schwellwert → null', () => {
    expect(extractPrice(lowConfidenceResult as RecognitionResult)).toBeNull();
  });

  it('empty-no-text → null', () => {
    expect(extractPrice(emptyResult as RecognitionResult)).toBeNull();
  });
});

// ─── PriceExtractor – Standard MUR-Preise ─────────────────────────────────────

describe('PriceExtractor – Standard MUR-Preise', () => {
  it('erkennt sauberes Label: "Rs 1,250" → { amount: 1250, currency: "MUR" }', () => {
    const r = makeResult([
      { value: 'Rs', confidence: 0.9 },
      { value: '1,250', confidence: 0.9 },
    ]);
    expect(extractPrice(r)).toEqual({ amount: 1250, currency: 'MUR' });
  });

  it('erkennt einfachen Preis ohne Tausendertrennung: "Rs 250"', () => {
    const r = makeResult([
      { value: 'Rs', confidence: 0.9 },
      { value: '250', confidence: 0.9 },
    ]);
    expect(extractPrice(r)).toEqual({ amount: 250, currency: 'MUR' });
  });

  it('erkennt Dezimalpreis: "Rs 19.95" → { amount: 19.95, currency: "MUR" }', () => {
    const r = makeResult([
      { value: 'Rs', confidence: 0.9 },
      { value: '19.95', confidence: 0.9 },
    ]);
    expect(extractPrice(r)).toEqual({ amount: 19.95, currency: 'MUR' });
  });

  it('erkennt MUR als alternativen Currency-Code: "MUR 1250"', () => {
    const r = makeResult([
      { value: 'MUR', confidence: 0.9 },
      { value: '1250', confidence: 0.9 },
    ]);
    expect(extractPrice(r)).toEqual({ amount: 1250, currency: 'MUR' });
  });
});

// ─── PriceExtractor – OCR-Fehlerkorrekturen ───────────────────────────────────

describe('PriceExtractor – OCR-Fehlerkorrekturen', () => {
  it('korrigiert O → 0: "1,25O" → amount: 1250', () => {
    const r = makeResult([
      { value: 'Rs', confidence: 0.87 },
      { value: '1,25O', confidence: 0.61 },
    ]);
    expect(extractPrice(r)).toEqual({ amount: 1250, currency: 'MUR' });
  });

  it('korrigiert l → 1: "l,250" → amount: 1250', () => {
    const r = makeResult([
      { value: 'Rs', confidence: 0.87 },
      { value: 'l,250', confidence: 0.65 },
    ]);
    expect(extractPrice(r)).toEqual({ amount: 1250, currency: 'MUR' });
  });

  it('korrigiert I → 1: "I,250" → amount: 1250', () => {
    const r = makeResult([
      { value: 'Rs', confidence: 0.87 },
      { value: 'I,250', confidence: 0.65 },
    ]);
    expect(extractPrice(r)).toEqual({ amount: 1250, currency: 'MUR' });
  });

  it('korrigiert R$ → Rs: wird als Währungssymbol erkannt', () => {
    const r = makeResult([
      { value: 'R$', confidence: 0.75 },
      { value: '1,250', confidence: 0.88 },
    ]);
    expect(extractPrice(r)).toEqual({ amount: 1250, currency: 'MUR' });
  });

  it('entfernt Punkt nach Rs: "Rs." → Währung MUR', () => {
    const r = makeResult([
      { value: 'Rs.', confidence: 0.85 },
      { value: '1250', confidence: 0.88 },
    ]);
    expect(extractPrice(r)).toEqual({ amount: 1250, currency: 'MUR' });
  });
});

// ─── PriceExtractor – Trennzeichen-Normalisierung ─────────────────────────────

describe('PriceExtractor – Trennzeichen-Normalisierung', () => {
  it('versteht Komma als Tausendertrenner: "1,250" → 1250', () => {
    const r = makeResult([
      { value: 'Rs', confidence: 0.9 },
      { value: '1,250', confidence: 0.9 },
    ]);
    expect(extractPrice(r)?.amount).toBe(1250);
  });

  it('versteht Punkt als Tausendertrenner: "1.250" → 1250', () => {
    const r = makeResult([
      { value: 'Rs', confidence: 0.9 },
      { value: '1.250', confidence: 0.9 },
    ]);
    expect(extractPrice(r)?.amount).toBe(1250);
  });

  it('verbindet "Rs" + "1" + "250" via Space-Merge → 1250', () => {
    const r = makeResult([
      { value: 'Rs', confidence: 0.9 },
      { value: '1', confidence: 0.9 },
      { value: '250', confidence: 0.9 },
    ]);
    expect(extractPrice(r)?.amount).toBe(1250);
  });

  it('versteht Komma als Dezimaltrenner: "19,95" → 19.95', () => {
    const r = makeResult([
      { value: 'Rs', confidence: 0.9 },
      { value: '19,95', confidence: 0.9 },
    ]);
    expect(extractPrice(r)?.amount).toBeCloseTo(19.95);
  });
});

// ─── PriceExtractor – Mehrteilige Ergebnisse ──────────────────────────────────

describe('PriceExtractor – Mehrteilige Ergebnisse', () => {
  it('verbindet benachbarte Zahl-Tokens auf gleicher Baseline', () => {
    const r = makeResult([
      { value: 'Rs', confidence: 0.89 },
      { value: '1', confidence: 0.82 },
      { value: '250', confidence: 0.84 },
    ]);
    expect(extractPrice(r)).toEqual({ amount: 1250, currency: 'MUR' });
  });

  it('ignoriert Label-Wort "PRICE" ohne Preisbezug', () => {
    const r = makeResult([
      { value: 'PRICE', confidence: 0.94, x: 0, y: 0 },
      { value: 'Rs', confidence: 0.88, x: 0, y: 60 },
      { value: '1,250', confidence: 0.85, x: 80, y: 60 },
    ]);
    expect(extractPrice(r)).toEqual({ amount: 1250, currency: 'MUR' });
  });

  it('akzeptiert Preis auch wenn Währungssymbol nach der Zahl steht: "1250 Rs"', () => {
    const r = makeResult([
      { value: '1250', confidence: 0.88 },
      { value: 'Rs', confidence: 0.9 },
    ]);
    expect(extractPrice(r)).toEqual({ amount: 1250, currency: 'MUR' });
  });
});

// ─── PriceExtractor – Confidence-Filterung ────────────────────────────────────

describe('PriceExtractor – Confidence-Filterung', () => {
  it('verwirft Ergebnis wenn alle Items unter Schwellwert (< 0.40) → null', () => {
    const r = makeResult([
      { value: 'Rs', confidence: 0.38 },
      { value: '1250', confidence: 0.35 },
    ]);
    expect(extractPrice(r)).toBeNull();
  });

  it('verwirft einzelne Items unter Schwellwert, behält valide', () => {
    const r = makeResult([
      { value: 'Rs', confidence: 0.88 },
      { value: '1250', confidence: 0.85 },
      { value: 'TRASH', confidence: 0.20 },
    ]);
    expect(extractPrice(r)).toEqual({ amount: 1250, currency: 'MUR' });
  });

  it('gibt null zurück für leeres RecognitionResult', () => {
    const r: RecognitionResult = { provider: 'test', processingTimeMs: 10, items: [] };
    expect(extractPrice(r)).toBeNull();
  });
});

// ─── PriceExtractor – Edge Cases ──────────────────────────────────────────────

describe('PriceExtractor – Edge Cases', () => {
  it('gibt null zurück wenn kein Währungssymbol vorhanden', () => {
    const r = makeResult([{ value: '1250', confidence: 0.9 }]);
    expect(extractPrice(r)).toBeNull();
  });

  it('gibt null zurück wenn nur Währungssymbol ohne Zahl', () => {
    const r = makeResult([{ value: 'Rs', confidence: 0.9 }]);
    expect(extractPrice(r)).toBeNull();
  });

  it('wählt Kandidaten mit höherer Confidence bei mehreren Preis-Mustern', () => {
    const r: RecognitionResult = {
      provider: 'test',
      processingTimeMs: 100,
      items: [
        // Zeile 1 (y=0): schwacher Kandidat
        { type: 'text', value: 'Rs', confidence: 0.55, boundingBox: { x: 0, y: 0, width: 40, height: 20 } },
        { type: 'text', value: '99', confidence: 0.52, boundingBox: { x: 80, y: 0, width: 40, height: 20 } },
        // Zeile 2 (y=80): starker Kandidat
        { type: 'text', value: 'Rs', confidence: 0.92, boundingBox: { x: 0, y: 80, width: 40, height: 20 } },
        { type: 'text', value: '1,250', confidence: 0.90, boundingBox: { x: 80, y: 80, width: 80, height: 20 } },
      ],
    };
    expect(extractPrice(r)).toEqual({ amount: 1250, currency: 'MUR' });
  });
});
