# IntelForge Task Runner
# Replaces Bash scripts with modern task automation
# Usage: just <task-name>

# Set variables
project_root := justfile_directory()
venv_path := project_root + "/venv"
python_path := venv_path + "/bin/python"

# Default recipe (shows available tasks)
default:
    @just --list

# Fast test execution with parallel processing
test-fast:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    pytest -n auto --maxfail=5 --durations=10 --ignore=tests/integration --ignore=tests/persona --ignore=tests/test_cli_regression.py --ignore=scripts/semantic_crawler/test_python_setup.py

# Full end-to-end test suite (replaces test_all.sh)
test-all:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "🧪 Running IntelForge End-to-End Test Suite"
    echo "============================================="
    
    echo "1. CLI Smoke Test..."
    python tests/smoketest_all_cli.py
    
    echo "2. Data Integrity Validation..."
    python -m scripts.validation.data_integrity_validator
    
    echo "3. Health Contract Test..."
    python -m pytest tests/test_health_contract_passes.py -v
    
    echo "4. Security Health Check..."
    python -c "
    from scripts.utils.vector_security_manager import VectorSecurityManager
    sm = VectorSecurityManager()
    health = sm.get_security_health_check()
    print('Security Health Check:')
    for component, status in health.items():
        print(f'  {component}: {status}')
    "
    
    echo "============================================="
    echo "✅ All tests completed successfully!"

# Multi-tool security scanning (replaces security_scan.sh)
security-scan:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "🔒 Running multi-tool security scan..."
    
    # Ripgrep for fast pattern matching
    rg --json 'secret|password|token' ./scripts || true
    
    # Gitleaks for Git history scanning
    gitleaks detect --source . --report-format json || true
    
    # Semgrep for context-aware analysis
    semgrep --config p/default . || true
    
    # TruffleHog for entropy-based detection
    trufflehog filesystem --directory . --json || true
    
    # Nuclei vulnerability scanning
    if command -v nuclei &> /dev/null; then
        echo "Running nuclei vulnerability scan..."
        nuclei -t security/nuclei-templates/ -u http://localhost:8080 -silent || true
    else
        echo "nuclei not found, skipping vulnerability scan"
    fi
    
    echo "✅ Security scan completed"

# Performance benchmarking
benchmark-all:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "📊 Running performance benchmarks..."
    
    # CLI benchmarking with hyperfine
    hyperfine --warmup 3 'python scripts/cli.py --help'
    
    # Rust components benchmarking (if available)
    if [ -f "scripts/semantic_crawler/rust_tests/Cargo.toml" ]; then
        cargo bench --manifest-path scripts/semantic_crawler/rust_tests/Cargo.toml
    fi
    
    # Load testing with k6 (if available)
    if [ -f "tests/load/cli_load_test.js" ]; then
        k6 run tests/load/cli_load_test.js
    fi
    
    echo "✅ Benchmarks completed"

# Security fuzzing with cargo-fuzz
fuzz-test TARGET="fuzz_target_1" DURATION="60s":
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "🔍 Running security fuzzing for {{TARGET}}..."
    
    if [ -f "scripts/semantic_crawler/rust_tests/Cargo.toml" ]; then
        cd scripts/semantic_crawler/rust_tests
        cargo fuzz run {{TARGET}} -- -max_total_time={{DURATION}}
        echo "✅ Fuzzing completed for {{TARGET}}"
    else
        echo "❌ Rust project not found"
    fi

# Run all fuzz targets
fuzz-all DURATION="30s":
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "🔍 Running all fuzz targets..."
    
    if [ -f "scripts/semantic_crawler/rust_tests/Cargo.toml" ]; then
        cd scripts/semantic_crawler/rust_tests
        
        # Initialize fuzz corpus if needed
        if [ ! -d "fuzz/corpus" ]; then
            cargo fuzz init
        fi
        
        # Run each fuzz target
        targets=("fuzz_target_1" "fuzz_url_validation" "fuzz_content_validation" "fuzz_semantic_scoring")
        
        for target in "${targets[@]}"; do
            echo "Running fuzz target: $target"
            timeout {{DURATION}} cargo fuzz run "$target" -- -max_total_time={{DURATION}} || true
        done
        
        echo "✅ All fuzz targets completed"
    else
        echo "❌ Rust project not found"
    fi

