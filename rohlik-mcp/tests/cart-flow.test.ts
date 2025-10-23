import { describe, it, expect, beforeAll } from 'vitest';
import { RohlikAPI } from '../src/rohlik-api.js';

describe('Cart Flow', () => {
  let api: RohlikAPI;

  beforeAll(async () => {
    api = new RohlikAPI();
    await api.loadSession();
  });

  it('should load session from disk', async () => {
    expect(api).toBeDefined();
  });

  it('should search for products', async () => {
    const results = await api.searchProducts('milk', 3);
    
    expect(results).toBeDefined();
    expect(results.length).toBeGreaterThan(0);
    expect(results.length).toBeLessThanOrEqual(3);
    
    // Verify product structure
    const product = results[0];
    expect(product).toHaveProperty('id');
    expect(product).toHaveProperty('name');
    expect(product).toHaveProperty('price');
    expect(product).toHaveProperty('brand');
    expect(product.id).toBeTypeOf('number');
    expect(product.name).toBeTypeOf('string');
  });

  it('should add product to cart', async () => {
    // First search for a product
    const results = await api.searchProducts('milk', 1);
    expect(results.length).toBeGreaterThan(0);
    
    const product = results[0];
    
    // Add to cart
    const addedProducts = await api.addToCart([
      {
        product_id: product.id,
        quantity: 1
      }
    ]);
    
    expect(addedProducts).toBeDefined();
    expect(addedProducts.length).toBe(1);
    expect(addedProducts[0]).toBe(product.id);
  });

  it('should retrieve cart content', async () => {
    const cart = await api.getCartContent();
    
    expect(cart).toBeDefined();
    expect(cart).toHaveProperty('total_items');
    expect(cart).toHaveProperty('total_price');
    expect(cart).toHaveProperty('can_make_order');
    expect(cart).toHaveProperty('currency');
    expect(cart).toHaveProperty('products');
    
    expect(cart.total_items).toBeGreaterThan(0);
    expect(cart.total_price).toBeGreaterThan(0);
    expect(cart.currency).toBeTypeOf('string');
    expect(Array.isArray(cart.products)).toBe(true);
    
    // Verify product structure in cart
    if (cart.products.length > 0) {
      const cartProduct = cart.products[0];
      expect(cartProduct).toHaveProperty('id');
      expect(cartProduct).toHaveProperty('name');
      expect(cartProduct).toHaveProperty('quantity');
      expect(cartProduct).toHaveProperty('price');
      expect(cartProduct).toHaveProperty('brand');
      expect(cartProduct).toHaveProperty('cart_item_id');
    }
  });

  it('should verify product is in cart', async () => {
    const results = await api.searchProducts('milk', 1);
    const searchedProduct = results[0];
    
    const cart = await api.getCartContent();
    
    // Check if any product in cart matches our search
    const foundInCart = cart.products.some(p => 
      p.name.toLowerCase().includes(searchedProduct.name.toLowerCase().split(' ')[0])
    );
    
    expect(foundInCart).toBe(true);
  });
});
