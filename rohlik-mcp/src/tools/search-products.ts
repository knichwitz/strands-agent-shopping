import { z } from "zod";
import { RohlikAPI } from "../rohlik-api.js";
import { debugLog } from "../utils/debug.js";
import type { SearchProductsOutput } from "../types.js";

export function createSearchProductsTool(createRohlikAPI: () => RohlikAPI) {
  return {
    name: "search_products",
    definition: {
      title: "Search Products",
      description: "Search the Rohlik/Knuspr grocery catalog for products by name or keyword. Returns product details including name, brand, price, and product ID needed for adding to cart. Use this when users want to find, browse, or check prices of grocery items.",
      inputSchema: {
        product_name: z.string().min(1, "Product name cannot be empty").describe("The product name, keyword, or search term (e.g., 'milk', 'organic bread', 'chocolate'). Can be in any language."),
        limit: z.number().min(1).max(50).default(5).describe("Maximum number of products to return in search results. Use lower numbers (3-5) for focused searches, higher numbers (10-20) for browsing. Default is 5 for better performance."),
        sort_by: z.enum(['price_asc', 'price_desc', 'unit_price_asc']).optional().describe("Sort results by price or value. Options: 'price_asc' (cheapest total price first), 'price_desc' (most expensive first), 'unit_price_asc' (best value per unit/kg/liter - RECOMMENDED for finding cheapest options). Default is relevance sorting."),
        organic_only: z.boolean().optional().describe("Filter to show only organic/BIO certified products. Set to true to find organic options. Default is false (shows all products).")
      }
    },
    handler: async (args: { product_name: string; limit?: number; sort_by?: 'price_asc' | 'price_desc' | 'unit_price_asc'; organic_only?: boolean }) => {
      const { product_name, limit = 5, sort_by, organic_only } = args;

      debugLog('search_products - Input', { product_name, limit, sort_by, organic_only });

      try {
        const api = createRohlikAPI();
        const results = await api.searchProducts(product_name, limit, sort_by, organic_only);

        debugLog('search_products - API Response', { resultCount: results.length, results });

        // Return optimized JSON data - keep essential fields but reduce verbosity
        // Images removed for token optimization
        const minimalProducts = results.map(product => ({
          id: product.id,
          name: product.name,
          price: product.price,
          brand: product.brand,
          amount: product.amount,
          category: product.categories?.[0] || '', // Include primary category for relevance
          categories: product.categories,
          inStock: product.inStock
        }));

        // Format as human-readable text with categories included (no images for token optimization)
        const formattedText = `Found ${results.length} products for "${product_name}":\n\n` +
          results.map((product, index) => {
            const categoryText = product.categories?.[0] ? `**Category:** ${product.categories[0]}\n` : '';
            return `### ${index + 1}. ${product.name}\n` +
              (product.brand ? `**Brand:** ${product.brand}\n` : '') +
              categoryText +
              `**Price:** ${product.price}\n` +
              `**Amount:** ${product.amount}\n` +
              `**Product ID:** ${product.id}\n\n---\n\n`;
          }).join('');

        const response = {
          content: [
            {
              type: "text" as const,
              text: formattedText
            }
          ]
        };

        debugLog('search_products - Output', response);
        return response;
      } catch (error) {
        debugLog('search_products - Error', { error: error instanceof Error ? error.message : String(error) });

        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify({
                success: false,
                error: error instanceof Error ? error.message : String(error)
              })
            }
          ],
          isError: true
        };
      }
    }
  };
}