# Property-based testing with proptest
proptest CASES="1000":
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "🎯 Running property-based tests with {{CASES}} cases..."
    
    if [ -f "scripts/semantic_crawler/rust_tests/Cargo.toml" ]; then
        cd scripts/semantic_crawler/rust_tests
        PROPTEST_CASES={{CASES}} cargo test --test property -- --nocapture
        echo "✅ Property-based testing completed"
    else
        echo "❌ Rust project not found"
    fi

# Run comprehensive property tests
proptest-comprehensive:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "🎯 Running comprehensive property-based tests..."
    
    if [ -f "scripts/semantic_crawler/rust_tests/Cargo.toml" ]; then
        cd scripts/semantic_crawler/rust_tests
        
        # Run with different case counts for thorough testing
        echo "Running basic property tests (1000 cases)..."
        PROPTEST_CASES=1000 cargo test --test property --release
        
        echo "Running extended property tests (10000 cases)..."
        PROPTEST_CASES=10000 cargo test --test property --release
        
        echo "Running stress property tests (100000 cases)..."
        PROPTEST_CASES=100000 cargo test --test property --release
        
        echo "✅ Comprehensive property-based testing completed"
    else
        echo "❌ Rust project not found"
    fi

# Nuclei vulnerability scanning
nuclei-scan TARGET="http://localhost:8080":
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "🔍 Running nuclei vulnerability scan on {{TARGET}}..."
    
    if command -v nuclei &> /dev/null; then
        # Update nuclei templates
        nuclei -update-templates
        
        # Run custom templates
        if [ -d "security/nuclei-templates/" ]; then
            echo "Running custom IntelForge security templates..."
            nuclei -t security/nuclei-templates/ -u {{TARGET}} -json -o logs/nuclei_custom_scan.json
        fi
        
        # Run community templates for web apps
        echo "Running community web application templates..."
        nuclei -t web-extensions,exposures,misconfiguration -u {{TARGET}} -json -o logs/nuclei_web_scan.json
        
        # Run API security templates
        echo "Running API security templates..."
        nuclei -t api,graphql -u {{TARGET}} -json -o logs/nuclei_api_scan.json
        
        echo "✅ Nuclei vulnerability scan completed"
        echo "📊 Results saved to logs/nuclei_*.json"
    else
        echo "❌ nuclei not found. Install with: wget -q -O nuclei.zip https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_*_linux_amd64.zip && unzip nuclei.zip && mv nuclei ~/.local/bin/"
    fi

