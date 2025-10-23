#!/usr/bin/env python3
"""
Batch Budget Test Script for Rohlik Shopping Agent
Runs the agent 10 times in sequence with the budget shopping prompt
"""

import asyncio
import subprocess
import time
import json
import os
from datetime import datetime
from pathlib import Path

# Budget shopping prompt
BUDGET_PROMPT = "I am on a tight budget. Find me Whole Milk, Chicken Breast, Eggs, bunch of Apples, and Bread."

# Script configuration
SCRIPT_NAME = "rohlik_agent.py"
TOTAL_RUNS = 50

def run_single_test(run_number: int):
    """Run a single test of the Rohlik agent"""
    print(f"🔄 Run {run_number}/{TOTAL_RUNS}...")
    
    start_time = time.time()
    
    try:
        # Run the Rohlik agent using virtual environment Python
        result = subprocess.run(
            ["venv/bin/python", SCRIPT_NAME, BUDGET_PROMPT],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per run
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ Run {run_number} completed in {duration:.2f}s")
        else:
            print(f"❌ Run {run_number} failed")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏰ Run {run_number} timed out")
        return False
    except Exception as e:
        print(f"❌ Run {run_number} failed: {e}")
        return False

def main():
    """Main function to run batch tests"""
    print("🚀 Batch Budget Test - Rohlik Shopping Agent")
    print(f"📝 Prompt: {BUDGET_PROMPT}")
    print(f"🔄 Running {TOTAL_RUNS} tests...")
    
    # Run all tests
    successful_runs = 0
    overall_start_time = time.time()
    
    for run_number in range(1, TOTAL_RUNS + 1):
        success = run_single_test(run_number)
        if success:
            successful_runs += 1
        
        # Small delay between runs
        if run_number < TOTAL_RUNS:
            time.sleep(2)
    
    overall_end_time = time.time()
    total_time = overall_end_time - overall_start_time
    
    print(f"🏁 Completed in {total_time:.2f}s")
    print(f"✅ {successful_runs}/{TOTAL_RUNS} runs successful")
    print(f"🛒 Check shopping_exports/ for detailed shopping results")

if __name__ == "__main__":
    main()
