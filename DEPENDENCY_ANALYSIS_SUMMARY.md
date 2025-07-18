# IntelForge Dependency Analysis Summary

## Overview
This document provides a comprehensive analysis of all dependencies used in the IntelForge project, based on scanning 183 Python files across the codebase.

## Analysis Method
1. **Automated AST Parsing**: Used Python's AST module to parse all .py files and extract import statements
2. **Regex Fallback**: For files with syntax errors, used regex-based import extraction
3. **Standard Library Filtering**: Excluded Python standard library modules
4. **Package Name Mapping**: Mapped common import names to their PyPI package names

## Key Findings

### Total Dependencies: 149 packages
- **Core Web Scraping**: 8 packages (scrapy, playwright, selenium, etc.)
- **Content Processing**: 8 packages (trafilatura, selectolax, beautifulsoup4, etc.)
- **AI/ML**: 6 packages (sentence-transformers, transformers, torch, etc.)
- **Vector Databases**: 2 packages (chromadb, qdrant-client)
- **Data Analysis**: 6 packages (pandas, numpy, matplotlib, plotly, etc.)
- **CLI/UI**: 4 packages (typer, rich, click, tqdm)
- **Testing**: 4 packages (pytest and extensions)
- **Security**: 3 packages (presidio-analyzer, presidio-anonymizer, cryptography)
- **Utilities**: 108 additional specialized packages

### Core Application Files Analyzed
- `scripts/cli.py` - Main CLI interface using Typer and Rich
- `scripts/semantic_crawler.py` - Core semantic analysis engine
- `scripts/monitoring_dashboard.py` - Performance monitoring using Plotly
- `scripts/canary_validation_system_v2.py` - Validation system
- `scripts/vector_storage_migration.py` - ChromaDB integration

### Existing Requirements Files Found
1. `scripts/semantic_crawler/requirements.txt` - 20 core dependencies
2. `build/requirements_scraping.txt` - 10 scraping-specific dependencies
3. `build/requirements_auto.txt` - 1 auto-generated dependency

## Dependency Categories

### 1. Web Scraping & Automation (8 packages)
- `scrapy>=2.11.0` - Primary scraping framework
- `playwright>=1.40.0` - Browser automation
- `selenium>=4.15.0` - WebDriver automation
- `botasaurus>=4.0.0` - Stealth scraping
- `undetected-chromedriver>=3.5.0` - Anti-detection
- `webdriver-manager>=4.0.0` - Driver management
- `scrapy-playwright>=0.0.26` - Scrapy-Playwright integration
- `scrapy-fake-useragent>=1.4.4` - User agent rotation

### 2. Content Extraction & Processing (8 packages)
- `trafilatura>=1.6.4` - Content extraction
- `selectolax>=0.3.17` - HTML parsing
- `beautifulsoup4>=4.12.0` - HTML/XML parsing
- `requests>=2.31.0` - HTTP library
- `httpx>=0.25.0` - Async HTTP client
- `aiohttp>=3.9.0` - Async HTTP framework
- `requests-html>=0.10.0` - JavaScript support for requests
- `requests-cache>=1.1.0` - HTTP caching

### 3. AI & Machine Learning (6 packages)
- `sentence-transformers>=2.2.2` - Semantic embeddings
- `transformers>=4.34.0` - Hugging Face transformers
- `torch>=2.0.0` - PyTorch deep learning
- `scikit-learn>=1.3.0` - Machine learning
- `spacy>=3.7.0` - NLP processing
- `keybert>=0.8.3` - Keyword extraction

### 4. Vector Databases (2 packages)
- `chromadb>=0.4.15` - Primary vector database
- `qdrant-client>=1.6.0` - Alternative vector database

### 5. Data Processing & Analysis (6 packages)
- `pandas>=2.1.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing
- `matplotlib>=3.7.0` - Plotting
- `plotly>=5.17.0` - Interactive visualizations
- `yfinance>=0.2.18` - Financial data
- `quantstats>=0.0.62` - Financial statistics

### 6. CLI & User Interface (4 packages)
- `typer>=0.9.0` - CLI framework
- `rich>=13.6.0` - Terminal formatting
- `click>=8.1.7` - Command-line interface
- `tqdm>=4.66.0` - Progress bars

### 7. Configuration & Utilities (6 packages)
- `PyYAML>=6.0.1` - YAML parsing
- `python-dotenv>=1.0.0` - Environment variables
- `python-dateutil>=2.8.2` - Date utilities
- `pytz>=2023.3` - Timezone handling
- `retrying>=1.3.4` - Retry logic
- `fake-useragent>=1.4.0` - User agent generation

### 8. Web APIs & Social Media (2 packages)
- `praw>=7.7.1` - Reddit API
- `PyGithub>=1.59.1` - GitHub API

### 9. Testing & Quality (4 packages)
- `pytest>=7.4.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-mock>=3.12.0` - Mock objects

### 10. Security & Privacy (3 packages)
- `presidio-analyzer>=2.2.0` - PII detection
- `presidio-anonymizer>=2.2.0` - PII anonymization
- `cryptography>=41.0.0` - Cryptographic operations

## Installation Instructions

### Standard Installation
```bash
pip install -r requirements.txt
```

### Development Installation
```bash
pip install -r requirements.txt
pip install -e .
```

### Minimal Installation (Core Only)
```bash
pip install scrapy trafilatura sentence-transformers chromadb typer rich
```

## Platform-Specific Notes

### Linux/macOS
All dependencies should install without issues.

### Windows
- `faiss-cpu` may require Microsoft Visual C++ Build Tools
- `torch` installation may be optimized with CUDA support
- Some packages may require Windows SDK

### Docker
The project includes Docker support. See `docker/` directory for containerized deployment.

## Dependency Management

### Version Constraints
- All packages use minimum version constraints (`>=`) to ensure compatibility
- Critical packages have specific version requirements tested in CI
- Regular dependency updates are performed monthly

### Security Considerations
- All dependencies are scanned for known vulnerabilities
- Security-critical packages (cryptography, presidio) are kept up-to-date
- PII detection is mandatory for all content processing

### Performance Considerations
- Vector operations use optimized libraries (faiss, chromadb)
- Async operations use httpx/aiohttp for scalability
- Caching is implemented at multiple levels (requests-cache, diskcache)

## Maintenance

### Regular Updates
- Monthly dependency updates with compatibility testing
- Automated security scanning via GitHub Dependabot
- Performance benchmarking with new versions

### Cleanup
- Remove unused dependencies quarterly
- Monitor for deprecated packages
- Migrate to maintained alternatives when needed

## Troubleshooting

### Common Issues
1. **ChromaDB Installation**: Requires C++ compiler on some systems
2. **Torch Installation**: Large download, consider CPU-only version
3. **Playwright Setup**: Requires `playwright install` after pip install
4. **Spacy Models**: May need `python -m spacy download en_core_web_sm`

### Performance Optimization
- Use `pip install --upgrade pip` before installation
- Consider using `pip install --no-cache-dir` for clean installs
- Use virtual environments to avoid conflicts

## Files Generated
- `requirements.txt` - Complete dependency list
- `dependency_report.md` - Detailed analysis report
- `DEPENDENCY_ANALYSIS_SUMMARY.md` - This summary document

## Last Updated
July 16, 2025 - Comprehensive analysis of 183 Python files
