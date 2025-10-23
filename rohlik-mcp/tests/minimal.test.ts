import { describe, it, expect, beforeAll } from 'vitest';
import { RohlikAPI } from '../src/rohlik-api.js';

describe('Minimal API Test', () => {
  let api: RohlikAPI;

  beforeAll(async () => {
    console.log('Setting up API...');
    api = new RohlikAPI();
    console.log('Loading session...');
    await api.loadSession();
    console.log('Session loaded in test');
  });

  it('should work with minimal test', async () => {
    console.log('Running minimal test...');
    const results = await api.searchProducts('milk', 1);
    
    console.log('Results:', results.length);
    expect(results).toBeDefined();
    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBeGreaterThan(0);
  });
});
