import { describe, expect, it } from 'vitest';

import { istGaId } from '../lib/zeitung/zustimmung';

describe('istGaId', () => {
  it('akzeptiert GA4-Mess-IDs', () => {
    expect(istGaId('G-ABC123XYZ9')).toBe(true);
  });
  it('lehnt Leeres und Fremdes ab', () => {
    expect(istGaId('')).toBe(false);
    expect(istGaId('UA-12345-1')).toBe(false);
    expect(istGaId('G-abc"><script>')).toBe(false);
  });
});
