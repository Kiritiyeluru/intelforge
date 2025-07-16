# IntelForge Repository Organization Plan

**Status**: Ready for implementation
**Configuration**: `.claude/repository_organization_tools.json`
**Target**: Transform chaotic 40+ root-level files into clean, maintainable structure

## 🎯 **Organization Strategy Overview**

IntelForge has grown organically with 40+ loose files at root level. This plan uses prebuilt tools to safely reorganize without breaking functionality.

## 📋 **4-Phase Implementation Plan**

### **Phase 1: Safe Cleanup (Immediate, Reversible)**
**Status**: Ready to execute
**Tools**: black, isort, autoflake
**Safety**: High - formatting only, no logic changes

```bash
# Install tools
pip install black isort autoflake

# Execute safe cleanup
black .                                                    # Format all Python files
isort .                                                    # Sort imports consistently
autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive .
```

**Expected Impact**: 80% visual chaos reduction, consistent formatting

### **Phase 2: Analysis & Understanding (Safe, Read-Only)**
**Tools**: vulture, snakefood, unimport
**Purpose**: Understand current structure before changes

```bash
# Install analysis tools
pip install vulture snakefood3 unimport graphviz

# Generate analysis reports
vulture . --exclude=venv,node_modules > reports/dead_code_analysis.txt
sfood . | sfood-graph | dot -Tpng -o reports/dependency_graph.png
unimport --check --diff > reports/unused_imports.txt
```

**Expected Outputs**: Dependency visualization, dead code report, import cleanup suggestions

### **Phase 3: Structural Reorganization (Careful, Planned)**
**Tools**: git mv, bowler, libcst
**Safety**: Medium - requires testing after each move

**Target Structure:**
```
intelforge/
├── core/              # Core validation, driver, config modules
│   ├── validation.py  # EnhancedCanaryValidator → canary_validation_system_v2.py
│   ├── driver.py      # IntelBotDriverV2 → intel_bot_driver_v2.py
│   ├── config.py      # Configuration management
│   └── __init__.py
├── plugins/           # Site-specific validation plugins
│   ├── finviz.py      # Finviz-specific validation
│   ├── yahoo.py       # Yahoo Finance validation
│   ├── detection.py   # Anti-detection logic
│   └── __init__.py
├── tools/             # CLI utilities and test runners
│   ├── cli.py         # Command-line interface
│   ├── test_runner.py # Test execution utilities
│   └── __init__.py
├── scripts/           # One-off automation scripts (keep existing)
├── tests/             # All test files (consolidate test_*.py)
├── docs/              # Documentation only
├── config/            # Configuration files (existing)
├── data/              # Data files and caches (existing)
└── reports/           # Generated reports and outputs (existing)
```

**File Migration Commands:**
```bash
# Create new structure
mkdir -p core plugins tools tests

# Move core files with git history preservation
git mv canary_validation_system_v2.py core/validation.py
git mv intel_bot_driver_v2.py core/driver.py
git mv forgecli.py tools/cli.py

# Move test files
find . -maxdepth 1 -name "test_*.py" -exec git mv {} tests/ \;

# Update imports automatically
bowler do update_imports --old-module canary_validation_system_v2 --new-module core.validation
```

### **Phase 4: Enforcement & Maintenance (Ongoing)**
**Tools**: flake8, pylint, pre-commit hooks
**Purpose**: Maintain organization standards

```bash
# Install enforcement tools
pip install flake8 pylint pre-commit

# Setup pre-commit hooks
pre-commit install

# Configure ongoing checks
flake8 --config=setup.cfg .
pylint core/ plugins/ tools/
```

## 🛠️ **Tool Installation & Configuration**

### **Immediate Installation (Phase 1)**
```bash
# Core formatting tools
pip install black isort autoflake

# Analysis tools
pip install vulture snakefood3 unimport
sudo apt install graphviz  # For dependency graphs

# Advanced refactoring (Phase 3)
pip install bowler libcst rope
```

