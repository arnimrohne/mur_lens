import type { CurrencyCode, ConvertedPrice, Price } from '../domain/price';

export const DEFAULT_RATE = 50.0; // 1 EUR = 50 MUR

// Port: implementierbar durch statische Kurse, API-Anbindung usw.
export interface ExchangeRateProvider {
  getRate(from: CurrencyCode, to: CurrencyCode): number;
}

export class CurrencyService {
  constructor(private readonly rates: ExchangeRateProvider) {}

  convert(price: Price, targetCurrency: CurrencyCode): ConvertedPrice {
    if (price.amount <= 0) {
      throw new Error(`Ungültiger Betrag: ${price.amount}`);
    }
    const rate = this.rates.getRate(price.currency, targetCurrency);
    const targetAmount = Math.round((price.amount / rate) * 100) / 100;
    return {
      source: price,
      target: { amount: targetAmount, currency: targetCurrency },
      rate,
    };
  }
}

class StaticRateProvider implements ExchangeRateProvider {
  constructor(private readonly murToEur: number) {}

  getRate(from: CurrencyCode, to: CurrencyCode): number {
    if (from === 'MUR' && to === 'EUR') return this.murToEur;
    throw new Error(`Kein Wechselkurs für ${from} → ${to}`);
  }
}

export const currencyService = new CurrencyService(
  new StaticRateProvider(DEFAULT_RATE),
);
