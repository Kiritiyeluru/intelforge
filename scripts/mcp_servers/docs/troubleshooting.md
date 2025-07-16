# 🚨 IntelForge MCP Servers Troubleshooting Guide

## Common Issues and Solutions

### 🔧 Installation Issues

#### Server Installation Fails
```bash
# Check Node.js version
node --version  # Should be 18+

# Check Python version
python3 --version  # Should be 3.8+

# Update npm
npm update -g npm

# Clear npm cache
npm cache clean --force
```

#### Permission Denied
```bash
# Fix script permissions
chmod +x scripts/*.sh

# Fix npm permissions
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
```

#### Git Clone Fails
```bash
# Check SSH keys
ssh -T git@github.com

# Use HTTPS instead
git config --global url.https://github.com/.insteadOf git@github.com:
```

### 🤖 Claude Code Issues

#### MCP Servers Not Loading
1. **Check configuration location:**
   ```bash
   ls -la ~/.claude/config.json
   ```

2. **Validate JSON syntax:**
   ```bash
   python3 -m json.tool ~/.claude/config.json
   ```

3. **Restart Claude Code completely**

#### Server Command Not Found
```bash
# For npx servers
npx -y @modelcontextprotocol/server-puppeteer --help

# For uvx servers
uvx mcp-server-git --help

# Install missing tools
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Environment Variables Not Loading
```bash
# Check current environment
env | grep -E "(BRAVE|FIRECRAWL)"

# Add to shell profile
echo 'export BRAVE_SEARCH_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### 🕷️ Scraping Server Issues

#### Puppeteer Browser Launch Fails
```bash
# Install Chrome dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y chromium-browser

# For headless mode issues
export PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
```

#### Playwright Installation Issues
```bash
# Install Playwright browsers
npx playwright install

# Install system dependencies
npx playwright install-deps

# For Ubuntu/Debian
sudo apt-get install -y libwoff1 libopus0 libwebp6 libwebpdemux2 libenchant1c2a libgudev-1.0-0 libsecret-1-0 libhyphen0 libgdk-pixbuf2.0-0 libegl1 libnotify4 libxss1 libasound2 libatspi2.0-0 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libgtk-3-0
```

#### Firecrawl API Issues
```bash
# Check API key
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.firecrawl.dev/v0/health

# Test configuration
echo $FIRECRAWL_API_KEY
```

### 📊 Performance Issues

#### High Memory Usage
```bash
# Monitor MCP processes
ps aux | grep -E "(mcp|puppeteer|playwright)" | awk '{print $4, $11}'

# Set memory limits in Claude Code config
{
  "puppeteer": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
    "env": {
      "NODE_OPTIONS": "--max-old-space-size=512"
    }
  }
}
```

#### Slow Response Times
```bash
# Check network connectivity
ping -c 4 8.8.8.8

# Test server response
curl -I https://api.githubcopilot.com/mcp/

# Enable debug logging
DEBUG=mcp:* npx @modelcontextprotocol/server-puppeteer
```

#### Rate Limiting
```bash
# Configure delays in scraping settings
# Edit config/scraping_settings.yaml
scraping:
  general:
    concurrent_requests: 1  # Reduce from 3
    timeout: 45000          # Increase timeout
```

### 🔐 Authentication Issues

#### GitHub MCP Authentication Fails
```bash
# Check GitHub CLI auth
gh auth status

# Re-authenticate if needed
gh auth login

# Test API access
curl -H "Authorization: Bearer $(gh auth token)" https://api.github.com/user
```

#### API Key Validation
```bash
# Test Brave Search API
curl -H "X-Subscription-Token: YOUR_KEY" "https://api.search.brave.com/res/v1/web/search?q=test"

# Test other APIs
./scripts/test_api_keys.sh
```

### 📁 File System Issues

#### Database Permissions
```bash
# Fix SQLite database permissions
chmod 664 /home/kiriti/alpha_projects/intelforge/vault/data/scraped_data.db
chown $USER:$USER /home/kiriti/alpha_projects/intelforge/vault/data/scraped_data.db
```

#### Log Directory Issues
```bash
# Create missing log directories
mkdir -p logs/{scraping,productivity,errors,performance}

# Fix log permissions
chmod 755 logs/
chmod 644 logs/*/*.log
```

### 🔍 Debug Mode

