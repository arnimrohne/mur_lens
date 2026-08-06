import { describe, it, expect } from 'vitest';
import {
  CurrencyService,
  DEFAULT_RATE,
  currencyService,
  type ExchangeRateProvider,
} from '@/lib/services/currency-service';

// ─── Helpers ──────────────────────────────────────────────────────────────────

function staticProvider(murToEur: number): ExchangeRateProvider {
  return {
    getRate(from, to) {
      if (from === 'MUR' && to === 'EUR') return murToEur;
      throw new Error(`No rate for ${from}/${to}`);
    },
  };
}

const service = new CurrencyService(staticProvider(50));

// ─── CurrencyService – Normale Preise ─────────────────────────────────────────

describe('CurrencyService – Normale Preise', () => {
  it('wandelt 1250 MUR in 25.00 EUR um (Kurs 50)', () => {
    const result = service.convert({ amount: 1250, currency: 'MUR' }, 'EUR');
    expect(result.target).toEqual({ amount: 25, currency: 'EUR' });
  });

  it('wandelt 500 MUR in 10.00 EUR um', () => {
    const result = service.convert({ amount: 500, currency: 'MUR' }, 'EUR');
    expect(result.target).toEqual({ amount: 10, currency: 'EUR' });
  });

  it('wandelt 50 MUR in 1.00 EUR um', () => {
    const result = service.convert({ amount: 50, currency: 'MUR' }, 'EUR');
    expect(result.target).toEqual({ amount: 1, currency: 'EUR' });
  });

  it('bewahrt den Quellpreis in result.source', () => {
    const price = { amount: 1250, currency: 'MUR' };
    const result = service.convert(price, 'EUR');
    expect(result.source).toEqual(price);
  });

  it('enthält den verwendeten Wechselkurs in result.rate', () => {
    const result = service.convert({ amount: 1250, currency: 'MUR' }, 'EUR');
    expect(result.rate).toBe(50);
  });
});

// ─── CurrencyService – Dezimalwerte ───────────────────────────────────────────

describe('CurrencyService – Dezimalwerte', () => {
  it('wandelt 1250.5 MUR → 25.01 EUR', () => {
    const result = service.convert({ amount: 1250.5, currency: 'MUR' }, 'EUR');
    expect(result.target.amount).toBe(25.01);
  });

  it('wandelt 19.95 MUR → 0.40 EUR (gerundet)', () => {
    const result = service.convert({ amount: 19.95, currency: 'MUR' }, 'EUR');
    expect(result.target.amount).toBe(0.40);
  });

  it('wandelt 1 MUR → 0.02 EUR', () => {
    const result = service.convert({ amount: 1, currency: 'MUR' }, 'EUR');
    expect(result.target.amount).toBe(0.02);
  });
});

// ─── CurrencyService – Rundung ────────────────────────────────────────────────

describe('CurrencyService – Rundung auf 2 Stellen', () => {
  it('rundet Ergebnis auf genau 2 Nachkommastellen', () => {
    // 100/3 = 33.333... → 33.33
    const svc = new CurrencyService(staticProvider(3));
    const result = svc.convert({ amount: 100, currency: 'MUR' }, 'EUR');
    expect(result.target.amount).toBe(33.33);
  });

  it('rundet 0.5 auf (kaufmännisch)', () => {
    // 1001/50 = 20.02
    const result = service.convert({ amount: 1001, currency: 'MUR' }, 'EUR');
    expect(result.target.amount).toBe(20.02);
  });

  it('gibt keine Gleitkomma-Artefakte zurück (z. B. 25.0000001)', () => {
    const result = service.convert({ amount: 1250, currency: 'MUR' }, 'EUR');
    const str = result.target.amount.toString();
    expect(str).toBe('25');
  });

  it('funktioniert auch mit nicht-ganzzahligem Kurs (48.5)', () => {
    const svc = new CurrencyService(staticProvider(48.5));
    const result = svc.convert({ amount: 1250, currency: 'MUR' }, 'EUR');
    // 1250 / 48.5 = 25.7731... → 25.77
    expect(result.target.amount).toBe(25.77);
  });
});

// ─── CurrencyService – Ungültige Eingaben ─────────────────────────────────────

describe('CurrencyService – Ungültige Eingaben', () => {
  it('wirft Fehler bei Betrag 0', () => {
    expect(() => service.convert({ amount: 0, currency: 'MUR' }, 'EUR')).toThrow();
  });

  it('wirft Fehler bei negativem Betrag', () => {
    expect(() => service.convert({ amount: -100, currency: 'MUR' }, 'EUR')).toThrow();
  });

  it('wirft Fehler bei nicht unterstütztem Währungspaar', () => {
    expect(() => service.convert({ amount: 100, currency: 'USD' }, 'EUR')).toThrow();
  });

  it('wirft Fehler bei nicht unterstützter Zielwährung', () => {
    expect(() => service.convert({ amount: 100, currency: 'MUR' }, 'GBP')).toThrow();
  });
});

// ─── CurrencyService – Konfiguration ──────────────────────────────────────────

describe('CurrencyService – Konfiguration', () => {
  it('DEFAULT_RATE ist 50.0', () => {
    expect(DEFAULT_RATE).toBe(50.0);
  });

  it('exportierter currencyService verwendet DEFAULT_RATE', () => {
    const result = currencyService.convert({ amount: 1250, currency: 'MUR' }, 'EUR');
    expect(result.rate).toBe(DEFAULT_RATE);
    expect(result.target.amount).toBe(25);
  });

  it('akzeptiert benutzerdefinierten ExchangeRateProvider', () => {
    const customService = new CurrencyService({
      getRate: () => 100,
    });
    const result = customService.convert({ amount: 1000, currency: 'MUR' }, 'EUR');
    expect(result.target.amount).toBe(10);
  });
});
