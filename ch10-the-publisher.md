# Chapter 10 — The Publisher: How You List Your Tool

*Part 2: The MCP Registry — A Real Backend, Explained*

---

## The Analogy

You have built an app. It works great. Your friends love it. Now you want to put it in the App Store so the whole world can find it.

You don't email Apple and attach your app. You use **Xcode** — Apple's official development tool — which has a built-in "submit to App Store" button. Behind the scenes, that button:
1. Checks your app meets Apple's requirements
2. Asks for your Apple developer ID (authentication)
3. Packages everything up correctly
4. Submits it to Apple's servers
5. Tells you if anything went wrong

The MCP Registry has an equivalent: the **`mcp-publisher`** CLI (Command Line Interface). It is a tool that developers run in their terminal to publish their MCP servers. It handles the entire submission process so the developer doesn't have to write raw HTTP requests by hand.

---

## The Concept

A **CLI (Command Line Interface)** is a program you run by typing commands in a terminal — a text window where you give instructions directly to your computer.

You might have seen this kind of window in movies (hackers typing furiously on black screens with green text). In reality, the terminal is just another way to interact with software — text-based instead of button-based.

The `mcp-publisher` CLI has four commands:

| Command | What it does | App Store analogy |
|---------|-------------|------------------|
| `mcp-publisher init` | Creates a `server.json` template | Creates an app submission form |
| `mcp-publisher login` | Authenticates with the Registry | Signs in with your Apple ID |
| `mcp-publisher validate` | Checks your `server.json` locally | Runs the App Store pre-checks |
| `mcp-publisher publish` | Submits your server to the Registry | Clicks "Submit to App Store" |

### The `server.json` File

Everything the Registry needs to know about your tool lives in one file: `server.json`. This is the application form. Here is a realistic example:

```json
{
  "$schema": "https://registry.modelcontextprotocol.io/schema/2025-12-11.json",
  "name": "io.github.abhay/calendar-mcp",
  "description": "Read and manage your Google Calendar from AI agents",
  "version": "1.0.0",
  "repository": {
    "url": "https://github.com/abhay/calendar-mcp",
    "type": "github"
  },
  "packages": [
    {
      "registry": "npm",
      "name": "@abhay/calendar-mcp",
      "version": "1.0.0",
      "runtimeArguments": ["--port", "3000"]
    }
  ]
}
```

---

## System Diagram

```
THE PUBLISH WORKFLOW

  Developer's laptop              MCP Registry Server
  ─────────────────               ───────────────────
  
  1. mcp-publisher init
     └─→ creates server.json
  
  2. mcp-publisher validate
     └─→ runs local checks (Ch 9)
         └─→ PASS / show errors
  
  3. mcp-publisher login
     └─→ POST /auth/login ──────────────────────────►
                           ◄──── JWT token (5 min) ──
         └─→ saves token to ~/.mcp-publisher/token.json
  
  4. mcp-publisher publish
     └─→ reads server.json
         reads token
         POST /publish ────────────────────────────►
         Authorization: Bearer <jwt>                 │
         Body: { ...server.json contents... }        │
                                                    ├── Auth middleware (Ch 7)
                                                    ├── Validator (Ch 9)
                                                    ├── Database INSERT (Ch 6)
         ◄──── 201 Created ────────────────────────
     └─→ "Published successfully!"
```

---

## The Real Code

Let's follow a publish request through the actual code in `registry-main/cmd/publisher/commands/publish.go`:

```go
func PublishCommand(args []string) error {
    // Step 1: Read the server.json file from disk
    serverData, err := os.ReadFile("server.json")
    if err != nil {
        return fmt.Errorf("server.json not found. Run 'mcp-publisher init' to create one")
    }

    // Step 2: Parse the JSON — make sure it's valid JSON at minimum
    var serverJSON apiv0.ServerJSON
    if err := json.Unmarshal(serverData, &serverJSON); err != nil {
        return fmt.Errorf("invalid server.json: %w", err)
    }

    // Step 3: Load the saved JWT token from the previous login
    tokenPath := filepath.Join(homeDir, ".mcp-publisher/token.json")
    tokenData, err := os.ReadFile(tokenPath)
    if err != nil {
        return errors.New("not authenticated. Run 'mcp-publisher login' first")
    }

    // Step 4: Send it all to the Registry API
    response, err := http.Post(
        "https://registry.modelcontextprotocol.io/v0/publish",
        "application/json",
        bytes.NewReader(serverData),
    )

    // Step 5: Report the result
    if response.StatusCode == 200 {
        fmt.Println("Published successfully!")
    } else {
        fmt.Printf("Failed: %s\n", response.Body)
    }
}
```