#### Enable Debug Logging
```bash
# For all MCP servers
export DEBUG=mcp:*

# For specific servers
export DEBUG=mcp:puppeteer:*
export DEBUG=mcp:github:*

# Run with debug
DEBUG=mcp:* ./scripts/status.sh
```

#### Check Server Health
```bash
# Create comprehensive health check
cat > scripts/health_check.sh << 'EOF'
#!/bin/bash
echo "🏥 IntelForge MCP Health Check"
echo "============================="

# Check system resources
echo "💻 System Resources:"
echo "  Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "  Disk: $(df -h . | awk 'NR==2 {print $3 "/" $2}')"
echo "  Load: $(uptime | awk -F'load average:' '{print $2}')"
echo ""

# Check required tools
echo "🔧 Required Tools:"
for tool in node npm python3 git uvx; do
    if command -v $tool &>/dev/null; then
        version=$(if [ "$tool" = "uvx" ]; then uvx --version 2>/dev/null || echo "unknown"; else $tool --version 2>&1 | head -1; fi)
        echo "  $tool: ✅ $version"
    else
        echo "  $tool: ❌ Not found"
    fi
done
echo ""

# Check MCP servers
echo "📡 MCP Server Connectivity:"
echo "  GitHub API: $(curl -s -o /dev/null -w "%{http_code}" https://api.github.com/)"
echo "  Brave Search: $(curl -s -o /dev/null -w "%{http_code}" https://api.search.brave.com/)"
echo ""

# Check configuration
echo "⚙️ Configuration:"
if [ -f "$HOME/.claude/config.json" ]; then
    echo "  Claude config: ✅ Exists"
    server_count=$(jq '.mcpServers | length' "$HOME/.claude/config.json" 2>/dev/null || echo "0")
    echo "  Configured servers: $server_count"
else
    echo "  Claude config: ❌ Missing"
fi

# Check processes
echo ""
echo "🔄 Running Processes:"
ps aux | grep -E "(claude|mcp)" | grep -v grep | awk '{print "  " $11}' || echo "  No MCP processes found"
EOF

chmod +x scripts/health_check.sh
```

### 🆘 Emergency Recovery

#### Reset Configuration
```bash
# Backup current config
cp ~/.claude/config.json ~/.claude/config.json.backup

# Use minimal config
cp config/claude_desktop_productivity.json ~/.claude/config.json

# Restart Claude Code
```

#### Clean Installation
```bash
# Remove problematic servers
rm -rf servers/scraping/*/

# Reinstall from scratch
./scripts/install.sh
```

#### Factory Reset
```bash
# Complete reset (WARNING: Removes all MCP data)
rm -rf ~/.claude/config.json
rm -rf servers/
./scripts/install.sh
```

## 📞 Getting Help

### Log Analysis
```bash
# Check recent errors
tail -f logs/errors/*.log

# Search for specific issues
grep -r "ERROR\|FAIL" logs/

# Monitor real-time activity
watch -n 2 './scripts/status.sh'
```

### Report Issues
When reporting issues, include:

1. **System Info:**
   ```bash
   uname -a
   node --version
   python3 --version
   ```

2. **Error Logs:**
   ```bash
   tail -50 logs/errors/latest.log
   ```

3. **Configuration:**
   ```bash
   jq '.mcpServers | keys' ~/.claude/config.json
   ```

4. **Steps to Reproduce**

### Useful Commands
```bash
# Quick status check
./scripts/status.sh

# Full health check
./scripts/health_check.sh

# Test specific server
npx @modelcontextprotocol/server-puppeteer --help

# Monitor resources
htop -p $(pgrep -f mcp)

# Check network
ss -tulpn | grep -E "(3000|8000|9000)"
```

## 🔄 Maintenance

### Regular Tasks
```bash
# Update servers monthly
npm update -g @modelcontextprotocol/server-*

# Clean logs weekly
find logs/ -name "*.log" -mtime +7 -delete

# Backup configuration
cp ~/.claude/config.json config/backup-$(date +%Y%m%d).json
```

### Performance Optimization
```bash
# Optimize browser settings
export PUPPETEER_ARGS="--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage"

# Limit concurrent requests
# Edit config/scraping_settings.yaml
concurrent_requests: 2
```

---

**💡 Pro Tips:**
- Always test changes in a separate config file first
- Keep a working backup of your configuration
- Monitor resource usage regularly
- Update servers and dependencies monthly
- Use debug mode to troubleshoot specific issues

**🚨 Emergency Contact:** Check the main IntelForge documentation or create an issue in the project repository.
