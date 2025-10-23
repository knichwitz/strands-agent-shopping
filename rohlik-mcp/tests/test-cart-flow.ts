#!/usr/bin/env node
/**
 * Test script for cart functionality
 * Tests: search -> add to cart -> get cart content
 */

import { RohlikAPI } from './src/rohlik-api.js';

// ANSI color codes for pretty output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message: string, color: string = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function logStep(step: number, message: string) {
  log(`\n[Step ${step}] ${message}`, colors.cyan);
}

function logSuccess(message: string) {
  log(`✓ ${message}`, colors.green);
}

function logError(message: string) {
  log(`✗ ${message}`, colors.red);
}

function logInfo(message: string) {
  log(`  ${message}`, colors.yellow);
}

async function testCartFlow() {
  log('\n=== Rohlik Cart Flow Test ===\n', colors.blue);
  
  // Create API instance (singleton pattern)
  const api = new RohlikAPI();
  
  try {
    // Step 1: Load existing session
    logStep(1, 'Loading session from disk');
    await api.loadSession();
    logSuccess('Session loaded');

    // Step 2: Search for a product
    logStep(2, 'Searching for products (query: "milk")');
    const searchResults = await api.searchProducts('milk', 3);
    
    if (searchResults.length === 0) {
      logError('No products found');
      return;
    }
    
    logSuccess(`Found ${searchResults.length} products`);
    searchResults.forEach((product, index) => {
      logInfo(`${index + 1}. ${product.name} - ${product.price} (ID: ${product.id})`);
    });

    // Step 3: Add first product to cart
    const productToAdd = searchResults[0];
    logStep(3, `Adding product to cart: ${productToAdd.name}`);
    
    const addedProducts = await api.addToCart([
      {
        product_id: productToAdd.id,
        quantity: 1
      }
    ]);

    if (addedProducts.length > 0) {
      logSuccess(`Product ${addedProducts[0]} added to cart`);
    } else {
      logError('Failed to add product to cart');
      return;
    }

    // Step 4: Get cart content
    logStep(4, 'Retrieving cart content');
    const cart = await api.getCartContent();
    
    logSuccess('Cart retrieved successfully');
    logInfo(`Total items: ${cart.total_items}`);
    logInfo(`Total price: ${cart.total_price} CZK`);
    logInfo(`Can make order: ${cart.can_make_order ? 'Yes' : 'No'}`);
    
    if (cart.products.length > 0) {
      log('\n  Products in cart:', colors.yellow);
      cart.products.forEach((product, index) => {
        logInfo(`  ${index + 1}. ${product.name} (${product.brand})`);
        logInfo(`     Quantity: ${product.quantity}, Price: ${product.price} CZK`);
        logInfo(`     Cart ID: ${product.cart_item_id}`);
      });
    }

    // Step 5: Verify the product we added is in the cart
    logStep(5, 'Verifying product is in cart');
    const foundInCart = cart.products.some(p => 
      p.name.toLowerCase().includes(productToAdd.name.toLowerCase().split(' ')[0])
    );
    
    if (foundInCart) {
      logSuccess('Product verified in cart!');
    } else {
      logError('Product not found in cart (might be a different product)');
    }

    log('\n=== Test Completed Successfully ===\n', colors.green);
    
  } catch (error) {
    logError(`Test failed: ${error instanceof Error ? error.message : String(error)}`);
    if (error instanceof Error && error.stack) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

// Run the test
testCartFlow();
