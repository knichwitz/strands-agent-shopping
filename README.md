# 🛒 Rohlik Shopping Agent & MCP Server

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue.svg)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)

> **Model Context Protocol server for autonomous grocery shopping with Rohlik Group services across 5 European markets. Features reliable shopping agents with comprehensive performance analysis and batch testing capabilities.**

## 🚀 Quick Start

```bash
# 1. Setup (installs dependencies and configures environment)
./setup.sh

# 2. Run the launcher (interactive menu)
./start.sh
```

## 📋 Features

### 🛒 MCP Server
- **Multi-Region Support**: Germany, Czech Republic, Austria, Hungary, Romania
- **Product Search**: Advanced filtering with price sorting and organic options
- **Cart Management**: Add, remove, and view cart items with session persistence
- **Reliable Responses**: Structured JSON outputs for consistent LLM interaction
- **Type-Safe**: Full TypeScript implementation with comprehensive error handling
- **Session Persistence**: Cart state maintained across agent runs

### 🤖 Shopping Agent
- **Autonomous Shopping**: Fully autonomous budget-optimized shopping workflows
- **Quality Focus**: Prioritizes shopping accuracy and reliability
- **Batch Testing**: Configurable test iterations with comprehensive metrics
- **Performance Analysis**: Success rate, execution time, and quality tracking
- **CSV Export**: Structured CSV reports for analysis and reporting
- **Interactive Interface**: Menu-driven launcher with multiple options

## 📊 Performance & Quality

### Quality Assurance Features

- **Reliable Shopping**: Prioritizes accuracy over speed optimization
- **Category Validation**: Ensures food-only product selection
- **Error Handling**: Comprehensive error recovery and retry logic
- **Session Management**: Persistent cart state across runs
- **Data Validation**: Structured JSON responses with type checking

### Performance Characteristics

| Metric | Shopping Agent | Notes |
|--------|----------------|-------|
| **Accuracy** | High | Prioritizes correct product selection |
| **Execution Time** | 30-60s | Varies by request complexity |
| **Success Rate** | >95% | Reliable shopping completion |
| **Cart Quality** | Excellent | Accurate product matching |
| **Error Recovery** | Robust | Handles API failures gracefully |

## 🛠️ Installation

### Prerequisites

- **Node.js 18+** (for MCP server)
- **Python 3.11+** (for Shopping Agent)
- **LM Studio** (for local LLM inference)

### LM Studio Setup

**⚠️ Important**: The Shopping Agent requires LM Studio to be running with a compatible model.

1. **Download and Install LM Studio**
   - Visit: https://lmstudio.ai/
   - Download for your platform (macOS, Windows, Linux)

2. **Download a Compatible Model**
   - Recommended: `qwen/qwen3-4b-2507` (4B parameters, good balance of speed/quality)
   - In LM Studio: Go to "Discover" → Search for "qwen3-4b" → Download

3. **Start the Local Server**
   - In LM Studio: Go to "Local Server" tab
   - Load your downloaded model
   - **Set port to 1234** (default)
   - Click "Start Server"
   - Verify it shows: `Server running on http://localhost:1234`

4. **Verify Connection**
   ```bash
   curl http://localhost:1234/v1/models
   # Should return JSON with your loaded model
   ```

**📝 Note**: The Shopping Agent is pre-configured to use:
- **Model**: `qwen/qwen3-4b-2507` 
- **Endpoint**: `http://localhost:1234/v1`
- **API Key**: `lm-studio` (default)

No additional configuration needed if you follow the setup above!

### Project Setup

```bash
# 1. Run automated setup
./setup.sh

# 2. Launch interactive menu
./start.sh
```

## 📖 Usage

### Interactive Launcher

The `start.sh` script provides an interactive menu with the following options:

1. **🛒 Run Single Shopping Agent** - Execute one shopping session
2. **📊 Run Batch Budget Test** - Run 50 automated shopping sessions
3. **📈 Generate CSV Report** - Export performance data to CSV
4. **🧹 Clean Results Directory** - Clear all test results
5. **❌ Exit** - Close the launcher

### Single Shopping Session

```bash
./start.sh
# Select option 1: Run Single Shopping Agent
```

The agent will:
- Connect to Rohlik.cz
- Search for budget-friendly products
- Add items to cart
- Generate detailed performance report

### Batch Testing

```bash
./start.sh
# Select option 2: Run Batch Budget Test
```

Runs 50 automated shopping sessions with:
- Randomized product searches
- Budget optimization
- Comprehensive metrics collection
- JSON export of all results

### CSV Report Generation

```bash
./start.sh
# Select option 3: Generate CSV Report
```

Generates three CSV files:
- **Detailed Report**: All metrics per run
- **Summary Report**: Aggregated statistics
- **Budget Format**: Compatible with existing analysis tools

## 📁 Project Structure

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

## 🔧 Configuration

### MCP Server Configuration

The MCP server supports multiple Rohlik regions:

- **Germany**: rohlik.de
- **Czech Republic**: rohlik.cz
- **Austria**: rohlik.at
- **Hungary**: rohlik.hu
- **Romania**: rohlik.ro

### Agent Configuration

Edit `strands-agent/batch_budget_test.py` to customize:

```python
# Script configuration
SCRIPT_NAME = "rohlik_agent.py"
TOTAL_RUNS = 50  # Number of test runs
```

## 📊 Data Analysis

### CSV Reports

The CSV generator creates three report types:

1. **Detailed CSV**: Complete metrics for each run
   - Execution time, token usage, cart contents
   - Tool call statistics, error rates
   - Item-level pricing and selection data

2. **Summary CSV**: Aggregated statistics
   - Average execution times and token usage
   - Success rates and error analysis
   - Total spending and item counts

3. **Budget Format CSV**: Compatible with existing tools
   - Standardized column format
   - Easy import into spreadsheet applications
   - Historical data comparison

### Metrics Tracked

- **Performance**: Execution time, cycle count, tool calls
- **Token Usage**: Input, output, cache read/write tokens
- **Shopping Quality**: Items selected, prices, cart totals
- **Success Rates**: Completion rates, error handling
- **Cost Analysis**: Budget adherence, price optimization

## 🔧 Troubleshooting

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Rohlik Group](https://www.rohlik.cz/) for their comprehensive API
- [Model Context Protocol](https://modelcontextprotocol.io/) for the integration framework
- [LM Studio](https://lmstudio.ai/) for local LLM inference capabilities

---

**Happy Shopping! 🛒✨**