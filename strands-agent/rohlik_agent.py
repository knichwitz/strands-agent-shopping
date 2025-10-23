#!/usr/bin/env python3
"""
Rohlik Shopping Agent - Simplified Production Version
Autonomous grocery shopping with budget optimization and metrics tracking
"""

import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from strands import Agent
from strands.models.openai import OpenAIModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RohlikShoppingAgent:
    """Simplified Rohlik Shopping Agent with essential functionality"""
    
    def __init__(self):
        self.model = None
        self.export_dir = Path("shopping_exports")
        self.export_dir.mkdir(exist_ok=True)
        
    def _build_system_prompt(self) -> str:
        """Build system prompt for sequential product processing with budget optimization"""
        return """# Rohlik Shopping Agent

You are a grocery shopping assistant for Rohlik/Knuspr. Execute tasks autonomously without asking for confirmation.

## Tools Available:
- **search_products**: Find products (use `limit: 7`, `sort_by: "unit_price_asc"` for budget optimization)
- **add_to_cart**: Add products to cart
- **get_cart_content**: Show cart contents (PRESERVE JSON FORMAT)
- **remove_from_cart**: Remove items from cart
- **handover_cart**: Get session cookie

## CRITICAL WORKFLOW - Process ONE item at a time:

1. **Parse the shopping list** - identify each individual item requested
2. **For EACH item individually:**
   a. Search for the item using `search_products` with `limit: 7` and `sort_by: "unit_price_asc"`
   b. **Check categories** - prefer products that match the requested item type
   c. Select the cheapest option that matches the correct category
   d. **IMMEDIATELY add that single item to cart** with `add_to_cart`
   e. **Move to the next item** - repeat the process
3. After processing ALL items, show final cart with `get_cart_content`

## IMPORTANT RULES:
- **NEVER batch multiple items** - always add items one by one
- **NEVER collect all items first** - search → add → next item
- **Check categories** to ensure correct product type
- **Start with `limit: 7`, If no perfect match, increase to `limit: 15`** and search again
- **Prioritize budget-friendly options** in correct categories

## Reporting:
Always include this summary at the end:
**TOOL_CALLS_SUMMARY:**
- Tool: search_products | Query: [term] | Results: [count] | Selected: [product] | Price: [price] | Categories: [categories]
- Tool: add_to_cart | Products: [items] | Quantity: [quantity] | Total: [cost]
- Tool: get_cart_content | Result: [summary]

Execute immediately. Complete the full workflow. Report results after completion.
"""
        
    async def initialize(self):
        """Initialize the shopping agent with LM Studio model"""
        try:
            # Clear session cookie for fresh start
            import os
            cookie_path = os.path.expanduser("~/.rohlik-session")
            if os.path.exists(cookie_path):
                os.remove(cookie_path)
                logger.info("🗑️ Cleared existing session cookie")
            
            # Configure LM Studio model
            self.model = OpenAIModel(
                model_id="qwen/qwen3-4b-2507",
                client_args={
                    "base_url": "http://localhost:1234/v1",
                    "api_key": "lm-studio"
                },
                params={
                    "temperature": 0,
                    "max_tokens": 4096
                }
            )
            logger.info("✅ LM Studio model configured: qwen/qwen3-4b-2507")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            raise
    
    async def run_task(self, task: str):
        """Run a shopping task with metrics collection and export"""
        try:
            logger.info(f"🎯 Processing task: {task}")
            
            # Create Rohlik MCP client
            rohlik_client = MCPClient(
                lambda: stdio_client(StdioServerParameters(
                    command="node",
                    args=["../rohlik-mcp/dist/index.js"],
                    stderr=subprocess.DEVNULL
                ))
            )
            
            # Run within MCP client context
            with rohlik_client:
                # Create agent with Rohlik tools
                agent = Agent(
                    model=self.model,
                    tools=rohlik_client.list_tools_sync(),
                    system_prompt=self._build_system_prompt()
                )
                logger.info(f"✅ Agent created with {len(rohlik_client.list_tools_sync())} tools")
                
                # Execute task and measure time
                start_time = datetime.now()
                result = await agent.invoke_async(task)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                logger.info("✅ Task completed successfully")
                
                # Extract metrics
                metrics = self._extract_metrics(result)
                
                # Get cart data by calling MCP server directly
                cart_data = await self._get_cart_direct()
                
                # Export data
                await self._export_data({
                    "task": task,
                    "timestamp": start_time.isoformat(),
                    "execution_time_seconds": execution_time,
                    "cart_data": cart_data,
                    "metrics": metrics,
                    "agent_response": str(result)
                })
                
                return {
                    "success": True,
                    "response": str(result),
                    "cart_data": cart_data,
                    "metrics": metrics,
                    "error": None
                }
                
        except Exception as e:
            logger.error(f"❌ Task failed: {e}")
            return {
                "success": False,
                "response": None,
                "cart_data": None,
                "metrics": None,
                "error": str(e)
            }
    
    def _extract_metrics(self, result):
        """Extract metrics from agent result"""
        try:
            metrics = result.metrics
            
            metrics_data = {
                "accumulated_usage": {
                    "inputTokens": metrics.accumulated_usage.get("inputTokens", 0),
                    "outputTokens": metrics.accumulated_usage.get("outputTokens", 0),
                    "totalTokens": metrics.accumulated_usage.get("totalTokens", 0),
                    "cacheWriteInputTokens": metrics.accumulated_usage.get("cacheWriteInputTokens", 0),
                    "cacheReadInputTokens": metrics.accumulated_usage.get("cacheReadInputTokens", 0)
                },
                "cycle_count": metrics.cycle_count,
                "cycle_durations": metrics.cycle_durations,
                "total_duration": sum(metrics.cycle_durations),
                "average_cycle_time": sum(metrics.cycle_durations) / len(metrics.cycle_durations) if metrics.cycle_durations else 0,
                "tool_metrics": {}
            }
            
            # Extract tool metrics
            for tool_name, tool_metric in metrics.tool_metrics.items():
                metrics_data["tool_metrics"][tool_name] = {
                    "call_count": tool_metric.call_count,
                    "success_count": tool_metric.success_count,
                    "error_count": tool_metric.error_count,
                    "success_rate": tool_metric.success_count / tool_metric.call_count if tool_metric.call_count > 0 else 0,
                    "total_time": tool_metric.total_time,
                    "average_time": tool_metric.total_time / tool_metric.call_count if tool_metric.call_count > 0 else 0
                }
            
            return metrics_data
            
        except Exception as e:
            logger.error(f"Failed to extract metrics: {e}")
            return {"error": str(e)}
    
    async def _get_cart_direct(self):
        """Call MCP server directly to get cart - simple and reliable"""
        try:
            # Call the MCP server's get_cart_content endpoint directly
            process = await asyncio.create_subprocess_exec(
                "node",
                "../rohlik-mcp/dist/index.js",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL
            )
            
            # Send MCP request for get_cart_content
            request = json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "get_cart_content",
                    "arguments": {}
                }
            }) + "\n"
            
            stdout, _ = await process.communicate(request.encode())
            response = json.loads(stdout.decode())
            
            # Extract cart data from MCP response
            if 'result' in response and 'content' in response['result']:
                cart_json_str = response['result']['content'][0]['text']
                cart_json = json.loads(cart_json_str)
                
                if 'cart' in cart_json:
                    cart_info = cart_json['cart']
                    
                    cart_data = {
                        "items": [],
                        "total_items": cart_info.get('total_items', 0),
                        "total_price": cart_info.get('total_price', 0),
                        "currency": cart_info.get('currency', 'EUR')
                    }
                    
                    for product in cart_info.get('products', []):
                        price_value = product.get('price', 0)
                        if isinstance(price_value, str):
                            price_value = float(price_value.replace('€', '').replace(',', '.').strip())
                        
                        cart_data["items"].append({
                            "name": product.get('name', ''),
                            "quantity": product.get('quantity', 1),
                            "price": price_value,
                            "currency": "EUR",
                            "product_id": product.get('cart_item_id', None)
                        })
                    
                    logger.info(f"✅ Retrieved cart: {cart_data['total_items']} items, €{cart_data['total_price']}")
                    return cart_data
            
            return {
                "items": [],
                "total_items": 0,
                "total_price": 0,
                "currency": "EUR"
            }
            
        except Exception as e:
            logger.error(f"Failed to get cart directly: {e}")
            return {"error": str(e)}
    
    async def _export_data(self, export_data):
        """Export shopping data to JSON file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.export_dir / f"shopping_run_{timestamp}.json"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Data exported to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return None


async def main():
    """Main function for standalone execution"""
    if len(sys.argv) < 2:
        print("Usage: python rohlik_agent.py \"Your shopping task\"")
        print("Example: python rohlik_agent.py \"Find me Milk, Chicken Breast, Eggs, Apples, and Bread\"")
        print("")
        print("Features:")
        print("- Sequential item processing")
        print("- Budget optimization (cheapest options)")
        print("- Metrics collection and export")
        print("- Cart data export to JSON")
        print("- Fully autonomous operation")
        sys.exit(1)
    
    task = sys.argv[1]
    
    print("🛒 Starting Rohlik Shopping Agent...")
    print("📡 MCP Integration: Rohlik/Knuspr (Germany, Czech, Austria, Hungary, Romania)")
    print("🤖 Model: qwen/qwen3-4b-2507")
    print("💰 Budget Optimization: Enabled")
    print("📊 Metrics Collection: Enabled")
    print("💾 Data Export: Enabled")
    print(f"🎯 Task: {task}")
    print("")
    
    # Create and initialize agent
    agent = RohlikShoppingAgent()
    await agent.initialize()
    
    print("✅ Rohlik Shopping Agent ready!")
    print("")
    
    # Run the task
    print(f"🔄 Processing: {task}")
    print("-" * 50)
    
    result = await agent.run_task(task)
    
    if result["success"]:
        print(f"\n✅ Response:")
        print(result["response"])
        
        print(f"\n🛒 Cart Content:")
        print(result["cart_data"])
        
        print(f"\n📊 Metrics Summary:")
        metrics = result["metrics"]
        print(f"  Total Tokens: {metrics['accumulated_usage']['totalTokens']}")
        print(f"  Execution Time: {metrics['total_duration']:.2f} seconds")
        print(f"  Cycles: {metrics['cycle_count']}")
        print(f"  Average Cycle Time: {metrics['average_cycle_time']:.2f} seconds")
        print(f"  Tools Used: {list(metrics['tool_metrics'].keys())}")
        
        for tool_name, tool_metric in metrics['tool_metrics'].items():
            print(f"    {tool_name}: {tool_metric['call_count']} calls, {tool_metric['success_rate']:.1%} success rate")
        
        print(f"\n💾 Data exported to shopping_exports/ folder")
        
    else:
        print(f"\n❌ Error: {result['error']}")
    
    print("-" * 50)
    print("")


if __name__ == "__main__":
    asyncio.run(main())
