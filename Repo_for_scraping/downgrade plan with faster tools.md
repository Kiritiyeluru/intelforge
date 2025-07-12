This plan is **well-structured, safe, and realistic** — especially for quant/finance work where raw performance matters. But if you’re aiming for **maximum speed and developer efficiency**, there are a few improvements and substitutions worth considering.

---

## ✅ **What’s Great About Your Plan**

* **System Python untouched** — ✔️ Smart and safe.
* **Pre-downgrade assessment** — ✔️ Good discipline.
* **Use of `pyenv` for isolation** — ✔️ Secure and repeatable.
* **Clean phased rollout with backup and rollback** — ✔️ Professional-level risk management.
* **Realistic target speedup expectations** — ✔️ Ambitious but grounded.

---

## 🔁 **Recommended Improvements (Tooling & Efficiency)**

### 1. 🔄 Replace `pyenv` with `micromamba` (optional but high impact)

| Why                                                                 |
| ------------------------------------------------------------------- |
| `pyenv` builds from source — **slow, flaky** on Ubuntu              |
| `micromamba` is **binary-based**, **instant** setup                 |
| Better dependency isolation & conflict resolution than `uv + pyenv` |
| Native support for `ta-lib`, `numba`, `vectorbt` (via conda-forge)  |

> 🧪 Bonus: With `micromamba`, you can install Python 3.10 + all tools in **under 90 seconds.**

#### Command Example:

```bash
micromamba create -n intelforge python=3.10 vectorbt ta-lib numba -c conda-forge -y
micromamba activate intelforge
```

---

### 2. 🔁 Replace `empyrical` (deprecated) with `btalib` or `finTA`

| Problem                                                         | Solution                                                                          |
| --------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `empyrical` is semi-abandoned, last major release was years ago | Use `btalib` (lightweight TA in pandas) or `finTA` (pure Python, works with 3.10) |
| `empyrical` doesn’t play well with newer pandas/numpy           | Avoid unless you're using `pyfolio` or `alphalens` specifically                   |

---

### 3. ✅ Add **`polars`** for ultra-fast tabular operations

* **100x faster than pandas** for many tasks
* Native Rust-core with multi-threading
* Compatible with Python 3.10
* Great for building vectorbt-like logic if needed

```bash
pip install polars
```

---

### 4. 🚫 Avoid `quantlib-python` unless strictly needed

| Why                                                                                                           |
| ------------------------------------------------------------------------------------------------------------- |
| Complex C++ wrapper, heavy, rarely maintained                                                                 |
| Often breaks with numpy or Boost versions                                                                     |
| Better alternatives for pricing/curve building: `QuantLib via CLI`, or use `QLNet` in .NET via Python interop |

---

### 5. 🧠 Add benchmarking sanity check

Add a separate **"fail fast" test**:

```python
import timeit
print(timeit.timeit('np.log(np.arange(1, 1e6))', setup='import numpy as np', number=10))
```

Run under:

* 3.10 base
* 3.10 + numba
* 3.12 base

Let the numbers validate the speed gains from JIT.

---

## ✅ Final Verdict: Should You Replace Any Tools?

| Tool                     | Replace?                                                 | With                                        |
| ------------------------ | -------------------------------------------------------- | ------------------------------------------- |
| `pyenv`                  | ✅ Optional                                               | `micromamba` (faster, cleaner)              |
| `empyrical`              | ✅ Recommended                                            | `btalib`, `finTA`, or raw numpy/pandas      |
| `quantlib-python`        | ⚠️ Avoid if not strictly required                        | Use CLI wrappers or offload to external API |
| `pandas` (for heavy ops) | ✅ Optional                                               | `polars`                                    |
| `uv`                     | ⚠️ Keep but be aware it doesn't resolve non-wheel issues | `micromamba` will auto-resolve binary deps  |

---

## 🎯 Updated “Lean” Version of Your Plan (If You Want Speed)

```bash
# 1. Install micromamba (one-liner)
curl micro.mamba.pm/install.sh | bash

# 2. Create and activate performance env
micromamba create -n intelforge python=3.10 vectorbt ta-lib numba polars -c conda-forge -y
micromamba activate intelforge

# 3. Run performance benchmarks
python run_perf_tests.py

# 4. Keep system Python untouched, use startup script to toggle envs
```

---

## Summary

✅ Your plan is solid — but can be optimized:

| Area              | Suggestion                                            |
| ----------------- | ----------------------------------------------------- |
| **Speed**         | Use `micromamba` instead of `pyenv`                   |
| **Compatibility** | Avoid `empyrical`, be cautious with `quantlib-python` |
| **Performance**   | Add `polars`, benchmark against native pandas         |
| **Maintenance**   | Use active libraries with Python 3.10 support         |

Let me know if you want the full micromamba setup script + perf test boilerplate.
