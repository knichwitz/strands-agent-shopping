#!/bin/bash

# 🛒 Rohlik MCP Server Setup Script
# Automated setup for the Rohlik MCP Server

set -e  # Exit on any error

echo "🛒 Setting up Rohlik MCP Server..."
echo "=================================="

# Check Node.js version
echo "📋 Checking prerequisites..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version $NODE_VERSION is too old. Please install Node.js 18+."
    exit 1
fi

echo "✅ Node.js $(node -v) detected"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm $(npm -v) detected"

# Navigate to rohlik-mcp directory
cd rohlik-mcp

echo ""
echo "📦 Installing dependencies..."
npm install

echo ""
echo "🔧 Setting up configuration..."

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env configuration file"
    
    # Prompt user for region selection
    echo ""
    echo "🌍 Select your region:"
    echo "1) Germany (Knuspr) - Default"
    echo "2) Czech Republic (Rohlik)"
    echo "3) Austria (Gurkerl)"
    echo "4) Hungary (Kifli)"
    echo "5) Romania (Sezamo)"
    echo ""
    read -p "Enter your choice (1-5) [1]: " region_choice
    
    case ${region_choice:-1} in
        1)
            sed -i.bak 's|# ROHLIK_BASE_URL=https://www.knuspr.de|ROHLIK_BASE_URL=https://www.knuspr.de|' .env
            echo "✅ Configured for Germany (Knuspr)"
            ;;
        2)
            sed -i.bak 's|ROHLIK_BASE_URL=https://www.knuspr.de|# ROHLIK_BASE_URL=https://www.knuspr.de|' .env
            sed -i.bak 's|# ROHLIK_BASE_URL=https://www.rohlik.cz|ROHLIK_BASE_URL=https://www.rohlik.cz|' .env
            echo "✅ Configured for Czech Republic (Rohlik)"
            ;;
        3)
            sed -i.bak 's|ROHLIK_BASE_URL=https://www.knuspr.de|# ROHLIK_BASE_URL=https://www.knuspr.de|' .env
            sed -i.bak 's|# ROHLIK_BASE_URL=https://www.gurkerl.at|ROHLIK_BASE_URL=https://www.gurkerl.at|' .env
            echo "✅ Configured for Austria (Gurkerl)"
            ;;
        4)
            sed -i.bak 's|ROHLIK_BASE_URL=https://www.knuspr.de|# ROHLIK_BASE_URL=https://www.knuspr.de|' .env
            sed -i.bak 's|# ROHLIK_BASE_URL=https://www.kifli.hu|ROHLIK_BASE_URL=https://www.kifli.hu|' .env
            echo "✅ Configured for Hungary (Kifli)"
            ;;
        5)
            sed -i.bak 's|ROHLIK_BASE_URL=https://www.knuspr.de|# ROHLIK_BASE_URL=https://www.knuspr.de|' .env
            sed -i.bak 's|# ROHLIK_BASE_URL=https://www.sezamo.ro|ROHLIK_BASE_URL=https://www.sezamo.ro|' .env
            echo "✅ Configured for Romania (Sezamo)"
            ;;
        *)
            echo "✅ Using default Germany (Knuspr) configuration"
            ;;
    esac
    
    # Clean up backup file
    rm -f .env.bak
else
    echo "✅ Configuration file .env already exists"
fi

echo ""
echo "🔨 Building TypeScript..."
npm run build

echo ""
echo "🧪 Running tests to verify setup..."
if npm test; then
    echo "✅ All tests passed"
else
    echo "⚠️  Some tests failed, but continuing with setup..."
    echo "   You can run 'npm test' later to check specific issues"
fi

echo ""
echo "🐍 Setting up Python virtual environment for Strands Agent..."
cd ../strands-agent

# Check for Python 3.11+ (prefer specific versions)
PYTHON_CMD=""
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "⚠️  Python 3 not found. Please install Python 3.10+ to use the Strands Agent."
    echo "   The MCP server will still work without Python."
    echo ""
    echo "   To install Python 3.11+ on macOS:"
    echo "   - Using Homebrew: brew install python@3.11"
    echo "   - Or download from: https://www.python.org/downloads/"
    echo ""
    cd ../rohlik-mcp
    echo "✅ Setup completed (MCP server only)!"
    echo "🚀 You can still use the MCP server with: cd rohlik-mcp && npm start"
    exit 0
fi

PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

echo "✅ Python $PYTHON_VERSION detected (using $PYTHON_CMD)"

# Check if Python version is 3.10+ (minimum for strands-agents)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "❌ Python $PYTHON_VERSION is too old. The strands-agents package requires Python 3.10+."
    echo "   Found Python versions:"
    command -v python3.11 &> /dev/null && echo "   - python3.11 available ✅"
    command -v python3.10 &> /dev/null && echo "   - python3.10 available ✅"
    echo ""
    echo "   The MCP server will still work without Python."
    cd ../rohlik-mcp
    echo "✅ Setup completed (MCP server only)!"
    echo "🚀 You can still use the MCP server with: cd rohlik-mcp && npm start"
    exit 0
elif [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]; then
    echo "⚠️  Python $PYTHON_VERSION detected. Python 3.11+ is recommended for optimal performance."
    echo "   Continuing with current version..."
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv
    echo "✅ Virtual environment created"
else
    # Check if existing venv uses the correct Python version
    VENV_PYTHON_VERSION=$(venv/bin/python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "unknown")
    if [ "$VENV_PYTHON_VERSION" != "$PYTHON_VERSION" ]; then
        echo "⚠️  Existing virtual environment uses Python $VENV_PYTHON_VERSION, but $PYTHON_CMD is Python $PYTHON_VERSION"
        echo "📦 Recreating virtual environment with correct Python version..."
        rm -rf venv
        $PYTHON_CMD -m venv venv
        echo "✅ Virtual environment recreated with $PYTHON_CMD"
    else
        echo "✅ Virtual environment already exists with correct Python version"
    fi
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
if [ -f requirements.txt ]; then
    echo "📦 Installing Python dependencies in virtual environment..."
    pip install -r requirements.txt
    echo "✅ Python dependencies installed in venv"
else
    echo "⚠️  requirements.txt not found in strands-agent/"
fi

# Deactivate virtual environment
deactivate
echo "✅ Virtual environment setup complete"

cd ../rohlik-mcp

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 Next steps:"
echo "   1. Run './start.sh' to run the batch budget test (50 iterations)"
echo "   2. Or manually start MCP server: cd rohlik-mcp && npm start"
echo "   3. Test MCP server: cd rohlik-mcp && npm run inspect"
echo ""
echo "📖 Configuration:"
echo "   - Edit rohlik-mcp/.env to change region"
echo "   - See README.md for MCP client configuration"
echo ""
echo "🎯 Example MCP client config:"
echo '   {'
echo '     "mcpServers": {'
echo '       "rohlik": {'
echo '         "command": "node",'
echo '         "args": ["'$(pwd)'/dist/index.js"]'
echo '       }'
echo '     }'
echo '   }'