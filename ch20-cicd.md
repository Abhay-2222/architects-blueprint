# Chapter 20 — CI/CD: The Factory Assembly Line

*Part 4: Shipping It — From Your Laptop to the World*

---

## The Analogy

Before the assembly line existed, a car was built by a small team of craftsmen who did everything — frame, engine, interior, finishing — from start to finish. Building one car took weeks.

Henry Ford's assembly line changed this. Each worker did one specific job. The car moved from station to station. At each station, the same checks happened every time, in the same order. Quality was consistent. Speed was revolutionary.

**CI/CD is the assembly line for software.**

Every time a developer pushes code — "I made a change, here it is" — the assembly line starts automatically. The code moves through stations: check for style errors → run tests → build the application → scan for security vulnerabilities → deploy to staging → deploy to production.

Each station does its job. If any station fails, the line stops. The defective part doesn't move forward. No human has to watch every step.

---

## The Concept

**CI (Continuous Integration)** — Every code change is automatically built and tested. This catches bugs before they reach users. The word "continuous" means it happens with every single change, not once a week.

**CD (Continuous Deployment/Delivery)** — Every code change that passes CI is automatically deployed — first to a staging environment, then to production. "Delivery" means the code is ready to deploy but a human presses the button. "Deployment" means it deploys automatically.

Together, CI/CD means the time from "developer writes a fix" to "users see the fix" can be minutes instead of weeks.

---

## System Diagram

```
CI/CD PIPELINE (triggered by git push)

Developer: git push → GitHub
                       │
                       ▼
          ┌────────────────────────────┐
          │  CI PIPELINE (GitHub Actions)│
          │                            │
          │  Station 1: Lint           │
          │    golangci-lint → PASS ✓  │
          │         │                  │
          │  Station 2: Tests          │
          │    go test ./... → PASS ✓  │
          │         │                  │
          │  Station 3: Build          │
          │    make build → PASS ✓     │
          │         │                  │
          │  Station 4: Security scan  │
          │    govulncheck → PASS ✓    │
          └────────────┬───────────────┘
                       │ all stations passed
                       ▼
          ┌────────────────────────────┐
          │  CD: Deploy to STAGING     │
          │  (test environment)        │
          │  Smoke tests → PASS ✓      │
          └────────────┬───────────────┘
                       │
                       ▼
          ┌────────────────────────────┐
          │  CD: Deploy to PRODUCTION  │
          │  Rolling update via K8s    │
          │  → Live in minutes         │
          └────────────────────────────┘

If ANY station FAILS → pipeline stops → no deploy → alert sent
```

---

## The Real Code

The MCP Registry's CI/CD pipeline lives in `.github/workflows/`. GitHub Actions runs these automatically. From `ci.yml`:

```yaml
name: CI Pipeline

# Run this pipeline whenever code is pushed to main, or when a pull request is opened
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:

  # Station 1: Build, Lint, and Validate
  build-lint-validate:
    name: Build, Lint, and Validate
    runs-on: ubuntu-latest     # Run on a fresh Ubuntu machine in the cloud
    steps:

    - name: Checkout code      # Get the code from GitHub
      uses: actions/checkout@...

    - name: Set up Go          # Install Go 1.24
      uses: actions/setup-go@...
      with:
        go-version-file: 'go.mod'

    - name: Run lint           # Check code style (no messy code allowed)
      uses: golangci/golangci-lint-action@...

    - name: Validate schemas and examples   # Run the schema validator (Ch 9)
      run: make validate

    - name: Build application  # Compile the Go code
      run: make build

    - name: Run govulncheck    # Scan for known security vulnerabilities
      uses: golang/govulncheck-action@...

  # Station 2: Tests
  tests:
    name: Tests
    runs-on: ubuntu-latest
    steps:
    - name: Run unit tests
      run: go test ./...
```

Each `step` is one task at one station of the assembly line. Notice:
- The pipeline uses pinned action versions (the long hash after `@`) — this prevents a security attack where someone modifies a popular action and your pipeline unknowingly runs malicious code
- The pipeline runs on **every pull request** — not just when code merges. This means bugs are caught before they even enter the main codebase

### The Deployment Pipelines

Three more workflow files handle deployment:

**`deploy-staging.yml`** — Runs when code merges to `main`. Deploys to the staging environment (a full copy of production that only the team uses for testing).

**`deploy-production.yml`** — Triggered manually or by a tagged release. Deploys to the live production environment (what the public uses).

**`release.yml`** — Creates a versioned release, builds binaries for different operating systems, and publishes them.

---

## 🔬 Lab Activity — Write a GitHub Actions Workflow

**What you'll build:** A real GitHub Actions CI workflow file (`.github/workflows/ci.yml`) that lints Python, runs tests, and reports results — matching the structure of `registry-main/.github/workflows/ci.yml`. Then a Python script that simulates the pipeline runner locally.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder and GitHub Actions structure.**

```powershell
mkdir C:\labs\ch20-cicd
mkdir C:\labs\ch20-cicd\.github
mkdir C:\labs\ch20-cicd\.github\workflows
cd C:\labs\ch20-cicd
```

---

**2. Create a simple Python app to test.**