# Comprehensive nuclei security audit
nuclei-audit:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "🔍 Running comprehensive nuclei security audit..."
    
    if command -v nuclei &> /dev/null; then
        # Create results directory
        mkdir -p logs/nuclei_audit
        
        # Update templates
        nuclei -update-templates
        
        # Scan local services
        echo "Scanning local services..."
        nuclei -t security/nuclei-templates/ -u http://localhost:8080 -json -o logs/nuclei_audit/local_scan.json || true
        
        # Scan for common vulnerabilities
        echo "Scanning for common web vulnerabilities..."
        nuclei -t cves,vulnerabilities,exposures -u http://localhost:8080 -json -o logs/nuclei_audit/vulnerability_scan.json || true
        
        # Scan for misconfigurations
        echo "Scanning for misconfigurations..."
        nuclei -t misconfiguration,default-logins -u http://localhost:8080 -json -o logs/nuclei_audit/misconfig_scan.json || true
        
        # Scan for information disclosure
        echo "Scanning for information disclosure..."
        nuclei -t exposures,files,directories -u http://localhost:8080 -json -o logs/nuclei_audit/info_disclosure_scan.json || true
        
        # Generate summary report
        echo "📊 Generating nuclei audit summary..."
        cat logs/nuclei_audit/*.json | jq -s '.' > logs/nuclei_audit/full_report.json
        
        echo "✅ Nuclei security audit completed"
        echo "📁 Full audit results: logs/nuclei_audit/"
    else
        echo "❌ nuclei not found. Please install nuclei first."
    fi

# Production readiness check
production-check:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    python scripts/production_readiness_checker.py --quick

# Health monitoring (replaces monitoring_wrapper.sh functionality)
health-check:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    python scripts/cli.py health --json --strict

# Continuous monitoring (replaces monitoring_wrapper.sh)
monitor:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    python scripts/continuous_monitoring.py

# Setup monitoring cron jobs (replaces setup_monitoring_cron.sh)
setup-monitoring:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "Setting up IntelForge production monitoring..."
    
    # Create log directories
    mkdir -p logs/cron logs/ttr logs/performance
    
    # Create temporary cron file with proper escaping
    echo "# IntelForge Production Monitoring - Every 5 minutes" > /tmp/intelforge_cron
    echo "*/5 * * * * cd {{project_root}} && ~/.local/bin/just monitor >> logs/cron_monitoring.log 2>&1" >> /tmp/intelforge_cron
    echo "" >> /tmp/intelforge_cron
    echo "# TTR Tracking with Alerts - Every 15 minutes" >> /tmp/intelforge_cron
    echo "*/15 * * * * cd {{project_root}} && ~/.local/bin/just ttr-track >> logs/ttr_cron.log 2>&1" >> /tmp/intelforge_cron
    echo "" >> /tmp/intelforge_cron
    echo "# Performance Monitoring - Every 10 minutes" >> /tmp/intelforge_cron
    echo "*/10 * * * * cd {{project_root}} && ~/.local/bin/just performance-monitor >> logs/performance_cron.log 2>&1" >> /tmp/intelforge_cron
    echo "" >> /tmp/intelforge_cron
    echo "# Daily health report generation - Every day at 8:00 AM" >> /tmp/intelforge_cron
    echo "0 8 * * * cd {{project_root}} && ~/.local/bin/just health-check > logs/daily_health_\$(date +%Y%m%d).json 2>&1" >> /tmp/intelforge_cron
    
    if crontab -l 2>/dev/null | grep -q "IntelForge Production Monitoring"; then
        echo "WARNING: IntelForge monitoring cron jobs already exist"
        echo "Use 'crontab -e' to manually manage existing entries"
    else
        echo "Adding cron jobs..."
        (crontab -l 2>/dev/null; cat /tmp/intelforge_cron) | crontab -
        echo "✅ Cron jobs added successfully!"
    fi
    
    rm -f /tmp/intelforge_cron

# TTR tracking
ttr-track:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    python scripts/utils/ttr_tracker.py --alert-threshold 300

# Performance monitoring
performance-monitor:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    python scripts/utils/performance_monitor.py --alert-on-threshold

# Full build and test pipeline
build-all:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "🚀 Running full build and test pipeline..."
    
    # Run tests
    just test-fast
    
    # Security scanning
    just security-scan
    
    # Performance benchmarking
    just benchmark-all
    
    # Production readiness check
    just production-check
    
    echo "✅ Build pipeline completed successfully!"

# Clean up logs and temporary files
clean:
    #!/usr/bin/env bash
    echo "🧹 Cleaning up temporary files..."
    rm -rf logs/temp_*
    rm -rf __pycache__
    find . -name "*.pyc" -delete
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    echo "✅ Cleanup completed"

# Development environment setup
dev-setup:
    #!/usr/bin/env bash
    echo "🔧 Setting up development environment..."
    
    # Activate virtual environment
    source {{venv_path}}/bin/activate
    
    # Install development dependencies
    pip install -r requirements.txt
    
    # Setup Git hooks
    if [ -f "scripts/setup_git_hooks.sh" ]; then
        bash scripts/setup_git_hooks.sh
    fi
    
    echo "✅ Development environment ready"

# Show system status
status:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "📊 IntelForge System Status"
    echo "=========================="
    
    # Health check
    echo "🏥 Health Status:"
    just health-check
    
    echo ""
    echo "🔒 Security Status:"
    python -c "
    from scripts.utils.vector_security_manager import VectorSecurityManager
    sm = VectorSecurityManager()
    health = sm.get_security_health_check()
    for component, status in health.items():
        print(f'  {component}: {status}')
    "
    
    echo ""
    echo "📈 Performance Status:"
    python scripts/production_readiness_checker.py --quick

