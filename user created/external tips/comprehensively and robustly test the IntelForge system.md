# 🧪 IntelForge Comprehensive Testing Plan (2025)

This plan maps your implementation architecture to a battle-tested QA strategy using the best-in-class tools already present in your stack.

It aligns fully with the tools outlined in `testing_tools_stack.json` and the implementation details in `IMP_A_IMPLEMENTATION_GUIDE_20250714_v1_CL.md`.

---

## ✅ Overview: Tool-to-Phase Alignment

| Phase | Goal                                 | Tools (Python)                                 | Tools (Rust)                            |
| ----- | ------------------------------------ | ---------------------------------------------- | --------------------------------------- |
| 1     | Core CLI, logic, async validation    | `pytest`, `pytest-asyncio`, `hypothesis`       | `cargo test`, `tokio`                   |
| 2     | Semantic & enhanced module testing   | `snapshottest`, `deepdiff`                     | `insta`, `criterion`, `cargo-insta`     |
| 3     | Fuzzing and edge case validation     | `atheris` (3.10), `hypothesis` fuzz mode       | `cargo-fuzz`, `arbitrary`, `quickcheck` |
| 4     | Observability, logging, failures     | `pytest`, `pytest-approvaltests`, `coverage`   | `cargo-nextest`, `logtest`              |
| 5     | Performance benchmarking             | `pytest-benchmark`, `timeit`, `py-spy`         | `criterion`, `hyperfine`                |
| 6     | Load testing and resource resilience | `k6`, `stress-ng`, `memory-profiler`, `psutil` | `stress`, `cargo-bench`                 |
| 7     | Mutation & coverage analysis         | `mutmut`, `pytest-cov`, `cosmic-ray` (opt)     | `cargo-mutants`, `grcov`                |

---

## 🧩 Phase 1: CLI & Core Logic Validation

* **Target:** All commands in `cli.py`, fallback logic, data routing
* **Tools:**

  * `pytest`, `pytest-asyncio`: full test coverage of CLI functions
  * `hypothesis`: property-based tests for input parsers

**Tests:**

* CLI returns correct exit codes
* Commands route to correct subprocess/scripts
* Async crawlers run without deadlocks

---

## 📦 Phase 2: Enhanced Semantic Modules + Snapshot Regression

* **Target:** `EnhancedResearchGapDetector`, `IntelligentKnowledgeGraph`, `adaptive_thresholding`
* **Tools:**

  * Python: `snapshottest`, `deepdiff`
  * Rust: `cargo test`, `insta`

**Tests:**

* Stable outputs across versions
* AI-generated results match gold-standard snapshots
* Fingerprints regenerated only when changes are valid

---

## 🧪 Phase 3: Fuzzing + Fault Injection

* **Target:** `content_validators`, response normalization, URL parsing
* **Tools:**

  * Python: `atheris`, `hypothesis`
  * Rust: `cargo-fuzz`, `quickcheck`

**Tests:**

* Inject corrupted JSON, malformed HTML
* Ensure TTR tracking and retry logic holds
* Validate all validators return safe fallbacks

---

## 🔭 Phase 4: Observability + Failure Monitoring

* **Target:** `system_health_monitor.py`, `crawl_failure_logger.py`, metadata indexer
* **Tools:**

  * Python: `pytest`, `pytest-approvaltests`, `loguru`
  * Rust: `cargo-nextest`, log inspection tools

**Tests:**

* Simulate crashes → logs & dashboards reflect failure
* Output logs hash-matched to fingerprints
* Timeout behavior handled and logged correctly

---

## 🚀 Phase 5: Performance Benchmarking

* **Target:** Numba optimizations, vector operations, backtesting
* **Tools:**

  * Python: `pytest-benchmark`, `py-spy`, `timeit`
  * Rust: `criterion`, `cargo bench`, `hyperfine`

**Tests:**

* Compare baseline Python to JIT’d vector pipeline
* Validate `vectorbt`, `polars`, Chroma throughput
* Time-to-index and embedding latency <1s

---

## 💣 Phase 6: Load + Stress Testing

* **Target:** Async crawler, vector db, Claude code loop
* **Tools:**

  * Python: `k6`, `psutil`, `memory-profiler`, `stress-ng`
  * Rust: `stress`, `cargo bench`, system tools

**Tests:**

* Simulate 100+ concurrent async crawl jobs
* Observe RAM, CPU, disk utilization across burst loads
* Catch memory leaks in semantic enrichment + embeddings

---

## 🧬 Phase 7: Mutation Testing + Coverage Validation

* **Target:** Test suite completeness + failure sensitivity
* **Tools:**

  * Python: `mutmut`, `cosmic-ray`, `pytest-cov`
  * Rust: `cargo-mutants`, `grcov`

**Tests:**

* Verify tests break correctly when key logic is altered
* Validate coverage over CLI, semantic pipeline, anti-detection logic
* Mutation diff report across time to detect test rot

---

## 🛠️ Additional Infrastructure Recommendations

* **GitHub Actions Matrix:** Split tests by CLI/snapshot/fuzz/benchmark stages
* **Makefile**:

  ```make
  test: pytest
  benchmark: pytest-benchmark
  fuzz: python fuzz/fuzz_url_parser.py
  snapshot: pytest --snapshot-update
  ``
  ```
* **Artifact Paths:**

  * `.snapshots/`: Snapshot test hashes
  * `logs/`: Failures, system reports
  * `benchmarks/`: CSV/MD performance logs

---

## ✅ Final Review Metrics

| Metric            | Target                 |
| ----------------- | ---------------------- |
| CLI Test Coverage | 100%                   |
| Snapshot Drift    | <2% week-over-week     |
| TTR Tracking      | No unlogged exceedance |
| Memory Spikes     | <2.5x baseline         |
| Benchmark Gap     | <20% vs reported max   |
| Mutant Kill Rate  | >95%                   |

---

This redesigned plan ensures **total coverage** of IntelForge’s hybrid codebase while leveraging the strongest prebuilt testing tools available in both Python and Rust ecosystems.

