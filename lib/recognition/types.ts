export type RecognitionCapability =
  | 'text'
  | 'barcode'
  | 'qrcode'
  | 'product'
  | 'price';

export type BarcodeFormat =
  | 'EAN_13'
  | 'EAN_8'
  | 'UPC_A'
  | 'UPC_E'
  | 'CODE_128'
  | 'QR_CODE';

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface TextItem {
  type: 'text';
  value: string;
  confidence: number;
  boundingBox?: BoundingBox;
}

export interface BarcodeItem {
  type: 'barcode';
  format: BarcodeFormat;
  value: string;
  confidence: number;
  boundingBox?: BoundingBox;
}

export interface QRCodeItem {
  type: 'qrcode';
  value: string;
  confidence: number;
  boundingBox?: BoundingBox;
}

export interface ProductItem {
  type: 'product';
  name: string;
  confidence: number;
  candidates: string[];
}

export type RecognitionItem = TextItem | BarcodeItem | QRCodeItem | ProductItem;

export interface RecognitionResult {
  provider: string;
  items: RecognitionItem[];
  processingTimeMs: number;
}

export interface RecognitionProvider {
  readonly name: string;
  readonly capabilities: RecognitionCapability[];
  recognize(image: Blob): Promise<RecognitionResult>;
}

export function getTexts(result: RecognitionResult): TextItem[] {
  return result.items.filter((i): i is TextItem => i.type === 'text');
}

export function getBarcodes(result: RecognitionResult): BarcodeItem[] {
  return result.items.filter((i): i is BarcodeItem => i.type === 'barcode');
}

export function getQRCodes(result: RecognitionResult): QRCodeItem[] {
  return result.items.filter((i): i is QRCodeItem => i.type === 'qrcode');
}

export function getProducts(result: RecognitionResult): ProductItem[] {
  return result.items.filter((i): i is ProductItem => i.type === 'product');
}
