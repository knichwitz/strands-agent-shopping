#!/usr/bin/env node

import { config } from 'dotenv';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

// Load .env from project root silently
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const envPath = resolve(__dirname, '..', '.env');
config({ path: envPath, quiet: true });

import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { RohlikAPI } from "./rohlik-api.js";
import { debugLog, isDebugEnabled } from "./utils/debug.js";
import { createSearchProductsTool } from "./tools/search-products.js";
import { createCartManagementTools } from "./tools/cart-management.js";

const server = new McpServer(
  {
    name: "rohlik-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Create a singleton instance that persists across all tool calls
const rohlikAPIInstance = new RohlikAPI();

function createRohlikAPI() {
  return rohlikAPIInstance;
}

// Wrapper to add debug logging to all tool handlers
function wrapHandlerWithDebug(toolName: string, handler: any) {
  return async (args: any) => {
    debugLog(`${toolName} - Request`, args);
    try {
      const result = await handler(args);
      debugLog(`${toolName} - Response`, result);
      return result;
    } catch (error) {
      debugLog(`${toolName} - Error`, { error: error instanceof Error ? error.message : String(error), stack: error instanceof Error ? error.stack : undefined });
      throw error;
    }
  };
}

// Register core shopping tools
const searchProducts = createSearchProductsTool(createRohlikAPI);
const cartTools = createCartManagementTools(createRohlikAPI);

// Product search
server.registerTool(searchProducts.name, searchProducts.definition, wrapHandlerWithDebug(searchProducts.name, searchProducts.handler));

// Cart management
server.registerTool(cartTools.addToCart.name, cartTools.addToCart.definition, wrapHandlerWithDebug(cartTools.addToCart.name, cartTools.addToCart.handler));
server.registerTool(cartTools.getCartContent.name, cartTools.getCartContent.definition, wrapHandlerWithDebug(cartTools.getCartContent.name, cartTools.getCartContent.handler));
server.registerTool(cartTools.removeFromCart.name, cartTools.removeFromCart.definition, wrapHandlerWithDebug(cartTools.removeFromCart.name, cartTools.removeFromCart.handler));
server.registerTool(cartTools.handoverCart.name, cartTools.handoverCart.definition, wrapHandlerWithDebug(cartTools.handoverCart.name, cartTools.handoverCart.handler));

async function main() {
  // Load saved session on startup
  await rohlikAPIInstance.loadSession();
  console.error("Session loaded from disk");

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Rohlik MCP server running on stdio");
  if (isDebugEnabled()) {
    console.error("DEBUG mode enabled - detailed logging active");
  }
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
