# Chapter 12 — Tools: The Agent's Hands

*Part 3: The AI Agent — How an AI Coding Assistant Actually Works*

---

## The Analogy

A surgeon's hands are useless without instruments. Without a scalpel, they cannot cut. Without forceps, they cannot hold. Without a suture, they cannot close.

The instruments are not the surgeon — the surgeon is the intelligence that decides which instrument to use, when, and how. But without instruments, the surgeon can only talk.

An AI agent is the same. The language model (the "brain") can describe what it wants to do in extraordinary detail. But without tools, it cannot actually *do* anything. It cannot read your files. It cannot run code. It cannot search the web. It can only produce words.

**Tools are the agent's hands.** Each tool is a specific capability — a scalpel, a forceps, a suture — that the agent can invoke to interact with the real world.

---

## The Concept

In an AI agent system, a **tool** is a defined capability with:
- A **name** (how the agent refers to it)
- A **description** (so the agent knows when to use it)
- An **input schema** (what parameters it accepts)
- A **permission level** (how dangerous it is to use)

The agent is shown all available tools at the start of a conversation. When it decides to use a tool, it says: "I want to use `read_file` with the parameter `path: /home/user/report.pdf`." The runtime executes the tool and returns the result.

The agent never directly accesses your filesystem, internet, or shell. The tools do. The agent only asks.

---

## System Diagram

```
TOOL SYSTEM ARCHITECTURE

┌─────────────────────────────────────────────────┐
│  AI MODEL (language model brain)                │
│  Sees all tool descriptions at start            │
│  Outputs: {"tool": "read_file",                 │
│            "input": {"path": "main.py"}}        │
└──────────────────────┬──────────────────────────┘
                       │ tool call request
                       ▼
┌─────────────────────────────────────────────────┐
│  TOOL DISPATCHER (runtime)                      │
│  1. Look up tool by name                        │
│  2. Check permission level                      │
│     ReadOnly       → run immediately            │
│     WorkspaceWrite → run if user allowed writes │
│     DangerFull     → run only if user approved  │
│  3. Execute tool with validated inputs          │
└──────────────────────┬──────────────────────────┘
                       │ runs actual code
          ┌────────────┼────────────────┐
          ▼            ▼                ▼
    [read_file]   [bash cmd]      [write_file]
    OS read()     subprocess      OS write()
          │            │                │
          └────────────┼────────────────┘
                       │ result string
                       ▼
              back to AI model
              (added to history)
```

---

## The Real Code

From `claw-code-main/rust/crates/tools/src/lib.rs`, here are the actual tools defined in the Rust agent:

```rust
// Tool 1: Run a shell command (most powerful — full access)
ToolSpec {
    name: "bash",
    description: "Execute a shell command in the current workspace.",
    input_schema: json!({
        "properties": {
            "command": { "type": "string" },        // What command to run
            "timeout": { "type": "integer" },       // Max time to wait
            "description": { "type": "string" },   // What this command does (for humans)
        },
        "required": ["command"],
    }),
    required_permission: PermissionMode::DangerFullAccess, // ← High risk
},

// Tool 2: Read a file (safe — read only)
ToolSpec {
    name: "read_file",
    description: "Read a text file from the workspace.",
    input_schema: json!({
        "properties": {
            "path": { "type": "string" },   // Which file to read
            "offset": { "type": "integer"}, // Start reading from line N
            "limit": { "type": "integer" }, // Read at most N lines
        },
        "required": ["path"],
    }),
    required_permission: PermissionMode::ReadOnly, // ← Low risk
},

// Tool 3: Write a file
ToolSpec {
    name: "write_file",
    description: "Write a text file in the workspace.",
    input_schema: json!({
        "properties": {
            "path": { "type": "string" },    // Where to write
            "content": { "type": "string" }, // What to write
        },
        "required": ["path", "content"],
    }),
    required_permission: PermissionMode::WorkspaceWrite, // ← Medium risk
},

// Tool 4: Search files by pattern
ToolSpec {
    name: "glob_search",
    description: "Find files by glob pattern.",
    input_schema: json!({
        "properties": {
            "pattern": { "type": "string" }, // e.g., "**/*.py" to find all Python files
            "path": { "type": "string" },    // Where to search
        },
        "required": ["pattern"],
    }),
    required_permission: PermissionMode::ReadOnly,
},
```

Notice the **permission levels**:
- `ReadOnly` — Can look but not touch
- `WorkspaceWrite` — Can write files in the project folder
- `DangerFullAccess` — Can run any shell command (most powerful, most risky)

