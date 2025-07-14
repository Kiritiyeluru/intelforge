#!/bin/bash
# install_productivity.sh - Install productivity and development MCP servers for IntelForge

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
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

log "🚀 Installing MCP Productivity Servers for IntelForge"
echo "===================================================="

# Create directory structure
mkdir -p servers/productivity/{github,git,sqlite,everything}
mkdir -p logs/productivity

# GitHub MCP (already active via remote)
log "🐙 Configuring GitHub MCP server..."
echo "GitHub MCP is already configured via remote HTTP endpoint"
echo "Endpoint: https://api.githubcopilot.com/mcp/"
success "GitHub MCP configured"

# Git MCP (local operations)
log "📝 Setting up Git MCP server..."
echo "Git MCP server will be available via uvx"
echo "Command: uvx mcp-server-git --repository /home/kiriti/alpha_projects/intelforge"
success "Git MCP configured"

# SQLite MCP (data storage)
log "🗄️ Setting up SQLite MCP server..."
mkdir -p /home/kiriti/alpha_projects/intelforge/vault/data
echo "SQLite MCP server will be available via npx"
echo "Database path: /home/kiriti/alpha_projects/intelforge/vault/data/scraped_data.db"
success "SQLite MCP configured"

# Everything MCP (reference server)
log "🔧 Setting up Everything MCP server..."
echo "Everything MCP server will be available via npx"
echo "Purpose: Reference implementation with prompts, resources, and tools"
success "Everything MCP configured"

# Create productivity configuration
cat > config/claude_desktop_productivity.json << EOF
{
  "mcpServers": {
    "github": {
      "transport": "http",
      "endpoint": "https://api.githubcopilot.com/mcp/"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/kiriti/alpha_projects/intelforge"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "/home/kiriti/alpha_projects/intelforge"]
    },
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "/home/kiriti/alpha_projects/intelforge/vault/data/scraped_data.db"]
    },
    "everything": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-everything"]
    }
  }
}
EOF

success "Productivity configuration created"

# Create combined configuration (scraping + productivity)
cat > config/claude_desktop_complete.json << EOF
{
  "mcpServers": {
    "github": {
      "transport": "http",
      "endpoint": "https://api.githubcopilot.com/mcp/"
    },
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
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "/home/kiriti/alpha_projects/intelforge"]
    },
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "/home/kiriti/alpha_projects/intelforge/vault/data/scraped_data.db"]
    }
  }
}
EOF

success "Complete configuration created"

log "📋 Productivity Installation Summary"
echo "===================================="
echo ""
echo "✅ Configured Productivity Servers:"
echo "   - GitHub MCP (remote HTTP)"
echo "   - Git MCP (local via uvx)"
echo "   - SQLite MCP (local database)"
echo "   - Everything MCP (reference server)"
echo ""
echo "📝 Configuration Files:"
echo "   - config/claude_desktop_productivity.json"
echo "   - config/claude_desktop_complete.json"
echo ""

success "🎉 IntelForge MCP productivity servers configured!"
echo ""
echo "📖 Use the complete configuration for full IntelForge capabilities"
echo "🔧 Copy: cp config/claude_desktop_complete.json ~/.claude/config.json"