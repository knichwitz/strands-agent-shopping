# Rohlik Shopping Agent & MCP Server

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue.svg)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)

> **⚠️ PROTOTYPE DISCLAIMER: This is a prototype implementation and is not production-ready. Use at your own risk. The software may contain bugs, incomplete features, and should not be used for actual shopping transactions without thorough testing.**

Model Context Protocol server for grocery shopping automation with Rohlik Group services across 5 European markets. Includes shopping agents with performance analysis and batch testing capabilities.

## Quick Start

```bash
# 1. Setup (installs dependencies and configures environment)
./setup.sh

# 2. Run the launcher (interactive menu)
./start.sh
```

## Features

### MCP Server
- Multi-region support for Germany, Czech Republic, Austria, Hungary, Romania
- Product search with filtering, price sorting, and organic options
- Cart management with add, remove, and view operations
- Session persistence for cart state maintenance
- TypeScript implementation with error handling
- Structured JSON responses for LLM integration

### Shopping Agent
- Automated shopping workflows with budget optimization
- Batch testing with configurable iterations
- Performance metrics collection and analysis
- CSV export functionality for data analysis
- Interactive menu-driven interface

## Performance & Quality

### Implementation Features

- Product selection validation for food categories only
- Error handling and retry logic
- Session management with persistent cart state
- Data validation with structured JSON responses
- Type checking and validation

### Performance Metrics

| Metric | Shopping Agent | Notes |
|--------|----------------|-------|
| Accuracy | Variable | Depends on product availability and search terms |
| Execution Time | 30-60s | Varies by request complexity and network conditions |
| Success Rate | Variable | Depends on API availability and product selection |
| Cart Quality | Variable | Based on product matching accuracy |
| Error Recovery | Implemented | Handles API failures with retry logic |

## Installation

### Prerequisites

- Node.js 24+ (for MCP server)
- Python 3.11+ (for Shopping Agent)
- LM Studio (for local LLM inference)

### LM Studio Setup

**Important**: The Shopping Agent requires LM Studio to be running with a compatible model.

1. **Download and Install LM Studio**
   - Visit: https://lmstudio.ai/
   - Download for your platform (macOS, Windows, Linux)

2. **Download a Compatible Model**
   - Recommended: `qwen/qwen3-4b-2507` (4B parameters, balance of speed/quality)
   - In LM Studio: Go to "Discover" → Search for "qwen3-4b" → Download

3. **Start the Local Server**
   - In LM Studio: Go to "Local Server" tab
   - Load your downloaded model
   - Set port to 1234 (default)
   - Click "Start Server"
   - Verify it shows: `Server running on http://localhost:1234`

4. **Verify Connection**
   ```bash
   curl http://localhost:1234/v1/models
   # Should return JSON with your loaded model
   ```

**Note**: The Shopping Agent is pre-configured to use:
- Model: `qwen/qwen3-4b-2507` 
- Endpoint: `http://localhost:1234/v1`
- API Key: `lm-studio` (default)

No additional configuration needed if you follow the setup above.

### Project Setup

```bash
# 1. Run automated setup
./setup.sh

# 2. Launch interactive menu
./start.sh
```

## Usage

### Interactive Launcher

The `start.sh` script provides an interactive menu with the following options:

1. Run Single Shopping Agent - Execute one shopping session
2. Run Batch Budget Test - Run 50 automated shopping sessions
3. Generate CSV Report - Export performance data to CSV
4. Clean Results Directory - Clear all test results
5. Exit - Close the launcher

### Single Shopping Session

```bash
./start.sh
# Select option 1: Run Single Shopping Agent
```

The agent will:
- Connect to Rohlik.cz
- Search for products
- Add items to cart
- Generate performance report

### Batch Testing

```bash
./start.sh
# Select option 2: Run Batch Budget Test
```

Runs 50 automated shopping sessions with:
- Randomized product searches
- Budget optimization
- Metrics collection
- JSON export of results

### CSV Report Generation

```bash
./start.sh
# Select option 3: Generate CSV Report
```

Generates three CSV files:
- Detailed Report: All metrics per run
- Summary Report: Aggregated statistics
- Budget Format: Compatible with existing analysis tools

## Project Structure

```
rohlik-mcp-server/
├── mcp-server/              # TypeScript MCP server
│   ├── src/                 # Server source code
│   └── package.json         # Node.js dependencies
├── strands-agent/           # Python shopping agent
│   ├── rohlik_agent.py      # Main shopping agent
│   ├── batch_budget_test.py # Batch testing script
│   ├── utils/               # Utility modules
│   │   └── csv_generator.py # CSV report generator
│   └── results/             # Test results and exports
├── setup.sh                 # Automated setup script
├── start.sh                 # Interactive launcher
└── README.md               # This file
```

## Configuration

### MCP Server Configuration

The MCP server supports multiple Rohlik regions:

- Germany: rohlik.de
- Czech Republic: rohlik.cz
- Austria: rohlik.at
- Hungary: rohlik.hu
- Romania: rohlik.ro

### Agent Configuration

Edit `strands-agent/batch_budget_test.py` to customize:

```python
# Script configuration
SCRIPT_NAME = "rohlik_agent.py"
TOTAL_RUNS = 50  # Number of test runs
```

## Data Analysis

### CSV Reports

The CSV generator creates three report types:

1. Detailed CSV: Complete metrics for each run
   - Execution time, token usage, cart contents
   - Tool call statistics, error rates
   - Item-level pricing and selection data

2. Summary CSV: Aggregated statistics
   - Average execution times and token usage
   - Success rates and error analysis
   - Total spending and item counts

3. Budget Format CSV: Compatible with existing tools
   - Standardized column format
   - Easy import into spreadsheet applications
   - Historical data comparison

### Metrics Tracked

- Performance: Execution time, cycle count, tool calls
- Token Usage: Input, output, cache read/write tokens
- Shopping Quality: Items selected, prices, cart totals
- Success Rates: Completion rates, error handling
- Cost Analysis: Budget adherence, price optimization

## Troubleshooting

### LM Studio Issues

**Agent fails with connection error:**
```bash
# Check if LM Studio server is running
curl http://localhost:1234/v1/models

# If connection refused:
# 1. Open LM Studio
# 2. Go to "Local Server" tab  
# 3. Load a model and click "Start Server"
# 4. Verify port is 1234
```

**"No model loaded" error:**
- In LM Studio: Load a model in the "Local Server" tab before starting
- Recommended models: qwen3-4b, llama-3.2-3b, or similar 2B-8B parameter models

**Slow performance:**
- Use smaller models (2B-4B parameters) for faster inference
- Ensure LM Studio is using GPU acceleration if available
- Close other applications to free up system resources

### Shopping Agent Issues

**"No products found":**
- Check your region setting in `rohlik-mcp/.env`
- Verify the MCP server is running: `cd rohlik-mcp && npm start`
- Try different search terms or check if the service is available in your area

**CSV generation fails:**
- Ensure you have run at least one shopping session first
- Check that JSON files exist in `strands-agent/shopping_exports/`
- Run: `./start.sh` → Option 1 (Single Agent) → then Option 3 (CSV Report)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Rohlik Group](https://www.rohlik.cz/) for their API
- [Model Context Protocol](https://modelcontextprotocol.io/) for the integration framework
- [LM Studio](https://lmstudio.ai/) for local LLM inference capabilities