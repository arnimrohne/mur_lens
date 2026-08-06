export type CurrencyCode = string;

export interface Price {
  amount: number;
  currency: CurrencyCode;
}

export interface ConvertedPrice {
  source: Price;
  target: Price;
  rate: number; // source units per 1 target unit (e.g. 50 means 1 EUR = 50 MUR)
}
