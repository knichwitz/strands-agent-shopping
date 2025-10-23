import { z } from 'zod';

export const ProductSchema = z.object({
  product_id: z.number(),
  quantity: z.number().min(1)
});

export const SearchResultSchema = z.object({
  id: z.number(),
  name: z.string(),
  price: z.string(),
  brand: z.string(),
  amount: z.string(),
  // imageUrl removed for token optimization
  categories: z.array(z.string()),
  pricePerUnit: z.string().optional(),
  inStock: z.boolean(),
  maxBasketAmount: z.number(),
  unit: z.string(),
  goodPrice: z.boolean(),
  sales: z.array(z.any())
});

export const CartItemSchema = z.object({
  id: z.string(),
  cart_item_id: z.string(),
  name: z.string(),
  quantity: z.number(),
  price: z.number(),
  category_name: z.string(),
  brand: z.string()
});

export const CartContentSchema = z.object({
  total_price: z.number(),
  total_items: z.number(),
  can_make_order: z.boolean(),
  currency: z.string().optional(),
  products: z.array(CartItemSchema)
});

export type Product = z.infer<typeof ProductSchema>;
export type SearchResult = z.infer<typeof SearchResultSchema>;
export type CartItem = z.infer<typeof CartItemSchema>;
export type CartContent = z.infer<typeof CartContentSchema>;

export interface RohlikAPIResponse<T = any> {
  status: number;
  data?: T;
  messages?: Array<{ content: string }>;
}

// Tool output types
export interface SearchProductsOutput {
  total_results: number;
  products: Array<{
    id: number;
    name: string;
    brand: string;
    price: string;
    amount: string;
    // image_url removed for token optimization
  }>;
}

export interface GetCartContentOutput {
  total_items: number;
  total_price: number;
  currency: string;
  can_make_order: boolean;
  products: Array<{
    id: string;
    cart_item_id: string;
    name: string;
    brand: string;
    quantity: number;
    price: number;
    category_name: string;
    // imageUrl removed for token optimization
  }>;
}

export interface AddToCartOutput {
  success: boolean;
  added_count: number;
  requested_count: number;
  added_product_ids: number[];
}

export interface RemoveFromCartOutput {
  success: boolean;
  removed_cart_item_id: string;
}

export interface HandoverCartOutput {
  success: boolean;
  session_cookie?: string;
  instructions?: string;
  message?: string;
}