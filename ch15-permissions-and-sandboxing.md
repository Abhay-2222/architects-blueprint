# Chapter 15 — Permissions and Sandboxing

*Part 3: The AI Agent — How an AI Coding Assistant Actually Works*

---

## The Analogy

A child's playpen is not a prison. It is a space designed so the child can explore, move, touch, and experiment — freely — without the risk of falling down stairs, touching a hot stove, or wandering into traffic.

The playpen doesn't limit what the child *wants* to do. It limits what the child *can reach*. Everything inside the playpen is fair game. Everything outside is inaccessible.

A **sandbox** is a digital playpen for software. It is an isolated environment where a program can run, try things, make mistakes — but cannot reach anything outside the sandbox's walls.

This is critical for AI agents. An AI agent can make mistakes. It might misunderstand a request and try to delete the wrong files. It might be manipulated by malicious content it reads. The sandbox is the safety net: even if the agent does something wrong, the damage is contained.

---

## The Concept

**Sandboxing** is the practice of running a program in a restricted environment that limits what resources it can access.

A sandbox can restrict:
- **Filesystem access** — which folders the agent can read or write
- **Network access** — which servers the agent can contact
- **Process access** — which other programs the agent can launch
- **System resources** — how much CPU and memory it can use

---

## System Diagram

```
FOUR LAYERS OF DEFENCE (defence in depth)

Request: bash("rm -rf /important-folder")
         │
         ▼
Layer 1: SANDBOX (OS level)
  WorkspaceOnly mode → /important-folder outside workspace
  → BLOCKED by kernel namespace restriction

         │ (if sandbox allowed it)
         ▼
Layer 2: PERMISSION MODE (runtime level)
  User is in ReadOnly mode
  bash requires DangerFullAccess
  → BLOCKED by permission mode check

         │ (if permission allowed it)
         ▼
Layer 3: PRE-TOOL HOOK (hook level)
  DangerFullAccess requires user confirmation
  User prompt: "Run rm -rf? [y/n]" → user says n
  → BLOCKED by hook

         │ (if user confirmed it)
         ▼
Layer 4: VALIDATION (input level)
  Path contains ".." or starts with "/"
  → BLOCKED by input validation

         │ (if validation passed)
         ▼
  Tool executes (only if ALL 4 layers allow it)
```

---

There are different levels of restriction. The claw-code sandbox defines three levels:

| Mode | Access | When to use |
|------|--------|-------------|
| `workspace-only` | Can only touch files in the current project folder | Default — safest |
| `allow-list` | Can access specific folders you explicitly list | When you need more reach |
| `off` | No filesystem restrictions | Only for trusted, advanced use |

The key insight: **every feature costs trust, and trust costs safety.** The more the agent can do, the more important it is to be sure it will do the right thing.

---

## The Real Code

From `claw-code-main/rust/crates/runtime/src/sandbox.rs`:

```rust
// The three isolation modes for filesystem access
pub enum FilesystemIsolationMode {
    Off,            // No restrictions — full access
    WorkspaceOnly,  // Only the current project folder (default)
    AllowList,      // Only explicitly listed paths
}

// The full sandbox configuration
pub struct SandboxConfig {
    pub enabled: Option<bool>,

    // Linux namespaces — OS-level isolation
    pub namespace_restrictions: Option<bool>,

    // Can the agent access the internet?
    pub network_isolation: Option<bool>,

    // How restricted is filesystem access?
    pub filesystem_mode: Option<FilesystemIsolationMode>,

    // Specific paths allowed in allow-list mode
    pub allowed_mounts: Vec<String>,
}
```

And the status report that tells you what is actually active:

```rust
pub struct SandboxStatus {
    pub enabled: bool,           // Is sandboxing on?
    pub active: bool,            // Is it actually enforced right now?
    pub namespace_active: bool,  // Is OS-level namespace isolation working?
    pub network_active: bool,    // Is network isolation enforced?
    pub filesystem_active: bool, // Is filesystem isolation enforced?
}
```

This structure separates what you *requested* from what is *supported* on your system and what is *actually active*. This distinction matters: you might request sandbox mode on a system that doesn't support it. The status tells you honestly whether the protection is real.

### Permissions at the Tool Level

From Chapter 12, each tool has a `required_permission` field:

