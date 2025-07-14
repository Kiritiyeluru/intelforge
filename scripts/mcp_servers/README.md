# 🔌 IntelForge MCP Servers

**Model Context Protocol (MCP) servers for enhancing IntelForge's AI-powered knowledge extraction capabilities.**

## 📁 Directory Structure

```
mcp_servers/
├── README.md                    # This file - comprehensive MCP server guide
├── config/                      # MCP server configurations
│   ├── claude_desktop.json     # Claude Code configuration
│   ├── server_configs.yaml     # Server-specific settings
│   └── recommended.json        # Recommended server configurations
├── scripts/                     # Installation and management scripts
│   ├── install.sh              # Master installation script
│   ├── install_scraping.sh     # Scraping-focused servers
│   ├── install_productivity.sh # Productivity servers
│   ├── start_servers.sh        # Start MCP servers
│   └── stop_servers.sh         # Stop MCP servers
├── servers/                     # MCP server implementations
│   ├── scraping/               # Web scraping & crawling servers
│   ├── productivity/           # Development & productivity servers
│   ├── data/                   # Data processing servers
│   └── community/              # Community-contributed servers
├── logs/                       # Server logs and debugging
└── docs/                       # Documentation and guides
    ├── installation.md         # Installation instructions
    ├── configuration.md        # Configuration guide
    └── troubleshooting.md      # Common issues and solutions
```

## 🎯 Server Categories

### 🕷️ Scraping & Crawling Servers

**Comprehensive web data extraction infrastructure for IntelForge.**

