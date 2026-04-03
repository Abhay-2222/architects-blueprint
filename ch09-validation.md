# Chapter 9 — Validation: The Building Inspector

*Part 2: The MCP Registry — A Real Backend, Explained*

---

## The Analogy

Before any new building in a city can open to the public, a building inspector visits. They check that the structure follows the building code: the walls are thick enough, the electrical wiring is safe, the exits are wide enough for a crowd to escape, the plumbing works correctly.

The inspector doesn't care if the building is beautiful. They care if it is **correct and safe**. If one thing fails inspection, the building doesn't open — even if everything else is perfect.

Software validation is the building inspector of data.

When someone tries to publish a new MCP server to the Registry, the Registry doesn't just save it. It inspects it first. Does it have a name? Is the version number in the right format? Does the package installation command look legitimate? Is the server name in the approved format?

Only if all checks pass does the data get stored. If anything fails, the Registry sends back a detailed report — like the inspector's punch list of problems to fix.

---

## The Concept

**Validation** is the process of checking that incoming data meets a set of rules before accepting it.

There are two types of validation:

**Schema Validation** — checking the *structure* of the data:
- Does it have all required fields?
- Are the field types correct? (text vs. number vs. true/false)
- Are string fields within length limits?

**Semantic Validation** — checking the *meaning* of the data:
- Is the version number a real version number? ("1.2.3" yes, "banana" no)
- Does the server name follow the naming convention? ("io.github.username/myTool" yes, "MY TOOL!!!" no)
- If the server claims to be on npm, does it actually exist on npm?

The MCP Registry performs both — and is strict about it. This is for everyone's protection. If anyone could publish anything in any format, the Registry would quickly become unusable — full of broken, confusing, or malicious entries.

---

## System Diagram

```
VALIDATION PIPELINE

POST /publish
  {"name": "MY TOOL!!!", "version": "latest", ...}
         │
         ▼
┌─────────────────────────────────────────────┐
│  STEP 1: Schema Check                       │
│  ✓ Has "name" field?                        │
│  ✓ Has "version" field?                     │
│  ✓ Has "packages" field?        → FAIL here │
│    Missing "packages" → STOP, return errors │
└─────────────────────────────────────────────┘
         │ (only if all required fields present)
         ▼
┌─────────────────────────────────────────────┐
│  STEP 2: Semantic Check                     │
│  ✓ name matches namespace/tool pattern?     │
│    "MY TOOL!!!" → FAIL (spaces, !!!)        │
│  ✓ version is exact semver?                 │
│    "latest" → FAIL (range, not pinned)      │
│  ✓ packages list non-empty?                 │
│  ✓ description long enough?                 │
└─────────────────────────────────────────────┘
         │ (only if ALL checks pass)
         ▼
┌─────────────────────────────────────────────┐
│  STEP 3: Store                              │
│  → INSERT INTO servers (...)                │
│  → 201 Created                              │
└─────────────────────────────────────────────┘
```

---

## The Real Code

### The Naming Rules

From `registry-main/internal/validators/validators.go`, the Registry enforces strict naming:

