#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

# Function to print section headers
print_header() {
    echo ""
    print_color $CYAN "=================================="
    print_color $CYAN "$1"
    print_color $CYAN "=================================="
    echo ""
}

# Function to print menu options
print_menu() {
    echo ""
    echo "🚀 Rohlik Shopping Agent Launcher"
    echo ""
    echo "1) 🛒 Run Single Shopping Agent"
    echo "2) 📊 Run Batch Budget Test (50 runs)"
    echo "3) 📈 Generate CSV Report"
    echo "4) 🧹 Clean Results Directory"
    echo "5) ❌ Exit"
    echo ""
}

# Function to run single agent
run_single_agent() {
    print_header "🛒 SINGLE SHOPPING AGENT"
    
    echo ""
    print_color $BLUE "Enter your shopping request (or press Enter for default budget shopping):"
    read -p "🛒 Shopping task: " shopping_task
    
    # Use default task if none provided
    if [ -z "$shopping_task" ]; then
        shopping_task="I am on a tight budget. Find me Whole Milk, Chicken Breast, Eggs, bunch of Apples, and Bread."
        print_color $YELLOW "Using default budget shopping task..."
    fi
    
    cd strands-agent
    
    print_color $YELLOW "Starting rohlik_agent.py with task: \"$shopping_task\""
    echo ""
    
    if [ -f "rohlik_agent.py" ]; then
        python rohlik_agent.py "$shopping_task"
    else
        print_color $RED "❌ Error: rohlik_agent.py not found!"
        return 1
    fi
    
    cd ..
    
    print_color $GREEN "✅ Single agent run completed!"
}

# Function to run batch test
run_batch_test() {
    print_header "📊 BATCH BUDGET TEST"
    
    cd strands-agent
    
    print_color $YELLOW "Starting batch test with 50 runs..."
    echo ""
    
    if [ -f "batch_budget_test.py" ]; then
        python batch_budget_test.py
    else
        print_color $RED "❌ Error: batch_budget_test.py not found!"
        return 1
    fi
    
    cd ..
    
    print_color $GREEN "✅ Batch test completed!"
}

# Function to generate CSV report
generate_csv() {
    print_header "📈 CSV REPORT GENERATION"
    
    cd strands-agent
    
    print_color $YELLOW "Generating CSV report from test results..."
    echo ""
    
    if [ -f "utils/csv_generator.py" ]; then
        python utils/csv_generator.py
    else
        print_color $RED "❌ Error: CSV generator not found!"
        return 1
    fi
    
    cd ..
    
    print_color $GREEN "✅ CSV report generated!"
}

# Function to clean results
clean_results() {
    print_header "🧹 CLEAN RESULTS"
    
    print_color $YELLOW "This will delete all files in strands-agent/results/"
    read -p "Are you sure? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        rm -rf strands-agent/results/*
        print_color $GREEN "✅ Results directory cleaned!"
    else
        print_color $BLUE "ℹ️  Cleaning cancelled."
    fi
}

# Main menu loop
main() {
    print_header "🛒 ROHLIK SHOPPING AGENT"
    
    while true; do
        print_menu
        read -p "Enter your choice (1-5): " choice
        
        case $choice in
            1)
                run_single_agent
                ;;
            2)
                run_batch_test
                ;;
            3)
                generate_csv
                ;;
            4)
                clean_results
                ;;
            5)
                print_color $GREEN "👋 Goodbye!"
                exit 0
                ;;
            *)
                print_color $RED "❌ Invalid option. Please choose 1-5."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Check if we're in the right directory
if [ ! -d "strands-agent" ]; then
    print_color $RED "❌ Error: strands-agent directory not found!"
    print_color $YELLOW "Please run this script from the project root directory."
    exit 1
fi

# Run main function
main