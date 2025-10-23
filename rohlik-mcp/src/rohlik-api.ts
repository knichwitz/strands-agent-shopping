import fetch from 'node-fetch';
import { Product, SearchResult, CartContent, RohlikAPIResponse } from './types.js';
import { promises as fs } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

const BASE_URL = process.env.ROHLIK_BASE_URL || 'https://www.knuspr.de';
const SESSION_FILE = join(homedir(), '.rohlik-session');

// Map base URLs to their CDN URLs
const CDN_MAP: Record<string, string> = {
  'https://www.rohlik.cz': 'https://cdn.rohlik.cz',
  'https://www.knuspr.de': 'https://cdn.knuspr.de',
  'https://www.gurkerl.at': 'https://cdn.gurkerl.at',
  'https://www.kifli.hu': 'https://cdn.kifli.hu',
  'https://www.sezamo.ro': 'https://cdn.sezamo.ro'
};

// Map base URLs to their currencies
const CURRENCY_MAP: Record<string, string> = {
  'https://www.rohlik.cz': 'CZK',
  'https://www.knuspr.de': 'EUR',
  'https://www.gurkerl.at': 'EUR',
  'https://www.kifli.hu': 'HUF',
  'https://www.sezamo.ro': 'RON'
};

function getCdnUrl(): string {
  return CDN_MAP[BASE_URL] || 'https://cdn.knuspr.de';
}

function getCurrency(): string {
  return CURRENCY_MAP[BASE_URL] || 'EUR';
}

export class RohlikAPIError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'RohlikAPIError';
  }
}

export class RohlikAPI {
  private sessionCookies: string = '';

  constructor() {
    // No credentials needed - works with session cookies only
  }

  async loadSession(): Promise<void> {
    try {
      const data = await fs.readFile(SESSION_FILE, 'utf-8');
      const session = JSON.parse(data);
      this.sessionCookies = session.cookie || '';
    } catch (error) {
      // File doesn't exist or is invalid, start fresh
      this.sessionCookies = '';
    }
  }

  getSessionCookie(): string {
    return this.sessionCookies;
  }

  private async saveSession(): Promise<void> {
    try {
      const session = {
        cookie: this.sessionCookies,
        lastUsed: new Date().toISOString()
      };
      await fs.writeFile(SESSION_FILE, JSON.stringify(session));
    } catch (error) {
      console.error('Failed to save session:', error);
    }
  }

  private async makeRequest<T>(
    url: string,
    options: Partial<Parameters<typeof fetch>[1]> = {}
  ): Promise<RohlikAPIResponse<T>> {
    // Set language cookies for English responses
    const languageCookies = 'language=en-GB; NEXT_LOCALE=en-DE;';
    const combinedCookies = this.sessionCookies 
      ? `${this.sessionCookies}; ${languageCookies}`
      : languageCookies;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      'Cookie': combinedCookies,
      ...(options.headers as Record<string, string> || {})
    };

    const response = await fetch(`${BASE_URL}${url}`, {
      ...options,
      headers
    });

    // Store cookies for session management
    const setCookieHeader = response.headers.get('set-cookie');
    if (setCookieHeader) {
      this.sessionCookies = setCookieHeader;
      // Save session asynchronously without blocking
      this.saveSession().catch(err => console.error('Session save error:', err));
    }

    if (!response.ok) {
      throw new RohlikAPIError(`HTTP ${response.status}: ${response.statusText}`, response.status);
    }

    return await response.json() as RohlikAPIResponse<T>;
  }



  async searchProducts(
    productName: string,
    limit: number = 10,
    sortBy?: 'price_asc' | 'price_desc' | 'unit_price_asc',
    organicOnly?: boolean
  ): Promise<SearchResult[]> {
    try {
      // Build filterData with optional sorting and filtering
      const filterData: any = { filters: [] };

      // Add organic filter if requested
      if (organicOnly) {
        filterData.filters.push({
          filterSlug: 'b-i-o',
          valueSlug: 'bio-items'
        });
      }

      // Add sorting if requested
      if (sortBy) {
        const sortTypeMap: Record<string, string> = {
          'price_asc': 'orderPriceAsc',
          'price_desc': 'orderPriceDesc',
          'unit_price_asc': 'orderUnitPriceAsc'
        };
        filterData.sortType = sortTypeMap[sortBy];
      }

      const searchParams = new URLSearchParams({
        search: productName,
        offset: '0',
        limit: String(limit + 5),
        companyId: '1',
        filterData: JSON.stringify(filterData),
        canCorrect: 'true'
      });

      const response = await this.makeRequest<any>(`/services/frontend-service/search-metadata?${searchParams}`);

      let products = response.data?.productList || [];

      // Remove sponsored content
      products = products.filter((p: any) =>
        !p.badge?.some((badge: any) => badge.slug === 'promoted')
      );

      // Filter out products that are not in stock
      products = products.filter((p: any) => p.inStock === true);

      // Limit results
      products = products.slice(0, limit);

      return products.map((p: any) => ({
        id: p.productId,
        name: p.productName,
        price: `${p.price.full} ${p.price.currency}`,
        brand: p.brand,
        amount: p.textualAmount,
        // imageUrl removed for token optimization
        categories: p.categories ? p.categories.map((cat: any) => cat.name) : [],
        pricePerUnit: p.pricePerUnit ? `${p.pricePerUnit.full} ${p.pricePerUnit.currency}` : undefined,
        inStock: p.inStock,
        maxBasketAmount: p.maxBasketAmount,
        unit: p.unit,
        goodPrice: p.goodPrice,
        sales: p.sales || []
      }));
    } catch (error) {
      throw error;
    }
  }

  async addToCart(products: Product[]): Promise<number[]> {
    const addedProducts: number[] = [];

    for (const product of products) {
      try {
        const payload = {
          actionId: null,
          productId: product.product_id,
          quantity: product.quantity,
          recipeId: null,
          source: 'true:Shopping Lists'
        };

        await this.makeRequest('/services/frontend-service/v2/cart', {
          method: 'POST',
          body: JSON.stringify(payload)
        });

        addedProducts.push(product.product_id);
      } catch (error) {
        console.error('Failed to add product:', product.product_id, error);
      }
    }

    return addedProducts;
  }

  async getCartContent(): Promise<CartContent> {
    const response = await this.makeRequest<any>('/services/frontend-service/v2/cart');
    const data = response.data || {};

    return {
      total_price: data.totalPrice || 0,
      total_items: Object.keys(data.items || {}).length,
      can_make_order: data.submitConditionPassed || false,
      currency: getCurrency(),
      products: Object.entries(data.items || {}).map(([productId, productData]: [string, any]) => ({
        id: productId,
        cart_item_id: productData.orderFieldId || '',
        name: productData.productName || '',
        quantity: productData.quantity || 0,
        price: productData.price || 0,
        category_name: productData.primaryCategoryName || '',
        brand: productData.brand || '',
        // imageUrl removed for token optimization
      }))
    };
  }

  async removeFromCart(orderFieldId: string): Promise<boolean> {
    try {
      await this.makeRequest(`/services/frontend-service/v2/cart?orderFieldId=${orderFieldId}`, {
        method: 'DELETE'
      });
      return true;
    } catch (error) {
      console.error('Failed to remove item:', orderFieldId, error);
      return false;
    }
  }


}