# Validate naming convention (replaces validate_naming.sh)
validate-naming:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    python scripts/validation/naming_validator.py

# Create documentation (replaces create_doc.sh)
create-doc NAME CATEGORY="IMP" PRIORITY="C":
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    python scripts/create_documentation.py --name "{{NAME}}" --category "{{CATEGORY}}" --priority "{{PRIORITY}}"

# Run specific test category
test-category CATEGORY:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    pytest -n auto -m "{{CATEGORY}}" -v

# Interactive development mode with file watching
dev-watch:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "👀 Watching for file changes..."
    if command -v watchexec &> /dev/null; then
        watchexec -e py,md 'just test-fast'
    else
        echo "❌ watchexec not installed. Install with: cargo install watchexec-cli"
        echo "Falling back to simple file monitoring..."
        while true; do
            sleep 5
            just test-fast
        done
    fi

# Watch for security issues on file changes
security-watch:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "🔒 Watching for security issues on file changes..."
    if command -v watchexec &> /dev/null; then
        watchexec -e py,js,ts,json,yaml,yml,toml,cfg,ini,env --ignore-paths 'logs/*,chroma_storage/*,node_modules/*,venv/*' 'just security-scan'
    else
        echo "❌ watchexec not installed. Install with: cargo install watchexec-cli"
        exit 1
    fi

# Watch for changes and run linting
lint-watch:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "🔍 Watching for code style issues..."
    if command -v watchexec &> /dev/null; then
        watchexec -e py --ignore-paths 'logs/*,chroma_storage/*,node_modules/*,venv/*' 'black --check . && ruff check .'
    else
        echo "❌ watchexec not installed. Install with: cargo install watchexec-cli"
        exit 1
    fi

# Watch for changes and run type checking
type-watch:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "🔍 Watching for type issues..."
    if command -v watchexec &> /dev/null; then
        watchexec -e py --ignore-paths 'logs/*,chroma_storage/*,node_modules/*,venv/*' 'mypy scripts/ --ignore-missing-imports'
    else
        echo "❌ watchexec not installed. Install with: cargo install watchexec-cli"
        exit 1
    fi

# Watch for changes and run performance benchmarks
benchmark-watch:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "📊 Watching for performance changes..."
    if command -v watchexec &> /dev/null; then
        watchexec -e py --ignore-paths 'logs/*,chroma_storage/*,node_modules/*,venv/*' 'hyperfine --warmup 3 --runs 5 "python scripts/cli.py --help"'
    else
        echo "❌ watchexec not installed. Install with: cargo install watchexec-cli"
        exit 1
    fi

# Watch for changes and run documentation validation
docs-watch:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "📚 Watching for documentation changes..."
    if command -v watchexec &> /dev/null; then
        watchexec -e md,rst,txt --ignore-paths 'logs/*,chroma_storage/*,node_modules/*,venv/*' 'just validate-naming'
    else
        echo "❌ watchexec not installed. Install with: cargo install watchexec-cli"
        exit 1
    fi

# Database operations
db-backup:
    #!/usr/bin/env bash
    source {{venv_path}}/bin/activate
    echo "💾 Creating database backup..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    cp -r chroma_storage chroma_storage_backup_$timestamp
    echo "✅ Backup created: chroma_storage_backup_$timestamp"

# Show help for all commands
help:
    @echo "IntelForge Task Runner - Available Commands:"
    @echo "=========================================="
    @just --list
    @echo ""
    @echo "Common workflows:"
    @echo "  just dev-setup     - Set up development environment"
    @echo "  just test-all      - Run full test suite"
    @echo "  just build-all     - Complete build and test pipeline"
    @echo "  just status        - Show system status"
    @echo "  just security-scan - Run security analysis"
    @echo "  just clean         - Clean up temporary files"
    @echo ""
    @echo "Monitoring:"
    @echo "  just setup-monitoring - Configure cron jobs"
    @echo "  just monitor          - Run continuous monitoring"
    @echo "  just health-check     - Check system health"