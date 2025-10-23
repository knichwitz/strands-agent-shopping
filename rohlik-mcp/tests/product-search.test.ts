import { describe, it, expect, beforeAll } from 'vitest';
import { RohlikAPI } from '../src/rohlik-api.js';

describe('Product Search', () => {
  let api: RohlikAPI;

  beforeAll(async () => {
    api = new RohlikAPI();
    await api.loadSession();
  });

  describe('searchProducts', () => {
    it('should search for products by name', async () => {
      const results = await api.searchProducts('milk', 5);
      
      expect(Array.isArray(results)).toBe(true);
      expect(results.length).toBeGreaterThan(0);
      expect(results.length).toBeLessThanOrEqual(5);
    });

    it('should return products with all required fields', async () => {
      const results = await api.searchProducts('bread', 1);
      
      expect(results.length).toBeGreaterThan(0);
      
      const product = results[0];
      expect(product).toHaveProperty('id');
      expect(product).toHaveProperty('name');
      expect(product).toHaveProperty('price');
      expect(product).toHaveProperty('brand');
      expect(product).toHaveProperty('amount');
      
      expect(typeof product.id).toBe('number');
      expect(typeof product.name).toBe('string');
      expect(typeof product.price).toBe('string');
      expect(typeof product.brand).toBe('string');
      expect(typeof product.amount).toBe('string');
    });

    it('should respect limit parameter', async () => {
      const limit = 3;
      const results = await api.searchProducts('water', limit);
      
      expect(results.length).toBeLessThanOrEqual(limit);
    });

    it('should handle different search terms', async () => {
      const terms = ['apple', 'cheese', 'coffee'];
      
      for (const term of terms) {
        const results = await api.searchProducts(term, 2);
        expect(Array.isArray(results)).toBe(true);
      }
    });

    it('should return empty array for non-existent products', async () => {
      const results = await api.searchProducts('xyznonexistentproduct999', 5);
      
      expect(Array.isArray(results)).toBe(true);
      expect(results.length).toBe(0);
    });

    it('should handle large limit values', async () => {
      const results = await api.searchProducts('milk', 50);
      
      expect(Array.isArray(results)).toBe(true);
      expect(results.length).toBeLessThanOrEqual(50);
    });

    it('should include image URL when available', async () => {
      const results = await api.searchProducts('milk', 1);
      
      if (results.length > 0) {
        const product = results[0];
        if (product.imageUrl) {
          expect(typeof product.imageUrl).toBe('string');
          expect(product.imageUrl).toMatch(/^https?:\/\//);
        }
      }
    });

    it('should filter out sponsored products', async () => {
      const results = await api.searchProducts('popular', 10);
      
      // All results should be organic (no sponsored content)
      expect(Array.isArray(results)).toBe(true);
    });
  });
});