```powershell
notepad app.py
```
Paste:
```python
def validate_name(name):
    """Validate an MCP server name."""
    import re
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._-]*/[a-zA-Z0-9][a-zA-Z0-9._-]*$'
    return bool(re.match(pattern, name))

def validate_version(version):
    """Validate a semver version string."""
    import re
    ranges = ["^", "~", ">=", "<=", ">", "<", "latest", "*"]
    if any(version.startswith(r) for r in ranges):
        return False
    return bool(re.match(r'^\d+\.\d+\.\d+', version))
```

---

**3. Create test file.**

```powershell
notepad test_app.py
```
Paste:
```python
from app import validate_name, validate_version

def test_valid_name():
    assert validate_name("io.github.user/my-tool") == True

def test_invalid_name_spaces():
    assert validate_name("My Tool!!!") == False

def test_invalid_name_no_slash():
    assert validate_name("toolname") == False

def test_valid_version():
    assert validate_version("1.2.3") == True

def test_invalid_version_range():
    assert validate_version("^1.2.3") == False

def test_invalid_version_latest():
    assert validate_version("latest") == False

if __name__ == "__main__":
    tests = [test_valid_name, test_invalid_name_spaces, test_invalid_name_no_slash,
             test_valid_version, test_invalid_version_range, test_invalid_version_latest]
    passed = 0
    for test in tests:
        try:
            test()
            print(f"  ✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {test.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
    exit(0 if passed == len(tests) else 1)
```

---

**4. Create the GitHub Actions workflow file.**

```powershell
notepad .github\workflows\ci.yml
```
Paste:
```yaml
# This mirrors registry-main/.github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    name: Lint, Test, Validate
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install lint tools
        run: pip install pyflakes

      - name: Lint (check for syntax errors)
        run: python -m pyflakes app.py test_app.py

      - name: Run tests
        run: python test_app.py

      - name: Verify app imports successfully
        run: python -c "import app; print('Import OK')"
```

---

**5. Simulate the pipeline locally.**

```powershell
notepad pipeline_runner.py
```
Paste:
```python
import subprocess
import sys

PIPELINE = [
    ("Lint check",   [sys.executable, "-m", "py_compile", "app.py"]),
    ("Run tests",    [sys.executable, "test_app.py"]),
    ("Import check", [sys.executable, "-c", "import app; print('Import OK')"]),
]

print("=== CI Pipeline Runner ===\n")
all_passed = True

for station_name, command in PIPELINE:
    print(f"Station: {station_name}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✓ PASSED")
        if result.stdout.strip():
            for line in result.stdout.strip().splitlines():
                print(f"    {line}")
    else:
        print(f"  ✗ FAILED — pipeline stopped")
        print(f"    {result.stderr.strip()[:200]}")
        all_passed = False
        break
    print()

if all_passed:
    print("✓ All stations passed — ready to deploy")
else:
    print("✗ Pipeline failed — no deployment")
    sys.exit(1)
```

**6. Run the local pipeline simulation.**

```powershell
python pipeline_runner.py
```
✅ You should see all 3 stations pass:
```
=== CI Pipeline Runner ===

Station: Lint check
  ✓ PASSED

Station: Run tests
  ✓ PASSED
    ✓ test_valid_name
    ✓ test_invalid_name_spaces
    ... 6/6 tests passed

Station: Import check
  ✓ PASSED
    Import OK

✓ All stations passed — ready to deploy
```

**7. Introduce a bug and watch the pipeline stop.**

Open `app.py` and break it — add a syntax error:
```powershell
notepad app.py
```
Add `SYNTAX ERROR HERE` on the first line (no quotes), save, then:
```powershell
python pipeline_runner.py
```
✅ You see the pipeline stop at Station 1 with a specific error. Fix the file and run again — it passes.

**What you just built:** A real GitHub Actions workflow YAML and a local pipeline simulator — matching the structure of `registry-main/.github/workflows/ci.yml`. Push the `.github/workflows/ci.yml` to any GitHub repo and it will run automatically on every push.

---

> **🌍 Real World**
> GitHub Actions runs 1 billion workflow runs per month across all repositories. Every major software company uses CI/CD: Google deploys to production thousands of times per day using their internal Blaze/Bazel build system. Amazon deploys every 11.7 seconds on average. The MCP Registry uses `govulncheck` in its CI pipeline — a tool that scans Go code for known security vulnerabilities from the CVE database. When the log4j vulnerability (CVE-2021-44228) was disclosed in 2021, companies with good CI pipelines detected it automatically within hours and deployed fixes within a day. Companies without it were still manually checking months later.

---

## The Takeaway

CI/CD is the automated assembly line that takes every code change from a developer's computer to running in production — automatically, consistently, safely. The MCP Registry's pipeline lints code, runs tests, scans for vulnerabilities, and deploys to staging and production, all triggered by a single `git push`. Zero human intervention required for a successful change.

---

## The Connection

The code is deployed and running. But how do you know it is healthy? How do you know if something is going wrong before users start complaining? In Chapter 21, we build the control room — the monitoring and metrics system that watches everything, always.

---

*→ Continue to [Chapter 21 — Monitoring: The Control Room Dashboard](./ch21-monitoring.md)*