Five clear steps:
1. Read the local file
2. Check it's valid JSON
3. Load your stored token (from a previous `mcp-publisher login`)
4. Send it to the Registry
5. Report success or failure

This is a **complete user flow** encoded in code: from a file on your laptop to a live entry in a global registry.

### What Happens on the Server Side?

When the Registry receives this request:
1. The **router** (Chapter 8) matches `POST /publish` → `PublishServer` handler
2. The **auth middleware** (Chapter 7) checks the JWT token
3. The **validator** (Chapter 9) runs the full validation suite
4. If everything passes, the **database** (Chapter 6) stores the new record

Every chapter we have covered comes together in this one operation.

---

## 🔬 Lab Activity — Simulate the Full Publish Workflow

**What you'll build:** A `server.json` for your own tool idea, a local validator script, and a Python script that simulates the complete publish flow — validate → authenticate → submit — exactly as `mcp-publisher` does.

**Time:** ~25 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch10-publisher
cd C:\labs\ch10-publisher
```

---

**2. Create your `server.json`.**

```powershell
notepad server.json
```
Fill in your own tool idea (or use this example):
```json
{
  "name": "io.github.yourname/homework-checker",
  "description": "Checks your homework calendar and surfaces upcoming deadlines. Connects to Google Calendar and returns tasks due within 7 days.",
  "version": "0.1.0",
  "repository": {
    "url": "https://github.com/yourname/homework-checker",
    "type": "github"
  },
  "packages": [
    {
      "registry": "npm",
      "name": "@yourname/homework-checker",
      "version": "0.1.0"
    }
  ]
}
```
Replace `yourname` with your actual name or handle.

---

**3. Create the file `publisher.py`.**

```powershell
notepad publisher.py
```
Paste:
```python
import json
import re
import sys

# ---- Step 1: VALIDATE ----
def validate(data):
    errors = []
    for field in ["name", "description", "version", "packages"]:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")

    if "name" in data:
        name_re = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*/[a-zA-Z0-9][a-zA-Z0-9._-]*$')
        if not name_re.match(data["name"]):
            errors.append(f"name '{data['name']}' must follow 'namespace/tool' format")

    if "version" in data:
        if any(data["version"].startswith(r) for r in ["^","~",">=","<=",">","<","*","latest"]):
            errors.append(f"version '{data['version']}' is a range — use exact semver like '1.2.3'")
        elif not re.match(r'^\d+\.\d+\.\d+', data["version"]):
            errors.append(f"version '{data['version']}' must follow MAJOR.MINOR.PATCH format")

    if "packages" in data and isinstance(data["packages"], list):
        if len(data["packages"]) == 0:
            errors.append("packages cannot be empty")

    if "description" in data and len(data.get("description","").strip()) < 15:
        errors.append("description is too short — write at least 15 characters")

    return errors

# ---- Step 2: AUTHENTICATE (simulated) ----
def authenticate(username):
    import base64, json, hmac, hashlib, time
    secret = b"registry-secret-key"
    payload = {"sub": username, "iss": "mcp-registry", "exp": int(time.time()) + 300}
    p = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    h = base64.urlsafe_b64encode(b'{"alg":"HS256"}').rstrip(b"=").decode()
    sig = base64.urlsafe_b64encode(
        hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest()
    ).rstrip(b"=").decode()
    return f"{h}.{p}.{sig}"

# ---- Step 3: PUBLISH (simulated) ----
def publish(data, token):
    # In real life: POST https://registry.modelcontextprotocol.io/v0/publish
    # Here we simulate the server response
    print(f"  Sending POST /v0/publish")
    print(f"  Authorization: Bearer {token[:20]}...")
    print(f"  Body: {json.dumps(data)[:80]}...")
    print(f"  Server response: 201 Created")
    return {"status": 201, "message": f"Published '{data['name']}' successfully"}

# ---- Main workflow ----
print("=== mcp-publisher simulation ===\n")

