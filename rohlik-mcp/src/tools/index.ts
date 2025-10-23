import { RohlikAPI } from "../rohlik-api.js";
import { createSearchProductsTool } from "./search-products.js";
import { createCartManagementTools } from "./cart-management.js";

export function createAllTools(createRohlikAPI: () => RohlikAPI) {
  const searchProducts = createSearchProductsTool(createRohlikAPI);
  const cartTools = createCartManagementTools(createRohlikAPI);

  return {
    [searchProducts.name]: searchProducts,
    [cartTools.addToCart.name]: cartTools.addToCart,
    [cartTools.getCartContent.name]: cartTools.getCartContent,
    [cartTools.removeFromCart.name]: cartTools.removeFromCart,
  };
}