#### 🏭 Enterprise-Grade Servers
| Server | Transport | Status | Use Case |
|--------|-----------|---------|----------|
| **[AgentQL](#agentql)** | Local/git | 🔥 Advanced | Structured data from unstructured web |
| **[Apify](#apify)** | Local/git | 💼 Enterprise | 3,000+ pre-built scraping tools |
| **[Browserbase](#browserbase)** | Remote/API | ☁️ Cloud | Cloud browser automation |
| **[Firecrawl](#firecrawl)** | Local/git | ⭐ Premium | Production-grade scraping |
| **[Oxylabs](#oxylabs)** | Remote/API | 💼 Enterprise | Professional proxy scraping |

#### 🔧 Core Automation Servers  
| Server | Transport | Status | Use Case |
|--------|-----------|---------|----------|
| **[Puppeteer](#puppeteer)** | Local/npx | ✅ Recommended | JavaScript-heavy trading sites |
| **[Playwright](#playwright)** | Local/git | ✅ Recommended | Modern browser automation |
| **[Hyperbrowser](#hyperbrowser)** | Remote/API | 🚀 Advanced | Scalable browser automation |

#### 🛡️ Anti-Detection Servers
| Server | Transport | Status | Use Case |
|--------|-----------|---------|----------|
| **[Rquest](#rquest)** | Local/git | 🔥 Advanced | TLS fingerprint bypass |
| **[Scrapling Fetch](#scrapling-fetch)** | Local/git | 🔥 Advanced | Bot-protected sites |
| **[RAG Web Browser](#rag-web-browser)** | Local/git | 📄 Specialized | Web search + Markdown conversion |

#### 🌐 Basic & Utility Servers
| Server | Transport | Status | Use Case |
|--------|-----------|---------|----------|
| **[Fetch](#fetch)** | Local/npx | ✅ Basic | Simple HTTP requests |
| **[ScreenshotOne](#screenshotone)** | Remote/API | 📸 Utility | Website screenshots |

### 📄 Content Processing & AI-Ready Servers

**Essential for converting scraped content to AI-readable, chunked format.**

#### 🔄 Document Conversion & Chunking
| Server | Transport | Status | Use Case |
|--------|-----------|---------|----------|
| **[Vectorize](#vectorize)** | Local/git | ⭐ Premium | Anything-to-Markdown + chunking |
| **[Pandoc](#pandoc)** | Local/git | ✅ Recommended | Universal document conversion |
| **[Markdownify](#markdownify)** | Local/git | ✅ Recommended | Multi-format to Markdown |
| **[Unstructured](#unstructured)** | Local/git | 💼 Enterprise | Enterprise document processing |

#### 🧠 RAG & Knowledge Management  
| Server | Transport | Status | Use Case |
|--------|-----------|---------|----------|
| **[Needle](#needle)** | Local/git | ⭐ Premium | Production-ready RAG |
| **[Chroma](#chroma)** | Local/git | 🔥 Advanced | Vector database + embeddings |
| **[Basic Memory](#basic-memory)** | Local/git | ✅ Recommended | Semantic graph from Markdown |
| **[Inkeep](#inkeep)** | Remote/API | 🤖 AI | RAG search over content |

### 📊 Data Processing Servers

**For organizing and analyzing scraped content.**

| Server | Transport | Status | Use Case |
|--------|-----------|---------|----------|
| **[SQLite](#sqlite)** | Local/npx | ✅ Recommended | Structured data storage |
| **[Memory](#memory)** | Local/npx | ✅ Active | Knowledge graph management |
| **[Filesystem](#filesystem)** | Local/npx | ✅ Active | File operations |
| **[PostgreSQL](#postgresql)** | Local/npx | 🔧 Optional | Advanced database operations |

### 🚀 Productivity Servers

**For development and workflow enhancement.**

| Server | Transport | Status | Use Case |
|--------|-----------|---------|----------|
| **[GitHub](#github)** | Remote/HTTP | ✅ Active | Repository management |
| **[Git](#git)** | Local/uvx | 🔧 Optional | Local git operations |
| **[Everything](#everything)** | Local/npx | 🔧 Optional | Reference/testing |

### 🔍 Search & Discovery Servers

**AI-powered content discovery and research infrastructure.**

#### 🤖 AI-Powered Search
| Server | Transport | Status | Use Case |
|--------|-----------|---------|----------|
| **[Exa](#exa)** | Remote/API | 🤖 AI | Search engine made for AIs |
| **[Tavily](#tavily)** | Remote/API | ⭐ Premium | AI agent search + extract |
| **[Perplexity](#perplexity)** | Remote/API | 🤖 AI | Real-time web research |

#### 🔍 Traditional Search
| Server | Transport | Status | Use Case |
|--------|-----------|---------|----------|
| **[Brave Search](#brave-search)** | Local/npx | ✅ Recommended | Privacy-focused web search |
| **[Kagi Search](#kagi-search)** | Remote/API | 🔒 Privacy | Premium privacy search |
| **[SearXNG](#searxng)** | Local/docker | 🔒 Privacy | Self-hosted metasearch |

#### 📊 Specialized Search
| Server | Transport | Status | Use Case |
|--------|-----------|---------|----------|
| **[Search1API](#search1api)** | Remote/API | 🔧 Utility | Unified search, crawling, sitemaps |

## 🚀 Quick Start

### 1. Install Essential Servers

```bash
# Navigate to MCP servers directory
cd /home/kiriti/alpha_projects/intelforge/mcp_servers

# Install scraping essentials
./scripts/install_scraping.sh

# Install content processing (AI-ready chunking)
./scripts/install_content_processing.sh

# Install productivity tools
./scripts/install_productivity.sh
```

### 2. Configure Claude Code

```bash
# Copy recommended configuration
cp config/recommended.json ~/.claude/config.json

# Or manually add to Claude Code settings
```

### 3. Start Servers

```bash
# Start all configured servers
./scripts/start_servers.sh

# Or start specific category
./scripts/start_servers.sh scraping
```

## 📋 Detailed Server Specifications

### 🕷️ Scraping Servers

#### Puppeteer
```bash
# Installation
npx @modelcontextprotocol/server-puppeteer

# Configuration
{
  "puppeteer": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
  }
}
```

**Features:**
- ✅ JavaScript execution
- ✅ Dynamic content rendering
- ✅ Screenshot capabilities
- ✅ Form interaction
- ⚡ Medium performance

**Best for:** Financial sites, SPAs, dynamic trading platforms

#### Firecrawl
```bash
# Installation
git clone https://github.com/mendableai/firecrawl-mcp-server
cd firecrawl-mcp-server && npm install

# Configuration
{
  "firecrawl": {
    "command": "node",
    "args": ["path/to/firecrawl-mcp-server/index.js"],
    "env": {
      "FIRECRAWL_API_KEY": "your-api-key"
    }
  }
}
```

**Features:**
- ⭐ Production-grade reliability
- ✅ Anti-detection measures
- ✅ PDF processing
- ✅ Rate limiting
- ✅ Structured data extraction
- 🚀 High performance

**Best for:** Large-scale scraping, enterprise sites, document processing

#### Playwright
```bash
# Installation
git clone https://github.com/executeautomation/mcp-playwright
cd mcp-playwright && npm install

# Configuration
{
  "playwright": {
    "command": "node",
    "args": ["path/to/mcp-playwright/index.js"]
  }
}
```

**Features:**
- 🔥 Modern browser automation
- ✅ Multi-browser support (Chrome, Firefox, Safari)
- ✅ Mobile emulation
- ✅ Network interception
- ✅ Advanced debugging
- ⚡ High performance

**Best for:** Modern web apps, testing, complex interactions

#### Brave Search
```bash
# Installation
npx @modelcontextprotocol/server-brave-search

# Configuration
{
  "brave-search": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
    "env": {
      "BRAVE_SEARCH_API_KEY": "your-api-key"
    }
  }
}
```

**Features:**
- 🔍 Web search integration
- ✅ Real-time results
- ✅ Privacy-focused
- ✅ Multiple result types
- ⚡ Fast response

**Best for:** Content discovery, research, trend analysis

#### AgentQL
```bash
# Installation
git clone https://github.com/tinyfish-io/agentql-mcp
cd agentql-mcp && npm install

# Configuration
{
  "agentql": {
    "command": "node",
    "args": ["path/to/agentql-mcp/index.js"],
    "env": {
      "AGENTQL_API_KEY": "your-api-key"
    }
  }
}
```

**Features:**
- 🧠 AI-powered data extraction
- ✅ Natural language queries
- ✅ Structured data output
- ✅ Dynamic web content handling
- 🚀 High accuracy

**Best for:** Complex data extraction, AI-driven scraping, structured output

#### Apify
```bash
# Installation
git clone https://github.com/apify/actors-mcp-server
cd actors-mcp-server && npm install

# Configuration
{
  "apify": {
    "command": "node",
    "args": ["path/to/actors-mcp-server/index.js"],
    "env": {
      "APIFY_TOKEN": "your-apify-token"
    }
  }
}
```

**Features:**
- 🏭 3,000+ pre-built scrapers
- ✅ Social media scraping
- ✅ E-commerce data extraction
- ✅ Search engine scraping
- ✅ Map data extraction
- ✅ Cloud-based processing

**Best for:** Large-scale scraping, social media, e-commerce, enterprise data

#### Browserbase
```bash
# Configuration (API-based)
{
  "browserbase": {
    "command": "node",
    "args": ["path/to/browserbase-mcp/index.js"],
    "env": {
      "BROWSERBASE_API_KEY": "your-api-key",
      "BROWSERBASE_PROJECT_ID": "your-project-id"
    }
  }
}
```

**Features:**
- ☁️ Cloud browser instances
- ✅ Scalable automation
- ✅ No infrastructure management
- ✅ Advanced debugging
- ✅ Session persistence
- 🚀 Enterprise reliability

**Best for:** Cloud automation, scalable scraping, enterprise deployments

#### Hyperbrowser
```bash
# Installation
git clone https://github.com/hyperbrowserai/mcp
cd mcp && npm install

# Configuration
{
  "hyperbrowser": {
    "command": "node",
    "args": ["path/to/hyperbrowser-mcp/index.js"],
    "env": {
      "HYPERBROWSER_API_KEY": "your-api-key"
    }
  }
}
```

**Features:**
- 🚀 Next-generation platform
- ✅ Effortless browser automation
- ✅ Scalable architecture
- ✅ AI agent optimization
- ✅ Advanced anti-detection

**Best for:** Modern automation, AI agents, scalable workflows

#### Rquest
```bash
# Installation
git clone https://github.com/xxxbrian/mcp-rquest
cd mcp-rquest && pip install -r requirements.txt

# Configuration
{
  "rquest": {
    "command": "python",
    "args": ["path/to/mcp-rquest/server.py"]
  }
}
```

**Features:**
- 🛡️ Realistic browser fingerprints
- ✅ TLS/JA3/JA4 fingerprinting
- ✅ Anti-bot bypass
- ✅ Proxy support
- ✅ High success rate

**Best for:** Bot-protected sites, anti-detection, security research

#### RAG Web Browser
```bash
# Installation
git clone https://github.com/apify/mcp-server-rag-web-browser
cd mcp-server-rag-web-browser && npm install

# Configuration
{
  "rag-web-browser": {
    "command": "node",
    "args": ["path/to/rag-web-browser/index.js"],
    "env": {
      "APIFY_TOKEN": "your-apify-token"
    }
  }
}
```

**Features:**
- 📄 Web search and scraping
- ✅ Markdown output
- ✅ Content summarization
- ✅ URL processing
- 🤖 RAG-optimized

**Best for:** Content research, document processing, RAG workflows

#### ScreenshotOne
```bash
# Configuration (API-based)
{
  "screenshotone": {
    "command": "node",
    "args": ["path/to/screenshotone-mcp/index.js"],
    "env": {
      "SCREENSHOTONE_API_KEY": "your-api-key"
    }
  }
}
```

**Features:**
- 📸 Website screenshots
- ✅ Multiple formats
- ✅ Custom dimensions
- ✅ Full page capture
- ⚡ Fast rendering

**Best for:** Visual documentation, website monitoring, UI testing

### 📊 Data Servers

#### SQLite
```bash
# Installation
npx @modelcontextprotocol/server-sqlite

# Configuration
{
  "sqlite": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/database.db"]
  }
}
```

**Features:**
- 🗄️ Local database storage
- ✅ SQL query interface
- ✅ ACID compliance
- ✅ Business intelligence
- ⚡ Fast queries

**Best for:** Structured data storage, analytics, reporting

#### Memory
```bash
# Installation (already active)
npx @modelcontextprotocol/server-memory

# Configuration
{
  "memory": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
  }
}
```

**Features:**
- 🧠 Knowledge graph storage
- ✅ Persistent memory
- ✅ Relationship mapping
- ✅ Semantic search
- 📚 Cross-session continuity

**Best for:** Knowledge management, relationship tracking, AI memory

### 🔍 Search & Discovery Servers

#### Exa
```bash
# Configuration (API-based)
{
  "exa": {
    "command": "node",
    "args": ["path/to/exa-mcp-server/index.js"],
    "env": {
      "EXA_API_KEY": "your-exa-api-key"
    }
  }
}
```

**Features:**
- 🤖 AI-optimized search
- ✅ Real-time web data
- ✅ Semantic understanding
- ✅ Developer-friendly API
- 🚀 Fast response times

**Best for:** AI agents, semantic search, real-time research

#### Tavily
```bash
# Installation
git clone https://github.com/tavily-ai/tavily-mcp
cd tavily-mcp && npm install

# Configuration
{
  "tavily": {
    "command": "node",
    "args": ["path/to/tavily-mcp/index.js"],
    "env": {
      "TAVILY_API_KEY": "your-tavily-api-key"
    }
  }
}
```

**Features:**
- 🔍 AI agent search engine
- ✅ Search + extract capabilities
- ✅ Real-time results
- ✅ Content summarization
- 🤖 Agent-optimized

**Best for:** AI agents, comprehensive research, content extraction

#### Kagi Search
```bash
# Installation
git clone https://github.com/kagisearch/kagimcp
cd kagimcp && npm install

# Configuration
{
  "kagi-search": {
    "command": "node",
    "args": ["path/to/kagimcp/index.js"],
    "env": {
      "KAGI_API_KEY": "your-kagi-api-key"
    }
  }
}
```

**Features:**
- 🔒 Privacy-focused search
- ✅ Ad-free results
- ✅ High-quality ranking
- ✅ Fast response
- 💰 Premium service

**Best for:** Privacy-conscious research, high-quality results, professional use

#### SearXNG
```bash
# Installation (Docker-based)
docker run -d --name searxng \
  -p 8080:8080 \
  searxng/searxng

# Configuration
{
  "searxng": {
    "command": "node",
    "args": ["path/to/searxng-mcp/index.js"],
    "env": {
      "SEARXNG_URL": "http://localhost:8080"
    }
  }
}
```

**Features:**
- 🔒 Self-hosted metasearch
- ✅ Privacy protection
- ✅ No tracking
- ✅ Multiple search engines
- 🆓 Open source

**Best for:** Privacy, self-hosting, aggregated search results

#### Perplexity
```bash
# Installation
git clone https://github.com/ppl-ai/modelcontextprotocol
cd modelcontextprotocol && npm install

# Configuration
{
  "perplexity": {
    "command": "node",
    "args": ["path/to/perplexity-mcp/index.js"],
    "env": {
      "PERPLEXITY_API_KEY": "your-perplexity-api-key"
    }
  }
}
```

**Features:**
- 🤖 AI-powered research
- ✅ Real-time web data
- ✅ Source citations
- ✅ Conversational interface
- 📚 Knowledge synthesis

**Best for:** Real-time research, cited information, conversational queries

#### Search1API
```bash
# Configuration (API-based)
{
  "search1api": {
    "command": "node",
    "args": ["path/to/search1api-mcp/index.js"],
    "env": {
      "SEARCH1API_KEY": "your-api-key"
    }
  }
}
```

**Features:**
- 🔗 Unified API
- ✅ Search capabilities
- ✅ Web crawling
- ✅ Sitemap generation
- ⚡ Single interface

**Best for:** Unified search operations, API consolidation, development efficiency

### 📄 Content Processing & AI-Ready Servers

#### Vectorize
```bash
# Installation
git clone https://github.com/vectorize-io/vectorize-mcp-server
cd vectorize-mcp-server && npm install

# Configuration
{
  "vectorize": {
    "command": "node",
    "args": ["path/to/vectorize-mcp-server/index.js"],
    "env": {
      "VECTORIZE_API_KEY": "your-vectorize-api-key"
    }
  }
}
```

**Features:**
- ⭐ Advanced retrieval capabilities
- 📄 Anything-to-Markdown file extraction
- ✂️ Automatic text chunking
- 🔍 Private Deep Research
- 🤖 AI-optimized processing

**Best for:** Automatic content chunking, document conversion, RAG preparation

#### Pandoc
```bash
# Installation
git clone https://github.com/vivekVells/mcp-pandoc
cd mcp-pandoc && npm install

# Configuration
{
  "pandoc": {
    "command": "node",
    "args": ["path/to/mcp-pandoc/index.js"]
  }
}
```

**Features:**
- 🔄 Universal document conversion
- 📋 Markdown, HTML, PDF, DOCX, CSV support
- ⚡ Industry-standard Pandoc engine
- ✅ High-quality conversions
- 🛠️ Extensive format support

**Best for:** Universal document conversion, format standardization

#### Markdownify
```bash
# Installation
git clone https://github.com/zcaceres/mcp-markdownify-server
cd mcp-markdownify-server && npm install

# Configuration
{
  "markdownify": {
    "command": "node",
    "args": ["path/to/markdownify-server/index.js"]
  }
}
```

**Features:**
- 📄 Convert almost anything to Markdown
- 🎥 PPTX, HTML, PDF, YouTube Transcripts
- 🤖 AI-optimized Markdown output
- ✅ Clean, structured conversion
- ⚡ Fast processing

**Best for:** Markdown standardization, YouTube/video content processing

#### Unstructured
```bash
# Installation
git clone https://github.com/Unstructured-IO/UNS-MCP
cd UNS-MCP && pip install -r requirements.txt

# Configuration
{
  "unstructured": {
    "command": "python",
    "args": ["path/to/unstructured-mcp/server.py"],
    "env": {
      "UNSTRUCTURED_API_KEY": "your-unstructured-api-key"
    }
  }
}
```

**Features:**
- 🏭 Enterprise-grade document processing
- 📊 Unstructured data workflows
- ✂️ Advanced chunking strategies
- 🔧 Customizable processing pipelines
- 🚀 Production-ready scaling

**Best for:** Enterprise document processing, complex data workflows

#### Needle
```bash
# Installation
git clone https://github.com/needle-ai/needle-mcp
cd needle-mcp && npm install

# Configuration
{
  "needle": {
    "command": "node",
    "args": ["path/to/needle-mcp/index.js"],
    "env": {
      "NEEDLE_API_KEY": "your-needle-api-key"
    }
  }
}
```

**Features:**
- 🎯 Production-ready RAG out of the box
- 🔍 Search and retrieve from your documents
- 📚 Document indexing and management
- 🤖 AI-optimized retrieval
- ⚡ Fast semantic search

**Best for:** Production RAG, document search, knowledge retrieval

#### Chroma
```bash
# Installation
git clone https://github.com/chroma-core/chroma-mcp
cd chroma-mcp && pip install -r requirements.txt

# Configuration
{
  "chroma": {
    "command": "python",
    "args": ["path/to/chroma-mcp/server.py"]
  }
}
```

**Features:**
- 🧠 Embeddings and vector search
- 📄 Document storage
- 🔍 Full-text search capabilities
- 🤖 AI application database
- 📊 Semantic similarity search

**Best for:** Vector database, embeddings storage, semantic search

#### Basic Memory
```bash
# Installation
git clone https://github.com/basicmachines-co/basic-memory
cd basic-memory && npm install

# Configuration
{
  "basic-memory": {
    "command": "node",
    "args": ["path/to/basic-memory/index.js"]
  }
}
```

**Features:**
- 🧠 Local-first knowledge management
- 📊 Semantic graph from Markdown files
- 💾 Persistent memory across conversations
- 🔗 Relationship mapping
- 📚 Cross-session continuity

**Best for:** Knowledge graphs, relationship tracking, persistent AI memory

#### Inkeep
```bash
# Configuration (API-based)
{
  "inkeep": {
    "command": "node",
    "args": ["path/to/inkeep-mcp/index.js"],
    "env": {
      "INKEEP_API_KEY": "your-inkeep-api-key"
    }
  }
}
```

**Features:**
- 🔍 RAG search over your content
- 🤖 AI-powered content retrieval
- 📚 Knowledge base integration
- ⚡ Fast semantic search
- 🎯 Precise content matching

**Best for:** Content search, knowledge base queries, RAG-powered retrieval

## 🔧 Installation Scripts

### All-in-One Installation

```bash
#!/bin/bash
# install.sh - Master installation script

echo "🚀 Installing IntelForge MCP Servers..."

# Create directories
mkdir -p servers/{scraping,productivity,data,community}
mkdir -p logs config

# Install essential scraping servers
echo "📥 Installing scraping servers..."
./scripts/install_scraping.sh

# Install productivity servers
echo "⚡ Installing productivity servers..."
./scripts/install_productivity.sh

# Install content processing servers
echo "📄 Installing content processing servers..."
./scripts/install_content_processing.sh

echo "✅ Installation complete!"
echo "📖 Next steps:"
echo "1. Configure Claude Code: cp config/recommended.json ~/.claude/config.json"
echo "2. Start servers: ./scripts/start_servers.sh"
echo "3. Check status: ./scripts/status.sh"
```

### Scraping-Focused Installation

```bash
#!/bin/bash
# install_scraping.sh - Install scraping and crawling servers

echo "🕷️ Installing scraping servers for IntelForge..."

# Official servers via npx
echo "📦 Installing official servers..."
echo "✅ Puppeteer - JavaScript browser automation"
echo "✅ Fetch - Basic HTTP requests"
echo "✅ Brave Search - Web search integration"

# Community servers via git
echo "📥 Installing community servers..."

# Firecrawl (production scraping)
if [ ! -d "servers/scraping/firecrawl-mcp-server" ]; then
    echo "📥 Installing Firecrawl..."
    cd servers/scraping
    git clone https://github.com/mendableai/firecrawl-mcp-server
    cd firecrawl-mcp-server && npm install
    cd ../../..
fi

# Playwright (modern automation)
if [ ! -d "servers/scraping/mcp-playwright" ]; then
    echo "📥 Installing Playwright..."
    cd servers/scraping
    git clone https://github.com/executeautomation/mcp-playwright
    cd mcp-playwright && npm install
    cd ../../..
fi

# Scrapling Fetch (anti-bot protection)
if [ ! -d "servers/scraping/scrapling-fetch-mcp" ]; then
    echo "📥 Installing Scrapling Fetch..."
    cd servers/scraping
    git clone https://github.com/cyberchitta/scrapling-fetch-mcp
    cd scrapling-fetch-mcp && pip install -r requirements.txt
    cd ../../..
fi

echo "✅ Scraping servers installed!"
```

### Content Processing Installation

```bash
#!/bin/bash
# install_content_processing.sh - Install content processing and AI-ready servers

echo "📄 Installing content processing servers for IntelForge..."

# Document conversion servers
echo "📥 Installing document conversion servers..."

# Vectorize (chunking + conversion)
if [ ! -d "servers/data/vectorize-mcp-server" ]; then
    echo "📥 Installing Vectorize..."
    cd servers/data
    git clone https://github.com/vectorize-io/vectorize-mcp-server
    cd vectorize-mcp-server && npm install
    cd ../../..
fi

# Pandoc (universal conversion)
if [ ! -d "servers/data/mcp-pandoc" ]; then
    echo "📥 Installing Pandoc..."
    cd servers/data
    git clone https://github.com/vivekVells/mcp-pandoc
    cd mcp-pandoc && npm install
    cd ../../..
fi

# Markdownify (markdown conversion)
if [ ! -d "servers/data/mcp-markdownify-server" ]; then
    echo "📥 Installing Markdownify..."
    cd servers/data
    git clone https://github.com/zcaceres/mcp-markdownify-server
    cd mcp-markdownify-server && npm install
    cd ../../..
fi

# Unstructured (enterprise processing)
if [ ! -d "servers/data/UNS-MCP" ]; then
    echo "📥 Installing Unstructured..."
    cd servers/data
    git clone https://github.com/Unstructured-IO/UNS-MCP
    cd UNS-MCP && pip install -r requirements.txt
    cd ../../..
fi

# RAG & knowledge management servers
echo "🧠 Installing RAG and knowledge management servers..."

# Needle (production RAG)
if [ ! -d "servers/data/needle-mcp" ]; then
    echo "📥 Installing Needle..."
    cd servers/data
    git clone https://github.com/needle-ai/needle-mcp
    cd needle-mcp && npm install
    cd ../../..
fi

# Chroma (vector database)
if [ ! -d "servers/data/chroma-mcp" ]; then
    echo "📥 Installing Chroma..."
    cd servers/data
    git clone https://github.com/chroma-core/chroma-mcp
    cd chroma-mcp && pip install -r requirements.txt
    cd ../../..
fi

# Basic Memory (knowledge graphs)
if [ ! -d "servers/data/basic-memory" ]; then
    echo "📥 Installing Basic Memory..."
    cd servers/data
    git clone https://github.com/basicmachines-co/basic-memory
    cd basic-memory && npm install
    cd ../../..
fi

echo "✅ Content processing servers installed!"
echo "📖 Key capabilities added:"
echo "  🔄 Document conversion: Vectorize, Pandoc, Markdownify"
echo "  🧠 RAG processing: Needle, Chroma, Basic Memory"
echo "  📊 Enterprise workflows: Unstructured"
echo "🎯 Perfect for: Article chunking, AI-ready content processing"
```

## 📝 Configuration Templates

### Claude Code Configuration

#### Essential Configuration
```json
{
  "mcpServers": {
    "github": {
      "command": "claude",
      "args": ["mcp", "add", "--transport", "http", "github", "https://api.githubcopilot.com/mcp/"]
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
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "/home/kiriti/alpha_projects/intelforge/vault/data/scraped_data.db"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_SEARCH_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Enterprise Scraping Configuration
```json
{
  "mcpServers": {
    "agentql": {
      "command": "node",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/scraping/agentql-mcp/index.js"],
      "env": {
        "AGENTQL_API_KEY": "your-agentql-api-key"
      }
    },
    "apify": {
      "command": "node",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/scraping/actors-mcp-server/index.js"],
      "env": {
        "APIFY_TOKEN": "your-apify-token"
      }
    },
    "firecrawl": {
      "command": "node",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/scraping/firecrawl-mcp-server/index.js"],
      "env": {
        "FIRECRAWL_API_KEY": "your-firecrawl-api-key"
      }
    },
    "playwright": {
      "command": "node",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/scraping/mcp-playwright/index.js"]
    },
    "rquest": {
      "command": "python",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/scraping/mcp-rquest/server.py"]
    }
  }
}
```

#### AI Search Configuration
```json
{
  "mcpServers": {
    "exa": {
      "command": "node",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/community/exa-mcp-server/index.js"],
      "env": {
        "EXA_API_KEY": "your-exa-api-key"
      }
    },
    "tavily": {
      "command": "node",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/community/tavily-mcp/index.js"],
      "env": {
        "TAVILY_API_KEY": "your-tavily-api-key"
      }
    },
    "perplexity": {
      "command": "node",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/community/perplexity-mcp/index.js"],
      "env": {
        "PERPLEXITY_API_KEY": "your-perplexity-api-key"
      }
    },
    "kagi-search": {
      "command": "node",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/community/kagimcp/index.js"],
      "env": {
        "KAGI_API_KEY": "your-kagi-api-key"
      }
    }
  }
}
```

#### Content Processing Configuration
```json
{
  "mcpServers": {
    "vectorize": {
      "command": "node",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/data/vectorize-mcp-server/index.js"],
      "env": {
        "VECTORIZE_API_KEY": "your-vectorize-api-key"
      }
    },
    "pandoc": {
      "command": "node",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/data/mcp-pandoc/index.js"]
    },
    "markdownify": {
      "command": "node",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/data/mcp-markdownify-server/index.js"]
    },
    "unstructured": {
      "command": "python",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/data/UNS-MCP/server.py"],
      "env": {
        "UNSTRUCTURED_API_KEY": "your-unstructured-api-key"
      }
    },
    "needle": {
      "command": "node",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/data/needle-mcp/index.js"],
      "env": {
        "NEEDLE_API_KEY": "your-needle-api-key"
      }
    },
    "chroma": {
      "command": "python",
      "args": ["/home/kiriti/alpha_projects/intelforge/mcp_servers/servers/data/chroma-mcp/server.py"]
    }
  }
}
```

### Server-Specific Settings

```yaml
# server_configs.yaml
scraping:
  # Core automation
  puppeteer:
    headless: true
    timeout: 30000
    viewport:
      width: 1920
      height: 1080
  
  playwright:
    browsers: ["chromium", "firefox"]
    mobile_emulation: false
    network_idle: 500
  
  # Enterprise-grade
  firecrawl:
    rate_limit: 10
    max_pages: 100
    formats: ["markdown", "html"]
    
  agentql:
    timeout: 45000
    max_retries: 3
    output_format: "structured"
    
  apify:
    max_concurrent: 5
    timeout: 60000
    storage_days: 7
    
  browserbase:
    session_timeout: 300
    keep_alive: true
    debug_mode: false
  
  # Anti-detection
  rquest:
    proxy_rotation: true
    fingerprint_randomization: true
    success_threshold: 0.95
    
  scrapling_fetch:
    stealth_mode: true
    js_rendering: true
    captcha_solving: false

search:
  # AI-powered
  exa:
    search_type: "neural"
    max_results: 20
    include_domains: []
    exclude_domains: []
    
  tavily:
    search_depth: "advanced"
    include_answer: true
    include_raw_content: false
    max_results: 10
    
  perplexity:
    model: "sonar-small-online"
    return_citations: true
    return_images: false
  
  # Traditional
  kagi_search:
    safe_search: "moderate"
    region: "us-en"
    freshness: "week"
    
  searxng:
    engines: ["google", "bing", "duckduckgo"]
    safe_search: 1
    time_range: ""

content_processing:
  # Document conversion
  vectorize:
    chunking_strategy: "semantic"
    chunk_size: 1000
    chunk_overlap: 200
    output_format: "markdown"
    
  pandoc:
    input_formats: ["html", "pdf", "docx", "csv"]
    output_format: "markdown"
    preserve_structure: true
    
  markdownify:
    clean_output: true
    preserve_links: true
    include_metadata: true
    
  unstructured:
    chunking_strategy: "by_title"
    max_characters: 1500
    combine_under_n_chars: 200
    new_after_n_chars: 2000
    
  # RAG & knowledge management
  needle:
    indexing_strategy: "semantic"
    chunk_size: 512
    similarity_threshold: 0.8
    max_results: 20
    
  chroma:
    collection_name: "intelforge_knowledge"
    embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
    distance_metric: "cosine"
    persist_directory: "/home/kiriti/alpha_projects/intelforge/vault/vectors"
    
  basic_memory:
    graph_storage: "/home/kiriti/alpha_projects/intelforge/vault/knowledge_graph"
    auto_link_threshold: 0.7
    max_entities: 50000
    
  inkeep:
    search_mode: "semantic"
    return_snippets: true
    max_snippet_length: 200

data:
  sqlite:
    database_path: "/home/kiriti/alpha_projects/intelforge/vault/data"
    backup_interval: "1h"
  
  memory:
    persistence: true
    max_entities: 10000

productivity:
  github:
    rate_limit: 5000
    cache_duration: "5m"
```

## 🔍 Server Status & Management

### Status Checking

```bash
#!/bin/bash
# status.sh - Check MCP server status

echo "🔍 IntelForge MCP Server Status"
echo "================================"

# Check active Claude Code servers
if claude mcp list &>/dev/null; then
    echo "✅ Claude Code MCP servers:"
    claude mcp list
else
    echo "❌ Claude Code not configured"
fi

# Check individual server health
echo ""
echo "🏥 Server Health Check:"

# Test basic servers
echo -n "🔧 Filesystem: "
if npx -y @modelcontextprotocol/server-filesystem --version &>/dev/null; then
    echo "✅ Available"
else
    echo "❌ Not available"
fi

echo -n "🧠 Memory: "
if npx -y @modelcontextprotocol/server-memory --version &>/dev/null; then
    echo "✅ Available"
else
    echo "❌ Not available"
fi

echo -n "🕷️ Puppeteer: "
if npx -y @modelcontextprotocol/server-puppeteer --version &>/dev/null; then
    echo "✅ Available"
else
    echo "❌ Not available"
fi
```

## 🚨 Troubleshooting

### Common Issues

**1. Server Won't Start**
```bash
# Check Claude Code config
cat ~/.claude/config.json

# Verify server installation
npx -y @modelcontextprotocol/server-puppeteer --help

# Check logs
tail -f logs/mcp_servers.log
```

**2. Permission Issues**
```bash
# Fix filesystem permissions
chmod +x scripts/*.sh

# Update npm permissions
npm config set prefix ~/.npm-global
```

**3. API Key Issues**
```bash
# Set environment variables
export BRAVE_SEARCH_API_KEY="your-key"
export FIRECRAWL_API_KEY="your-key"

# Verify in Claude Code config
```

### Debug Mode

```bash
# Start servers in debug mode
DEBUG=mcp:* ./scripts/start_servers.sh

# Check specific server logs
tail -f logs/puppeteer.log
```

## 📈 Performance Optimization

### Resource Management

```yaml
# Performance settings
performance:
  concurrent_requests: 5
  timeout: 30000
  memory_limit: "512MB"
  
  scraping:
    delay_between_requests: 1000
    max_retries: 3
    cache_responses: true
    
  data:
    batch_size: 100
    index_frequency: "5m"
```

### Monitoring

```bash
# Monitor resource usage
htop -p $(pgrep -f "mcp-server")

# Check memory usage
ps aux | grep mcp-server | awk '{print $4, $11}'

# Log rotation
logrotate -f /etc/logrotate.d/mcp-servers
```

## 🔮 Future Enhancements

### Current Coverage Status

✅ **Phase 1: Essential Scraping** - 15+ servers implemented  
✅ **Phase 2: Enterprise & Anti-Detection** - AgentQL, Apify, Rquest, etc.  
✅ **Phase 3: AI Search & Discovery** - Exa, Tavily, Perplexity, etc.  
🔄 **Phase 4: Specialized Integration** - In progress  

### Planned Additions

- **🤖 LLM Integration**: Local model servers, Claude/OpenAI endpoints
- **📊 Financial Data**: Bloomberg, Yahoo Finance, Trading View APIs
- **🔐 Advanced Security**: Proxy management, VPN integration, CAPTCHA solving
- **📱 Social Media**: LinkedIn, Twitter, Instagram specialized scrapers
- **☁️ Cloud Platform**: Kubernetes deployment, monitoring, scaling

### Integration Roadmap

1. **Phase 1**: Essential scraping servers (✅ Complete - 6 servers)
2. **Phase 2**: Enterprise & anti-detection (✅ Complete - 9 additional servers)  
3. **Phase 3**: AI search & discovery (✅ Complete - 7 additional servers)
4. **Phase 4**: Specialized domains (📋 Planned - Financial, social, cloud)
5. **Phase 5**: Enterprise deployment (🔄 Infrastructure scaling, monitoring)

---

## 📚 Resources

- **[MCP Official Documentation](https://modelcontextprotocol.io)**
- **[Docker MCP Servers](https://github.com/docker/mcp-servers)**
- **[IntelForge Project Documentation](../README.md)**
- **[Claude Code Integration Guide](../docs/claude_code_integration.md)**

---

**🎯 Next Steps:**
1. **Essential Setup**: Run `./scripts/install_scraping.sh` for core servers
2. **Enterprise Upgrade**: Install AgentQL, Apify, and Browserbase for production scraping
3. **AI Integration**: Configure Exa, Tavily, and Perplexity for intelligent research
4. **Anti-Detection**: Set up Rquest and Scrapling for protected sites
5. **Performance**: Monitor and optimize with the comprehensive server suite

**📊 Current Status:** 
- **30+ MCP servers** available across all categories
- **Enterprise-grade** scraping infrastructure 
- **AI-powered** search and discovery
- **Professional content processing** with automatic chunking
- **Production-ready** for comprehensive web intelligence workflows

**🚀 Capability Overview:**
- **Basic Scraping**: Fetch, Puppeteer, Playwright (✅)
- **Enterprise Scraping**: AgentQL, Apify, Firecrawl, Browserbase (✅) 
- **Anti-Detection**: Rquest, Scrapling Fetch (✅)
- **Content Processing**: Vectorize, Pandoc, Markdownify, Unstructured (✅)
- **RAG & Knowledge**: Needle, Chroma, Basic Memory (✅)
- **AI Search**: Exa, Tavily, Perplexity (✅)
- **Privacy Search**: Kagi, SearXNG (✅)
- **Specialized Tools**: Screenshot, RAG processing (✅)