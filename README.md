# From Pixels to Protocols: Building Production-Ready AI Shopping Agents

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue.svg)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)

> **After spending 40 hours building a screenshot-based shopping agent and running 300 tests to understand its limitations, this project demonstrates the shift to API-based architecture using Model Context Protocol (MCP) for production-ready autonomous grocery shopping across 5 European markets.**

## 🚀 Quick Start

```bash
# 1. Setup (installs dependencies and configures environment)
./setup.sh

# 2. Run the launcher (interactive menu)
./start.sh
```

## 🚀 The Journey: From Screenshots to APIs

After 40 hours of building screenshot-based shopping agents and running 300 tests, the fundamental question emerged: **"Should we make screenshot-based agents work better, or were they the wrong choice entirely?"**

The answer was clear. This project demonstrates the shift from computer vision-based approaches to **API-based architecture using Model Context Protocol (MCP)** — a standard that lets AI systems interact with APIs through structured schemas.

### 🛒 MCP Server (API-Based Architecture)
- **Multi-Region Support**: Germany, Czech Republic, Austria, Hungary, Romania
- **Direct API Integration**: No screenshots, no UI scraping — pure API communication
- **Product Search**: Advanced filtering with price sorting and organic options
- **Cart Management**: Add, remove, and view cart items with session persistence
- **Reliable Responses**: Structured JSON outputs for consistent LLM interaction
- **Type-Safe**: Full TypeScript implementation with comprehensive error handling
- **Session Persistence**: Cookie-based state management, not browser state

### 🤖 Production-Ready Shopping Agent
- **100% Success Rate**: Reliable shopping completion (vs 60% with screenshot approach)
- **Sequential Processing**: One item at a time, preventing cascade failures
- **Stateless Operation**: No memory between runs, just single-session task completion
- **Cost-Effective**: 0.42-0.70% of transaction margin in inference costs
- **Batch Testing**: 200+ test runs with comprehensive performance tracking
- **CSV Export**: Structured reports for analysis and business intelligence

## 📊 Production-Ready Performance Metrics

### The Shift: From 60% to 100% Success Rate

The transition from screenshot-based to API-based architecture delivered production-viable metrics across every dimension:

| Metric | Screenshot Approach | API-Based Approach | Improvement |
|--------|-------------------|-------------------|-------------|
| **Success Rate** | 60% | 100% | +40% |
| **Execution Time** | 30-60s | 30-60s | Consistent |
| **Cost Efficiency** | High operational overhead | 0.42-0.70% of margin | 99%+ cost reduction |
| **Reliability** | UI-dependent failures | API-stable | Production-ready |
| **Maintenance** | High (UI changes = breaking changes) | Low (API contracts) | Minimal overhead |

### Cost Analysis & Business Viability

**Typical Scenario (€39 cart, 3-5% margin):**
- Gross profit: €1.17 to €1.95
- Agent costs: €0.005 to €0.008 (0.42-0.70% of margin)

**Best Case (Private label, 25% margin):**
- Gross profit: €9.75
- Agent costs: €0.008 (0.08% of margin)

**Scale Projection (1,000 carts/month):**
- Monthly inference costs: €8.22
- Gross profit range: €1,170 to €9,750
- ROI: 14,000% to 118,000%

### Quality Assurance Features

- **Sequential Processing**: One item at a time, preventing cascade failures
- **Category Validation**: Ensures food-only product selection with structured data
- **Error Handling**: Comprehensive API error recovery and retry logic
- **Session Management**: Cookie-based persistence, not browser state
- **Data Validation**: Structured JSON responses with type checking

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

## 🏗️ Architecture: API-First Design

### Model Context Protocol (MCP) Integration

This system uses **Model Context Protocol (MCP)** — a standard that lets AI systems interact with APIs through structured schemas. Instead of fighting with computer vision to extract data from pixels, we work directly with the structured data that e-commerce platforms are built on.

