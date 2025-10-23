import { z } from "zod";
import { RohlikAPI } from "../rohlik-api.js";
import type { GetCartContentOutput, AddToCartOutput, RemoveFromCartOutput, HandoverCartOutput } from "../types.js";

export function createCartManagementTools(createRohlikAPI: () => RohlikAPI) {
  return {
    addToCart: {
      name: "add_to_cart",
      definition: {
        title: "Add to Cart",
        description: "Add one or more products to the shopping cart. Use the product_id from search results. You can add multiple different products in a single call. The cart persists across sessions automatically.",
        inputSchema: {
          products: z.array(z.object({
            product_id: z.number().int().describe("The product ID number obtained from search_products results. This is the unique identifier for each product."),
            quantity: z.number().int().min(1).describe("How many units of this product to add to the cart. Must be a whole number (integer) of at least 1. For items sold by weight (e.g., 1.5kg), just add 1 unit and adjust in the cart later.")
          })).min(1, "At least one product is required").describe("IMPORTANT: Pass as an object with 'products' key, not a raw array. Format: {\"products\": [{\"product_id\": 2207, \"quantity\": 2}, {\"product_id\": 5432, \"quantity\": 1}]}")
        }
      },
      handler: async ({ products }: {
        products: Array<{ product_id: number; quantity: number }>;
      }) => {
        try {
          const api = createRohlikAPI();
          const addedProducts = await api.addToCart(products);

          // Minimal response to reduce tokens
          const output: AddToCartOutput = {
            success: true,
            added_count: addedProducts.length,
            requested_count: products.length,
            added_product_ids: addedProducts
          };

          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify(output)
              }
            ]
          };
        } catch (error) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  success: false,
                  error: error instanceof Error ? error.message : String(error)
                }, null, 2)
              }
            ],
            isError: true
          };
        }
      }
    },

    getCartContent: {
      name: "get_cart_content",
      definition: {
        title: "Get Cart Content",
        description: "Retrieve the current shopping cart contents including all products, quantities, prices, and total. Use this to show users what's in their cart, check the total price, or get cart_item_id values needed for removing items. The cart persists between sessions.",
        inputSchema: {}
      },
      handler: async () => {
        try {
          const api = createRohlikAPI();
          const cart = await api.getCartContent();

          // Return optimized cart data - keep essential fields but reduce verbosity
          const minimalCart = {
            success: true,
            cart: {
              total_items: cart.total_items,
              total_price: cart.total_price,
              currency: cart.currency,
              products: cart.products.map(product => ({
                cart_item_id: product.cart_item_id,
                id: product.id,
                name: product.name,
                brand: product.brand,
                quantity: product.quantity,
                price: product.price,
                category_name: product.category_name
              }))
            }
          };

          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify(minimalCart)
              }
            ]
          };
        } catch (error) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  success: false,
                  error: error instanceof Error ? error.message : String(error)
                }, null, 2)
              }
            ],
            isError: true
          };
        }
      }
    },

    removeFromCart: {
      name: "remove_from_cart",
      definition: {
        title: "Remove from Cart",
        description: "Remove a specific item from the shopping cart. You must first call get_cart_content to obtain the cart_item_id for the product you want to remove. Each item in the cart has a unique cart_item_id even if it's the same product.",
        inputSchema: {
          order_field_id: z.string().describe("The cart_item_id string from get_cart_content results. This identifies which specific cart item to remove. Example: '182654691'")
        }
      },
      handler: async ({ order_field_id }: { order_field_id: string }) => {
        try {
          const api = createRohlikAPI();
          await api.removeFromCart(order_field_id);

          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  success: true,
                  message: "Item removed from cart"
                })
              }
            ]
          };
        } catch (error) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  success: false,
                  error: error instanceof Error ? error.message : String(error)
                }, null, 2)
              }
            ],
            isError: true
          };
        }
      }
    },

    handoverCart: {
      name: "handover_cart",
      definition: {
        title: "Handover Cart",
        description: "Get the session cookie to transfer the current cart to a web browser. Use this when the user wants to complete their order. IMPORTANT: After calling this, immediately call 'open_browser_with_cart' from the Cart Checkout MCP to automatically open a browser - don't just give the user manual instructions. The workflow is: handover_cart → open_browser_with_cart.",
        inputSchema: {}
      },
      handler: async () => {
        try {
          const api = createRohlikAPI();
          const sessionCookie = api.getSessionCookie();

          if (!sessionCookie) {
            return {
              content: [
                {
                  type: "text" as const,
                  text: JSON.stringify({
                    success: false,
                    message: "No active session found. Please ensure you have a valid session cookie in ~/.rohlik-session"
                  }, null, 2)
                }
              ]
            };
          }

          const output: HandoverCartOutput = {
            success: true,
            session_cookie: sessionCookie,
            instructions: "Import this cookie into your browser to access your cart. In Chrome/Firefox: Open DevTools > Application/Storage > Cookies, then add this cookie value."
          };

          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify(output)
              }
            ]
          };
        } catch (error) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  success: false,
                  error: error instanceof Error ? error.message : String(error)
                }, null, 2)
              }
            ],
            isError: true
          };
        }
      }
    }
  };
}
