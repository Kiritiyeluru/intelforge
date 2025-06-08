# MCP (Model Context Protocol) Setup Guide for Claude Code

## Overview
Model Context Protocol (MCP) allows Claude Code to connect to external tools and data sources, extending its capabilities with specialized servers for search, databases, APIs, and more.

## Official Documentation
- **Primary Guide**: https://docs.anthropic.com/en/docs/claude-code/tutorials#set-up-model-context-protocol-mcp
- **MCP Specification**: https://modelcontextprotocol.io/
- **Available MCP Servers**: https://github.com/topics/mcp-server

## Installation Commands

### Basic MCP Server Management
```bash
# List all configured MCP servers
claude mcp list

# Get details for a specific server
claude mcp get <server_name>

# Remove an MCP server
claude mcp remove <server_name>
```

### Adding MCP Servers

#### 1. MCP Stdio Server (most common)
```bash
claude mcp add <server_name> -e API_KEY=your_api_key -- /path/to/server arg1 arg2
```

#### 2. MCP SSE Server (Server-Sent Events)
```bash
claude mcp add --transport sse <server_name> <url>
```

### Server Scope Options
Use `-s` flag to specify server availability:
- `local`: Available only in current project directory
- `project`: Shared with team via `.mcp.json` file in project
- `user`: Available across all your projects (default)

Example:
```bash
claude mcp add -s local search-server -e API_KEY=123 -- /path/to/server
```

## Popular MCP Servers for Development

