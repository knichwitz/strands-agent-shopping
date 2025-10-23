#!/usr/bin/env python3
"""
Rohlik Shopping Agent with Parallel Processing, Metrics, and Data Export
"""

import asyncio
import json
import logging
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from strands import Agent
from strands.models.openai import OpenAIModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

# Configure logging with file output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rohlik_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RohlikShoppingAgent:
    """Rohlik Shopping Agent with parallel processing and metrics"""
    
    def __init__(self):
        self.session_state = {}
        self.model = None
        self.system_prompt = self._build_system_prompt()
        self.export_dir = Path("shopping_exports")
        self.export_dir.mkdir(exist_ok=True)
        
    def _build_system_prompt(self) -> str:
        """Build system prompt for individual product processing with budget optimization"""
        
        return """# Rohlik Shopping Agent

You are a grocery shopping assistant for Rohlik/Knuspr. Execute tasks autonomously without asking for confirmation.

## Tools Available:
- **search_products**: Find products (use `limit: 7`, `sort_by: "unit_price_asc"` for budget optimization)
- **add_to_cart**: Add products to cart
- **get_cart_content**: Show cart contents (PRESERVE JSON FORMAT - do not convert to text)
- **remove_from_cart**: Remove items from cart
- **handover_cart**: Get session cookie

## CRITICAL WORKFLOW - Process ONE item at a time:

1. **Parse the shopping list** - identify each individual item requested
2. **For EACH item individually:**
   a. Search for the item using `search_products` with `limit: 7` and `sort_by: "unit_price_asc"`
   b. **Check categories** - prefer products that match the requested item type
   c. Select the cheapest option that matches the correct category (or best available if no perfect match)
   d. **IMMEDIATELY add that single item to cart** with `add_to_cart`
   e. **Move to the next item** - repeat the process
3. After processing ALL items, show final cart with `get_cart_content` (PRESERVE the raw JSON output - do not convert to human-readable text)

## IMPORTANT RULES:
- **NEVER batch multiple items** - always add items one by one
- **NEVER collect all items first** - search → add → next item
- **Check categories** to ensure correct product type
- **If no perfect match, increase limit to 20** and search again for the same item
- **Prioritize budget-friendly options** in correct categories
- **Process each item completely** before moving to the next

## Product Selection:
- **Check the `categories` field** to ensure correct product type
- **If no perfect match, increase the limit to 20 and search again for the same item and select the best available option**
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
        """Initialize the Rohlik shopping agent"""
        try:
            logger.info("🚀 Starting Rohlik Shopping Agent initialization...")
            
            # Clear session cookie to start fresh
            import os
            cookie_path = os.path.expanduser("~/.rohlik-session")
            if os.path.exists(cookie_path):
                os.remove(cookie_path)
                logger.info("🗑️ Cleared existing session cookie for fresh start")
            
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
            logger.info("✅ Rohlik Shopping Agent ready!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Rohlik Shopping Agent: {e}")
            raise
    
    async def run_task(self, task: str):
        """Run a shopping task with metrics collection and export"""
        try:
            logger.info(f"🎯 Processing task: {task}")
            
            # Update session state
            self.session_state.update({
                "current_task": task,
                "timestamp": datetime.now().isoformat(),
                "task_count": self.session_state.get("task_count", 0) + 1
            })
            
            # Create Rohlik MCP client
            rohlik_client = MCPClient(
                lambda: stdio_client(StdioServerParameters(
                    command="node",
                    args=["../rohlik-mcp/dist/index.js"],
                    stderr=subprocess.DEVNULL
                ))
            )
            
            logger.info("✅ Rohlik MCP client created")
            
            # Run everything within the Rohlik MCP client context
            with rohlik_client:
                # Get tools from Rohlik MCP server
                rohlik_tools = rohlik_client.list_tools_sync()
                logger.info(f"✅ Loaded {len(rohlik_tools)} tools from Rohlik MCP server")
                
                # Create Strands Agent with Rohlik tools
                agent = Agent(
                    model=self.model, 
                    tools=rohlik_tools,
                    system_prompt=self.system_prompt
                )
                logger.info(f"✅ Agent created with {len(rohlik_tools)} Rohlik tools")
                
                # Run the agent and collect metrics
                start_time = datetime.now()
                result = await agent.invoke_async(task)
                end_time = datetime.now()
                
                logger.info(f"✅ Task completed successfully")
                
                # Collect metrics, tool calls, and cart data (within the context)
                metrics_data = self._extract_metrics(result)
                tool_calls_data = self._extract_tool_calls(result)
                
                # Try to extract structured cart data from tool calls first
                logger.info("🔍 DEBUG: Attempting structured cart extraction from tool calls")
                cart_data = self._extract_cart_from_tool_calls(tool_calls_data)
                
                # If that failed, try agent response as fallback
                if not cart_data or (isinstance(cart_data, dict) and not cart_data.get('items')):
                    logger.warning("🔍 DEBUG: Tool calls extraction failed, trying agent response")
                    agent_response = str(result)
                    structured_cart = self._extract_cart_from_agent_response(agent_response)
                    if structured_cart:
                        logger.info("🔍 DEBUG: Agent response extraction successful")
                        cart_data = structured_cart
                    else:
                        logger.warning("🔍 DEBUG: All cart extraction methods failed")
                
                # Export data
                export_data = {
                    "task": task,
                    "timestamp": start_time.isoformat(),
                    "execution_time_seconds": (end_time - start_time).total_seconds(),
                    "cart_data": cart_data,
                    "metrics": metrics_data,
                    "tool_calls": tool_calls_data,
                    "agent_response": str(result)
                }
                
                await self._export_data(export_data)
                
                # Update session state
                self.session_state["last_response"] = str(result)
                self.session_state["last_task"] = task
                self.session_state["last_metrics"] = metrics_data
                self.session_state["last_cart"] = cart_data
                
                return {
                    "success": True,
                    "response": str(result),
                    "cart_data": cart_data,
                    "metrics": metrics_data,
                    "tool_calls": tool_calls_data,
                    "session_state": self.session_state,
                    "error": None,
                    "message": None
                }
            
        except Exception as e:
            logger.error(f"❌ Task failed: {e}")
            return {
                "success": False,
                "response": None,
                "cart_data": None,
                "metrics": None,
                "session_state": self.session_state,
                "error": str(e),
                "message": "Task execution failed"
            }
    
    def _extract_metrics(self, result):
        """Extract metrics from agent result following Strands documentation"""
        try:
            metrics = result.metrics
            
            # Extract key metrics as per documentation
            metrics_data = {
                "accumulated_usage": {
                    "inputTokens": metrics.accumulated_usage.get("inputTokens", 0),
                    "outputTokens": metrics.accumulated_usage.get("outputTokens", 0),
                    "totalTokens": metrics.accumulated_usage.get("totalTokens", 0),
                    # Cache-related tokens (if available)
                    "cacheWriteInputTokens": metrics.accumulated_usage.get("cacheWriteInputTokens", 0),
                    "cacheReadInputTokens": metrics.accumulated_usage.get("cacheReadInputTokens", 0)
                },
                "accumulated_metrics": {
                    "latencyMs": metrics.accumulated_metrics.get("latencyMs", 0)
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
            logger.error(f"❌ Failed to extract metrics: {e}")
            return {"error": str(e)}
    
    def _extract_actual_tool_calls(self, result):
        """Extract actual tool calls from Strands framework"""
        try:
            tool_calls = []
            
            # Check if result has cycles (Strands framework structure)
            if hasattr(result, 'cycles') and result.cycles:
                logger.info(f"🔍 Found {len(result.cycles)} cycles")
                for cycle in result.cycles:
                    if hasattr(cycle, 'tool_calls') and cycle.tool_calls:
                        for call in cycle.tool_calls:
                            tool_call_info = {
                                "tool_name": getattr(call, 'name', 'unknown'),
                                "arguments": getattr(call, 'arguments', {}),
                                "result": getattr(call, 'result', None),
                                "status": "success" if getattr(call, 'result', None) is not None else "unknown"
                            }
                            tool_calls.append(tool_call_info)
                            logger.info(f"🔍 Extracted tool call: {tool_call_info['tool_name']}")
            
            # Check if result has tool_calls directly
            elif hasattr(result, 'tool_calls') and result.tool_calls:
                logger.info(f"🔍 Found {len(result.tool_calls)} direct tool calls")
                for call in result.tool_calls:
                    tool_call_info = {
                        "tool_name": getattr(call, 'name', 'unknown'),
                        "arguments": getattr(call, 'arguments', {}),
                        "result": getattr(call, 'result', None),
                        "status": "success" if getattr(call, 'result', None) is not None else "unknown"
                    }
                    tool_calls.append(tool_call_info)
                    logger.info(f"🔍 Extracted direct tool call: {tool_call_info['tool_name']}")
            
            # Check state for tool calls
            elif hasattr(result, 'state') and result.state:
                logger.info(f"🔍 Checking state for tool calls")
                if hasattr(result.state, 'tool_calls') and result.state.tool_calls:
                    for call in result.state.tool_calls:
                        tool_call_info = {
                            "tool_name": getattr(call, 'name', 'unknown'),
                            "arguments": getattr(call, 'arguments', {}),
                            "result": getattr(call, 'result', None),
                            "status": "success" if getattr(call, 'result', None) is not None else "unknown"
                        }
                        tool_calls.append(tool_call_info)
                        logger.info(f"🔍 Extracted state tool call: {tool_call_info['tool_name']}")
            
            if tool_calls:
                logger.info(f"✅ Successfully extracted {len(tool_calls)} actual tool calls")
                return tool_calls
            else:
                logger.info("❌ No actual tool calls found in Strands framework")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to extract actual tool calls: {e}")
            return []
    
    def _extract_tool_calls(self, result):
        """Extract detailed tool call information from agent result"""
        try:
            tool_calls = []
            
            # Try to extract actual tool calls from Strands framework first
            actual_tool_calls = self._extract_actual_tool_calls(result)
            if actual_tool_calls:
                return actual_tool_calls
            
            # Fallback: parse from the agent's response text
            response_text = str(result)
            tool_calls_from_response = self._parse_tool_calls_from_response(response_text)
            if tool_calls_from_response:
                return tool_calls_from_response
            
            # Debug: Print all available attributes
            logger.info(f"🔍 Result object attributes: {dir(result)}")
            
            # Check the state attribute for tool calls
            if hasattr(result, 'state') and result.state:
                logger.info(f"🔍 State attributes: {dir(result.state)}")
                logger.info(f"🔍 State content: {result.state}")
                
                # Check if state has tool_calls or similar
                if hasattr(result.state, 'tool_calls') and result.state.tool_calls:
                    logger.info(f"🔍 Found tool_calls in state: {result.state.tool_calls}")
                    for call in result.state.tool_calls:
                        tool_call_info = {
                            "tool_name": getattr(call, 'name', 'unknown'),
                            "arguments": getattr(call, 'arguments', {}),
                            "result": getattr(call, 'result', None),
                            "status": getattr(call, 'status', 'unknown')
                        }
                        tool_calls.append(tool_call_info)
                
                # Check for other possible attributes in state
                for attr in ['messages', 'steps', 'actions', 'tool_results', 'history']:
                    if hasattr(result.state, attr):
                        logger.info(f"🔍 Found {attr} in state: {getattr(result.state, attr)}")
            
            # Check if result has tool_calls attribute
            if hasattr(result, 'tool_calls') and result.tool_calls:
                logger.info(f"🔍 Found tool_calls: {result.tool_calls}")
                for call in result.tool_calls:
                    tool_call_info = {
                        "tool_name": getattr(call, 'name', 'unknown'),
                        "arguments": getattr(call, 'arguments', {}),
                        "result": getattr(call, 'result', None),
                        "status": getattr(call, 'status', 'unknown')
                    }
                    tool_calls.append(tool_call_info)
            
            # Also check for cycles if available
            if hasattr(result, 'cycles') and result.cycles:
                logger.info(f"🔍 Found cycles: {result.cycles}")
                for cycle in result.cycles:
                    if hasattr(cycle, 'tool_calls') and cycle.tool_calls:
                        for call in cycle.tool_calls:
                            tool_call_info = {
                                "tool_name": getattr(call, 'name', 'unknown'),
                                "arguments": getattr(call, 'arguments', {}),
                                "result": getattr(call, 'result', None),
                                "status": getattr(call, 'status', 'unknown'),
                                "cycle_id": getattr(cycle, 'id', 'unknown')
                            }
                            tool_calls.append(tool_call_info)
            
            # Check for other possible attributes
            for attr in ['messages', 'steps', 'actions', 'tool_results']:
                if hasattr(result, attr):
                    logger.info(f"🔍 Found {attr}: {getattr(result, attr)}")
            
            return tool_calls
            
        except Exception as e:
            logger.error(f"❌ Failed to extract tool calls: {e}")
            return []
    
    def _parse_tool_calls_from_response(self, response_text):
        """Parse tool calls from the agent's response text"""
        try:
            tool_calls = []
            
            # Look for TOOL_CALLS_SUMMARY section
            if "TOOL_CALLS_SUMMARY:" in response_text:
                lines = response_text.split('\n')
                in_summary = False
                current_tool_call = None
                cart_content_lines = []
                in_cart_content = False
                
                for i, line in enumerate(lines):
                    if "TOOL_CALLS_SUMMARY:" in line:
                        in_summary = True
                        continue
                    
                    if in_summary and line.strip().startswith('- Tool:'):
                        # Save previous tool call if exists
                        if current_tool_call:
                            tool_calls.append(current_tool_call)
                        
                        # Parse line like: "- Tool: search_products | Query: milk | Results: 8 products found | Selected: Fresh Milk 1L | Price: 0.99€"
                        parts = line.strip()[2:].split(' | ')  # Remove "- " and split by " | "
                        
                        current_tool_call = {
                            "tool_name": "unknown",
                            "arguments": {},
                            "result": {},
                            "status": "success"
                        }
                        
                        for part in parts:
                            if part.startswith('Tool: '):
                                current_tool_call["tool_name"] = part[6:]
                            elif part.startswith('Query: '):
                                current_tool_call["arguments"]["product_name"] = part[7:]
                            elif part.startswith('Results: '):
                                current_tool_call["result"]["results_count"] = part[9:]
                            elif part.startswith('Selected: '):
                                current_tool_call["result"]["selected_product"] = part[10:]
                            elif part.startswith('Price: '):
                                current_tool_call["result"]["price"] = part[7:]
                            elif part.startswith('Categories: '):
                                current_tool_call["result"]["categories"] = part[12:]
                            elif part.startswith('Products: '):
                                current_tool_call["arguments"]["products"] = part[10:]
                            elif part.startswith('Quantity: '):
                                current_tool_call["arguments"]["quantity"] = part[10:]
                            elif part.startswith('Total Cost: '):
                                current_tool_call["result"]["total_cost"] = part[12:]
                            elif part.startswith('Total: '):
                                current_tool_call["result"]["total_cost"] = part[7:]
                            elif part.startswith('Result: '):
                                # Check if this is cart content (multi-line)
                                if current_tool_call["tool_name"] == "get_cart_content":
                                    in_cart_content = True
                                    result_content = part[8:].strip()
                                    if result_content:
                                        cart_content_lines = [result_content]
                                    else:
                                        cart_content_lines = []  # Empty, will be filled by next lines
                                else:
                                    current_tool_call["result"]["cart_summary"] = part[8:]
                    
                    elif in_summary and in_cart_content and current_tool_call:
                        # Collect multi-line cart content
                        if line.strip().startswith('  - Product:') or line.strip().startswith('  - Total:'):
                            cart_content_lines.append(line.strip())
                        elif line.strip() == '' or line.strip().startswith('- Tool:'):
                            # End of cart content
                            if cart_content_lines:
                                current_tool_call["result"]["cart_summary"] = '\n'.join(cart_content_lines)
                            in_cart_content = False
                            cart_content_lines = []
                    
                    elif in_summary and line.strip() == '':
                        # Empty line might end the summary
                        if current_tool_call:
                            tool_calls.append(current_tool_call)
                        break
                
                # Add the last tool call if exists
                if current_tool_call:
                    tool_calls.append(current_tool_call)
            
            return tool_calls
            
        except Exception as e:
            logger.error(f"❌ Failed to parse tool calls from response: {e}")
            return []
    
    async def _get_cart_data_within_context(self, rohlik_client):
        """Get current cart data within the existing MCP client context"""
        try:
            # Instead of calling the tool directly, let's try to access the tool from the client
            logger.info("🔍 Attempting to get cart content...")
            
            # List available tools to see what's available
            tools = await rohlik_client.list_tools_async()
            logger.info(f"🔍 Available tools: {[tool.name for tool in tools]}")
            
            # Find the get_cart_content tool
            cart_tool = None
            for tool in tools:
                if tool.name == "get_cart_content":
                    cart_tool = tool
                    break
            
            if cart_tool:
                logger.info(f"🔍 Found cart tool: {cart_tool}")
                # Try to call the tool using its invoke method
                cart_result = await cart_tool.invoke({})
                logger.info(f"🔍 Cart result: {cart_result}")
                
                if hasattr(cart_result, 'content') and cart_result.content:
                    if isinstance(cart_result.content[0], dict):
                        return cart_result.content[0].get("text", str(cart_result.content[0]))
                    else:
                        return str(cart_result.content[0])
                else:
                    return "Cart is empty"
            else:
                logger.error("❌ get_cart_content tool not found")
                return "Cart tool not found"
                
        except Exception as e:
            logger.error(f"❌ Failed to get cart data: {e}")
            return {"error": str(e)}
    
    def _extract_cart_from_tool_calls(self, tool_calls_data):
        """Extract cart information from tool calls data"""
        try:
            cart_items = []
            total_cost = None
            cart_content_result = None
            cart_data = None  # Initialize cart_data variable
            
            for call in tool_calls_data:
                if call['tool_name'] == 'add_to_cart':
                    # Extract cart information from add_to_cart tool call
                    if 'result' in call and 'total_cost' in call['result']:
                        total_cost = call['result']['total_cost']
                    
                    if 'arguments' in call and 'products' in call['arguments']:
                        products = call['arguments']['products']
                        cart_items.append(f"Products added: {products}")
                    
                    if 'arguments' in call and 'quantity' in call['arguments']:
                        quantity = call['arguments']['quantity']
                        cart_items.append(f"Quantity: {quantity}")
                
                elif call['tool_name'] == 'get_cart_content':
                    # Extract cart content from get_cart_content tool call
                    logger.info(f"🔍 DEBUG: Found get_cart_content tool call: {call}")
                    
                    if 'result' in call and call['result']:
                        result_data = call['result']
                        logger.info(f"🔍 DEBUG: get_cart_content result: {result_data}")
                        
                        # Check if the JSON is in cart_summary field
                        if isinstance(result_data, dict) and 'cart_summary' in result_data:
                            json_string = result_data['cart_summary']
                            logger.info(f"🔍 DEBUG: Found JSON in cart_summary: {json_string}")
                            
                            try:
                                import json
                                parsed_result = json.loads(json_string)
                                logger.info(f"🔍 DEBUG: Successfully parsed JSON: {parsed_result}")
                                
                                # Extract cart data from the parsed JSON
                                if isinstance(parsed_result, dict):
                                    # Handle both formats: direct cart data or wrapped in success/cart
                                    if 'cart' in parsed_result:
                                        cart_info = parsed_result['cart']
                                    else:
                                        cart_info = parsed_result  # Direct cart data
                                    
                                    logger.info(f"🔍 DEBUG: Found cart info: {cart_info}")
                                    
                                    # Convert to our standard format
                                    cart_data = {
                                        "items": [],
                                        "total_items": cart_info.get('total_items', len(cart_info.get('items', []))),
                                        "total_price": float(cart_info.get('total_price', cart_info.get('total', '0'))) if isinstance(cart_info.get('total_price', cart_info.get('total', '0')), (int, float)) else float(str(cart_info.get('total_price', cart_info.get('total', '0'))).replace('€', '').replace(',', '.').strip()),
                                        "currency": cart_info.get('currency', 'EUR')
                                    }
                                    
                                    # Add products - handle both 'products' and 'items' fields
                                    products = cart_info.get('products', cart_info.get('items', []))
                                    for product in products:
                                        cart_data["items"].append({
                                            "name": product.get('name', ''),
                                            "quantity": product.get('quantity', 1),
                                            "price": float(product.get('price', '0')) if isinstance(product.get('price'), (int, float)) else float(str(product.get('price', '0')).replace('€', '').replace(',', '.').strip()),
                                            "currency": cart_info.get('currency', 'EUR'),
                                            "product_id": product.get('product_id', product.get('cart_item_id', None))
                                        })
                                    
                                    logger.info(f"🔍 DEBUG: Converted to standard format: {cart_data}")
                                    return cart_data
                                    
                            except json.JSONDecodeError as e:
                                logger.warning(f"🔍 DEBUG: Failed to parse JSON from cart_summary: {e}")
                                cart_content_result = str(result_data)
                        
                        # Try to parse JSON from the result
                        elif isinstance(result_data, str):
                            try:
                                import json
                                parsed_result = json.loads(result_data)
                                logger.info(f"🔍 DEBUG: Successfully parsed JSON: {parsed_result}")
                                
                                # Extract cart data from the parsed JSON
                                if isinstance(parsed_result, dict):
                                    # Handle both formats: direct cart data or wrapped in success/cart
                                    if 'cart' in parsed_result:
                                        cart_info = parsed_result['cart']
                                    else:
                                        cart_info = parsed_result  # Direct cart data
                                    
                                    logger.info(f"🔍 DEBUG: Found cart info: {cart_info}")
                                    
                                    # Convert to our standard format
                                    cart_data = {
                                        "items": [],
                                        "total_items": cart_info.get('total_items', len(cart_info.get('items', []))),
                                        "total_price": float(cart_info.get('total_price', cart_info.get('total', '0'))) if isinstance(cart_info.get('total_price', cart_info.get('total', '0')), (int, float)) else float(str(cart_info.get('total_price', cart_info.get('total', '0'))).replace('€', '').replace(',', '.').strip()),
                                        "currency": cart_info.get('currency', 'EUR')
                                    }
                                    
                                    # Add products - handle both 'products' and 'items' fields
                                    products = cart_info.get('products', cart_info.get('items', []))
                                    for product in products:
                                        cart_data["items"].append({
                                            "name": product.get('name', ''),
                                            "quantity": product.get('quantity', 1),
                                            "price": float(product.get('price', '0')) if isinstance(product.get('price'), (int, float)) else float(str(product.get('price', '0')).replace('€', '').replace(',', '.').strip()),
                                            "currency": cart_info.get('currency', 'EUR'),
                                            "product_id": product.get('product_id', product.get('cart_item_id', None))
                                        })
                                    
                                    logger.info(f"🔍 DEBUG: Converted to standard format: {cart_data}")
                                    return cart_data
                                    
                            except json.JSONDecodeError as e:
                                logger.warning(f"🔍 DEBUG: Failed to parse JSON: {e}")
                                cart_content_result = str(result_data)
                        elif isinstance(result_data, dict):
                            cart_content_result = str(result_data)
                        else:
                            cart_content_result = str(result_data)
                    else:
                        cart_content_result = "Cart content retrieved but not parsed"
            
            # If we successfully parsed structured cart data, return it
            if cart_data and isinstance(cart_data, dict) and cart_data.get('items'):
                logger.info(f"🔍 DEBUG: Returning structured cart data from tool calls: {cart_data}")
                return cart_data
            
            # Prefer cart content result if available (fallback)
            if cart_content_result and cart_content_result != "Cart content retrieved but not parsed":
                return cart_content_result
            
            # Fallback to add_to_cart information
            if cart_items:
                cart_summary = "Cart Summary:\n" + "\n".join(cart_items)
                if total_cost:
                    cart_summary += f"\nTotal Cost: {total_cost}"
                return cart_summary
            else:
                return "No cart items found in tool calls"
                
        except Exception as e:
            logger.error(f"❌ Failed to extract cart from tool calls: {e}")
            return {"error": str(e)}
    
    def _extract_cart_from_agent_response(self, agent_response):
        """Extract structured cart data from agent response text"""
        try:
            import re
            
            # Debug logging
            logger.info("🔍 DEBUG: Starting cart extraction from agent response")
            logger.info(f"🔍 DEBUG: Agent response length: {len(agent_response)}")
            
            # Look for get_cart_content result in the agent response
            cart_pattern = r'- Tool: get_cart_content \| Result: (.*?)(?=\n- Tool:|$)'
            cart_match = re.search(cart_pattern, agent_response, re.DOTALL)
            
            if not cart_match:
                logger.warning("🔍 DEBUG: No get_cart_content pattern found in agent response")
                # Let's try to find any cart-related content
                if 'cart' in agent_response.lower():
                    logger.info("🔍 DEBUG: Found 'cart' in response, but pattern didn't match")
                    # Log a snippet around cart mentions
                    lines = agent_response.split('\n')
                    for i, line in enumerate(lines):
                        if 'cart' in line.lower():
                            logger.info(f"🔍 DEBUG: Cart-related line {i}: {line}")
                            # Show context
                            for j in range(max(0, i-2), min(len(lines), i+3)):
                                logger.info(f"🔍 DEBUG: Context line {j}: {lines[j]}")
                return None
            
            cart_text = cart_match.group(1).strip()
            logger.info(f"🔍 DEBUG: Found cart text: '{cart_text}'")
            logger.info(f"🔍 DEBUG: Cart text length: {len(cart_text)}")
            
            # Parse cart content into structured JSON
            cart_data = {
                "items": [],
                "total_items": 0,
                "total_price": 0,
                "currency": "EUR"
            }
            
            # Handle different cart formats
            lines = cart_text.split('\n')
            logger.info(f"🔍 DEBUG: Cart text split into {len(lines)} lines")
            for i, line in enumerate(lines):
                logger.info(f"🔍 DEBUG: Line {i}: '{line}'")
            
            # Format 0: JSON format (most accurate)
            if cart_text.strip().startswith('[') and cart_text.strip().endswith(']'):
                logger.info("🔍 DEBUG: Detected Format 0: JSON array format")
                try:
                    import json
                    cart_json = json.loads(cart_text)
                    logger.info(f"🔍 DEBUG: Successfully parsed JSON with {len(cart_json)} items")
                    
                    for item in cart_json:
                        # Extract price as float (remove currency symbol)
                        price_str = item.get('price', '0 €').replace(' €', '').replace('€', '')
                        price = float(price_str)
                        
                        cart_data["items"].append({
                            "name": item.get('name', ''),
                            "quantity": item.get('quantity', 1),
                            "price": price,
                            "currency": "EUR",
                            "product_id": item.get('product_id', None)
                        })
                        cart_data["total_items"] += item.get('quantity', 1)
                        cart_data["total_price"] += price
                    
                    logger.info(f"🔍 DEBUG: JSON parsing successful: {len(cart_data['items'])} items, total: {cart_data['total_price']}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"🔍 DEBUG: JSON parsing failed: {e}")
                    # Fall through to other formats
            
            # Format 1: "Total items: X | Total price: Y € | Items:" format
            if 'Total items:' in cart_text and 'Total price:' in cart_text and 'Items:' in cart_text:
                logger.info("🔍 DEBUG: Detected Format 1: 'Total items: X | Total price: Y € | Items:'")
                # Extract total price
                total_price_match = re.search(r'Total price: ([\d.]+) €', cart_text)
                if total_price_match:
                    cart_data["total_price"] = float(total_price_match.group(1))
                
                # Extract total items count
                total_items_match = re.search(r'Total items: (\d+)', cart_text)
                if total_items_match:
                    cart_data["total_items"] = int(total_items_match.group(1))
                
                # Parse individual items from the lines
                for line in lines:
                    line = line.strip()
                    # Parse product lines: "- Product Name (1x) | Price: X €"
                    if line.startswith('- ') and '(1x)' in line and '| Price:' in line:
                        product_match = re.search(r'- ([^(]+) \(1x\) \| Price: ([\d.]+) €', line)
                        if product_match:
                            name = product_match.group(1).strip()
                            price = float(product_match.group(2))
                            
                            cart_data["items"].append({
                                "name": name,
                                "quantity": 1,
                                "price": price,
                                "currency": "EUR"
                            })
            
            # Format 2: "X items total | Total price: Y € | Items: 1x Product (Price €), 1x Product (Price €)"
            elif 'items total' in cart_text and 'Total price:' in cart_text and 'Items:' in cart_text:
                logger.info("🔍 DEBUG: Detected Format 2: 'items total | Total price: | Items:' format")
                # Extract total price
                total_price_match = re.search(r'Total price: ([\d.]+) €', cart_text)
                if total_price_match:
                    cart_data["total_price"] = float(total_price_match.group(1))
                
                # Extract total items count
                total_items_match = re.search(r'(\d+) items total', cart_text)
                if total_items_match:
                    cart_data["total_items"] = int(total_items_match.group(1))
                
                # Extract items from the Items: section
                items_match = re.search(r'Items: (.*)', cart_text)
                if items_match:
                    items_text = items_match.group(1)
                    # Split by comma and parse each item
                    item_parts = items_text.split(', ')
                    for item_part in item_parts:
                        # Parse format: "1x Product Name (Price €)"
                        item_match = re.search(r'1x ([^(]+) \(([\d.]+) €\)', item_part.strip())
                        if item_match:
                            name = item_match.group(1).strip()
                            price = float(item_match.group(2))
                            
                            cart_data["items"].append({
                                "name": name,
                                "quantity": 1,
                                "price": price,
                                "currency": "EUR"
                            })
            
            # Format 3: Single line with items and total
            # "2 items total (Yutto Organic Oat milk: 0.89 €, Yutto Butter Toast: 0.79 €) | Total: 1.68 €"
            elif 'items total' in cart_text and 'Total:' in cart_text:
                logger.info("🔍 DEBUG: Detected Format 3: 'items total' format")
                # Extract total price
                total_match = re.search(r'Total: ([\d.]+) €', cart_text)
                if total_match:
                    cart_data["total_price"] = float(total_match.group(1))
                
                # Extract items from the format "Name: Price €"
                items_match = re.search(r'items total \((.*?)\)', cart_text)
                if items_match:
                    items_text = items_match.group(1)
                    # Split by comma and parse each item
                    item_parts = items_text.split(', ')
                    for item_part in item_parts:
                        item_match = re.search(r'([^:]+): ([\d.]+) €', item_part.strip())
                        if item_match:
                            name = item_match.group(1).strip()
                            price = float(item_match.group(2))
                            
                            cart_data["items"].append({
                                "name": name,
                                "quantity": 1,  # Default to 1 since not specified
                                "price": price,
                                "currency": "EUR"
                            })
                            cart_data["total_items"] += 1
            
            # Format 4: "X item(s) in cart: Product Name (1x, Price €)"
            elif 'item(s) in cart:' in cart_text:
                logger.info("🔍 DEBUG: Detected Format 4: 'item(s) in cart:' format")
                # Extract items from the format: "X item(s) in cart: Product Name (1x, Price €)"
                cart_match = re.search(r'(\d+) item\(s\) in cart: (.+)', cart_text)
                if cart_match:
                    total_items = int(cart_match.group(1))
                    items_text = cart_match.group(2)
                    
                    cart_data["total_items"] = total_items
                    
                    # Parse the items text
                    # Format: "Product Name (1x, Price €)" or "Product Name (1x, Price €), Product Name (1x, Price €)"
                    # Since there might be commas inside the parentheses, we need to be more careful
                    logger.info(f"🔍 DEBUG: Parsing items_text: '{items_text}'")
                    
                    # Try to parse the single item format first
                    item_match = re.search(r'([^(]+) \(1x, ([\d.]+) €\)', items_text.strip())
                    if item_match:
                        name = item_match.group(1).strip()
                        price = float(item_match.group(2))
                        logger.info(f"🔍 DEBUG: Parsed single item: name='{name}', price={price}")
                        
                        cart_data["items"].append({
                            "name": name,
                            "quantity": 1,
                            "price": price,
                            "currency": "EUR"
                        })
                        cart_data["total_price"] += price
                    else:
                        # Try to split by comma, but be more careful about parentheses
                        logger.info(f"🔍 DEBUG: Single item parsing failed, trying comma split")
                        # This is a more complex case - for now, let's handle the simple case
                        logger.warning(f"🔍 DEBUG: Complex multi-item format not yet supported")
            
            # Format 5: Multi-line format with individual product lines
            else:
                for line in lines:
                    line = line.strip()
                    
                    # Parse product lines with dashes: "- Product Name (Price €)"
                    if line.startswith('- ') and '(' in line and '€' in line:
                        product_match = re.search(r'- ([^(]+) \(([\d.]+) €\)', line)
                        if product_match:
                            name = product_match.group(1).strip()
                            price = float(product_match.group(2))
                            
                            cart_data["items"].append({
                                "name": name,
                                "quantity": 1,  # Default to 1 since not specified
                                "price": price,
                                "currency": "EUR"
                            })
                            cart_data["total_items"] += 1
                            cart_data["total_price"] += price
                    
                    # Parse product lines: "Product: Name | Quantity: X | Price: Y €"
                    elif 'Product:' in line and 'Quantity:' in line and 'Price:' in line:
                        product_match = re.search(r'Product: ([^|]+) \| Quantity: (\d+) \| Price: ([\d.]+) €', line)
                        if product_match:
                            name = product_match.group(1).strip()
                            quantity = int(product_match.group(2))
                            price = float(product_match.group(3))
                            
                            cart_data["items"].append({
                                "name": name,
                                "quantity": quantity,
                                "price": price,
                                "currency": "EUR"
                            })
                            cart_data["total_items"] += quantity
                            cart_data["total_price"] += price
                    
                    # Parse total line: "Total: X €"
                    elif line.startswith('Total:') and '€' in line:
                        total_match = re.search(r'Total: ([\d.]+) €', line)
                        if total_match:
                            cart_data["total_price"] = float(total_match.group(1))
            
            # If we found items, return structured data
            logger.info(f"🔍 DEBUG: Final cart_data: {cart_data}")
            logger.info(f"🔍 DEBUG: Found {len(cart_data['items'])} items")
            
            if cart_data["items"]:
                logger.info("🔍 DEBUG: Returning structured cart data")
                return cart_data
            else:
                logger.warning("🔍 DEBUG: No items found, falling back to text format")
                return cart_text
                
        except Exception as e:
            logger.error(f"❌ Failed to extract cart from agent response: {e}")
            return None
    
    async def _get_cart_data_direct(self, rohlik_client):
        """Get cart data directly from MCP tool, bypassing Strands text conversion"""
        try:
            logger.info("🔍 DEBUG: Calling MCP get_cart_content tool directly")
            
            # Call get_cart_content tool directly
            cart_result = await rohlik_client.call_tool_async("get_cart_content", {})
            logger.info(f"🔍 DEBUG: Raw MCP result: {cart_result}")
            
            if hasattr(cart_result, 'content') and cart_result.content:
                # Extract the raw JSON text from MCP response
                raw_json_text = cart_result.content[0]["text"] if isinstance(cart_result.content[0], dict) else str(cart_result.content[0])
                logger.info(f"🔍 DEBUG: Raw JSON text: {raw_json_text}")
                
                # Parse the JSON
                import json
                parsed_cart = json.loads(raw_json_text)
                logger.info(f"🔍 DEBUG: Parsed JSON: {parsed_cart}")
                
                # Convert to our standard format
                if isinstance(parsed_cart, dict) and 'cart' in parsed_cart:
                    cart_info = parsed_cart['cart']
                    
                    cart_data = {
                        "items": [],
                        "total_items": cart_info.get('total_items', 0),
                        "total_price": cart_info.get('total_price', 0),
                        "currency": cart_info.get('currency', 'EUR')
                    }
                    
                    # Add products
                    for product in cart_info.get('products', []):
                        cart_data["items"].append({
                            "name": product.get('name', ''),
                            "quantity": product.get('quantity', 1),
                            "price": product.get('price', 0),
                            "currency": cart_info.get('currency', 'EUR'),
                            "product_id": product.get('cart_item_id', None)
                        })
                    
                    logger.info(f"🔍 DEBUG: Converted to standard format: {cart_data}")
                    return cart_data
                else:
                    logger.warning(f"🔍 DEBUG: Unexpected JSON structure: {parsed_cart}")
                    return None
            else:
                logger.warning("🔍 DEBUG: No content in MCP result")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get cart data directly: {e}")
            return None

    async def _get_cart_data(self, rohlik_client):
        """Get current cart data (legacy method for external use)"""
        try:
            with rohlik_client:
                # Call get_cart_content tool directly
                cart_result = await rohlik_client.call_tool_async("get_cart_content", {})
                if hasattr(cart_result, 'content') and cart_result.content:
                    return cart_result.content[0]["text"] if isinstance(cart_result.content[0], dict) else str(cart_result.content[0])
                else:
                    return "Cart is empty"
                    
        except Exception as e:
            logger.error(f"❌ Failed to get cart data: {e}")
            return {"error": str(e)}
    
    async def _export_data(self, export_data):
        """Export cart and metrics data to JSON file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"shopping_run_{timestamp}.json"
            filepath = self.export_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Data exported to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to export data: {e}")
            return None


async def main():
    """Main function for standalone execution"""
    if len(sys.argv) < 2:
        print("Usage: python rohlik_agent.py \"Your shopping task\"")
        print("Example: python rohlik_agent.py \"Find me Milk, Chicken Breast, Eggs, Apples, and Bread\"")
        print("")
        print("Features:")
        print("- Parallel processing for multiple items")
        print("- Budget optimization (cheapest options)")
        print("- Metrics collection and export")
        print("- Cart data export to JSON")
        print("- Comprehensive performance tracking")
        print("- Fully autonomous operation")
        sys.exit(1)
    
    task = sys.argv[1]
    
    print("🛒 Starting Rohlik Shopping Agent...")
    print("📡 MCP Integration: Rohlik/Knuspr (Germany, Czech, Austria, Hungary, Romania)")
    print("🤖 Model: qwen/qwen3-4b-2507")
    print("💰 Budget Optimization: Enabled")
    print("📊 Metrics Collection: Enabled")
    print("💾 Data Export: Enabled")
    print("🤖 Mode: Fully Autonomous")
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
        
        print(f"\n🔧 Tool Call Details:")
        tool_calls = result["tool_calls"]
        if tool_calls:
            for i, call in enumerate(tool_calls, 1):
                print(f"  {i}. {call['tool_name']}")
                print(f"     Arguments: {call['arguments']}")
                if call['result']:
                    # Truncate long results for display
                    result_str = str(call['result'])
                    if len(result_str) > 200:
                        result_str = result_str[:200] + "..."
                    print(f"     Result: {result_str}")
                print(f"     Status: {call['status']}")
        else:
            print("  No detailed tool call information available")
        
        print(f"\n💾 Data exported to shopping_exports/ folder")
        
    else:
        print(f"\n❌ Error: {result['error']}")
    
    print("-" * 50)
    print("")


if __name__ == "__main__":
    asyncio.run(main())