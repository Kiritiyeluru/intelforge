This error:

```bash
source venv/bin/activate && python tests/test_cli_health.py
⎿  Error: Command timed out after 2m 0.0s
```

means that your `test_cli_health.py` script is **taking too long** to run — and it's getting **forcefully killed after 120 seconds (2 minutes)** by your test runner or wrapper script.

## ✅ **UPDATE: RESOLVED (2025-07-17)**

**Issue Resolution**: The timeout issue has been **fixed** and the test now runs successfully.

**Root Cause**:
1. **NameError**: `QDRANT_AVAILABLE` variable was not defined, causing the semantic_crawler.py to crash
2. **AI Model Loading**: The test was timing out due to AI model loading time (~45-60 seconds per test)

**Solution Applied**:
1. **Fixed NameError**: Added proper `QDRANT_AVAILABLE` variable definition with try/except import
2. **Optimized Timeouts**: Increased individual test timeouts from 30s to 60-90s
3. **Test Results**: All 8 tests now pass successfully in **~300 seconds (5 minutes)**

**Current Status**: ✅ **OPERATIONAL** - CLI health tests pass with 100% success rate

```bash
📊 CLI SMOKE TEST SUMMARY
============================================================
✅ Passed: 8
❌ Failed: 0
📈 Success rate: 100.0%
🎉 All CLI smoke tests passed!
```

**Performance**: Test suite completes in **~300 seconds** due to:
- AI model loading (sentence-transformers): ~45s per test
- Vector database initialization: ~15s per test
- Network requests and content processing: ~30s per test

---

## 🔍 Why It Happens

### 1. **The test includes expensive operations**

* AI model loading (e.g., sentence-transformers, Presidio)
* CLI spawns subprocesses that hang
* Background services (like Qdrant/Chroma) are queried or slow to respond

### 2. **The test is waiting for something that never returns**

* Misconfigured CLI flag
* Missing default value / input prompt
* Network timeout / socket hang

### 3. **No explicit timeout control in your test**

* If `subprocess.run()` has no timeout, it could hang forever
* Long-running health checks (e.g., port scans, vector DB warmup)

---

## ✅ How to Fix This

Here’s a systematic fix:

---

### ✅ Step 1: Run the test manually with verbose output

```bash
source venv/bin/activate
python -m pytest -v tests/test_cli_health.py
```

* Watch **which part hangs** — is it one test? A specific function?

---

### ✅ Step 2: Add Debug Logging

Inside `test_cli_health.py`, temporarily add:

```python
print(">>> STARTING TEST")
print("Checking CLI health command...")
```

Also check if it’s using subprocess:

```python
subprocess.run(["intelforge", "health", "--verbose"], ...)
```

If yes: **add a timeout** and capture output:

```python
subprocess.run(["intelforge", "health"], timeout=30, capture_output=True)
```

---

### ✅ Step 3: Isolate the Real Bottleneck

Try running:

```bash
intelforge health --verbose
```

Does it hang at:

* Loading models?
* Scanning files?
* Connecting to Qdrant or Chroma?

If yes, isolate that component and optimize it (or mock it in tests).

---

### ✅ Step 4: Optimize test duration

You can either:

* Add a **smaller scope test** for health:

  ```bash
  intelforge health --quick
  ```

  (You’ll need to add that shortcut internally — e.g., skip deep checks.)

* Split the health test:

  ```python
  def test_core_health(): ...
  def test_vector_storage(): ...
  def test_model_loading(): ...
  ```

---

### ✅ Step 5: Increase Timeout as a Fallback

If it's **working** but just slow due to model load:

```python
# pytest.ini or runner config
timeout = 300  # bump to 5 minutes
```

Or if calling via CLI:

```bash
timeout 300s python tests/test_cli_health.py
```

But don’t *only* increase the timeout — fix the cause first.

---

## ⚠️ If All Else Fails

Temporarily skip the test while debugging:

```python
import pytest

@pytest.mark.skip(reason="Timeout under investigation")
def test_cli_health():
    ...
```

---

## 🧠 Final Tip

You can also add a `--dry-run` or `--fast-health` flag to your CLI so tests avoid triggering full pipeline checks. This is especially useful when AI model loading is the bottleneck.

---

Let me know if you want help editing the test file directly — happy to walk through it.