### Search and Research
1. **Perplexity Search MCP**
   - Repository: TBD (check https://github.com/topics/mcp-server)
   - Requires: Perplexity Pro API key
   - Use case: Real-time research and fact-checking

2. **Google Search MCP**
   - Repository: TBD
   - Requires: Google Custom Search API key
   - Use case: Web search integration

3. **Brave Search MCP**
   - Repository: TBD
   - Requires: Brave Search API key
   - Use case: Privacy-focused web search

### Database and Storage
4. **PostgreSQL MCP**
   - Use case: Database query and management

5. **SQLite MCP**
   - Use case: Local database operations

### Development Tools
6. **GitHub MCP**
   - Use case: Repository management, issue tracking

7. **Filesystem MCP**
   - Use case: Enhanced file operations

## Security Considerations

### Important Warning
> "Use third party MCP servers at your own risk" - Official documentation

**Risks:**
- Potential prompt injection attacks
- Unauthorized data access
- Malicious code execution

**Best Practices:**
1. Only install MCP servers from trusted sources
2. Review MCP server code before installation
3. Use environment variables for sensitive API keys
4. Regularly audit installed MCP servers
5. Remove unused MCP servers

## Configuration Files

### Project-Level Configuration
File: `.mcp.json` (in project root)
```json
{
  "servers": {
    "search-server": {
      "command": "/path/to/search-server",
      "args": ["arg1", "arg2"],
      "env": {
        "API_KEY": "your_api_key"
      }
    }
  }
}
```

### User-Level Configuration
Location: `~/.claude/mcp.json`

## Installed MCP Servers for IntelForge

### Currently Active Servers

#### 1. Perplexity Search MCP ✅ INSTALLED & CONFIGURED
- **Purpose**: Real-time web search and research validation
- **Repository**: https://github.com/ppl-ai/modelcontextprotocol
- **Installation Path**: `/home/kiriti/alpha_projects/intelforge/modelcontextprotocol/perplexity-ask/`
- **Configuration**: `perplexity_api_key` in `.env` file
- **Use Cases**: Tool validation, best practice verification, current trend analysis
- **Status**: Active and tested

#### 2. Financial Datasets MCP ✅ INSTALLED
- **Purpose**: Stock market data and financial analysis
- **Repository**: https://github.com/financial-datasets/mcp-server
- **Installation Path**: `/home/kiriti/alpha_projects/intelforge/financial-datasets-mcp/`
- **Use Cases**: Stock prices, financial statements, crypto data, market news
- **Tools**: get_income_statements, get_stock_price, get_crypto_prices, get_company_news
- **Status**: Installed (API key may be required for full functionality)

#### 3. SQLite MCP Server ✅ INSTALLED
- **Purpose**: Local database operations for storing extracted content
- **Repository**: https://github.com/modelcontextprotocol/servers-archived/tree/main/src/sqlite
- **Installation Path**: `/home/kiriti/alpha_projects/intelforge/mcp-servers/src/sqlite/`
- **Use Cases**: Store scraped Reddit posts, GitHub data, analysis results
- **Benefits**: Fast local storage, SQL queries, data persistence
- **Status**: Active

#### 4. Puppeteer MCP Server ✅ INSTALLED
- **Purpose**: Advanced web scraping and browser automation
- **Repository**: https://github.com/modelcontextprotocol/servers-archived/tree/main/src/puppeteer
- **Installation Path**: `/home/kiriti/alpha_projects/intelforge/mcp-servers/src/puppeteer/`
- **Use Cases**: JavaScript-heavy sites, dynamic content, complex scraping scenarios
- **Benefits**: Full browser automation, handles SPAs, can interact with pages
- **Status**: Active

#### 5. GitHub MCP Server ✅ INSTALLED & CONFIGURED
- **Purpose**: Repository mining and code analysis
- **Repository**: https://github.com/modelcontextprotocol/servers-archived/tree/main/src/github
- **Installation Path**: `/home/kiriti/alpha_projects/intelforge/mcp-servers/src/github/`
- **Use Cases**: Search repos, analyze code, extract documentation, find trading strategies
- **Configuration**: `github_pat` in `.env` file
- **Status**: Ready for use

#### 6. Brave Search MCP ✅ INSTALLED
- **Purpose**: Privacy-focused web search alternative
- **Repository**: https://github.com/modelcontextprotocol/servers-archived/tree/main/src/brave-search
- **Installation Path**: `/home/kiriti/alpha_projects/intelforge/mcp-servers/src/brave-search/`
- **Use Cases**: Web research, content discovery, search result analysis
- **Benefits**: Privacy-focused, complements Perplexity search
- **Status**: Active

### API Keys Configuration

The following API keys are configured in `.env` file for enhanced MCP functionality:

```bash
# Search and Research
perplexity_api_key=pplx-**** (Perplexity Pro subscription)
serper_api_key=1de2**** (Google Search API alternative)

# Web Scraping
firecrawl_api_key=fc-**** (Advanced web data extraction)
browserbase_project_id=fc59**** (Browser automation)
browserbase_api_key=bb_live_**** (Browser automation)

# Development
github_pat=ghp_**** (GitHub Personal Access Token)
```

**Security Notes:**
- All API keys are gitignored in `.env` file
- Keys are partially redacted for security
- Backup keys securely outside repository
- Rotate keys periodically for security

## Installation Workflow for IntelForge

### Step 1: Research Available MCP Servers
```bash
# Official MCP servers repository
# Visit: https://github.com/modelcontextprotocol/servers
# Check: https://github.com/topics/mcp-server
```

### Step 2: Install Required Dependencies
Most MCP servers require Node.js or Python:
```bash
# Check if Node.js is installed
node --version
npm --version

# Check if Python is installed
python3 --version
pip3 --version
```

### Step 3: Install Specific MCP Server
Example for a hypothetical search MCP:
```bash
# Install via npm (if Node.js-based)
npm install -g @mcp/search-server

# Or install via pip (if Python-based)
pip install mcp-search-server
```

### Step 4: Configure in Claude Code
```bash
# Add the MCP server to Claude Code
claude mcp add search-mcp -e API_KEY=your_key -- mcp-search-server --config config.json
```

### Step 5: Verify Installation
```bash
# List servers to confirm installation
claude mcp list

# Test server functionality (if available)
claude mcp get search-mcp
```

## Troubleshooting

### Common Issues

#### MCP Server Not Found
**Problem**: `claude mcp add` fails with "server not found"
**Solution**: 
- Verify server is installed and in PATH
- Check the exact path to the server executable
- Ensure all dependencies are installed

#### Authentication Errors
**Problem**: MCP server fails to authenticate with external APIs
**Solution**:
- Verify API keys are correct and active
- Check API key permissions and quotas
- Ensure environment variables are properly set

#### Permission Errors
**Problem**: Claude Code cannot access MCP server
**Solution**:
- Check file permissions on server executable
- Ensure Claude Code has necessary system permissions
- Run with appropriate user privileges

### Debugging Commands
```bash
# Check Claude Code logs for MCP errors
# (Location varies by system)
tail -f ~/.claude/logs/claude.log

# Test MCP server manually (if supported)
/path/to/mcp-server --test

# Verify environment variables
env | grep API_KEY
```

## Use Cases for IntelForge

### Research Enhancement
- Real-time tool discovery during development
- Validation of technical decisions
- Market research for trading strategies
- Academic paper searches

### Development Workflow
- Enhanced debugging capabilities
- External API integration testing
- Database query assistance
- Code repository analysis

### Content Validation
- Fact-checking extracted information
- Cross-referencing trading strategies
- Verifying code examples and patterns

## Best Practices for IntelForge

1. **Start Simple**: Begin with one search MCP server
2. **Document Usage**: Add MCP usage to session checklists
3. **Security First**: Never commit API keys to repository
4. **Test Thoroughly**: Verify MCP functionality before relying on it
5. **Monitor Usage**: Track API quotas and costs
6. **Regular Updates**: Keep MCP servers updated for security

## Integration with IntelForge Workflow

### Session Checklist Addition
Add to `session_checklist.md`:
- [ ] Check if MCP servers are needed for current task
- [ ] Verify MCP server status before complex research
- [ ] Document any new MCP findings in learning_log.md

### Configuration Management
Add to `docs/config_changelog.md`:
- Track MCP server installations and removals
- Document API key rotations
- Note performance impacts

## Future Considerations

- Evaluate MCP server performance impact
- Consider developing custom MCP servers for IntelForge-specific needs
- Monitor MCP ecosystem for new research-focused servers
- Assess cost-benefit of premium MCP services

---

**Last Updated**: 2025-01-06  
**Next Review**: When adding first MCP server to IntelForge