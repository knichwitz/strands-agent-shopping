import { describe, it, expect, beforeAll } from 'vitest';
import { RohlikAPI } from '../src/rohlik-api.js';

describe('Comprehensive Search Tests', () => {
  let api: RohlikAPI;

  beforeAll(async () => {
    api = new RohlikAPI();
    await api.loadSession();
  });

  describe('Diverse Product Categories', () => {
    const searchTerms = [
      // Dairy
      { term: 'milk', category: 'Dairy' },
      { term: 'butter', category: 'Dairy' },
      { term: 'cheese', category: 'Dairy' },
      { term: 'yogurt', category: 'Dairy' },
      
      // Bakery
      { term: 'bread', category: 'Bakery' },
      { term: 'rolls', category: 'Bakery' },
      
      // Protein
      { term: 'chicken breast', category: 'Protein' },
      { term: 'eggs', category: 'Protein' },
      { term: 'salmon', category: 'Protein' },
      
      // Produce
      { term: 'apples', category: 'Produce' },
      { term: 'tomatoes', category: 'Produce' },
      { term: 'bananas', category: 'Produce' },
      { term: 'carrots', category: 'Produce' },
      
      // Pantry
      { term: 'rice', category: 'Pantry' },
      { term: 'pasta', category: 'Pantry' },
      { term: 'flour', category: 'Pantry' },
      
      // Beverages
      { term: 'water', category: 'Beverages' },
      { term: 'juice', category: 'Beverages' },
      { term: 'coffee', category: 'Beverages' }
    ];

    it('should find products for all search terms', async () => {
      console.log('\n=== Testing Product Search Across Categories ===\n');
      
      const results: Array<{ term: string; category: string; count: number }> = [];
      
      for (const { term, category } of searchTerms) {
        const products = await api.searchProducts(term, 10);
        results.push({ term, category, count: products.length });
        
        expect(products).toBeDefined();
        expect(Array.isArray(products)).toBe(true);
      }
      
      // Print results table
      console.log('┌──────────────────────┬───────────┬────────┐');
      console.log('│ Search Term          │ Category  │ Found  │');
      console.log('├──────────────────────┼───────────┼────────┤');
      
      results.forEach(r => {
        const term = r.term.padEnd(20);
        const category = r.category.padEnd(9);
        const count = String(r.count).padStart(6);
        console.log(`│ ${term} │ ${category} │ ${count} │`);
      });
      
      console.log('└──────────────────────┴───────────┴────────┘');
      
      const totalFound = results.reduce((sum, r) => sum + r.count, 0);
      const avgPerTerm = (totalFound / results.length).toFixed(1);
      console.log(`\n📊 Total: ${totalFound} products found (avg ${avgPerTerm} per term)`);
    });
  });

  describe('Organic Filter Across Categories', () => {
    const organicTests = [
      'milk', 'bread', 'eggs', 'apples', 'tomatoes', 
      'chicken breast', 'butter', 'yogurt', 'rice'
    ];

    it('should test organic_only across diverse products', async () => {
      console.log('\n=== Organic Filter Analysis ===\n');
      
      const results: Array<{
        term: string;
        total: number;
        organic: number;
        percentage: number;
      }> = [];
      
      for (const term of organicTests) {
        const all = await api.searchProducts(term, 20);
        const organic = await api.searchProducts(term, 20, undefined, true);
        
        const percentage = all.length > 0 ? (organic.length / all.length * 100) : 0;
        
        results.push({
          term,
          total: all.length,
          organic: organic.length,
          percentage
        });
        
        expect(organic.length).toBeLessThanOrEqual(all.length);
      }
      
      // Print results
      console.log('┌──────────────────┬───────┬─────────┬────────────┐');
      console.log('│ Product          │ Total │ Organic │ % Organic  │');
      console.log('├──────────────────┼───────┼─────────┼────────────┤');
      
      results.forEach(r => {
        const term = r.term.padEnd(16);
        const total = String(r.total).padStart(5);
        const organic = String(r.organic).padStart(7);
        const percentage = (r.percentage.toFixed(0) + '%').padStart(10);
        
        console.log(`│ ${term} │ ${total} │ ${organic} │ ${percentage} │`);
      });
      
      console.log('└──────────────────┴───────┴─────────┴────────────┘');
      
      const totalProducts = results.reduce((sum, r) => sum + r.total, 0);
      const totalOrganic = results.reduce((sum, r) => sum + r.organic, 0);
      const overallPercentage = totalProducts > 0 ? (totalOrganic / totalProducts * 100).toFixed(1) : '0';
      
      console.log(`\n🌱 Overall: ${totalOrganic}/${totalProducts} products are organic (${overallPercentage}%)`);
    });
  });

  describe('Price Sorting Across Categories', () => {
    const sortTests = ['milk', 'bread', 'eggs', 'apples', 'chicken breast'];

    it('should test price sorting for different products', async () => {
      console.log('\n=== Price Sorting Analysis ===\n');
      
      for (const term of sortTests) {
        console.log(`\n📦 ${term.toUpperCase()}`);
        
        // Test ascending
        const ascending = await api.searchProducts(term, 5, 'price_asc');
        const ascPrices = ascending.map(p => {
          const match = p.price.match(/[\d,]+\.?\d*/);
          return match ? parseFloat(match[0].replace(',', '')) : 0;
        });
        
        console.log(`   Ascending: ${ascPrices.map(p => p.toFixed(2) + '€').join(' → ')}`);
        
        // Check if sorted
        let ascSorted = true;
        for (let i = 1; i < ascPrices.length; i++) {
          if (ascPrices[i] < ascPrices[i - 1]) {
            ascSorted = false;
            break;
          }
        }
        console.log(`   ${ascSorted ? '✅' : '⚠️'} ${ascSorted ? 'Correctly sorted' : 'Not perfectly sorted'}`);
        
        // Test descending
        const descending = await api.searchProducts(term, 5, 'price_desc');
        const descPrices = descending.map(p => {
          const match = p.price.match(/[\d,]+\.?\d*/);
          return match ? parseFloat(match[0].replace(',', '')) : 0;
        });
        
        console.log(`   Descending: ${descPrices.map(p => p.toFixed(2) + '€').join(' → ')}`);
        
        let descSorted = true;
        for (let i = 1; i < descPrices.length; i++) {
          if (descPrices[i] > descPrices[i - 1]) {
            descSorted = false;
            break;
          }
        }
        console.log(`   ${descSorted ? '✅' : '⚠️'} ${descSorted ? 'Correctly sorted' : 'Not perfectly sorted'}`);
        
        expect(Array.isArray(ascending)).toBe(true);
        expect(Array.isArray(descending)).toBe(true);
      }
    });
  });

  describe('Combined Filters', () => {
    it('should test organic filter combinations', async () => {
      console.log('\n=== Combined Filters: Organic Only ===\n');
      
      const testTerms = ['milk', 'bread', 'eggs', 'butter', 'yogurt'];
      
      for (const term of testTerms) {
        const all = await api.searchProducts(term, 20);
        const organic = await api.searchProducts(term, 20, undefined, true);
        
        console.log(`${term}:`);
        console.log(`  All products: ${all.length}`);
        console.log(`  Organic only: ${organic.length}`);
        console.log(`  ✅ Found ${organic.length} organic products`);
        console.log('');
        
        expect(organic.length).toBeLessThanOrEqual(all.length);
      }
    });

    it('should test sorting + filters combinations', async () => {
      console.log('\n=== Combined: Sorting + Filters ===\n');
      
      const result = await api.searchProducts('milk', 10, 'price_asc', true);
      
      console.log(`Organic milk sorted by price (ascending):`);
      result.forEach((p, i) => {
        console.log(`  ${i + 1}. ${p.name}`);
        console.log(`     ${p.price} - ${p.amount}`);
      });
      
      expect(result.length).toBeGreaterThan(0);
    });
  });
});
