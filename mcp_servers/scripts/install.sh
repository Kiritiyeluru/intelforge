#!/bin/bash
# install.sh - Master installation script for IntelForge MCP servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

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

header() {
    echo -e "${PURPLE}$1${NC}"
}

# Main installation function
main() {
    header "🚀 IntelForge MCP Servers Installation"
    header "======================================"
    echo ""
    
    log "Setting up IntelForge MCP server infrastructure..."
    
    # Check if we're in the right directory
    if [[ ! -f "README.md" ]] || [[ ! -d "../scrapers" ]]; then
        error "Please run this script from the mcp_servers directory"
        exit 1
    fi
    
    # Create base directory structure
    log "📁 Creating directory structure..."
    mkdir -p {config,scripts,servers,logs,docs}
    mkdir -p servers/{scraping,productivity,data,community}
    mkdir -p logs/{scraping,productivity,errors,performance}
    mkdir -p docs
    success "Directory structure created"
    
    # Make scripts executable
    log "🔧 Setting up permissions..."
    chmod +x scripts/*.sh 2>/dev/null || true
    success "Script permissions set"
    
    # Installation options
    echo ""
    header "📦 Installation Options:"
    echo "1. Full Installation (Scraping + Productivity)"
    echo "2. Scraping Only"
    echo "3. Productivity Only"
    echo "4. Custom Installation"
    echo ""
    
    read -p "Choose installation type (1-4): " choice
    echo ""
    
    case $choice in
        1)
            log "Installing full MCP server suite..."
            install_full
            ;;
        2)
            log "Installing scraping servers only..."
            install_scraping_only
            ;;
        3)
            log "Installing productivity servers only..."
            install_productivity_only
            ;;
        4)
            log "Starting custom installation..."
            install_custom
            ;;
        *)
            error "Invalid choice. Please run the script again."
            exit 1
            ;;
    esac
    
    # Final setup
    post_installation
}

install_full() {
    header "🔥 Full Installation - All MCP Servers"
    echo ""
    
    log "Installing scraping servers..."
    if [ -f "scripts/install_scraping.sh" ]; then
        ./scripts/install_scraping.sh
    else
        warning "Scraping installation script not found"
    fi
    
    echo ""
    log "Installing productivity servers..."
    if [ -f "scripts/install_productivity.sh" ]; then
        ./scripts/install_productivity.sh
    else
        warning "Productivity installation script not found"
    fi
    
    success "Full installation completed"
}

install_scraping_only() {
    header "🕷️ Scraping Servers Only"
    echo ""
    
    if [ -f "scripts/install_scraping.sh" ]; then
        ./scripts/install_scraping.sh
    else
        error "Scraping installation script not found"
        exit 1
    fi
    
    success "Scraping servers installation completed"
}

install_productivity_only() {
    header "🚀 Productivity Servers Only"
    echo ""
    
    if [ -f "scripts/install_productivity.sh" ]; then
        ./scripts/install_productivity.sh
    else
        error "Productivity installation script not found"
        exit 1
    fi
    
    success "Productivity servers installation completed"
}

install_custom() {
    header "🛠️ Custom Installation"
    echo ""
    
    echo "Select servers to install:"
    echo ""
    
    # Scraping servers
    echo "🕷️ Scraping Servers:"
    read -p "  Install Puppeteer? (y/n): " install_puppeteer
    read -p "  Install Firecrawl? (y/n): " install_firecrawl
    read -p "  Install Playwright? (y/n): " install_playwright
    read -p "  Install Brave Search? (y/n): " install_brave
    echo ""
    
    # Productivity servers
    echo "🚀 Productivity Servers:"
    read -p "  Install Git MCP? (y/n): " install_git
    read -p "  Install SQLite MCP? (y/n): " install_sqlite
    read -p "  Install Everything MCP? (y/n): " install_everything
    echo ""
    
    # Install selected servers
    config_json='{"mcpServers":{'
    
    # Always include filesystem and memory (core)
    config_json+='"filesystem":{"command":"npx","args":["-y","@modelcontextprotocol/server-filesystem","/home/kiriti/alpha_projects/intelforge"]},'
    config_json+='"memory":{"command":"npx","args":["-y","@modelcontextprotocol/server-memory"]},'
    config_json+='"github":{"transport":"http","endpoint":"https://api.githubcopilot.com/mcp/"}'
    
    # Add selected servers
    if [[ "$install_puppeteer" =~ ^[Yy]$ ]]; then
        config_json+=',"puppeteer":{"command":"npx","args":["-y","@modelcontextprotocol/server-puppeteer"]}'
    fi
    
    if [[ "$install_brave" =~ ^[Yy]$ ]]; then
        config_json+=',"brave-search":{"command":"npx","args":["-y","@modelcontextprotocol/server-brave-search"],"env":{"BRAVE_SEARCH_API_KEY":"your-brave-search-api-key-here"}}'
    fi
    
    if [[ "$install_git" =~ ^[Yy]$ ]]; then
        config_json+=',"git":{"command":"uvx","args":["mcp-server-git","--repository","/home/kiriti/alpha_projects/intelforge"]}'
    fi
    
    if [[ "$install_sqlite" =~ ^[Yy]$ ]]; then
        mkdir -p /home/kiriti/alpha_projects/intelforge/vault/data
        config_json+=',"sqlite":{"command":"npx","args":["-y","@modelcontextprotocol/server-sqlite","/home/kiriti/alpha_projects/intelforge/vault/data/scraped_data.db"]}'
    fi
    
    if [[ "$install_everything" =~ ^[Yy]$ ]]; then
        config_json+=',"everything":{"command":"npx","args":["-y","@modelcontextprotocol/server-everything"]}'
    fi
    
    config_json+='}}'
    
    # Save custom configuration
    echo "$config_json" | python3 -m json.tool > config/claude_desktop_custom.json
    success "Custom configuration created"
    
    # Install community servers if selected
    if [[ "$install_firecrawl" =~ ^[Yy]$ ]] || [[ "$install_playwright" =~ ^[Yy]$ ]]; then
        log "Installing selected community servers..."
        
        if [[ "$install_firecrawl" =~ ^[Yy]$ ]]; then
            log "Installing Firecrawl..."
            mkdir -p servers/scraping/firecrawl
            cd servers/scraping/firecrawl
            git clone https://github.com/mendableai/firecrawl-mcp-server.git 2>/dev/null || true
            cd ../../..
        fi
        
        if [[ "$install_playwright" =~ ^[Yy]$ ]]; then
            log "Installing Playwright..."
            mkdir -p servers/scraping/playwright
            cd servers/scraping/playwright
            git clone https://github.com/executeautomation/mcp-playwright.git 2>/dev/null || true
            cd ../../..
        fi
    fi
    
    success "Custom installation completed"
}

post_installation() {
    echo ""
    header "🔧 Post-Installation Setup"
    echo ""
    
    # Create master status script
    cat > scripts/status.sh << 'EOF'
#!/bin/bash
# Check status of all IntelForge MCP servers

echo "🔍 IntelForge MCP Server Status"
echo "==============================="

# Check Claude Code configuration
echo ""
echo "🤖 Claude Code:"
if [ -f "$HOME/.claude/config.json" ]; then
    echo "  Configuration: ✅ Exists"
    server_count=$(jq '.mcpServers | length' "$HOME/.claude/config.json" 2>/dev/null || echo "0")
    echo "  Configured servers: $server_count"
else
    echo "  Configuration: ❌ Not found"
fi

# Check official servers
echo ""
echo "📦 Official Servers (available via npx):"
servers=("filesystem" "memory" "puppeteer" "fetch" "brave-search" "sqlite" "everything")
for server in "${servers[@]}"; do
    echo -n "  @modelcontextprotocol/server-$server: "
    if npx -y "@modelcontextprotocol/server-$server" --help &>/dev/null; then
        echo "✅ Available"
    else
        echo "❌ Not available"
    fi
done

# Check Git server (uvx)
echo ""
echo "📝 Git Server:"
echo -n "  mcp-server-git: "
if uvx mcp-server-git --help &>/dev/null; then
    echo "✅ Available"
else
    echo "❌ Not available"
fi

# Check community servers
echo ""
echo "🌍 Community Servers:"
if [ -d "servers/scraping/firecrawl/firecrawl-mcp-server" ]; then
    echo "  Firecrawl: ✅ Installed"
else
    echo "  Firecrawl: ❌ Not installed"
fi

if [ -d "servers/scraping/playwright/mcp-playwright" ]; then
    echo "  Playwright: ✅ Installed"
else
    echo "  Playwright: ❌ Not installed"
fi

echo ""
echo "📁 Configuration Files:"
for config in config/*.json; do
    if [ -f "$config" ]; then
        echo "  $(basename "$config"): ✅ Available"
    fi
done
EOF
    
    chmod +x scripts/status.sh
    success "Status script created"
    
    # Create documentation
    cat > docs/installation.md << 'EOF'
# IntelForge MCP Servers Installation Guide

## Quick Start

1. **Install servers:**
   ```bash
   cd mcp_servers
   ./scripts/install.sh
   ```

2. **Configure Claude Code:**
   ```bash
   cp config/claude_desktop_complete.json ~/.claude/config.json
   ```

3. **Restart Claude Code**

4. **Verify installation:**
   ```bash
   ./scripts/status.sh
   ```

## Configuration Files

- `claude_desktop_complete.json` - Full server configuration
- `claude_desktop_scraping.json` - Scraping servers only
- `claude_desktop_productivity.json` - Productivity servers only
- `claude_desktop_custom.json` - Custom installation

## Troubleshooting

### Server not starting
- Check Claude Code configuration
- Verify server installation
- Check logs in `logs/` directory

### Permission denied
```bash
chmod +x scripts/*.sh
```

### API key issues
- Copy `.env.template` to `.env`
- Add your API keys
- Restart Claude Code
EOF
    
    success "Documentation created"
    
    # Final summary
    echo ""
    header "🎉 Installation Complete!"
    echo ""
    echo "📁 Directory structure created at: mcp_servers/"
    echo "📝 Configuration files available in: config/"
    echo "🔧 Management scripts available in: scripts/"
    echo "📖 Documentation available in: docs/"
    echo ""
    
    warning "Next Steps:"
    echo "1. Choose a configuration file from config/"
    echo "2. Copy it to ~/.claude/config.json"
    echo "3. Add any required API keys"
    echo "4. Restart Claude Code"
    echo "5. Run ./scripts/status.sh to verify"
    echo ""
    
    echo "📋 Available configurations:"
    for config in config/claude_desktop_*.json; do
        if [ -f "$config" ]; then
            echo "  - $(basename "$config")"
        fi
    done
    echo ""
    
    success "🚀 IntelForge MCP servers are ready to use!"
}

# Run main function
main "$@"