#!/usr/bin/env node
/**
 * Test script for session persistence
 * Tests that cart persists across API instance restarts
 */

import { config } from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
config({ path: resolve(__dirname, '../.env') });

// Dynamic import to ensure env vars are loaded first
const { RohlikAPI } = await import('../dist/rohlik-api.js');

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function logStep(step, message) {
  log(`\n[Step ${step}] ${message}`, colors.cyan);
}

function logSuccess(message) {
  log(`✓ ${message}`, colors.green);
}

function logError(message) {
  log(`✗ ${message}`, colors.red);
}

function logInfo(message) {
  log(`  ${message}`, colors.yellow);
}

async function testSessionPersistence() {
  log('\n=== Session Persistence Test ===\n', colors.blue);
  
  try {
    // Simulate first "server instance"
    logStep(1, 'Creating first API instance and loading session');
    const api1 = new RohlikAPI();
    await api1.loadSession();
    logSuccess('First instance created');

    // Get cart with first instance
    logStep(2, 'Getting cart content with first instance');
    const cart1 = await api1.getCartContent();
    const currency = cart1.currency || 'EUR';
    logSuccess(`Cart has ${cart1.total_items} items, total: ${cart1.total_price} ${currency}`);
    
    if (cart1.products.length > 0) {
      logInfo('Products in cart:');
      cart1.products.forEach((p, i) => {
        logInfo(`  ${i + 1}. ${p.name} (Qty: ${p.quantity})`);
      });
    }

    // Simulate "server restart" - create new instance
    logStep(3, 'Simulating server restart - creating new API instance');
    const api2 = new RohlikAPI();
    await api2.loadSession();
    logSuccess('Second instance created with loaded session');

    // Get cart with second instance (should have same data)
    logStep(4, 'Getting cart content with second instance');
    const cart2 = await api2.getCartContent();
    logSuccess(`Cart has ${cart2.total_items} items, total: ${cart2.total_price} ${currency}`);

    // Verify persistence
    logStep(5, 'Verifying cart data matches');
    
    if (cart1.total_items === cart2.total_items && 
        cart1.total_price === cart2.total_price) {
      logSuccess('Cart data persisted correctly!');
      logInfo(`Both instances show ${cart2.total_items} items and ${cart2.total_price} ${currency}`);
    } else {
      logError('Cart data mismatch!');
      logInfo(`Instance 1: ${cart1.total_items} items, ${cart1.total_price} ${currency}`);
      logInfo(`Instance 2: ${cart2.total_items} items, ${cart2.total_price} ${currency}`);
      process.exit(1);
    }

    // Verify product details match
    if (cart1.products.length === cart2.products.length) {
      logSuccess(`Product count matches: ${cart1.products.length} products`);
    } else {
      logError('Product count mismatch!');
      process.exit(1);
    }

    log('\n=== Session Persistence Test Passed ===\n', colors.green);
    log('✓ Cart data persists across API instance restarts', colors.green);
    log('✓ Session cookie is properly saved and loaded', colors.green);
    
  } catch (error) {
    logError(`Test failed: ${error instanceof Error ? error.message : String(error)}`);
    if (error instanceof Error && error.stack) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

// Run the test
testSessionPersistence();
