# Chapter 3 — Protocols: The Language of Machines

*Part 1: What Is a System?*

---

## The Analogy

Imagine two people, one from Japan and one from Brazil, trying to work together to build a house. One speaks Japanese, the other Portuguese. They stand in front of a pile of bricks and tools and... nothing happens. They can't agree on what to do next.

So they make a decision: they will both learn to speak English. Not because English is the best language — but because they both agreed to use it. Now when one says "hand me the hammer," the other understands. Work begins.

This agreement — "we will use English" — is a **protocol**.

A protocol is not about what to say. It is about *how* to say it so both sides can understand.

Machines have exactly the same problem. A phone in your pocket, a server in Iceland, a smart thermostat on your wall — they are built by different companies, using different hardware, running different software. They need an agreed-upon language to communicate. That language is a protocol.

---

## The Concept

A **protocol** is a set of rules that two systems agree to follow when communicating.

Protocols define:
- **What format messages must be in** (like agreeing to write letters instead of speak)
- **What order things happen in** (like agreeing that you say "hello" before getting to business)
- **What to do when something goes wrong** (like agreeing on what "I didn't understand" looks like)

### The Protocols That Run Your Life

**HTTP (HyperText Transfer Protocol)** — The language of the web. When you type a URL into a browser, your browser sends an HTTP request to a server. The server sends back an HTTP response. Every webpage you have ever seen was delivered via HTTP. It is the most widely used protocol in the world.

**JSON (JavaScript Object Notation)** — Not quite a protocol, but a *format* — a way of structuring data so any machine can read it. It looks like this:

```json
{
  "name": "FileReader MCP",
  "version": "1.2.0",
  "author": "Acme Tools",
  "description": "Reads files from your computer"
}
```

JSON is how the MCP Registry sends data to clients. It is human-readable *and* machine-readable — you can look at it and understand it without a special tool.

**MCP (Model Context Protocol)** — This is the star of our book. MCP is a protocol specifically designed to let AI agents talk to tools. It defines how an agent says "I want to use this tool," how the tool responds, and how errors are handled. Without MCP, every AI agent would have to learn a different language for every tool it wanted to use. With MCP, one protocol works for everything.

---

## System Diagram

```
PROTOCOL = A shared agreement on message format

WITHOUT a protocol:
  Client: "Hello give me servers"      Server: ???  (doesn't understand)
  Client: "Servers please list them"   Server: ???  (still confused)
  ── NOTHING WORKS ──

WITH HTTP + JSON protocol:
  Client: GET /v0/servers HTTP/1.1     Server: 200 OK
          Accept: application/json            {"servers": [...]}
  ── BOTH SIDES UNDERSTAND, EVERY TIME ──

MCP Protocol stack in this book:
  ┌──────────────────────────────────┐
  │  MCP Protocol                   │  ← What AI agents use to call tools
  ├──────────────────────────────────┤
  │  HTTP/HTTPS                     │  ← How requests travel
  ├──────────────────────────────────┤
  │  JSON                           │  ← How data is formatted
  ├──────────────────────────────────┤
  │  TCP/IP                         │  ← How packets are delivered
  └──────────────────────────────────┘
```

---

## The Real Code

The MCP Registry stores information about tools in a structured format defined by JSON schemas. Look at one of the real schema files in the registry:

`registry-main/internal/validators/schemas/2025-12-11.json`

This file defines *the rules* for what a valid MCP server entry must look like. It is the protocol contract — the shared language that every publisher and consumer must agree on.

A simplified version of what it enforces:

```json
{
  "required": ["name", "description", "packages"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Human-readable name of the MCP server"
    },
    "description": {
      "type": "string",
      "description": "What this server does"
    },
    "packages": {
      "type": "array",
      "description": "How to install this server (npm, pip, docker, etc.)"
    }
  }
}
```

This is a contract. If you try to register an MCP server without a `name`, the Registry will reject it — because you have broken the protocol. You have tried to communicate in a way the other side cannot understand.

The Registry checks every incoming submission against this schema in `internal/validators/validators.go`. Think of it as a translator who refuses to relay messages that aren't in the agreed language.

---

## 🔬 Lab Activity — Inspect a Real Protocol in Action

**What you'll build:** A `server.json` file (the MCP Registry's protocol format), plus a Python script that validates it against the protocol rules and shows the raw HTTP headers — the protocol "envelope" — of a real request.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch03-protocols
cd C:\labs\ch03-protocols
```

---

**2. Create the file `server.json`.**

This is the MCP Registry protocol format for registering a tool:
```powershell
notepad server.json
```
Paste exactly:
```json
{
  "$schema": "https://registry.modelcontextprotocol.io/schema/2025-12-11.json",
  "name": "io.github.yourname/study-timer",
  "description": "A Pomodoro study timer MCP server. Start, pause, and track focus sessions.",
  "version": "0.1.0",
  "repository": {
    "url": "https://github.com/yourname/study-timer-mcp",
    "type": "github"
  },
  "packages": [
    {
      "registry": "npm",
      "name": "@yourname/study-timer-mcp",
      "version": "0.1.0"
    }
  ]
}
```
Save the file.

---

**3. Create the file `validate_protocol.py`.**

This validates your server.json against the protocol rules:
```powershell
notepad validate_protocol.py
```
Paste:
```python
import json
import re
import sys

