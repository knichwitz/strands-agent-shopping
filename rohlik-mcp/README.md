# Rohlik MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue.svg)](https://www.typescriptlang.org/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)

> **Enable AI assistants to search products and manage shopping carts across Rohlik Group's online grocery services.**

⚠️ **Note**: This server uses reverse-engineered APIs and is intended for personal use and educational purposes only.

## Features

- 🔍 **Product Search** - Search grocery catalogs with organic filtering and price sorting
- 🛒 **Cart Management** - Add, remove, and view cart items with persistent sessions
- 🌍 **Multi-Region** - Supports 5 countries (Germany, Czech Republic, Austria, Hungary, Romania)
- 🔄 **Session Persistence** - Cart state maintained across server restarts
- 🤝 **Browser Handover** - Get session cookie to transfer cart to browser for checkout
- 📦 **Type-Safe** - Full TypeScript implementation with structured outputs

## Quick Start

### Installation

```bash
npm install
npm run build
```

### Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` to set your region and enable debug mode:
   ```bash
   # Debug mode (optional)
   DEBUG=true
   
   # Choose your region (default: Germany)
   ROHLIK_BASE_URL=https://www.knuspr.de
   
   # Other regions:
   # ROHLIK_BASE_URL=https://www.rohlik.cz      # Czech Republic
   # ROHLIK_BASE_URL=https://www.gurkerl.at     # Austria  
   # ROHLIK_BASE_URL=https://www.kifli.hu       # Hungary
   # ROHLIK_BASE_URL=https://www.sezamo.ro      # Romania
   ```

### Usage with MCP Client

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "rohlik": {
      "command": "node",
      "args": ["/path/to/rohlik-mcp/dist/index.js"],
      "env": {
        "ROHLIK_BASE_URL": "https://www.knuspr.de",
        "DEBUG": "true"
      }
    }
  }
}
```

## Available Tools

### Product Search
- **`search_products`** - Search products with filters
  - **Parameters**: 
    - `product_name` (required) - Product name, keyword, or search term
    - `limit` (optional, default: 5) - Maximum number of results (1-50)
    - `sort_by` (optional) - Sort by: `'price_asc'`, `'price_desc'`, `'unit_price_asc'`
    - `organic_only` (optional) - Filter to show only organic/BIO products
  
  **💡 Tip for finding cheapest products:**
  - Use `sort_by='unit_price_asc'` to find best value per unit/kg/liter
  - Use `sort_by='price_asc'` to find lowest total price
  - Combine with `organic_only=true` for organic options

### Cart Management
- **`add_to_cart`** - Add products to cart using product IDs from search results
- **`get_cart_content`** - View current cart contents, totals, and get cart item IDs
- **`remove_from_cart`** - Remove specific items using cart_item_id from cart contents
- **`handover_cart`** - Get session cookie to transfer cart to browser for checkout

## Example Prompts

```
"Find organic milk sorted by price"
"Add 2 bottles of the cheapest milk to my cart"
"Show me what's in my cart"
"Give me the session cookie to checkout in my browser"
```

**Finding the best deals:**
```
"Find the cheapest milk per liter"
→ Uses sort_by='unit_price_asc' to compare unit prices

"Show me budget-friendly bread options"
→ Uses sort_by='price_asc' to find lowest prices

"I want organic products with the best value"
→ Combines organic_only=true with sort_by='unit_price_asc'
```

## Session Management

### How It Works

The server uses browser-like session cookies stored in `~/.rohlik-session`. Sessions persist across restarts, maintaining your cart state.

### Getting a Session Cookie

**Option 1: Automatic (Recommended)**
- The server creates an anonymous session automatically when you search for products or add items to cart
- No login credentials required - works out of the box
- Session is saved to `~/.rohlik-session` and persists across server restarts

**Option 2: Import from Browser (Optional)**
1. Log in to Rohlik/Knuspr in your browser (if you want to use your existing account)
2. Open DevTools (F12) → Application → Cookies
3. Copy the `PHPSESSION_*` cookie value
4. Create `~/.rohlik-session`:
   ```json
   {
     "cookie": "PHPSESSION_de-production=YOUR_COOKIE_HERE",
     "lastUsed": "2025-10-23T12:00:00.000Z"
   }
   ```

### Clear Session

```bash
rm ~/.rohlik-session
```

## Development

### Scripts

```bash
npm run build          # Compile TypeScript
npm run start          # Start MCP server
npm test              # Run all tests
npm run test:watch    # Watch mode  
npm run test:ui       # Interactive test UI
npm run test:coverage # Run tests with coverage
npm run inspect       # Test with MCP Inspector
npm run watch         # Watch TypeScript compilation
```

### Testing

The project includes comprehensive tests covering:
- Product search with all parameters and sorting options
- Cart operations (add, remove, get content)
- Session persistence across server restarts
- Handover cart functionality
- Error handling and edge cases

Run tests:
```bash
npm test              # Run all tests
npm run test:ui       # Interactive test interface
npm run test:coverage # Run with coverage report
```

### Project Structure

```
rohlik-mcp/
├── src/
│   ├── index.ts              # MCP server entry point
│   ├── rohlik-api.ts         # Core API client
│   ├── types.ts              # TypeScript types
│   ├── tools/                # MCP tool implementations
│   │   ├── index.ts          # Tool exports
│   │   ├── search-products.ts # Product search tool
│   │   └── cart-management.ts # Cart management tools
│   └── utils/
│       └── debug.ts          # Debug logging utility
├── tests/                    # Comprehensive test suite
├── dist/                     # Compiled JavaScript output
├── .env.example              # Environment template
└── .env                      # Your configuration (not in git)
```

## Output Format

All tools return structured data optimized for LLM consumption:

**Search Results** (formatted as human-readable text):
```
Found 5 products for "milk":

### 1. Organic Milk 3.5%
**Brand:** Brand Name
**Category:** Dairy Products
**Price:** 1.99 €
**Amount:** 1 l
**Product ID:** 29432

---
```

**Cart Content** (JSON format):
```json
{
  "success": true,
  "cart": {
    "total_items": 3,
    "total_price": 12.50,
    "currency": "EUR",
    "products": [
      {
        "cart_item_id": "182654691",
        "id": 29432,
        "name": "Organic Milk 3.5%",
        "brand": "Brand Name",
        "quantity": 2,
        "price": "3.98 €",
        "category_name": "Dairy Products"
      }
    ]
  }
}
```

## Known Limitations

- **Single user per instance**: The server uses a singleton session pattern with one session file (`~/.rohlik-session`). For multiple concurrent users, you need to run separate MCP server instances.
- **Sorting with filters**: The upstream Rohlik API may not work perfectly when sorting is combined with organic filtering.
- **Checkout**: Order placement must be completed in the browser using the `handover_cart` tool to get the session cookie
- **Delivery address**: Not configurable via MCP; uses the address saved in your browser session
- **Authentication**: Uses anonymous sessions by default; no login credentials required

## Troubleshooting

### Wrong region/currency
1. Check `ROHLIK_BASE_URL` in `.env`
2. Clear session: `rm ~/.rohlik-session`
3. Restart the server

### No products found
- Verify `ROHLIK_BASE_URL` matches your region
- Try different search terms
- Check if the service is available in your area

### Tests failing
```bash
npm install
npm run build
npm test
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgements

- [dvejsada/HA-RohlikCZ](https://github.com/dvejsada/HA-RohlikCZ) - API reverse engineering
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- Original implementation by Tomas Pavlin

## Version

Current version: 2.0.0-no-auth (Modified fork with optional authentication)