### **Tool Configuration Files**
```bash
# .isort.cfg
[settings]
profile = black
multi_line_output = 3

# pyproject.toml (black config)
[tool.black]
line-length = 88
target-version = ['py38']

# .flake8
[flake8]
max-line-length = 88
exclude = venv,node_modules,.git
```

## 📊 **Success Metrics**

| Metric | Before | Target | Tool |
|--------|--------|--------|------|
| Root-level .py files | 40+ | <10 | Manual count |
| Import consistency | Mixed | 100% | isort |
| Code formatting | Inconsistent | 100% | black |
| Dead code lines | Unknown | <5% | vulture |
| Circular imports | Unknown | 0 | snakefood |

## ⚠️ **Risk Mitigation**

1. **Git History Preservation**: Use `git mv` instead of `mv`
2. **Incremental Changes**: Test after each file move
3. **Backup Strategy**: Create branch before Phase 3
4. **Import Updates**: Use bowler for automatic import fixing
5. **Testing**: Run existing tests after each phase

## 🚀 **Immediate Next Steps**

1. **Execute Phase 1** (safe formatting)
2. **Generate Phase 2 analysis reports**
3. **Review dependency graph** for logical groupings
4. **Plan Phase 3 file moves** based on analysis
5. **Implement gradual reorganization**

## 📚 **Additional Resources**

- **Configuration Reference**: `.claude/repository_organization_tools.json`
- **Dependency Analysis**: `reports/dependency_graph.png` (after Phase 2)
- **Dead Code Report**: `reports/dead_code_analysis.txt` (after Phase 2)
- **Tool Documentation**: Individual tool repos and docs

This plan transforms IntelForge from chaotic to maintainable while preserving all functionality and git history.


----------------------------------
Absolutely — you're not alone! Most developers *don’t realize how many smart tools exist* for organizing and maintaining codebases until a repo becomes overwhelming.

Here’s a **deeper, curated list** of tools and techniques (beyond just formatting) for **codebase organization, maintenance, and modernization** — including smart tools that can **automatically refactor, move, rename, document, analyze dependencies, and more**.

---

## 🧠 **Smart Code Refactoring & Organization Tools**

### ✅ 1. **[Bazel Codemod](https://github.com/bazelbuild/bazel-codemod) / Facebook’s Codemod**

> Bulk refactoring tool using regex or AST transformations

* Can **rename classes/functions**, **move files**, or **modify imports** across hundreds of files
* Good for **consistency cleanup** (e.g., rename all `run_canary_check` to `execute_canary`)
* ❗ Not Python-specific — better used with tooling like Bowler/LibCST for Python

---

### ✅ 2. **[Bowler](https://pybowler.io/)**

> A powerful Python-specific codemod tool built on LibCST
> 💡 *Bowler understands your syntax and safely modifies it.*

Use-cases:

* **Move functions to new modules**
* Rename functions or methods **and fix imports**
* Delete unused code across the codebase

```bash
# Move a function to another file and auto-update references
bowler query 'select function where name="run_canary_check"' | modify move to 'core/checks.py'
```

---

### ✅ 3. **[LibCST](https://github.com/Instagram/LibCST)**

> The engine behind Bowler. Use it directly for custom AST refactoring.

* Lets you **write Python scripts that transform other Python code**
* Supports **code formatting**, rewriting, and restructuring
* Ideal for **large-scale reorganizations** with logic

---

### ✅ 4. **[Rope](https://github.com/python-rope/rope)**

> An older but powerful refactoring library (used in VSCode/PyCharm)

* Rename/move classes and update references
* Detect unused code
* Refactor modules (inline method, extract variable)

---

## 📦 **Import Management Tools**

### ✅ 5. **[Autoflake](https://github.com/myint/autoflake)**

> Cleans **unused imports and variables** (better than flake8 for this)

```bash
autoflake --remove-all-unused-imports -r -i .
```

---

### ✅ 6. **[Isort](https://pycqa.github.io/isort/)**

> Sort and group imports intelligently

* Groups standard libs, 3rd party, internal
* Custom profiles for Django, monorepo, or microservice layouts