def validate_server_json(path):
    print(f"Validating: {path}\n")
    errors = []

    # Load the file
    with open(path) as f:
        data = json.load(f)

    # Rule 1: Required fields
    required = ["name", "description", "version", "packages"]
    for field in required:
        if field not in data:
            errors.append(f"MISSING required field: '{field}'")
        else:
            print(f"  ✓ '{field}' present")

    # Rule 2: Name format must be namespace/tool-name
    name = data.get("name", "")
    name_pattern = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*/[a-zA-Z0-9][a-zA-Z0-9._-]*$')
    if not name_pattern.match(name):
        errors.append(f"INVALID name format: '{name}' — must be 'namespace/tool-name'")
    else:
        print(f"  ✓ name format valid: '{name}'")

    # Rule 3: Version must be exact (e.g. 1.2.3), not a range
    version = data.get("version", "")
    range_patterns = [r'^\^', r'^~', r'^>=', r'^<=', r'^>', r'^<']
    is_range = any(re.match(p, version) for p in range_patterns)
    if is_range:
        errors.append(f"INVALID version: '{version}' — must be an exact version like '1.2.3'")
    elif not re.match(r'^\d+\.\d+\.\d+', version):
        errors.append(f"INVALID version: '{version}' — must follow semver like '0.1.0'")
    else:
        print(f"  ✓ version format valid: '{version}'")

    # Rule 4: packages must be a non-empty list
    packages = data.get("packages", [])
    if not isinstance(packages, list) or len(packages) == 0:
        errors.append("INVALID packages: must be a non-empty list")
    else:
        print(f"  ✓ packages: {len(packages)} package(s) defined")

    # Rule 5: description must be present and non-empty
    desc = data.get("description", "")
    if len(desc) < 10:
        errors.append(f"INVALID description: too short ('{desc}')")
    else:
        print(f"  ✓ description: '{desc[:50]}...' " if len(desc) > 50 else f"  ✓ description: '{desc}'")

    print()
    if errors:
        print(f"VALIDATION FAILED — {len(errors)} error(s):")
        for e in errors:
            print(f"  ✗ {e}")
        return False
    else:
        print("VALIDATION PASSED — server.json is ready to publish.")
        return True

# Validate our file
result = validate_server_json("server.json")
print("\nThis is what the MCP Registry does to every submission.")
print("The protocol contract means every publisher follows the same rules.")
```

**4. Run the validator.**

```powershell
python validate_protocol.py
```
✅ You should see:
```
Validating: server.json

  ✓ 'name' present
  ✓ 'description' present
  ✓ 'version' present
  ✓ 'packages' present
  ✓ name format valid: 'io.github.yourname/study-timer'
  ✓ version format valid: '0.1.0'
  ✓ packages: 1 package(s) defined
  ✓ description: 'A Pomodoro study timer MCP server...'

VALIDATION PASSED — server.json is ready to publish.
```

---

**5. Break the protocol deliberately.**

Edit `server.json` — change `"version": "0.1.0"` to `"version": "^1.0.0"` (a range, not an exact version). Save it. Run the validator again:
```powershell
python validate_protocol.py
```
✅ You should see:
```
VALIDATION FAILED — 1 error(s):
  ✗ INVALID version: '^1.0.0' — must be an exact version like '1.2.3'
```

Change it back to `"0.1.0"` and save.

---

**6. See the raw HTTP protocol headers.**

```powershell
python -c "
import urllib.request
req = urllib.request.Request('https://registry.modelcontextprotocol.io/v0/servers?limit=1')
with urllib.request.urlopen(req) as r:
    print('STATUS:', r.status, r.reason)
    for k, v in r.headers.items():
        print(f'{k}: {v}')
"
```
✅ You should see the raw HTTP protocol conversation:
```
STATUS: 200 OK
Content-Type: application/json
Content-Length: 847
Cache-Control: public, max-age=60
...
```
These headers ARE the HTTP protocol. Every line follows the `Header-Name: value` format, defined by the HTTP specification. Both client and server agreed on this format before you were born.

**What you just built:** A real `server.json` protocol document, a validator that enforces the protocol rules, and a view of the raw HTTP protocol headers — the actual text that travels across the internet.

---

> **🌍 Real World**
> The `server.json` format you just validated is the actual contract the MCP Registry enforces on every submission. The schema file at `registry-main/internal/validators/schemas/2025-12-11.json` defines these exact rules in JSON Schema format. When Anthropic updates the protocol (adds a new required field), they publish a new schema file with a new date in the name — `2026-xx-xx.json`. Older submissions validated against the old schema still work, but new submissions use the new rules. This is versioned protocol evolution — the same challenge every internet standard (HTTP/1.1 → HTTP/2 → HTTP/3) has solved over decades.

---

## The Takeaway

A protocol is a shared agreement about how to communicate. Without protocols, machines (and humans) cannot understand each other no matter how close they are. With protocols, a phone in your pocket can reliably speak to a server on the other side of the planet.

---

## The Connection

Now you know what protocols are and why they exist. But a protocol without a door is useless. In Chapter 4, we meet the **API** — the actual front door of every server, the place where requests arrive and responses leave.

---

*→ Continue to [Chapter 4 — APIs: The Front Door](./ch04-apis.md)*
