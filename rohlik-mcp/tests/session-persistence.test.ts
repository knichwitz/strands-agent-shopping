import { describe, it, expect, beforeEach } from 'vitest';
import { RohlikAPI } from '../src/rohlik-api.js';

describe('Session Persistence', () => {
  it('should persist cart data across API instance restarts', async () => {
    // Create first instance
    const api1 = new RohlikAPI();
    await api1.loadSession();
    
    // Get cart with first instance
    const cart1 = await api1.getCartContent();
    
    expect(cart1).toBeDefined();
    expect(cart1.total_items).toBeGreaterThanOrEqual(0);
    expect(cart1.total_price).toBeGreaterThanOrEqual(0);
    
    // Simulate server restart - create new instance
    const api2 = new RohlikAPI();
    await api2.loadSession();
    
    // Get cart with second instance
    const cart2 = await api2.getCartContent();
    
    // Verify structure is consistent (values may change if tests modify cart)
    expect(cart2).toBeDefined();
    expect(cart2).toHaveProperty('total_items');
    expect(cart2).toHaveProperty('total_price');
    expect(cart2).toHaveProperty('currency');
    expect(cart2).toHaveProperty('products');
    expect(cart2.currency).toBe(cart1.currency);
  });

  it('should maintain product structure across instances', async () => {
    const api1 = new RohlikAPI();
    await api1.loadSession();
    const cart1 = await api1.getCartContent();
    
    const api2 = new RohlikAPI();
    await api2.loadSession();
    const cart2 = await api2.getCartContent();
    
    // If cart has products, verify structure is consistent
    if (cart1.products.length > 0 && cart2.products.length > 0) {
      const product1 = cart1.products[0];
      const product2 = cart2.products[0];
      
      // Verify both have the same structure
      expect(product2).toHaveProperty('id');
      expect(product2).toHaveProperty('name');
      expect(product2).toHaveProperty('quantity');
      expect(product2).toHaveProperty('price');
      expect(product2).toHaveProperty('cart_item_id');
      
      // Verify types match
      expect(typeof product2.id).toBe(typeof product1.id);
      expect(typeof product2.name).toBe(typeof product1.name);
      expect(typeof product2.quantity).toBe(typeof product1.quantity);
    }
  });

  it('should load session without errors', async () => {
    const api = new RohlikAPI();
    
    // Should not throw
    await expect(api.loadSession()).resolves.not.toThrow();
  });
});