```bash
isort .
```

---

### ✅ 7. **\[Reorder Python Imports (VSCode Extension)]**

> Live reorderer in the editor — auto-group on save

---

## 🧪 **Code Health & Maintenance Tools**

### ✅ 8. **[Pylint](https://pylint.pycqa.org/)** + **[Flake8](https://flake8.pycqa.org/)**

> Deep static analysis for:

* Long functions
* Over-complex classes
* Duplicate logic
* Unreachable or dead code
* Unused arguments, variables

```bash
pylint .
flake8 .
```

---

### ✅ 9. **[Vulture](https://github.com/jendrikseipp/vulture)**

> Dead code finder — identifies unused functions, classes, variables

```bash
vulture your_project/
```

---

### ✅ 10. **[Refurb](https://github.com/dosisod/refurb)**

> AI-powered Python refactoring suggestions

* Flags **outdated patterns**, **unused constructs**, **inefficient idioms**

```bash
pip install refurb
refurb path/to/code
```

---

### ✅ 11. **[Pyre](https://pyre-check.org/)** or **[Mypy](http://mypy-lang.org/)**

> Static type checkers

* Enforce type contracts to prevent incorrect refactors
* Helps **detect misused refactored functions**

---

## 🔍 Code Structure Analysis Tools

### ✅ 12. **[Snakefood](https://furius.ca/snakefood/)** or **[Pydeps](https://github.com/thebjorn/pydeps)**

> Visualize file/module dependencies

```bash
pydeps your_module.py --show-deps
```

This helps you:

* Break circular imports
* See candidates for splitting into packages

---

### ✅ 13. **\[Sourcegraph (Self-hosted)** or **[GitHub Code Search](https://cs.github.com/)**

> Index and search your codebase like an IDE
> Find where everything is used before refactoring.

---

## 📂 **Folder Restructuring Aids**

### ✅ 14. **[Cookiecutter](https://cookiecutter.readthedocs.io/)**

> Templates for project folder layouts
> Use this to **apply a modern structure** to your repo and migrate code

Popular templates:

