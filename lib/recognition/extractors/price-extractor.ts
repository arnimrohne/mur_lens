import type { RecognitionResult, TextItem } from '../types';
import type { Price } from '../../domain/price';

const CONFIDENCE_THRESHOLD = 0.40;
const LINE_Y_TOLERANCE = 0.60;

const CURRENCY_RE = /^(Rs\.?|MUR|R\$)$/i;
const NOISE_RE = /^(PRICE|TOTAL|EACH|SALE|OFFER|ITEM|CODE|REF|TAX|INCL|EXCL|PER|KG|GM|ML|LT)$/i;

type TokenRole = 'currency' | 'number' | 'noise';

interface ClassifiedItem {
  item: TextItem;
  role: TokenRole;
}

interface PriceCandidate {
  amount: number;
  currency: string;
  confidence: number;
}

export function extractPrice(result: RecognitionResult): Price | null {
  // Stage 1 – Candidate Filtering: drop everything below confidence threshold
  const above = result.items
    .filter((i): i is TextItem => i.type === 'text')
    .filter((i) => i.confidence >= CONFIDENCE_THRESHOLD);
  if (above.length === 0) return null;

  // Stage 2 – Token Classification: currency, number, or noise
  const classified: ClassifiedItem[] = above
    .map((item) => ({ item, role: classifyToken(item.value) }))
    .filter((c) => c.role !== 'noise');
  if (classified.length === 0) return null;

  // Stage 3 – Line Grouping: cluster by y-proximity before merging
  const lines = groupIntoLines(classified);

  // Stage 4 – Per-line: merge number tokens, normalise, validate
  const candidates: PriceCandidate[] = [];
  for (const line of lines) {
    const sorted = [...line].sort(
      (a, b) => (a.item.boundingBox?.x ?? 0) - (b.item.boundingBox?.x ?? 0),
    );
    const c = extractFromLine(sorted);
    if (c) candidates.push(c);
  }
  if (candidates.length === 0) return null;

  // Stage 5 – Best Match Selection: highest composite confidence wins
  const best = candidates.reduce((b, c) => (c.confidence > b.confidence ? c : b));
  return { amount: best.amount, currency: best.currency };
}

// ─── Classification ────────────────────────────────────────────────────────────

function classifyToken(value: string): TokenRole {
  const v = value.trim();
  if (CURRENCY_RE.test(v)) return 'currency';
  if (NOISE_RE.test(v)) return 'noise';
  if (looksLikeNumber(v)) return 'number';
  return 'noise';
}

function looksLikeNumber(value: string): boolean {
  const c = applyCharCorrections(value);
  return /^[\d][,.\d\s]*$/.test(c) || /^[,.\d\s]*[\d]$/.test(c);
}

// ─── Line Grouping ─────────────────────────────────────────────────────────────

function groupIntoLines(items: ClassifiedItem[]): ClassifiedItem[][] {
  const enriched = items.map((c) => ({
    ...c,
    yCenter: (c.item.boundingBox?.y ?? 0) + (c.item.boundingBox?.height ?? 20) / 2,
    height: c.item.boundingBox?.height ?? 20,
  }));
  enriched.sort((a, b) => a.yCenter - b.yCenter);

  const avgHeight = enriched.reduce((s, i) => s + i.height, 0) / enriched.length;
  const threshold = avgHeight * LINE_Y_TOLERANCE;

  const lines: ClassifiedItem[][] = [];
  let current: typeof enriched = [enriched[0]];

  for (let i = 1; i < enriched.length; i++) {
    if (enriched[i].yCenter - current[current.length - 1].yCenter <= threshold) {
      current.push(enriched[i]);
    } else {
      lines.push(current.map(({ item, role }) => ({ item, role })));
      current = [enriched[i]];
    }
  }
  lines.push(current.map(({ item, role }) => ({ item, role })));
  return lines;
}

// ─── Per-line Extraction ───────────────────────────────────────────────────────

function extractFromLine(tokens: ClassifiedItem[]): PriceCandidate | null {
  const currencies = tokens.filter((t) => t.role === 'currency');
  const numbers = tokens.filter((t) => t.role === 'number');
  if (currencies.length === 0 || numbers.length === 0) return null;

  const amountStr = numbers.map((t) => t.item.value).join(' ');
  const amount = normalizeAmount(amountStr);
  if (amount === null) return null;

  const currency = normalizeCurrency(currencies[0].item.value);
  if (!currency) return null;

  const all = [...currencies, ...numbers];
  const confidence = all.reduce((s, t) => s + t.item.confidence, 0) / all.length;

  return { amount, currency, confidence };
}

// ─── Normalisation ─────────────────────────────────────────────────────────────

function applyCharCorrections(raw: string): string {
  return raw.replace(/[Oo]/g, '0').replace(/[lI]/g, '1');
}

function normalizeAmount(raw: string): number | null {
  let s = applyCharCorrections(raw).replace(/\s+/g, '');

  const commas = (s.match(/,/g) ?? []).length;
  const dots = (s.match(/\./g) ?? []).length;

  if (commas === 1 && dots === 0) {
    const frac = s.split(',')[1] ?? '';
    s = frac.length === 3 ? s.replace(',', '') : s.replace(',', '.');
  } else if (dots === 1 && commas === 0) {
    const frac = s.split('.')[1] ?? '';
    if (frac.length === 3) s = s.replace('.', '');
    // 1–2 digits after dot → decimal, leave as-is
  } else if (commas >= 1 && dots === 1) {
    // English format: 1,250.50 – comma is thousands, dot is decimal
    s = s.replace(/,/g, '');
  }

  const n = parseFloat(s);
  return Number.isFinite(n) && n > 0 ? n : null;
}

function normalizeCurrency(raw: string): 'MUR' | null {
  const v = raw.replace(/\.$/, '').toUpperCase().replace('R$', 'RS');
  return /^(RS|MUR)$/.test(v) ? 'MUR' : null;
}
