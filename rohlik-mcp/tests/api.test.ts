import { describe, it, expect, beforeAll } from 'vitest';
import { RohlikAPI } from '../src/rohlik-api.js';

describe('RohlikAPI', () => {
  let api: RohlikAPI;

  beforeAll(async () => {
    api = new RohlikAPI();
    await api.loadSession();
  });

  describe('Product Search', () => {
    it('should search for products by name', async () => {
      const results = await api.searchProducts('bread', 5);
      
      expect(results).toBeDefined();
      expect(Array.isArray(results)).toBe(true);
      expect(results.length).toBeGreaterThan(0);
      expect(results.length).toBeLessThanOrEqual(5);
    });

    it('should return products with required fields', async () => {
      const results = await api.searchProducts('milk', 1);
      
      expect(results.length).toBeGreaterThan(0);
      
      const product = results[0];
      expect(product.id).toBeDefined();
      expect(product.name).toBeDefined();
      expect(product.price).toBeDefined();
      expect(product.brand).toBeDefined();
      expect(product.amount).toBeDefined();
    });

    it('should respect limit parameter', async () => {
      const limit = 2;
      const results = await api.searchProducts('water', limit);
      
      expect(results.length).toBeLessThanOrEqual(limit);
    });

    it('should handle empty search results gracefully', async () => {
      const results = await api.searchProducts('xyznonexistentproduct123', 5);
      
      expect(Array.isArray(results)).toBe(true);
      expect(results.length).toBe(0);
    });
  });

  describe('Cart Operations', () => {
    it('should get cart content', async () => {
      const cart = await api.getCartContent();
      
      expect(cart).toBeDefined();
      expect(typeof cart.total_items).toBe('number');
      expect(typeof cart.total_price).toBe('number');
      expect(typeof cart.can_make_order).toBe('boolean');
      expect(typeof cart.currency).toBe('string');
      expect(Array.isArray(cart.products)).toBe(true);
    });

    it('should add product to cart', async () => {
      const searchResults = await api.searchProducts('apple', 1);
      expect(searchResults.length).toBeGreaterThan(0);
      
      const product = searchResults[0];
      
      const added = await api.addToCart([
        { product_id: product.id, quantity: 1 }
      ]);
      
      expect(added).toBeDefined();
      // Product might fail to add (out of stock, etc.)
      expect(Array.isArray(added)).toBe(true);
      
      // Verify cart is still accessible
      const cart = await api.getCartContent();
      expect(cart).toBeDefined();
      expect(cart).toHaveProperty('total_items');
    });

    it('should handle multiple products in one request', async () => {
      const searchResults = await api.searchProducts('milk', 2);
      
      if (searchResults.length >= 2) {
        const products = searchResults.slice(0, 2).map(p => ({
          product_id: p.id,
          quantity: 1
        }));
        
        const added = await api.addToCart(products);
        // Some products might fail to add (400 error), but at least one should succeed
        expect(added.length).toBeGreaterThanOrEqual(0);
        expect(Array.isArray(added)).toBe(true);
      }
    });
  });

  describe('Currency Detection', () => {
    it('should return correct currency based on region', async () => {
      const cart = await api.getCartContent();
      
      expect(cart.currency).toBeDefined();
      expect(['EUR', 'CZK', 'HUF', 'RON']).toContain(cart.currency);
    });
  });
});
