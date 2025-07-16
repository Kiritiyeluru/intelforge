💡 Verdict for Your Case (Algo trading, scraping, speed-critical):
If you’re relying on:

vectorbt

numba

ta-lib

→ Stick to Python 3.10.13 for now — it’s the most stable + compatible combo for quant performance tooling.

When 3.11 gets full numba/vectorbt support without regressions, then it’s worth switching.

Let me know if you want a ready-made conda or pyenv environment setup script.

Here’s how to **safely downgrade to Python 3.10** on **Ubuntu** (without breaking your system Python):

> ⚠️ **Never touch the system Python** (`/usr/bin/python3`) — it’s used by Ubuntu internals like apt, snap, etc. Downgrade only inside isolated environments.

---

### ✅ Recommended: Install Python 3.10 via **`pyenv`** (non-destructive, safe, isolated)

#### 🔧 Step 1: Install dependencies

```bash
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
libffi-dev liblzma-dev
```

#### 🧰 Step 2: Install `pyenv`

```bash
curl https://pyenv.run | bash
```

Then add this to the end of your `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
```

Apply changes:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

---

#### ⬇️ Step 3: Install Python 3.10.13

```bash
pyenv install 3.10.13
```

---

#### 🧪 Step 4: Create a virtual environment

```bash
pyenv virtualenv 3.10.13 trading-env
pyenv activate trading-env
```

This virtualenv uses Python 3.10 safely, completely isolated.

You can set it project-wide by navigating into your project directory and running:

```bash
pyenv local trading-env
```

Now `python` and `pip` in that folder will always point to Python 3.10.

---

### ✅ Check It Worked:

```bash
python --version
# Should show: Python 3.10.13

which python
# Should show something like: ~/.pyenv/versions/trading-env/bin/python
```

---

### 🧠 Bonus: Avoiding Conflicts

* Don’t alias `python3` globally.
* Never uninstall system Python or change `/usr/bin/python3` links.
* Always use `pyenv`, `virtualenv`, or `conda` for isolation.

---
