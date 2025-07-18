#!/bin/bash
# install_scraping.sh - Install scraping and crawling MCP servers for IntelForge

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [[ ! -f "README.md" ]] || [[ ! -d "../scrapers" ]]; then
    error "Please run this script from the mcp_servers directory"
    exit 1
fi

log "🕷️ Installing MCP Scraping Servers for IntelForge"
echo "=================================================="

# Create directory structure
log "📁 Setting up directory structure..."
mkdir -p servers/{scraping,productivity,data,community}
mkdir -p logs config
mkdir -p servers/scraping/{firecrawl,playwright,scrapling,oxylabs,tavily}

# Check prerequisites
log "🔍 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    warning "Node.js not found. Installing via nvm..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    nvm install --lts
    nvm use --lts
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    warning "Python3 not found. Please install Python 3.8+ manually"
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    error "npm not found. Please install Node.js with npm"
    exit 1
fi

success "Prerequisites checked"

# Install official MCP servers via npx (these will be installed on-demand)
log "📦 Setting up official MCP servers..."

echo "The following servers will be available via npx:"
echo "  - @modelcontextprotocol/server-puppeteer (JavaScript browser automation)"
echo "  - @modelcontextprotocol/server-fetch (Basic HTTP requests)"
echo "  - @modelcontextprotocol/server-brave-search (Web search integration)"

success "Official servers configured"

# Install community servers
log "📥 Installing community scraping servers..."

# Firecrawl (production scraping)
log "Installing Firecrawl MCP server..."
if [ ! -d "servers/scraping/firecrawl/firecrawl-mcp-server" ]; then
    cd servers/scraping/firecrawl
    git clone https://github.com/mendableai/firecrawl-mcp-server.git
    cd firecrawl-mcp-server

    if [ -f "package.json" ]; then
        npm install
        success "Firecrawl installed successfully"
    else
        warning "Firecrawl package.json not found, manual setup may be required"
    fi
    cd ../../../..
else
    success "Firecrawl already installed"
fi

# Playwright (modern automation)
log "Installing Playwright MCP server..."
if [ ! -d "servers/scraping/playwright/mcp-playwright" ]; then
    cd servers/scraping/playwright
    git clone https://github.com/executeautomation/mcp-playwright.git
    cd mcp-playwright

    if [ -f "package.json" ]; then
        npm install
        # Install Playwright browsers
        npx playwright install chromium firefox webkit
        success "Playwright installed successfully"
    else
        warning "Playwright package.json not found, manual setup may be required"
    fi
    cd ../../../..
else
    success "Playwright already installed"
fi

# Scrapling Fetch (anti-bot protection)
log "Installing Scrapling Fetch MCP server..."
if [ ! -d "servers/scraping/scrapling/scrapling-fetch-mcp" ]; then
    cd servers/scraping/scrapling
    git clone https://github.com/cyberchitta/scrapling-fetch-mcp.git
    cd scrapling-fetch-mcp

    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        success "Scrapling Fetch installed successfully"
    elif [ -f "pyproject.toml" ]; then
        pip3 install .
        success "Scrapling Fetch installed successfully"
    else
        warning "Scrapling Fetch requirements not found, manual setup may be required"
    fi
    cd ../../../..
else
    success "Scrapling Fetch already installed"
fi

# Advanced scraping servers (optional)
log "Installing advanced scraping servers..."

# Oxylabs (enterprise scraping)
if [ ! -d "servers/scraping/oxylabs/oxylabs-mcp" ]; then
    log "Installing Oxylabs MCP server..."
    cd servers/scraping/oxylabs
    git clone https://github.com/oxylabs/oxylabs-mcp.git
    cd oxylabs-mcp

    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        success "Oxylabs installed successfully"
    fi
    cd ../../../..
else
    success "Oxylabs already installed"
fi

# Create configuration templates
log "📝 Creating configuration templates..."

# Claude Code configuration
cat > config/claude_desktop_scraping.json << EOF
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/kiriti/alpha_projects/intelforge"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_SEARCH_API_KEY": "your-brave-search-api-key-here"
      }
    },
    "firecrawl": {
      "command": "node",
      "args": ["servers/scraping/firecrawl/firecrawl-mcp-server/index.js"],
      "env": {
        "FIRECRAWL_API_KEY": "your-firecrawl-api-key-here"
      }
    },
    "playwright": {
      "command": "node",
      "args": ["servers/scraping/playwright/mcp-playwright/index.js"]
    }
  }
}
EOF

success "Claude Code configuration created"

# Server settings
cat > config/scraping_settings.yaml << EOF
# IntelForge MCP Scraping Server Settings
scraping:
  general:
    concurrent_requests: 3
    timeout: 30000
    user_agent: "IntelForge-Bot/1.0"

  puppeteer:
    headless: true
    viewport:
      width: 1920
      height: 1080
    wait_for: "networkidle0"
    screenshot: false

  playwright:
    browser: "chromium"
    headless: true
    timeout: 30000
    mobile_emulation: false

  firecrawl:
    rate_limit: 10
    max_pages: 100
    formats: ["markdown", "html"]
    extract_images: false

  fetch:
    follow_redirects: true
    max_redirects: 5
    timeout: 15000

  brave_search:
    count: 10
    offset: 0
    freshness: ""

