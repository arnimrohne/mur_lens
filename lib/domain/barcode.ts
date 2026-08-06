import type { BarcodeFormat } from '../recognition/types';

export interface Barcode {
  format: BarcodeFormat;
  value: string;
}
