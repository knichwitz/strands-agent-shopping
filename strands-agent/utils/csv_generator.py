#!/usr/bin/env python3
"""
CSV Generator Utility

Generates CSV reports from shopping agent run data for analysis and reporting.
"""

import json
import csv
import glob
import os
from datetime import datetime
from typing import List, Dict, Any


class CSVGenerator:
    """Generates CSV reports from shopping agent run data."""
    
    def __init__(self, input_directory: str = "shopping_exports"):
        """Initialize CSV generator.
        
        Args:
            input_directory: Directory containing JSON run files
        """
        self.input_directory = input_directory
    
    def load_run_data(self) -> List[Dict[str, Any]]:
        """Load all run JSON files from directory."""
        # Look for both patterns: run_*.json and shopping_run_*.json
        patterns = [
            os.path.join(self.input_directory, "run_*.json"),
            os.path.join(self.input_directory, "shopping_run_*.json")
        ]
        
        files = []
        for pattern in patterns:
            files.extend(glob.glob(pattern))
        
        runs = []
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    runs.append(data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return sorted(runs, key=lambda x: x['timestamp'])
    
    def generate_detailed_csv(self, runs: List[Dict[str, Any]], output_file: str):
        """Generate detailed CSV file with all metrics."""
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'timestamp', 'execution_time_seconds', 'total_tokens', 'input_tokens', 
                'output_tokens', 'cache_read_tokens', 'cache_write_tokens', 'cycle_count',
                'total_items', 'total_price', 'currency', 'items_count', 'item_names', 
                'average_item_price', 'tool_calls_total', 'search_products_calls',
                'add_to_cart_calls', 'get_cart_content_calls', 'task'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for run in runs:
                # Extract basic info
                timestamp = run.get('timestamp', '')
                execution_time = run.get('execution_time_seconds', 0)
                
                # Extract token metrics
                usage = run.get('metrics', {}).get('accumulated_usage', {})
                total_tokens = usage.get('totalTokens', 0)
                input_tokens = usage.get('inputTokens', 0)
                output_tokens = usage.get('outputTokens', 0)
                cache_read = usage.get('cacheReadInputTokens', 0)
                cache_write = usage.get('cacheWriteInputTokens', 0)
                
                # Extract other metrics
                cycle_count = run.get('metrics', {}).get('cycle_count', 0)
                
                # Extract cart info
                cart_data = run.get('cart_data', {})
                total_items = cart_data.get('total_items', 0)
                total_price = cart_data.get('total_price', 0)
                currency = cart_data.get('currency', 'EUR')
                
                # Extract items
                items = cart_data.get('items', [])
                item_names = [item.get('name', '') for item in items]
                item_prices = [item.get('price', 0) for item in items]
                
                # Extract tool metrics
                tool_metrics = run.get('metrics', {}).get('tool_metrics', {})
                search_calls = tool_metrics.get('search_products', {}).get('call_count', 0)
                add_cart_calls = tool_metrics.get('add_to_cart', {}).get('call_count', 0)
                get_cart_calls = tool_metrics.get('get_cart_content', {}).get('call_count', 0)
                total_tool_calls = search_calls + add_cart_calls + get_cart_calls
                
                writer.writerow({
                    'timestamp': timestamp,
                    'execution_time_seconds': execution_time,
                    'total_tokens': total_tokens,
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'cache_read_tokens': cache_read,
                    'cache_write_tokens': cache_write,
                    'cycle_count': cycle_count,
                    'total_items': total_items,
                    'total_price': total_price,
                    'currency': currency,
                    'items_count': len(items),
                    'item_names': '; '.join(item_names),
                    'average_item_price': sum(item_prices) / len(item_prices) if item_prices else 0,
                    'tool_calls_total': total_tool_calls,
                    'search_products_calls': search_calls,
                    'add_to_cart_calls': add_cart_calls,
                    'get_cart_content_calls': get_cart_calls,
                    'task': run.get('task', '')
                })
        
        print(f"✅ Detailed CSV generated: {output_file}")
        return output_file
    
    def generate_summary_csv(self, runs: List[Dict[str, Any]], output_file: str):
        """Generate summary CSV with aggregated statistics."""
        
        if not runs:
            print("❌ No data to summarize")
            return
        
        # Calculate aggregated metrics
        from statistics import mean, median
        
        exec_times = [run['execution_time_seconds'] for run in runs]
        total_tokens = [run['metrics']['accumulated_usage']['totalTokens'] for run in runs]
        input_tokens = [run['metrics']['accumulated_usage']['inputTokens'] for run in runs]
        output_tokens = [run['metrics']['accumulated_usage']['outputTokens'] for run in runs]
        cache_read = [run['metrics']['accumulated_usage'].get('cacheReadInputTokens', 0) for run in runs]
        cycles = [run['metrics']['cycle_count'] for run in runs]
        cart_totals = [run['cart_data']['total_price'] for run in runs]
        item_counts = [run['cart_data']['total_items'] for run in runs]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Runs', len(runs)])
            writer.writerow(['Average Execution Time (s)', f"{mean(exec_times):.2f}"])
            writer.writerow(['Median Execution Time (s)', f"{median(exec_times):.2f}"])
            writer.writerow(['Min Execution Time (s)', f"{min(exec_times):.2f}"])
            writer.writerow(['Max Execution Time (s)', f"{max(exec_times):.2f}"])
            writer.writerow(['Average Total Tokens', f"{mean(total_tokens):.0f}"])
            writer.writerow(['Average Input Tokens', f"{mean(input_tokens):.0f}"])
            writer.writerow(['Average Output Tokens', f"{mean(output_tokens):.0f}"])
            writer.writerow(['Average Cache Read Tokens', f"{mean(cache_read):.0f}"])
            writer.writerow(['Total Cache Read Tokens', f"{sum(cache_read):,}"])
            writer.writerow(['Average Cycles', f"{mean(cycles):.1f}"])
            writer.writerow(['Average Cart Price (EUR)', f"{mean(cart_totals):.2f}"])
            writer.writerow(['Average Items per Cart', f"{mean(item_counts):.1f}"])
            writer.writerow(['Total Items Purchased', f"{sum(item_counts)}"])
            writer.writerow(['Total Amount Spent (EUR)', f"{sum(cart_totals):.2f}"])
        
        print(f"✅ Summary CSV generated: {output_file}")
        return output_file
    
    def generate_budget_format_csv(self, runs: List[Dict[str, Any]], output_file: str):
        """Generate CSV file in the same format as Budget.csv for compatibility."""
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Timestamp', 'Task', 'Time (s)', 'Input Tokens', 'Output Tokens', 
                'Total Tokens', 'Cache Read', 'Cycles', 'Items', 'Total',
                'Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for run in runs:
                # Format timestamp
                timestamp = datetime.fromisoformat(run['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%dT%H:%M:%S')
                
                # Get metrics
                exec_time = run['execution_time_seconds']
                input_tokens = run['metrics']['accumulated_usage']['inputTokens']
                output_tokens = run['metrics']['accumulated_usage']['outputTokens']
                total_tokens = run['metrics']['accumulated_usage']['totalTokens']
                cache_read = run['metrics']['accumulated_usage'].get('cacheReadInputTokens', 0)
                cycles = run['metrics']['cycle_count']
                items = run['cart_data']['total_items']
                total_price = f"€{run['cart_data']['total_price']:.2f}"
                
                # Get item names with prices (up to 5)
                item_columns = ['', '', '', '', '']
                for i, item in enumerate(run['cart_data']['items'][:5]):
                    item_columns[i] = f"{item['name']} (€{item['price']:.2f})"
                
                # Write row
                writer.writerow({
                    'Timestamp': timestamp,
                    'Task': run['task'],
                    'Time (s)': exec_time,
                    'Input Tokens': input_tokens,
                    'Output Tokens': output_tokens,
                    'Total Tokens': total_tokens,
                    'Cache Read': cache_read,
                    'Cycles': cycles,
                    'Items': items,
                    'Total': total_price,
                    'Item 1': item_columns[0],
                    'Item 2': item_columns[1],
                    'Item 3': item_columns[2],
                    'Item 4': item_columns[3],
                    'Item 5': item_columns[4]
                })
        
        print(f"✅ Budget format CSV generated: {output_file}")
        return output_file
    
    def generate_all_reports(self, base_filename: str = None) -> Dict[str, str]:
        """Generate all CSV report types.
        
        Args:
            base_filename: Base filename for reports (timestamp will be added)
            
        Returns:
            Dictionary mapping report type to generated filename
        """
        print("📊 Loading run data...")
        runs = self.load_run_data()
        
        if not runs:
            raise ValueError("No run data found!")
        
        print(f"📈 Loaded {len(runs)} runs")
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if base_filename is None:
            base_filename = f"shopping_analysis_{timestamp}"
        
        generated_files = {}
        
        # Generate detailed CSV
        detailed_file = f"{base_filename}_detailed.csv"
        generated_files['detailed'] = self.generate_detailed_csv(runs, detailed_file)
        
        # Generate summary CSV
        summary_file = f"{base_filename}_summary.csv"
        generated_files['summary'] = self.generate_summary_csv(runs, summary_file)
        
        # Generate budget format CSV
        budget_file = f"{base_filename}_budget.csv"
        generated_files['budget'] = self.generate_budget_format_csv(runs, budget_file)
        
        print(f"📊 Generated {len(generated_files)} CSV reports")
        return generated_files


if __name__ == "__main__":
    """Main entry point for CSV generation."""
    try:
        generator = CSVGenerator()
        generated_files = generator.generate_all_reports()
        
        print("\n🎉 CSV Generation Complete!")
        print("Generated files:")
        for report_type, filename in generated_files.items():
            print(f"  📄 {report_type.title()}: {filename}")
            
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Tip: Run some shopping agent tests first to generate data!")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")