import type TesseractNS from 'tesseract.js';
import type {
  RecognitionCapability,
  RecognitionProvider,
  RecognitionResult,
  TextItem,
} from '../types';

export class TesseractProvider implements RecognitionProvider {
  readonly name = 'tesseract';
  readonly capabilities: RecognitionCapability[] = ['text'];

  private workerPromise: Promise<TesseractNS.Worker> | null = null;

  private getWorker(): Promise<TesseractNS.Worker> {
    if (!this.workerPromise) {
      this.workerPromise = this.initWorker();
    }
    return this.workerPromise;
  }

  private async initWorker(): Promise<TesseractNS.Worker> {
    const { createWorker, OEM } = await import('tesseract.js');
    return createWorker('eng', OEM.LSTM_ONLY);
  }

  async warmUp(): Promise<void> {
    await this.getWorker();
  }

  async recognize(image: Blob): Promise<RecognitionResult> {
    const worker = await this.getWorker();
    const start = performance.now();

    const { data } = await worker.recognize(image, {}, { blocks: true });

    const words: TesseractNS.Word[] =
      data.blocks?.flatMap((block: TesseractNS.Block) =>
        block.paragraphs.flatMap((para: TesseractNS.Paragraph) =>
          para.lines.flatMap((line: TesseractNS.Line) => line.words),
        ),
      ) ?? [];

    const items: TextItem[] = words
      .filter((w) => w.text.trim().length > 0)
      .map((w) => ({
        type: 'text' as const,
        value: w.text.trim(),
        confidence: w.confidence / 100,
        boundingBox: {
          x: w.bbox.x0,
          y: w.bbox.y0,
          width: w.bbox.x1 - w.bbox.x0,
          height: w.bbox.y1 - w.bbox.y0,
        },
      }));

    return {
      provider: this.name,
      items,
      processingTimeMs: Math.round(performance.now() - start),
    };
  }
}