The permission system is a safety mechanism. The agent cannot use a `DangerFullAccess` tool unless the user has explicitly enabled it. This prevents the agent from running destructive commands by accident.

### How the Agent Chooses a Tool

The AI model sees all tool descriptions. When you ask "read the file at `/home/user/notes.txt`," the model sees:
- `bash`: "Execute a shell command" — could work, but heavy
- `read_file`: "Read a text file from the workspace" — perfect match

It picks `read_file`. Not because of magic, but because its training has taught it to match task descriptions to tool descriptions. The more precise the tool description, the better the agent's choices.

---

## 🔬 Lab Activity — Build a Tool Registry

**What you'll build:** A Python tool registry with 4 tools (list files, read file, search text, write note), a dispatcher with permission checking, and an interactive session where you call tools manually — the same pattern as `claw-code-main/rust/crates/tools/src/lib.rs`.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch12-tools
cd C:\labs\ch12-tools
```

---

**2. Create the file `tool_registry.py`.**

```powershell
notepad tool_registry.py
```
Paste:
```python
import os
import json

# ── PERMISSION LEVELS ──────────────────────────────────
READ_ONLY       = "read_only"        # safe, never modifies anything
WORKSPACE_WRITE = "workspace_write"  # writes files in current folder only
DANGER_FULL     = "danger_full"      # can do anything (bash, delete, etc.)

# ── TOOL IMPLEMENTATIONS ────────────────────────────────

def tool_list_files(folder="."):
    """List files in a folder."""
    try:
        files = [f for f in os.listdir(folder) if os.path.isfile(f)]
        return {"files": files, "count": len(files)}
    except PermissionError:
        return {"error": "permission_denied", "folder": folder}

def tool_read_file(path, offset=0, limit=50):
    """Read lines from a file."""
    try:
        with open(path) as f:
            lines = f.readlines()
        selected = lines[offset:offset+limit]
        return {
            "path": path,
            "total_lines": len(lines),
            "lines_returned": len(selected),
            "content": "".join(selected)
        }
    except FileNotFoundError:
        return {"error": "file_not_found", "path": path}

def tool_search_text(pattern, folder="."):
    """Search for a text pattern in all files in a folder."""
    matches = []
    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath) as f:
                for i, line in enumerate(f, 1):
                    if pattern.lower() in line.lower():
                        matches.append({"file": fname, "line": i, "text": line.strip()})
        except (UnicodeDecodeError, PermissionError):
            pass
    return {"pattern": pattern, "matches": matches, "total": len(matches)}

def tool_write_note(filename, content):
    """Write a note file in the current workspace."""
    if "/" in filename or "\\" in filename:
        return {"error": "invalid_filename", "reason": "No path separators allowed"}
    with open(filename, "w") as f:
        f.write(content)
    return {"written": filename, "bytes": len(content)}

# ── TOOL REGISTRY ───────────────────────────────────────

REGISTRY = {
    "list_files": {
        "fn": tool_list_files,
        "description": "List all files in a folder. Use when you need to see what files exist.",
        "params": {"folder": "string (optional, default '.')"},
        "permission": READ_ONLY,
    },
    "read_file": {
        "fn": tool_read_file,
        "description": "Read content from a file. Use when you need to see what a file contains.",
        "params": {"path": "string (required)", "offset": "int (optional)", "limit": "int (optional)"},
        "permission": READ_ONLY,
    },
    "search_text": {
        "fn": tool_search_text,
        "description": "Search for text across all files in a folder. Use when looking for specific content.",
        "params": {"pattern": "string (required)", "folder": "string (optional)"},
        "permission": READ_ONLY,
    },
    "write_note": {
        "fn": tool_write_note,
        "description": "Write a text note to a file in the workspace. Use to save information.",
        "params": {"filename": "string (required)", "content": "string (required)"},
        "permission": WORKSPACE_WRITE,
    },
}

# ── DISPATCHER ──────────────────────────────────────────

# Simulate user-approved permissions
APPROVED_PERMISSIONS = {READ_ONLY, WORKSPACE_WRITE}  # user has approved both

def dispatch(tool_name, **kwargs):
    if tool_name not in REGISTRY:
        return {"error": "unknown_tool", "tool": tool_name}

    tool = REGISTRY[tool_name]
    if tool["permission"] not in APPROVED_PERMISSIONS:
        return {
            "error": "permission_denied",
            "tool": tool_name,
            "required": tool["permission"],
            "message": "User has not approved this permission level"
        }

    return tool["fn"](**kwargs)

