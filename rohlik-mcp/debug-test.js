import { RohlikAPI } from './dist/rohlik-api.js';

async function debugTest() {
  console.log('=== Debug Test ===');
  
  try {
    const api = new RohlikAPI();
    console.log('API instance created');
    
    console.log('Loading session...');
    await api.loadSession();
    console.log('Session loaded successfully');
    
    console.log('Testing search with "bread"...');
    const result = await api.searchProducts('bread', 5);
    console.log('✅ Search successful:', result.length, 'products found');
    
    if (result.length > 0) {
      console.log('First product:', result[0].name);
    }
    
    console.log('Testing cart content...');
    const cart = await api.getCartContent();
    console.log('✅ Cart content retrieved:', cart.products.length, 'items');
    
  } catch (error) {
    console.error('❌ Error details:', error.message);
    console.error('Status:', error.status);
    
    // Try to get more details about the request
    if (error.response) {
      try {
        const responseText = await error.response.text();
        console.error('Response body:', responseText);
      } catch (e) {
        console.error('Could not read response body');
      }
    }
  }
}

debugTest();