# Read server.json
try:
    with open("server.json") as f:
        server_data = json.load(f)
    print(f"Read server.json: '{server_data.get('name', '???')}'")
except FileNotFoundError:
    print("ERROR: server.json not found. Create it first.")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"ERROR: server.json is not valid JSON: {e}")
    sys.exit(1)

# Validate
print("\n[Step 1] Validating...")
errors = validate(server_data)
if errors:
    print(f"  VALIDATION FAILED — {len(errors)} error(s):")
    for e in errors:
        print(f"    ✗ {e}")
    print("\nFix these errors before publishing.")
    sys.exit(1)
print("  ✓ All checks passed")

# Authenticate
print("\n[Step 2] Authenticating...")
token = authenticate("github:yourname")
print(f"  ✓ Token issued (valid 5 minutes): {token[:30]}...")

# Publish
print("\n[Step 3] Publishing to Registry...")
result = publish(server_data, token)
print(f"\n  ✓ {result['message']}")
print(f"\n=== Done. Your tool is now in the Registry. ===")
```

**4. Run the publisher.**

```powershell
python publisher.py
```
✅ You should see:
```
=== mcp-publisher simulation ===

Read server.json: 'io.github.yourname/homework-checker'

[Step 1] Validating...
  ✓ All checks passed

[Step 2] Authenticating...
  ✓ Token issued (valid 5 minutes): eyJhbGciOiJIUzI1NiJ9...

[Step 3] Publishing to Registry...
  Sending POST /v0/publish
  Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
  Body: {"name": "io.github.yourname/homework-checker"...
  Server response: 201 Created

  ✓ Published 'io.github.yourname/homework-checker' successfully

=== Done. Your tool is now in the Registry. ===
```

**5. Test with a broken `server.json`.**

Create a second file to see what failures look like:
```powershell
notepad bad_server.json
```
Paste:
```json
{
  "name": "My Broken Tool!!!",
  "description": "short",
  "version": "^1.0.0"
}
```
Then run:
```powershell
python -c "
import json, sys
sys.argv = ['']
import publisher
" 2>&1
```
Or just rename it temporarily:
```powershell
copy server.json server_backup.json
copy bad_server.json server.json
python publisher.py
copy server_backup.json server.json
```
✅ You should see 4 validation errors before any authentication attempt.

**What you just built:** A working simulation of all four `mcp-publisher` steps — read, validate, authenticate (JWT), publish — mirroring the real `registry-main/cmd/publisher/commands/publish.go` workflow.

---

> **🌍 Real World**
> The `npm publish` command works identically to this simulation: it reads `package.json`, validates required fields, authenticates you with npm's registry via a stored token, then sends a POST request to `registry.npmjs.org`. The Homebrew package manager for macOS uses the same pattern — a CLI wrapping a validated JSON submission to a central registry. When a developer publishes a Python package with `twine upload`, it authenticates against PyPI and POSTs the package metadata. The `mcp-publisher` CLI you simulated here is the same pattern, purpose-built for AI tools.

---

## Connecting Part 2

You now understand the complete lifecycle of the MCP Registry:

```
Developer writes server.json
    → mcp-publisher validates it locally (Ch 9)
    → mcp-publisher login gets a JWT token (Ch 7)
    → mcp-publisher publish sends it to the API (Ch 4)
    → Router directs it to the PublishServer handler (Ch 8)
    → Auth middleware checks the token (Ch 7)
    → Validator runs full checks (Ch 9)
    → Database stores the record (Ch 6)
    → AI agents query GET /servers to discover it (Ch 5)
```

This chain — every chapter linking to the next — is what a **backend system** looks like. Not magic. Not mystery. A series of clear, understandable steps.

---

## The Takeaway

The `mcp-publisher` CLI is the developer's App Store submission tool. It wraps the entire publication workflow — reading a local file, authenticating, validating, and sending to the API — into four simple commands. Every step it takes corresponds to a system we have already studied.

---

## The Connection

We have finished the Registry — the city hall and marketplace. Now we meet the other character in our story: the AI agent that uses the Registry. In Part 3, we open up claw-code and see how an AI coding assistant actually works — not as magic, but as a loop, a set of tools, and a memory system.

---

*→ Continue to [Chapter 11 — What Is an AI Agent?](./ch11-what-is-an-ai-agent.md)*