# ── DEMO ────────────────────────────────────────────────

print("=== Tool Registry Demo ===\n")
print("Available tools:")
for name, spec in REGISTRY.items():
    print(f"  [{spec['permission']:18}] {name}")
    print(f"     → {spec['description']}")

print("\n--- Calling: list_files ---")
result = dispatch("list_files")
print(json.dumps(result, indent=2))

print("\n--- Calling: read_file (this file) ---")
result = dispatch("read_file", path="tool_registry.py", limit=5)
print(json.dumps(result, indent=2))

print("\n--- Calling: search_text ---")
result = dispatch("search_text", pattern="permission")
print(f"Found {result['total']} matches for 'permission'")
for m in result["matches"][:3]:
    print(f"  {m['file']}:{m['line']} → {m['text'][:60]}")

print("\n--- Calling: write_note ---")
result = dispatch("write_note", filename="agent_notes.txt",
                  content="Tools checked: list_files, read_file, search_text, write_note\n")
print(json.dumps(result, indent=2))

print("\n--- Attempting dangerous tool (not registered) ---")
result = dispatch("bash")
print(json.dumps(result, indent=2))
```

**3. Run it.**

```powershell
python tool_registry.py
```
✅ You should see:
```
=== Tool Registry Demo ===

Available tools:
  [read_only         ] list_files
     → List all files in a folder...
  [read_only         ] read_file
     → Read content from a file...
  [read_only         ] search_text
     → Search for text across all files...
  [workspace_write   ] write_note
     → Write a text note to a file...

--- Calling: list_files ---
{"files": ["tool_registry.py"], "count": 1}

--- Calling: read_file (this file) ---
{"path": "tool_registry.py", "total_lines": 95, "lines_returned": 5, ...}

--- Calling: search_text ---
Found 6 matches for 'permission'
  tool_registry.py:12 → READ_ONLY       = "read_only"...

--- Calling: write_note ---
{"written": "agent_notes.txt", "bytes": 63}

--- Attempting dangerous tool (not registered) ---
{"error": "unknown_tool", "tool": "bash"}
```
✅ Confirm `agent_notes.txt` was created:
```powershell
type agent_notes.txt
```
✅ You see: `Tools checked: list_files, read_file, search_text, write_note`

**What you just built:** A complete tool registry with permission levels, a dispatcher that enforces permissions, and 4 working tools — matching the structure of the real `ToolSpec` definitions in `claw-code-main/rust/crates/tools/src/lib.rs`.

---

> **🌍 Real World**
> Claude Code (Anthropic's AI coding tool) defines its tools in exactly this format — each has a name, description, input schema, and permission level. The `Bash` tool requires `DangerFullAccess`, while `Read` and `Glob` run at `ReadOnly`. When you approve "allow all tools," you are granting all permission levels. When you run in "safe mode," only `ReadOnly` tools execute without a prompt. OpenAI's function calling API is the same structure: developers register tool schemas, and GPT-4 picks which to call. The entire ecosystem of AI agents (LangChain, AutoGen, CrewAI) is built on this one pattern: tools as named functions with typed inputs.

---

## Research Spotlight

> **"ImageNet Classification with Deep Convolutional Neural Networks"** — Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012).

This paper — known as "AlexNet" — was the moment deep learning proved itself to the world. It won the ImageNet competition (a global contest to recognize objects in images) by a margin so large that the field was never the same again.

Why does this matter for tools? Because AlexNet showed that neural networks could look at raw pixels and identify objects — without being programmed with rules about what objects look like. That same principle — learning patterns from data, not from rules — is what allows a language model to read tool descriptions and decide which one to use for a given task.

The paper is available through Hinton's archive: https://www.cs.toronto.edu/~hinton/pages/publications.html

---

## The Takeaway

Tools are the agent's hands — specific, named capabilities with defined inputs, descriptions, and permission levels. The agent reads all tool descriptions at the start of a conversation and chooses the right tool for each step based on learned pattern-matching. The permission system ensures that dangerous tools require explicit user approval.

---

## The Connection

Tools let the agent act. But how does it remember what it has already done? In Chapter 13, we open the memory system — **sessions and conversations** — and understand how the agent keeps track of the entire history of a task, and what happens when that history gets too long.

---

*→ Continue to [Chapter 13 — Sessions and Conversations](./ch13-sessions-and-conversations.md)*