```rust
PermissionMode::ReadOnly          // Can only read files
PermissionMode::WorkspaceWrite    // Can read and write project files
PermissionMode::DangerFullAccess  // Can run arbitrary commands
```

These are not suggestions. The agent runtime checks the current permission mode against the tool's required permission before executing. If you are in `ReadOnly` mode and the agent tries to use `write_file`, the runtime rejects it before anything happens.

This creates layered defense:
1. **Sandbox** — limits what the OS allows the agent process to touch
2. **Permission mode** — limits what tools the agent is allowed to use
3. **Hooks** — check specific operations before they run
4. **Validation** — checks inputs before they are acted on

Four walls. Each one independently effective. Together, very hard to breach by accident.

---

## 🔬 Lab Activity — Build a Sandbox Enforcer

**What you'll build:** A Python sandbox enforcer that checks file paths against allowed zones, enforces permission modes, and blocks out-of-bounds access — matching the `FilesystemIsolationMode` logic in `claw-code-main/rust/crates/runtime/src/sandbox.rs`.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch15-sandbox
cd C:\labs\ch15-sandbox
mkdir workspace
```

---

**2. Create the file `sandbox.py`.**

```powershell
notepad sandbox.py
```
Paste:
```python
import os

# ── SANDBOX CONFIGURATION ──────────────────────────────────

class SandboxConfig:
    OFF            = "off"            # No restrictions
    WORKSPACE_ONLY = "workspace_only" # Only the project folder
    ALLOW_LIST     = "allow_list"     # Only explicitly listed paths

class PermissionMode:
    READ_ONLY       = "read_only"
    WORKSPACE_WRITE = "workspace_write"
    DANGER_FULL     = "danger_full"

# Active sandbox settings (change these to test different modes)
SANDBOX_MODE     = SandboxConfig.WORKSPACE_ONLY
PERMISSION_MODE  = PermissionMode.WORKSPACE_WRITE
WORKSPACE_ROOT   = os.path.abspath("workspace")
ALLOW_LIST_PATHS = [WORKSPACE_ROOT, os.path.abspath("shared-docs")]

# ── SANDBOX ENFORCER ───────────────────────────────────────

class SandboxViolation(Exception):
    pass

def check_path(path):
    """Check if a path is within the allowed sandbox zone."""
    abs_path = os.path.abspath(path)

    if SANDBOX_MODE == SandboxConfig.OFF:
        return True  # No restrictions

    elif SANDBOX_MODE == SandboxConfig.WORKSPACE_ONLY:
        if not abs_path.startswith(WORKSPACE_ROOT):
            raise SandboxViolation(
                f"Path '{abs_path}' is outside the workspace.\n"
                f"Workspace root: {WORKSPACE_ROOT}\n"
                f"Sandbox mode: {SANDBOX_MODE}"
            )

    elif SANDBOX_MODE == SandboxConfig.ALLOW_LIST:
        if not any(abs_path.startswith(p) for p in ALLOW_LIST_PATHS):
            raise SandboxViolation(
                f"Path '{abs_path}' is not in the allowed list.\n"
                f"Allowed paths: {ALLOW_LIST_PATHS}"
            )
    return True

def check_permission(operation):
    """Check if the current permission mode allows this operation."""
    perm_rank = {PermissionMode.READ_ONLY: 1,
                 PermissionMode.WORKSPACE_WRITE: 2,
                 PermissionMode.DANGER_FULL: 3}

    required = {
        "read":    PermissionMode.READ_ONLY,
        "write":   PermissionMode.WORKSPACE_WRITE,
        "execute": PermissionMode.DANGER_FULL,
    }

    required_perm = required.get(operation, PermissionMode.READ_ONLY)
    if perm_rank[PERMISSION_MODE] < perm_rank[required_perm]:
        raise SandboxViolation(
            f"Operation '{operation}' requires '{required_perm}' "
            f"but current mode is '{PERMISSION_MODE}'"
        )

# ── SANDBOXED FILE OPERATIONS ──────────────────────────────

def safe_read(path):
    check_permission("read")
    check_path(path)
    with open(path) as f:
        return f.read()

def safe_write(path, content):
    check_permission("write")
    check_path(path)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return f"Written {len(content)} bytes to {path}"

def safe_execute(command):
    check_permission("execute")
    return f"Would execute: {command}"

