# Performance Regression Test Report

**Date**: 2025-07-16 23:06:29
**Platform**: Linux 6.11.0-29-generic
**Python**: 3.12.3

## Summary

- **Total Tests**: 3
- **Passed**: 0 ✅
- **Improved**: 3 🚀
- **Degraded**: 0 ⚠️
- **Regressed**: 0 ❌
- **No Baseline**: 0

## Detailed Results

| Test | Mean Time | Std Dev | Baseline | Regression | Verdict |
|------|-----------|---------|----------|------------|---------|
| python -m scripts.cli status --skip-vali... | 0.184s | 0.003s | 0.500s | 0.37x | ✅ IMPROVED |
| python -m scripts.cli status --detailed... | 0.181s | 0.005s | 2.000s | 0.09x | ✅ IMPROVED |
| python -m scripts.cli status --json... | 0.176s | 0.003s | 1.000s | 0.18x | ✅ IMPROVED |