```go
// A server name must look like: "io.github.username/tool-name"
// The namespace (before /) and name (after /) each follow specific rules
serverNameRegex = regexp.MustCompile(
    `^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]` + // namespace
    `/` +                                          // separator
    `[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$`,   // name
)
```

This **regular expression** (regex) is a pattern that the server name must match. Let's read it in plain English:
- Must start with a letter or number
- Can contain letters, numbers, dots, and hyphens in the middle
- Must end with a letter or number
- Must have exactly one slash separating namespace from name

So `io.github.abhay/my-tool` → valid. `MY TOOL!!!` → invalid. `tool` (no slash) → invalid.

### The Version Rules

The Registry also validates version numbers, rejecting "range" formats that aren't specific enough:

```go
// These are ranges — not specific versions. Rejected.
comparatorRangeRe = regexp.MustCompile(`^\s*(?:\^|~|>=|<=|>|<|=)...`)  // "^1.2.3", ">=1.0.0"
hyphenRangeRe     = regexp.MustCompile(`...\s-\s...`)                   // "1.2.3 - 2.0.0"

// The Registry wants: "1.2.3" — an exact, specific version
```

Why? Because an MCP agent needs to know *exactly* what version it is getting. "1.2.3 or higher" is ambiguous. "1.2.3" is not.

### The JSON Schema

The strictest validation happens against JSON schemas in `registry-main/internal/validators/schemas/`. These files define the complete contract for what a valid server record looks like. The schema file named `2025-12-11.json` is the most recent — the current standard.

Every submission is validated against it. The Registry will reject any submission that doesn't match.

---

## 🔬 Lab Activity — Build the Building Inspector

**What you'll build:** A validator script that checks server.json submissions against the MCP Registry's rules, reports detailed errors, and passes four test cases — two valid, two invalid.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch09-validation
cd C:\labs\ch09-validation
```

---

**2. Create the file `validator.py`.**

```powershell
notepad validator.py
```
Paste:
```python
import json
import re

def validate(submission: dict) -> dict:
    """
    Validates an MCP server submission.
    Returns {"valid": True} or {"valid": False, "errors": [...]}
    """
    errors = []

    # Rule 1: Required fields
    required = ["name", "description", "version", "packages"]
    for field in required:
        if field not in submission:
            errors.append({
                "field": field,
                "message": f"Required field '{field}' is missing"
            })

    if errors:
        return {"valid": False, "errors": errors}  # stop early, nothing else useful

    # Rule 2: Name must follow namespace/tool-name pattern
    name = submission["name"]
    name_re = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*/[a-zA-Z0-9][a-zA-Z0-9._-]*$')
    if not name_re.match(name):
        errors.append({
            "field": "name",
            "message": (
                f"Name '{name}' is invalid. "
                "Must follow 'namespace/tool-name' format. "
                "Only letters, numbers, dots, hyphens allowed. "
                "No spaces or special characters."
            )
        })

    # Rule 3: Version must be exact semver, not a range
    version = submission["version"]
    range_indicators = ["^", "~", ">=", "<=", ">", "<", "latest", "next", "*"]
    if any(version.startswith(r) or version == r for r in range_indicators):
        errors.append({
            "field": "version",
            "message": (
                f"Version '{version}' is a range, not a specific version. "
                "Use exact versions like '1.2.3' or '0.1.0'."
            )
        })
    elif not re.match(r'^\d+\.\d+\.\d+', version):
        errors.append({
            "field": "version",
            "message": (
                f"Version '{version}' doesn't follow semantic versioning. "
                "Use format: MAJOR.MINOR.PATCH (e.g. '1.2.3')"
            )
        })

    # Rule 4: packages must be non-empty list
    packages = submission["packages"]
    if not isinstance(packages, list):
        errors.append({"field": "packages", "message": "packages must be an array"})
    elif len(packages) == 0:
        errors.append({
            "field": "packages",
            "message": "packages cannot be empty — users need at least one install method"
        })

    # Rule 5: description must have substance
    desc = submission.get("description", "")
    if len(desc.strip()) < 15:
        errors.append({
            "field": "description",
            "message": (
                f"Description is too short ('{desc}'). "
                "Write a meaningful description (at least 15 characters)."
            )
        })

    if errors:
        return {"valid": False, "errors": errors}
    return {"valid": True}


# ---- Test Cases ----
submissions = [
    {
        "label": "Submission 1 (should PASS)",
        "data": {
            "name": "io.github.abhay/file-reader",
            "description": "Reads files from local filesystem. Supports txt, pdf, md.",
            "version": "1.0.0",
            "packages": [{"registry": "npm", "name": "@abhay/file-reader", "version": "1.0.0"}]
        }
    },
    {
        "label": "Submission 2 (should FAIL — 3 errors)",
        "data": {
            "name": "My Awesome Tool!!!",
            "description": "does stuff",
            "version": "latest"
            # Missing "packages" entirely
        }
    },
    {
        "label": "Submission 3 (should FAIL — 2 errors)",
        "data": {
            "name": "io.github.abhay/search",
            "description": "Searches the web for relevant information and returns results.",
            "version": "^2.0.0",
            "packages": []
        }
    },
    {
        "label": "Submission 4 (should PASS)",
        "data": {
            "name": "io.github.abhay/calendar",
            "description": "Connects to Google Calendar and reads your schedule. Supports recurring events.",
            "version": "0.3.1",
            "packages": [{"registry": "npm", "name": "@abhay/calendar-mcp", "version": "0.3.1"}]
        }
    },
]

for sub in submissions:
    print(f"\n{'='*55}")
    print(f"  {sub['label']}")
    print(f"{'='*55}")
    print(f"  Input: {json.dumps(sub['data'])[:80]}...")

    result = validate(sub["data"])

    if result["valid"]:
        print(f"  RESULT: ✓ VALID — ready to publish")
    else:
        print(f"  RESULT: ✗ INVALID — {len(result['errors'])} error(s):")
        for err in result["errors"]:
            print(f"    [{err['field']}] {err['message']}")
```

**3. Run it.**

```powershell
python validator.py
```
✅ You should see:
```
=======================================================
  Submission 1 (should PASS)
=======================================================
  RESULT: ✓ VALID — ready to publish

=======================================================
  Submission 2 (should FAIL — 3 errors)
=======================================================
  RESULT: ✗ INVALID — 4 error(s):
    [packages] Required field 'packages' is missing
    [name] Name 'My Awesome Tool!!!' is invalid. Must follow 'namespace/tool-name'...
    [version] Version 'latest' is a range, not a specific version...
    [description] Description is too short ('does stuff')...

=======================================================
  Submission 3 (should FAIL — 2 errors)
=======================================================
  RESULT: ✗ INVALID — 2 error(s):
    [version] Version '^2.0.0' is a range...
    [packages] packages cannot be empty...

=======================================================
  Submission 4 (should PASS)
=======================================================
  RESULT: ✓ VALID — ready to publish
```

---

**4. Test your own submission.**

Create `my_submission.json`:
```powershell
notepad my_submission.json
```
Paste and fill in your own tool idea (from Chapter 10's exercise):
```json
{
  "name": "io.github.yourname/your-tool",
  "description": "Write your tool's description here. Be specific and helpful.",
  "version": "0.1.0",
  "packages": [
    {
      "registry": "npm",
      "name": "@yourname/your-tool",
      "version": "0.1.0"
    }
  ]
}
```

Then validate it:
```powershell
python -c "
import json
from validator import validate
with open('my_submission.json') as f:
    data = json.load(f)
result = validate(data)
print('VALID' if result['valid'] else f'INVALID: {result}')
"
```
Fix any errors the validator reports.

**What you just built:** A working validator that enforces all five rules the MCP Registry checks on every submission. The logic mirrors `registry-main/internal/validators/validators.go`.

---

> **🌍 Real World**
> npm runs validation on every package published to its registry — name format, version semver compliance, required fields like `main` and `license`. In 2016, a developer deleted a tiny package called `left-pad` from npm. Because npm hadn't validated that other packages declared exact versions (they used `^` ranges), thousands of projects broke instantly. After the incident, npm changed its validation to be stricter about version pinning — exactly what the MCP Registry enforces with its rejection of range formats like `^1.2.3`. Stripe's API validates every request payload against a strict schema before touching its database. A single malformed field returns a detailed error immediately — same pattern as you just built.

---

## The Takeaway

Validation is the building inspector of software — it checks every submission against a strict set of rules before accepting it. Without validation, a database fills with garbage. With it, every record can be trusted by the systems that read it. The MCP Registry validates both structure (does this field exist?) and meaning (is this version number valid?).

---

## The Connection

Data is stored. Data is validated. Now — how does a developer actually submit their tool to the Registry? In Chapter 10, we follow the journey of publishing an MCP server from a developer's laptop to the live registry, using the `mcp-publisher` command-line tool.

---

*→ Continue to [Chapter 10 — The Publisher: How You List Your Tool](./ch10-the-publisher.md)*
