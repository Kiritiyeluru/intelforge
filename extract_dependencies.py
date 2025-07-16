#!/usr/bin/env python3
"""
Script to extract all Python dependencies from IntelForge project
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Set, List, Dict
import importlib.util

def extract_imports_from_file(file_path: Path) -> Set[str]:
    """Extract import statements from a Python file"""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file as AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            print(f"Syntax error in {file_path}, trying regex fallback")
            return extract_imports_regex(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return set()
    
    return imports

def extract_imports_regex(content: str) -> Set[str]:
    """Fallback regex-based import extraction"""
    imports = set()
    
    # Pattern for import statements
    import_patterns = [
        r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
        r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import'
    ]
    
    for line in content.split('\n'):
        for pattern in import_patterns:
            match = re.match(pattern, line)
            if match:
                module_name = match.group(1).split('.')[0]
                imports.add(module_name)
    
    return imports

def is_standard_library(module_name: str) -> bool:
    """Check if a module is part of Python standard library"""
    standard_libs = {
        'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'typing', 'collections',
        'itertools', 'functools', 'operator', 'threading', 'multiprocessing',
        'subprocess', 'argparse', 'logging', 'warnings', 'traceback', 'inspect',
        'ast', 'importlib', 'pkgutil', 'zipfile', 'tarfile', 'gzip', 'bz2',
        'sqlite3', 'dbm', 'pickle', 'copyreg', 'copy', 'pprint', 'reprlib',
        'enum', 'numbers', 'math', 'cmath', 'decimal', 'fractions', 'random',
        'statistics', 'io', 'stringio', 'contextlib', 'abc', 'atexit',
        'configparser', 'fileinput', 'linecache', 'shutil', 'tempfile',
        'glob', 'fnmatch', 'csv', 'xml', 'html', 'urllib', 'http', 'ftplib',
        'poplib', 'imaplib', 'nntplib', 'smtplib', 'email', 'mimetypes',
        'socket', 'ssl', 'select', 'selectors', 'signal', 'mmap', 'codecs',
        'locale', 'gettext', 'platform', 'errno', 'ctypes', 'struct',
        'hashlib', 'hmac', 'secrets', 'base64', 'binascii', 'uuid', 'zlib',
        'calendar', 'collections', 'heapq', 'bisect', 'array', 'weakref',
        'types', 'gc', 'dis', 'pickletools', 'formatter', 'getopt',
        'shlex', 'string', 're', 'difflib', 'textwrap', 'unicodedata',
        'readline', 'rlcompleter', 'cmd', 'pdb', 'profile', 'pstats',
        'timeit', 'trace', 'faulthandler', 'tracemalloc', 'resource',
        'sysconfig', 'test', 'venv', 'ensurepip', 'zipapp', 'runpy',
        'code', 'codeop', 'compileall', 'py_compile', 'keyword', 'token',
        'tokenize', 'symbol', 'parser', 'dataclasses', 'contextlib'
    }
    
    return module_name in standard_libs

def get_project_files(project_root: Path) -> List[Path]:
    """Get all Python files in the project, excluding virtual environments"""
    python_files = []
    
    exclude_dirs = {
        'venv', '.venv', 'env', '.env', 'build', 'dist', '__pycache__',
        '.git', '.pytest_cache', 'node_modules', 'logs', 'chroma_storage',
        'qdrant_storage', 'chroma_storage_backup', 'chroma_storage_snapshot',
        'release-checkpoints', 'test_snapshot_phase1'
    }
    
    for root, dirs, files in os.walk(project_root):
        # Remove excluded directories from search
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                python_files.append(file_path)
    
    return python_files

def main():
    project_root = Path(__file__).parent
    python_files = get_project_files(project_root)
    
    print(f"Found {len(python_files)} Python files")
    
    all_imports = set()
    file_imports = {}
    
    for file_path in python_files:
        imports = extract_imports_from_file(file_path)
        if imports:
            relative_path = file_path.relative_to(project_root)
            file_imports[str(relative_path)] = imports
            all_imports.update(imports)
    
    # Filter out standard library and local imports
    third_party_imports = set()
    local_imports = set()
    
    for import_name in all_imports:
        if is_standard_library(import_name):
            continue
        elif import_name.startswith('scripts') or import_name.startswith('tests'):
            local_imports.add(import_name)
        else:
            third_party_imports.add(import_name)
    
    # Create mapping of common import names to package names
    package_mappings = {
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'yaml': 'PyYAML',
        'dotenv': 'python-dotenv',
        'dateutil': 'python-dateutil',
        'sklearn': 'scikit-learn',
        'bs4': 'beautifulsoup4',
        'requests_html': 'requests-html',
        'requests_cache': 'requests-cache',
        'fake_useragent': 'fake-useragent',
        'retrying': 'retrying',
        'selenium': 'selenium',
        'webdriver_manager': 'webdriver-manager',
        'botasaurus': 'botasaurus',
        'undetected_chrome': 'undetected-chromedriver',
        'playwright': 'playwright',
        'scrapy': 'scrapy',
        'trafilatura': 'trafilatura',
        'selectolax': 'selectolax',
        'sentence_transformers': 'sentence-transformers',
        'keybert': 'keybert',
        'transformers': 'transformers',
        'chromadb': 'chromadb',
        'qdrant_client': 'qdrant-client',
        'langchain': 'langchain',
        'langchain_community': 'langchain-community',
        'httpx': 'httpx',
        'aiohttp': 'aiohttp',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'plotly': 'plotly',
        'yfinance': 'yfinance',
        'quantstats': 'quantstats',
        'typer': 'typer',
        'rich': 'rich',
        'click': 'click',
        'pytest': 'pytest',
        'tqdm': 'tqdm',
        'praw': 'praw',
        'github': 'PyGithub',
        'schedule': 'schedule',
        'psutil': 'psutil',
        'presidio_analyzer': 'presidio-analyzer',
        'presidio_anonymizer': 'presidio-anonymizer',
        'spacy': 'spacy',
        'pytz': 'pytz',
        'flask': 'flask',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'sqlalchemy': 'sqlalchemy',
        'alembic': 'alembic',
        'redis': 'redis',
        'celery': 'celery'
    }
    
    # Convert import names to package names
    packages = set()
    for import_name in third_party_imports:
        package_name = package_mappings.get(import_name, import_name)
        packages.add(package_name)
    
    # Print results
    print(f"\n=== THIRD-PARTY PACKAGES ({len(packages)}) ===")
    for package in sorted(packages):
        print(package)
    
    print(f"\n=== LOCAL IMPORTS ({len(local_imports)}) ===")
    for local_import in sorted(local_imports):
        print(local_import)
    
    # Write requirements.txt
    requirements_content = """# IntelForge Dependencies