# ── DEMO ───────────────────────────────────────────────────

def try_op(description, fn, *args):
    print(f"\n  {description}")
    try:
        result = fn(*args)
        print(f"    ✓ ALLOWED: {str(result)[:60]}")
    except SandboxViolation as e:
        print(f"    ✗ BLOCKED: {str(e).splitlines()[0]}")

print("=== Sandbox Enforcer Demo ===")
print(f"  Mode: {SANDBOX_MODE} | Permission: {PERMISSION_MODE}")
print(f"  Workspace: {WORKSPACE_ROOT}\n")

# Write a file inside the workspace (should succeed)
try_op("Write inside workspace", safe_write,
       "workspace/notes.txt", "hello from the sandbox")

# Read that file back (should succeed)
try_op("Read inside workspace", safe_read,
       "workspace/notes.txt")

# Try to read outside workspace (should be blocked)
try_op("Read outside workspace (C:/Windows/System32/drivers/etc/hosts)",
       safe_read, "C:/Windows/System32/drivers/etc/hosts")

# Try to write outside workspace (should be blocked)
try_op("Write to C:/important.txt (outside workspace)",
       safe_write, "C:/important.txt", "hacked")

# Try to execute a command (needs DANGER_FULL — should be blocked)
try_op("Execute shell command (requires danger_full)",
       safe_execute, "rm -rf build/")

print(f"\nSandbox status:")
print(f"  Filesystem mode  : {SANDBOX_MODE}")
print(f"  Permission mode  : {PERMISSION_MODE}")
print(f"  Network isolation: not implemented (exercise: add it)")
```

**3. Run it.**

```powershell
python sandbox.py
```
✅ You should see:
```
=== Sandbox Enforcer Demo ===
  Mode: workspace_only | Permission: workspace_write
  Workspace: C:\labs\ch15-sandbox\workspace

  Write inside workspace
    ✓ ALLOWED: Written 23 bytes to workspace/notes.txt

  Read inside workspace
    ✓ ALLOWED: hello from the sandbox

  Read outside workspace (C:/Windows/System32/...)
    ✗ BLOCKED: Path '...' is outside the workspace.

  Write to C:/important.txt (outside workspace)
    ✗ BLOCKED: Path 'C:\important.txt' is outside the workspace.

  Execute shell command (requires danger_full)
    ✗ BLOCKED: Operation 'execute' requires 'danger_full' but current mode is 'workspace_write'
```

**4. Test switching to `OFF` mode.**

Open `sandbox.py` and change:
```python
SANDBOX_MODE = SandboxConfig.OFF
PERMISSION_MODE = PermissionMode.DANGER_FULL
```
Run again — all operations succeed. This is the "no restrictions" mode: useful for a trusted environment, dangerous anywhere else.

**What you just built:** A working sandbox enforcer with path isolation and permission level checking — mirroring the `FilesystemIsolationMode` enum and `SandboxConfig` struct from `claw-code-main/rust/crates/runtime/src/sandbox.rs`.

---

> **🌍 Real World**
> Every major cloud provider enforces sandboxing at the OS level. AWS Lambda runs each function in a separate MicroVM using the Firecracker hypervisor — functions literally cannot reach each other even if they run on the same physical machine. Docker containers are software sandboxes: they share the host kernel but have isolated filesystems, process trees, and network stacks. When Chrome opens a web page, it runs the tab in a separate OS process with reduced privileges — even if the page contains malicious code, it can't escape the sandbox to read your files. The MCP Registry uses this same principle: published tools are not trusted. They run in isolated containers that cannot touch the registry's database or operating system directly.

---

## The Takeaway

Sandboxing is the digital playpen — it defines the walls within which an agent operates. Combined with tool-level permissions, pre-tool hooks, and validation, it creates four independent layers of safety. A well-sandboxed agent can be powerful without being reckless, because even its worst mistakes cannot escape the playpen.

---

## The Connection

The agent has tools, memory, hooks, and a sandbox. It can work independently. But how does it *discover* new tools? How does it connect to the MCP Registry we studied in Part 2? In Chapter 16, we follow the agent's connection to the outside world through the **MCP client**.

---

*→ Continue to [Chapter 16 — MCP Client: The Agent Calls the Registry](./ch16-mcp-client.md)*
