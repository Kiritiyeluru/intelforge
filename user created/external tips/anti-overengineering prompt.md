Here’s your distilled **anti-overengineering prompt** — use this before you refactor or add any tool:

---

### 🧠 **Overengineering Check Prompt (Before You Build)**

> **Before I add this tool or refactor this code, answer the following:**

1. 🔍 **Problem Size**

   * Is this more than 20 lines of non-trivial logic?
   * ❌ If it’s under 10 lines and works → **don’t replace it**

2. 🔁 **Problem Frequency**

   * Will I solve this again in 3+ places or 2+ times a month?
   * ❌ If it’s a one-off → **keep it simple**

3. ⚙️ **Problem Complexity**

   * Does it involve parsing, async IO, crawling, ML, vector ops, or API quirks?
   * ✅ Yes → use proven tools
   * ❌ If it’s basic control flow or config mapping → **write it yourself**

4. 📈 **Future Growth**

   * Am I building this for 1 case or for 10+ extensions/modules?
   * ❌ If the scale isn’t guaranteed → **YAGNI** (You Aren’t Gonna Need It)

5. 🧮 **Cost vs Value**

   * Will this tool *reduce* 30+ lines of hairy logic or eliminate bugs?
   * ❌ If it just replaces 5 lines with 30 more + boilerplate → **don’t do it**

---

### ✅ Acceptable Reasons to Use Tools:

* “This task has edge cases I don’t want to handle manually”
* “This replaces 50+ lines of logic with 1 line”
* “This will be reused across the system”
* “This adds strong guarantees (e.g. typing, validation, retry)”

---

### ❌ Red Flags That You're Over-Engineering:

* “Let’s use plugin architecture for 5 validators”
* “We might add dynamic loading later”
* “We could make this extensible now”
* “Cleaner separation, even if it's more code”

---

### 🔒 Final Check

> **Is this working, 5–10 lines, and not reused?**
> ✅ Then **leave it alone.**

---

Would you like this as a `reuse_guard.md` file to include in your repo or as a shell prompt reminder for critical decisions?