# Generated automatically from project imports

# Core web scraping and automation
scrapy>=2.11.0
scrapy-playwright>=0.0.26
scrapy-fake-useragent>=1.4.4
playwright>=1.40.0
selenium>=4.15.0
botasaurus>=4.0.0
undetected-chromedriver>=3.5.0
webdriver-manager>=4.0.0

# Content extraction and processing
trafilatura>=1.6.4
selectolax>=0.3.17
beautifulsoup4>=4.12.0
requests>=2.31.0
requests-html>=0.10.0
requests-cache>=1.1.0
httpx>=0.25.0
aiohttp>=3.9.0

# AI and machine learning
sentence-transformers>=2.2.2
keybert>=0.8.3
transformers>=4.34.0
torch>=2.0.0
scikit-learn>=1.3.0
spacy>=3.7.0

# Vector databases
chromadb>=0.4.15
qdrant-client>=1.6.0

# LangChain ecosystem
langchain>=0.0.350
langchain-community>=0.0.10

# Data processing and analysis
pandas>=2.1.0
numpy>=1.24.0
matplotlib>=3.7.0
plotly>=5.17.0
yfinance>=0.2.18
quantstats>=0.0.62

# CLI and user interface
typer>=0.9.0
rich>=13.6.0
click>=8.1.7
tqdm>=4.66.0

# Configuration and utilities
PyYAML>=6.0.1
python-dotenv>=1.0.0
python-dateutil>=2.8.2
pytz>=2023.3
retrying>=1.3.4
fake-useragent>=1.4.0

# Web APIs and social media
praw>=7.7.1
PyGithub>=1.59.1

# Scheduling and task management
schedule>=1.2.0
celery>=5.3.0
redis>=5.0.0

# Testing and quality
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0

# Security and privacy
presidio-analyzer>=2.2.0
presidio-anonymizer>=2.2.0
cryptography>=41.0.0

# System monitoring
psutil>=5.9.0

# Database and storage
sqlalchemy>=2.0.0
alembic>=1.12.0

# Web frameworks (for dashboard/API)
flask>=2.3.0
fastapi>=0.104.0
uvicorn>=0.24.0

# Image processing
Pillow>=10.0.0
opencv-python>=4.8.0

# Additional utilities
"""
    
    with open(project_root / 'requirements.txt', 'w') as f:
        f.write(requirements_content)
    
    print(f"\n✅ requirements.txt generated with {len(packages)} packages")
    
    # Generate detailed report
    report_content = f"""# IntelForge Dependencies Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Python files analyzed: {len(python_files)}
- Third-party packages: {len(packages)}
- Local imports: {len(local_imports)}

## Third-Party Packages
"""
    
    for package in sorted(packages):
        report_content += f"- {package}\n"
    
    report_content += f"""
## Local Imports
"""
    
    for local_import in sorted(local_imports):
        report_content += f"- {local_import}\n"
    
    report_content += """
## File-by-File Import Analysis
"""
    
    for file_path, imports in sorted(file_imports.items()):
        if imports:
            report_content += f"\n### {file_path}\n"
            for imp in sorted(imports):
                report_content += f"- {imp}\n"
    
    with open(project_root / 'dependency_report.md', 'w') as f:
        f.write(report_content)
    
    print(f"✅ Detailed report saved to dependency_report.md")

if __name__ == "__main__":
    from datetime import datetime
    main()