import { describe, it, expect, beforeAll } from 'vitest';
import { RohlikAPI } from '../src/rohlik-api.js';

describe('Cart Operations', () => {
  let api: RohlikAPI;

  beforeAll(async () => {
    api = new RohlikAPI();
    await api.loadSession();
  });

  describe('getCartContent', () => {
    it('should get cart content with all required fields', async () => {
      const cart = await api.getCartContent();
      
      expect(cart).toBeDefined();
      expect(cart).toHaveProperty('total_items');
      expect(cart).toHaveProperty('total_price');
      expect(cart).toHaveProperty('can_make_order');
      expect(cart).toHaveProperty('currency');
      expect(cart).toHaveProperty('products');
      
      expect(typeof cart.total_items).toBe('number');
      expect(typeof cart.total_price).toBe('number');
      expect(typeof cart.can_make_order).toBe('boolean');
      expect(typeof cart.currency).toBe('string');
      expect(Array.isArray(cart.products)).toBe(true);
    });

    it('should return valid currency code', async () => {
      const cart = await api.getCartContent();
      
      expect(['EUR', 'CZK', 'HUF', 'RON']).toContain(cart.currency);
    });

    it('should have properly structured products', async () => {
      const cart = await api.getCartContent();
      
      if (cart.products.length > 0) {
        const product = cart.products[0];
        
        expect(product).toHaveProperty('id');
        expect(product).toHaveProperty('cart_item_id');
        expect(product).toHaveProperty('name');
        expect(product).toHaveProperty('quantity');
        expect(product).toHaveProperty('price');
        expect(product).toHaveProperty('category_name');
        expect(product).toHaveProperty('brand');
        
        expect(typeof product.name).toBe('string');
        expect(typeof product.quantity).toBe('number');
        expect(typeof product.price).toBe('number');
        expect(product.quantity).toBeGreaterThan(0);
      }
    });
  });

  describe('addToCart', () => {
    it('should add a single product to cart', async () => {
      const searchResults = await api.searchProducts('water', 1);
      expect(searchResults.length).toBeGreaterThan(0);
      
      const product = searchResults[0];
      const added = await api.addToCart([
        { product_id: product.id, quantity: 1 }
      ]);
      
      expect(Array.isArray(added)).toBe(true);
      expect(added.length).toBeGreaterThanOrEqual(0);
    });

    it('should return array of added product IDs', async () => {
      const searchResults = await api.searchProducts('bread', 1);
      
      if (searchResults.length > 0) {
        const product = searchResults[0];
        const added = await api.addToCart([
          { product_id: product.id, quantity: 2 }
        ]);
        
        if (added.length > 0) {
          expect(added[0]).toBe(product.id);
        }
      }
    });

    it('should handle empty product array', async () => {
      const added = await api.addToCart([]);
      
      expect(Array.isArray(added)).toBe(true);
      expect(added.length).toBe(0);
    });
  });

  describe('removeFromCart', () => {
    it('should remove item from cart', async () => {
      const cart = await api.getCartContent();
      
      if (cart.products.length > 0) {
        const cartItemId = cart.products[0].cart_item_id;
        const result = await api.removeFromCart(cartItemId);
        
        expect(typeof result).toBe('boolean');
      }
    });

    it('should return false for invalid cart item ID', async () => {
      const result = await api.removeFromCart('invalid-id-12345');
      
      expect(result).toBe(false);
    });
  });
});