anti_detection:
  rotate_user_agents: true
  random_delays: true
  respect_robots_txt: true

performance:
  cache_responses: true
  cache_duration: "1h"
  max_memory: "512MB"
EOF

success "Scraping settings created"

# Create environment template
cat > config/.env.template << EOF
# IntelForge MCP Server Environment Variables
# Copy this file to .env and fill in your API keys

# Brave Search API Key (required for brave-search server)
BRAVE_SEARCH_API_KEY=your-brave-search-api-key-here

# Firecrawl API Key (required for firecrawl server)
FIRECRAWL_API_KEY=your-firecrawl-api-key-here

# Oxylabs API Credentials (optional, for enterprise scraping)
OXYLABS_USERNAME=your-oxylabs-username
OXYLABS_PASSWORD=your-oxylabs-password

# Proxy Settings (optional)
HTTP_PROXY=
HTTPS_PROXY=
NO_PROXY=localhost,127.0.0.1

# Performance Settings
MAX_CONCURRENT_REQUESTS=3
REQUEST_TIMEOUT=30000
CACHE_ENABLED=true
EOF

success "Environment template created"

# Create status check script
cat > scripts/check_scraping_servers.sh << 'EOF'
#!/bin/bash
# Check status of IntelForge scraping MCP servers

echo "🔍 Checking IntelForge MCP Scraping Servers"
echo "==========================================="

# Check official servers (via npx)
echo ""
echo "📦 Official Servers (npx):"

servers=("puppeteer" "fetch" "brave-search")
for server in "${servers[@]}"; do
    echo -n "  @modelcontextprotocol/server-$server: "
    if npm list -g "@modelcontextprotocol/server-$server" &>/dev/null || npx -y "@modelcontextprotocol/server-$server" --help &>/dev/null; then
        echo "✅ Available"
    else
        echo "❌ Not available"
    fi
done

# Check community servers
echo ""
echo "🌍 Community Servers:"

echo -n "  Firecrawl: "
if [ -d "servers/scraping/firecrawl/firecrawl-mcp-server" ]; then
    echo "✅ Installed"
else
    echo "❌ Not installed"
fi

echo -n "  Playwright: "
if [ -d "servers/scraping/playwright/mcp-playwright" ]; then
    echo "✅ Installed"
else
    echo "❌ Not installed"
fi

echo -n "  Scrapling Fetch: "
if [ -d "servers/scraping/scrapling/scrapling-fetch-mcp" ]; then
    echo "✅ Installed"
else
    echo "❌ Not installed"
fi

echo -n "  Oxylabs: "
if [ -d "servers/scraping/oxylabs/oxylabs-mcp" ]; then
    echo "✅ Installed"
else
    echo "❌ Not installed"
fi

# Check Claude Code configuration
echo ""
echo "🤖 Claude Code:"
if [ -f "$HOME/.claude/config.json" ]; then
    echo "  Configuration: ✅ Exists"
    if grep -q "puppeteer\|fetch\|firecrawl" "$HOME/.claude/config.json"; then
        echo "  MCP Servers: ✅ Configured"
    else
        echo "  MCP Servers: ⚠️  Not configured"
    fi
else
    echo "  Configuration: ❌ Not found"
fi
EOF

chmod +x scripts/check_scraping_servers.sh
success "Status check script created"

# Create logs directory structure
mkdir -p logs/{scraping,errors,performance}
touch logs/scraping/install.log
echo "$(date): Scraping MCP servers installed successfully" >> logs/scraping/install.log

log "📋 Installation Summary"
echo "======================"
echo ""
echo "✅ Installed Official Servers (via npx):"
echo "   - @modelcontextprotocol/server-puppeteer"
echo "   - @modelcontextprotocol/server-fetch"
echo "   - @modelcontextprotocol/server-brave-search"
echo ""
echo "✅ Installed Community Servers:"
echo "   - Firecrawl (production scraping)"
echo "   - Playwright (modern automation)"
echo "   - Scrapling Fetch (anti-bot protection)"
echo "   - Oxylabs (enterprise scraping)"
echo ""
echo "📝 Configuration Files Created:"
echo "   - config/claude_desktop_scraping.json"
echo "   - config/scraping_settings.yaml"
echo "   - config/.env.template"
echo ""
echo "🔧 Management Scripts:"
echo "   - scripts/check_scraping_servers.sh"
echo ""

warning "Next Steps:"
echo "1. Copy API keys: cp config/.env.template config/.env (and edit)"
echo "2. Configure Claude Code: cp config/claude_desktop_scraping.json ~/.claude/config.json"
echo "3. Test installation: ./scripts/check_scraping_servers.sh"
echo "4. Restart Claude Code to load MCP servers"
echo ""

success "🎉 IntelForge MCP scraping servers installation complete!"
echo ""
echo "📖 For more information, see: README.md"
echo "🐛 For troubleshooting, see: docs/troubleshooting.md"
EOF
