export type CurrencyCode = string;

export interface Price {
  amount: number;
  currency: CurrencyCode;
}

export interface ConvertedPrice {
  source: Price;
  target: Price;
}