* [`cookiecutter-pypackage`](https://github.com/audreyfeldroy/cookiecutter-pypackage)
* [`cookiecutter-data-science`](https://github.com/drivendata/cookiecutter-data-science)
* [`cookiecutter-pyproject`](https://github.com/rochacbruno/cookiecutter-pyproject)

---

### ✅ 15. **\[Monorepo tools: Pants / Bazel / Poetry Workspaces]**

> Help **organize multiple logical packages or services** inside a single repo

Great if you're moving toward:

* `core/`
* `plugins/`
* `cli/`
* `services/`
  ... and want dependency isolation per component.

---

## 🤖 BONUS: AI-Assisted Helpers

### ✅ 16. **CodiumAI (VS Code Plugin)**

> Adds in-editor test generation, bug detection, refactor proposals

### ✅ 17. **GPT-4 / ChatGPT Plugins + Workspace (Beta)**

> You can now use GPT-4 (via Copilot Workspace or ChatGPT Code Interpreter) to:

* Extract functions
* Suggest packages
* Move functions across files
* Maintain imports

---

## 🧩 Combine These into a Workflow

```bash
# Format + cleanup
black . && isort . && autoflake -r -i .

# Detect dead code
vulture .
pylint .

# Visualize structure
pydeps your_module.py --show-deps

# Refactor safely
bowler query 'select function where name="fetch_target"' | modify move to 'core/fetcher.py'

# Apply monorepo layout
cookiecutter https://github.com/your-org/your-template
```

---

Yes — if you're looking for **faster, Rust-based, or performance-optimized tools** for **code organization, formatting, linting, and refactoring**, there’s a growing ecosystem of high-performance tools that beat traditional Python ones in speed and efficiency — some of which are already **drop-in replacements**.

Here’s a curated list of the **fastest and most modern tools**, especially those written in **Rust** (⚡) or otherwise focused on **performance and static safety**:

---

## ⚡ **Rust-Based / Ultra-Fast Tools for Python Repos**

### ✅ **1. [Ruff](https://github.com/astral-sh/ruff)** (Rust)

> 🚀 **The fastest Python linter & formatter** — 100x faster than flake8 + pylint
> Replaces: `flake8`, `pylint`, `pycodestyle`, `pyflakes`, `isort`, parts of `black`

* **One tool** for linting, sorting imports, enforcing code style
* Built in Rust for **blazing speed** (can lint 1000+ files in <2s)
* Has support for **autofix**, import sorting, and even complexity checks

```bash
# Install
pip install ruff

# Run lint + fix + import sort
ruff check . --fix
```

✅ Ideal for large or messy codebases.

---

### ✅ **2. [RustPython](https://github.com/RustPython/RustPython)**

> 🧪 Experimental Python interpreter in Rust (not a tool itself, but…)

* Being used as the base for tools like `pylyzer`, `pyright-rs`, and others
* Enables **very fast AST analysis** and toolchains

---

### ✅ **3. [Pylyzer](https://github.com/mtshiba/pylyzer)** (Rust)

> 💡 Type-checker and linter using `RustPython`
> Blazing-fast type analysis and dead code detection

* Detects **dead code**, **undefined variables**, **unreachable branches**
* Lightweight and self-contained
* Still early-stage but promising for large codebases

```bash
cargo install pylyzer
pylyzer check src/
```

---

### ✅ **4. [dprint](https://dprint.dev/)** (Rust)

> ⚡ Ultra-fast, extensible code formatter (like Prettier or Black)
> Supports: JavaScript, TypeScript, Markdown, JSON, Python (experimental)

* Plugin-based: You can write or use a Python formatter plugin
* Blazing fast, suitable for CI/CD pipelines

---

### ✅ **5. [tree-sitter](https://tree-sitter.github.io/)** (C + Rust ecosystem)

> 🧬 Universal parsing system for syntax trees in any language

* Used by [Zed Editor](https://zed.dev/), Neovim, and [Sourcegraph Cody](https://sourcegraph.com/blog/cody-2.0-ai-dev-assistant)
* Fast syntax tree generation
* Combined with Rust-based tools, can power **code search, classification, folding, refactoring**

✅ Used in:

* `helix` editor (Rust-based)
* `tree-sitter-python`
* Custom refactor pipelines

---

### ✅ **6. [Zellij](https://zellij.dev/)** (Rust)

> Not a code tool per se, but a **Rust-based terminal multiplexer** — helps organize **complex dev sessions**, especially in monorepos.

---

## 🧠 AI + LLM-Driven Tools (Faster with Native Execution)

### ✅ **7. [Refact.ai CLI (Small LLMs)](https://github.com/smallcloudai/refact)**

> Use local small LLMs (Mistral etc.) to **refactor, split, and rename code intelligently**

* Can **understand structure** and **propose splits**
* Much faster than cloud LLMs when running on GPU locally

---

### ✅ **8. [JetBrains RustRover](https://www.jetbrains.com/rustrover/)** + Python Plugin

> Supports Rust + Python monorepos
> Powerful refactor engine (based on JetBrains’ PSI model)
> Great for interactive renaming, moving, refactoring across languages.

---

## 🔍 Other Fast Non-Rust Tools Worth Mentioning

| Tool      | Lang   | Function                | Notes                       |
| --------- | ------ | ----------------------- | --------------------------- |
| `black`   | Python | Formatter               | Slow-ish, but robust        |
| `pyright` | TS     | Type checker for Python | Fast, typed AST             |
| `pyre`    | OCaml  | Type checker, Facebook  | Good for big teams          |
| `rope`    | Python | Refactor API            | A bit dated, but scriptable |

---

## 🛠 Suggested Fast Toolchain (Rust-Friendly)

```bash
# Install the fastest combo
pip install ruff black
cargo install pylyzer

# Lint + autofix + sort imports
ruff check . --fix

# Format code
black .

# Type and dead code check (Rust-based)
pylyzer check ./src
```

---

## ✨ TL;DR: Best Picks for You

| Purpose                     | Tool            | Why Use It                     |
| --------------------------- | --------------- | ------------------------------ |
| Fastest linter+formatter    | ✅ `ruff`        | One tool to replace 5 others   |
| Fast type + dead code check | ✅ `pylyzer`     | Lightweight, Rust, AST-based   |
| Modular formatter           | ✅ `dprint`      | Plugin-based, CI-friendly      |
| AST refactoring             | ✅ `bowler`      | Python-safe structural changes |
| Code search & analysis      | ✅ `tree-sitter` | Great for plugin + indexing    |
| Intelligent CLI refactor    | ✅ `refact.ai`   | Small LLM for local context    |

---

Great — here’s a starter pack with powerful, ready-to-use scripts and commands across:

---

## 🧹 1. **Shell Script for Cleanup & Refactor**

**Tools:** Ruff, Pylyzer, Bowler
🔧 Goal: Clean imports, format, lint, remove dead code, and apply safe refactors.

```bash
#!/bin/bash
# 🧹 Python Codebase Cleanup Script
# Requires: ruff, black, pylyzer, bowler

echo "🧹 Starting full code cleanup..."

echo "📦 Sorting imports and fixing style with Ruff"
ruff check . --fix --unsafe-fixes

echo "🎨 Formatting with Black"
black .

echo "🕵️ Dead code/type checking with Pylyzer"
pylyzer check .

echo "🪄 Optional: Structural refactor using Bowler (e.g. rename functions)"
bowler --pattern 'def old_func_name' --rewrite 'def new_func_name' .

echo "✅ Cleanup complete"
```

**Save as:** `clean_refactor.sh`
**Run:** `chmod +x clean_refactor.sh && ./clean_refactor.sh`

---

## 🌳 2. **Tree-sitter Script: Extract & Rename Python Structure**

**Tools:** tree-sitter CLI + Python grammar
🔧 Goal: Print structure (functions, classes) and optionally rename them.

### Step 1: Install Tree-sitter CLI + Python grammar

```bash
brew install tree-sitter  # or use cargo: cargo install tree-sitter-cli
mkdir -p tree-sitter-python && cd tree-sitter-python
git clone https://github.com/tree-sitter/tree-sitter-python .
```

### Step 2: Run a script to extract structure

```bash
tree-sitter parse ../your_script.py --quiet --lang python > ast.txt
```

To extract all functions via AST:

```bash
tree-sitter parse ../your_script.py --quiet --lang python \
| grep 'function_definition' -A 2
```

---

## 🦀 3. **Rust CLI Starter: Bulk Refactor or Move Python Files**

Use [clap](https://docs.rs/clap), [walkdir](https://docs.rs/walkdir), and [regex](https://docs.rs/regex) crates.

```rust
// src/main.rs
use std::fs;
use std::path::Path;
use walkdir::WalkDir;
use clap::Parser;
use regex::Regex;

/// 🦀 Bulk Rename or Move Python Functions in Files
#[derive(Parser)]
struct Args {
    #[arg(short, long)]
    path: String,

    #[arg(short, long)]
    pattern: String,

    #[arg(short, long)]
    replace: String,
}

fn main() {
    let args = Args::parse();
    let pattern = Regex::new(&args.pattern).expect("Invalid regex");

    for entry in WalkDir::new(&args.path)
        .into_iter()
        .filter_map(Result::ok)
        .filter(|e| e.path().extension().map_or(false, |ext| ext == "py"))
    {
        let path = entry.path();
        let content = fs::read_to_string(path).expect("Could not read file");

        if pattern.is_match(&content) {
            let new_content = pattern.replace_all(&content, &*args.replace);
            fs::write(path, new_content.as_bytes()).expect("Failed to write file");
            println!("✔ Updated: {}", path.display());
        }
    }
}
```

**Run example:**

```bash
cargo run -- --path ./src --pattern 'def my_old_func' --replace 'def my_new_func'
```

---

Perfect — here's how we'll break it down into 4 tools:
// 📦 lib.rs — Refactor Toolkit Core Library
// Provides utilities to refactor, rename, and process Python files

use std::fs;
use std::path::Path;
use walkdir::WalkDir;
use regex::Regex;

pub fn refactor_python_code<P: AsRef<Path>>(
    dir: P,
    pattern: &str,
    replacement: &str,
) -> Result<(), Box<dyn std::error::Error>> {
    let regex = Regex::new(pattern)?;

    for entry in WalkDir::new(dir)
        .into_iter()
        .filter_map(Result::ok)
        .filter(|e| e.path().extension().map_or(false, |ext| ext == "py"))
    {
        let path = entry.path();
        let content = fs::read_to_string(path)?;

        if regex.is_match(&content) {
            let new_content = regex.replace_all(&content, replacement);
            fs::write(path, new_content.as_bytes())?;
            println!("✔ Updated: {}", path.display());
        }
    }
    Ok(())
}

---

## 🧠 1. **Watch Mode: Auto-Format on Save**

```bash
# watch_format.sh
#!/bin/bash
# Auto-runs Ruff and Black on file change

watchmedo shell-command \
  --patterns="*.py" \
  --recursive \
  --command='echo 🧠 Detected change: ${watch_src_path} && ruff check ${watch_src_path} --fix && black ${watch_src_path}' \
  .
```

**Requires:** `watchdog[watchmedo]`, Ruff, Black

```bash
pip install watchdog ruff black
chmod +x watch_format.sh && ./watch_format.sh
```

---

## 🧰 2. **Convert Rust CLI → `lib.rs` for Toolkit Integration**

🔧 Already done above — you now have a reusable function:

```rust
pub fn refactor_python_code(path, pattern, replace)
```

Use it from `main.rs` like:

```rust
use refactor_toolkit::refactor_python_code;
```

---

## 🔍 3. **Tree-Sitter + Graphviz Export (AST → .dot file)**

```bash
# tree_export.py
from tree_sitter import Language, Parser
import sys

Language.build_library(
  'build/my-languages.so',
  ['tree-sitter-python']
)

PY_LANGUAGE = Language('build/my-languages.so', 'python')
parser = Parser()
parser.set_language(PY_LANGUAGE)

with open(sys.argv[1], 'r') as f:
    code = f.read()

tree = parser.parse(bytes(code, "utf8"))

def print_tree(node, source, indent=""):
    print(f"{indent}{node.type} [{node.start_point} - {node.end_point}]")
    for child in node.children:
        print_tree(child, source, indent + "  ")

print_tree(tree.root_node, code)
```

To export as Graphviz:

```python
def export_dot(node, out):
    out.write(f'"{id(node)}" [label="{node.type}"];\n')
    for child in node.children:
        out.write(f'"{id(node)}" -> "{id(child)}";\n')
        export_dot(child, out)

with open("ast.dot", "w") as out:
    out.write("digraph AST {\n")
    export_dot(tree.root_node, code)
    out.write("}")
```

Then run:

```bash
dot -Tpng ast.dot -o ast.png
```

---

## 🪄 4. **Auto-Split Large Files by Class/Function Count**

```python
# split_by_structure.py
import ast, os, textwrap

def count_defs(node):
    return sum(isinstance(n, (ast.FunctionDef, ast.ClassDef)) for n in ast.walk(node))

def split_file(filename, max_defs=10):
    with open(filename) as f:
        code = f.read()
    tree = ast.parse(code)
    defs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]

    chunks = [defs[i:i+max_defs] for i in range(0, len(defs), max_defs)]
    base = os.path.splitext(filename)[0]

    for i, chunk in enumerate(chunks):
        out_path = f'{base}_part{i+1}.py'
        with open(out_path, 'w') as f:
            for node in chunk:
                src = ast.get_source_segment(code, node)
                f.write(textwrap.dedent(src) + "\n\n")
        print(f"🪄 Saved {out_path}")

split_file("your_big_script.py")
```

---

Would you like all these bundled into a `scripts/` directory with a setup script and Makefile? I can auto-generate the project scaffold.