**Key Architectural Decisions:**
- **API-Based**: Direct integration with Rohlik's reverse-engineered APIs
- **Sequential Processing**: One item at a time, preventing cascade failures
- **Stateless Operation**: No memory between runs, just single-session task completion
- **Cookie Persistence**: Session management via cookies, not browser state
- **Structured Data**: Product categories and metadata for better decision-making

### Project Structure

```
rohlik-mcp-server/
├── rohlik-mcp/              # TypeScript MCP server
│   ├── src/                 # Server source code
│   │   ├── tools/           # MCP tool implementations
│   │   └── rohlik-api.ts    # API integration layer
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

## 🎯 Lessons Learned: Why API-Based Architecture Won

### The Hardest Decision: Abandoning 40 Hours of Work

The hardest part wasn't building the API-based agent in 6 hours. It was deciding to abandon 40 hours of work on the screenshot approach. **Sunk cost fallacy is real**, especially when you've invested significant time debugging, prompt engineering, and convincing yourself that "one more iteration" will fix the fundamental issues.

### Key Insights from 300 Test Runs

**Screenshot Approach Problems:**
- Every UI change becomes a breaking change
- Every modal dialog becomes a potential infinite loop  
- Every "X" button the agent fails to detect becomes a support ticket
- High operational cost of maintaining a system that fights against the medium

**API Approach Advantages:**
- E-commerce platforms are structured data systems built on APIs
- Using computer vision to extract structured data from rendered pixels is like OCR-ing a PDF generated from a Word document — technically possible, but why?
- When the right abstraction clicks, the code writes itself
- When you're fighting the wrong abstraction, every line is a struggle

### The Signal to Rebuild Instead of Iterate

- When your 10% improvements require 100% effort, you're optimizing the wrong thing
- When fixing one bug creates two new ones, the foundation is wrong
- When you spend more time maintaining the system than improving it, the abstraction doesn't match the problem

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

## ⚠️ Important Disclaimer

**This is NOT a production-ready system.** This project is a **proof-of-concept** that demonstrates the technical foundation and business viability of API-based shopping agents. It showcases that the approach works and is economically feasible, but requires significant additional development for production deployment.

## 🚀 What This Proves: Technical Foundation & Business Viability

When we say this system demonstrates **production-readiness**, we're talking about the approach and business case, not the deployment. The codebase you'll find on GitHub is a fully functional proof-of-concept that demonstrates:

- **Technical Foundation**: API-based architecture, MCP integration, reliable execution
- **Business Viability**: Predictable costs at 0.42-0.70% of transaction margin
- **Scalability Path**: Clear implementation roadmap for production deployment

**Current State (Proof-of-Concept):**
- Runs locally with LM Studio
- Handles single-user sessions through file-based cookie store
- 100% success rate across 200+ test runs
- Cost-effective at 0.42-0.70% of transaction margin

**What Production Would Require (2-4 weeks additional work):**
- Session management via DynamoDB
- Request queuing through SQS  
- Proper authentication and user management
- Multi-tenant support
- Error monitoring and alerting
- Rate limiting and abuse prevention
- Compliance and security hardening

**The Key Insight:** These are solved problems with clear implementation paths. The hard part — proving that API-based agents can reliably complete shopping tasks with predictable performance and viable economics — is done. The rest is engineering, not research.

**For Business Decision Makers:** This demonstrates that AI shopping agents are technically feasible and economically viable. The question isn't whether this exact code runs at scale, but whether the approach is fundamentally sound enough to invest in productionizing. The answer, backed by 200 test runs and cost analysis, is yes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Rohlik Group](https://www.rohlik.cz/) for their comprehensive API across 5 European markets
- [Model Context Protocol](https://modelcontextprotocol.io/) for the integration framework that made this possible
- [LM Studio](https://lmstudio.ai/) for local LLM inference capabilities
- The 40 hours of screenshot-based development that taught us what not to build

---

**From Pixels to Protocols: The future of AI shopping agents is API-first. 🛒✨**