# Chapter 14 — Hooks: Rules the Agent Must Follow

*Part 3: The AI Agent — How an AI Coding Assistant Actually Works*

---

## The Analogy

A construction worker is about to pick up a power drill. But before they do, there is a mandatory safety checklist posted on the wall:

**Before using power tools:**
- [ ] Is the work area clear?
- [ ] Are you wearing safety glasses?
- [ ] Is the power source rated for this tool?
- [ ] Have you locked out the circuit if working near electrical lines?

**After using power tools:**
- [ ] Power off and secured?
- [ ] Debris cleared?
- [ ] Incident log updated if anything went wrong?

The worker cannot skip this. Even if they are in a hurry. Even if they have done it a thousand times. The checklist is a **hook** — an automatic step that runs before and after a specific action.

AI agents have the same system. Before an agent uses a tool (like running a shell command or deleting a file), certain checks run automatically. After the tool runs, certain cleanup steps run automatically. These are called **hooks**.

---

## The Concept

A **hook** is a piece of code that runs automatically at a specific point in the agent's workflow — before a tool runs, after it runs, or when certain events occur.

There are two primary types of hooks in an AI agent:

**Pre-tool hooks (Before):**
- Check if the user has permission to use this tool
- Log that this tool is about to be called (for auditing)
- Pause and ask the user for confirmation before dangerous operations
- Check if the action is on the allowed list

**Post-tool hooks (After):**
- Log what happened (for debugging and auditing)
- Check if the result contains anything unexpected
- Notify the user that something changed
- Update a cost/usage tracker

Together, hooks are the **safety layer** between the agent's decisions and their consequences.

---

## System Diagram

```
HOOK EXECUTION FLOW

Agent decides: use bash("rm -rf build/")
                │
                ▼
┌───────────────────────────────────────────────┐
│  PRE-TOOL HOOKS (run in order)                │
│  1. PermissionCheck  → is bash allowed?       │
│     User mode = "safe" → DENIED               │
│     User mode = "full" → ALLOWED              │
│  2. AuditLog → write to log: "bash called"    │
│  3. CostCheck → estimate token cost           │
│  4. UserConfirm (if DangerFull) →             │
│     "Agent wants to run: rm -rf build/        │
│      Allow? [y/n]" ← blocks until answered   │
└──────────────────────┬────────────────────────┘
                       │ if all hooks pass
                       ▼
              [TOOL EXECUTES]
              rm -rf build/  → success
                       │
                       ▼
┌───────────────────────────────────────────────┐
│  POST-TOOL HOOKS (run in order)               │
│  1. AuditLog → write result to log            │
│  2. CostTracker → update token usage total    │
│  3. Notifier → send alert if result is error  │
└───────────────────────────────────────────────┘
                       │
                       ▼
            result returned to AI model
```

---

## The Real Code

The hooks subsystem in claw-code is large — 104 modules in the original TypeScript system, as recorded in the reference data at `claw-code-main/src/reference_data/subsystems/hooks.json`.

This tells us something important: **safety and permissions are not an afterthought.** 104 modules dedicated to hooks means the developers treated this as a first-class concern from the beginning.

The hook files reveal the scope:

```
hooks/toolPermission/handlers/interactiveHandler.ts  ← Asks user before dangerous tools
hooks/toolPermission/handlers/coordinatorHandler.ts  ← Coordinates team of agents
hooks/toolPermission/permissionLogging.ts            ← Records all permission decisions
hooks/notifs/useMcpConnectivityStatus.tsx            ← Notifies when MCP is disconnected
hooks/notifs/useRateLimitWarningNotification.tsx     ← Warns when approaching API limits
```

The permission handler is the most important. When an agent wants to run a `bash` command, this hook runs:

1. **Check the permission level** of the `bash` tool — it is `DangerFullAccess` (Chapter 12)
2. **Check the user's permission mode** — did they enable full access?
3. If yes → allow. If no → prompt the user: "The agent wants to run: `rm -rf build/`. Allow?"
4. **Log the decision** — whether allowed or denied, record it for auditing

This is how you get an AI that is powerful but not reckless.

### The Cost Hook

One of the most practically important hooks is the cost tracker:

```
hooks/costHook.py     ← Tracks API token usage and estimates dollar cost
```

Every call to the AI model costs money (tokens). Without tracking, it is easy to spend hundreds of dollars in a long session without realizing it. The cost hook runs after every model call, updates the running total, and warns the user when costs get high.

---

## 🔬 Lab Activity — Build a Hook System

**What you'll build:** A Python hook system with pre-tool and post-tool hooks, permission checking, audit logging, and cost tracking — mirroring the hooks subsystem in `claw-code-main/src/reference_data/subsystems/hooks.json`.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch14-hooks
cd C:\labs\ch14-hooks
```

---

**2. Create the file `hooks.py`.**

```powershell
notepad hooks.py
```
Paste:
```python
import time
import json

# ── PERMISSION LEVELS ──────────────────────────────────────
READ_ONLY       = "read_only"
WORKSPACE_WRITE = "workspace_write"
DANGER_FULL     = "danger_full"

# User's approved permission mode (simulate different settings)
USER_PERMISSION_MODE = WORKSPACE_WRITE  # change to DANGER_FULL to allow bash

TOOL_PERMISSIONS = {
    "read_file":   READ_ONLY,
    "list_files":  READ_ONLY,
    "write_file":  WORKSPACE_WRITE,
    "bash":        DANGER_FULL,
    "delete_file": DANGER_FULL,
}

# ── AUDIT LOG ──────────────────────────────────────────────
audit_log = []

def log_audit(event, tool, details=""):
    entry = {
        "time": time.strftime("%H:%M:%S"),
        "event": event,
        "tool": tool,
        "details": details
    }
    audit_log.append(entry)
    print(f"  [AUDIT] {entry['time']} | {event:20} | {tool:15} | {details[:40]}")

# ── COST TRACKER ───────────────────────────────────────────
cost_tracker = {"calls": 0, "total_ms": 0}

# ── PRE-TOOL HOOKS ─────────────────────────────────────────

def hook_permission_check(tool_name, **kwargs):
    """Check if the user has approved this tool's permission level."""
    required = TOOL_PERMISSIONS.get(tool_name, READ_ONLY)

    level_rank = {READ_ONLY: 1, WORKSPACE_WRITE: 2, DANGER_FULL: 3}
    user_rank = level_rank.get(USER_PERMISSION_MODE, 1)
    required_rank = level_rank.get(required, 1)

    if required_rank > user_rank:
        log_audit("DENIED (permission)", tool_name, f"requires {required}, user={USER_PERMISSION_MODE}")
        return False, f"Permission denied: '{tool_name}' requires '{required}' but user mode is '{USER_PERMISSION_MODE}'"
    return True, None

def hook_pre_log(tool_name, **kwargs):
    """Log before tool runs."""
    log_audit("PRE_CALL", tool_name, str(kwargs)[:40])
    return True, None

# ── POST-TOOL HOOKS ────────────────────────────────────────

def hook_post_log(tool_name, result, elapsed_ms):
    """Log after tool runs."""
    log_audit("POST_CALL", tool_name, f"result={str(result)[:30]} ({elapsed_ms}ms)")

def hook_cost_track(tool_name, result, elapsed_ms):
    """Track usage costs."""
    cost_tracker["calls"] += 1
    cost_tracker["total_ms"] += elapsed_ms

# ── DISPATCHER WITH HOOKS ──────────────────────────────────

PRE_HOOKS  = [hook_permission_check, hook_pre_log]
POST_HOOKS = [hook_post_log, hook_cost_track]

# Fake tool implementations
def read_file(path):
    return f"Contents of {path}: [simulated file content here]"

def write_file(path, content):
    return f"Written {len(content)} bytes to {path}"

def bash(command):
    return f"Executed: {command}"  # never actually runs — permission block stops it

TOOLS = {"read_file": read_file, "write_file": write_file, "bash": bash}

def call_tool(tool_name, **kwargs):
    print(f"\n{'─'*55}")
    print(f"Tool call: {tool_name}({kwargs})")

    # Run pre-hooks
    for hook in PRE_HOOKS:
        allowed, msg = hook(tool_name, **kwargs)
        if not allowed:
            print(f"  ✗ BLOCKED by hook: {msg}")
            return {"error": msg}

    # Execute tool
    start = time.time()
    result = TOOLS.get(tool_name, lambda **k: {"error": "unknown tool"})(**kwargs)
    elapsed_ms = int((time.time() - start) * 1000)

    # Run post-hooks
    for hook in POST_HOOKS:
        hook(tool_name, result=result, elapsed_ms=elapsed_ms)

    print(f"  ✓ Result: {str(result)[:60]}")
    return result

# ── DEMO ───────────────────────────────────────────────────

print("=== Hook System Demo ===")
print(f"User permission mode: {USER_PERMISSION_MODE}\n")

call_tool("read_file", path="main.py")
call_tool("write_file", path="output.txt", content="hello world")
call_tool("bash", command="rm -rf /")  # should be BLOCKED

print(f"\n{'='*55}")
print("AUDIT LOG:")
for entry in audit_log:
    print(f"  {entry['time']} | {entry['event']:20} | {entry['tool']:15} | {entry['details'][:35]}")

print(f"\nCOST SUMMARY:")
print(f"  Total tool calls attempted : {len(audit_log)}")
print(f"  Calls that executed        : {cost_tracker['calls']}")
print(f"  Total execution time       : {cost_tracker['total_ms']}ms")
print(f"  Calls blocked by hooks     : {len([e for e in audit_log if 'DENIED' in e['event']])}")
```

**3. Run it.**

```powershell
python hooks.py
```
✅ You should see:
```
=== Hook System Demo ===
User permission mode: workspace_write

───────────────────────────────────────────────────────
Tool call: read_file({'path': 'main.py'})
  [AUDIT] 12:34:01 | PRE_CALL              | read_file       | ...
  [AUDIT] 12:34:01 | POST_CALL             | read_file       | ...
  ✓ Result: Contents of main.py: [simulated file content here]

───────────────────────────────────────────────────────
Tool call: write_file({'path': 'output.txt', 'content': 'hello world'})
  [AUDIT] 12:34:01 | PRE_CALL              | write_file      | ...
  [AUDIT] 12:34:01 | POST_CALL             | write_file      | ...
  ✓ Result: Written 11 bytes to output.txt

───────────────────────────────────────────────────────
Tool call: bash({'command': 'rm -rf /'})
  [AUDIT] 12:34:01 | DENIED (permission)   | bash            | requires danger_full...
  ✗ BLOCKED by hook: Permission denied: 'bash' requires 'danger_full'...

AUDIT LOG:
  ... PRE_CALL  | read_file ...
  ... POST_CALL | read_file ...
  ... DENIED    | bash      ...

COST SUMMARY:
  Total tool calls attempted : 6
  Calls that executed        : 2
  Total execution time       : 0ms
  Calls blocked by hooks     : 1
```

**4. Change the permission mode and see the difference.**

Open `hooks.py` and change line:
```python
USER_PERMISSION_MODE = WORKSPACE_WRITE
```
to:
```python
USER_PERMISSION_MODE = DANGER_FULL
```
Run again — the `bash` call will now pass the permission hook and execute.

**What you just built:** A complete pre-hook/post-hook pipeline with permission enforcement, audit logging, and cost tracking — the same pattern as the 104-module hooks subsystem in `claw-code-main/src/reference_data/subsystems/hooks.json`.

---

> **🌍 Real World**
> GitHub Actions uses hooks extensively: `pre-` and `post-` steps run before and after every job step, performing setup and cleanup. AWS Lambda has lifecycle hooks that run before function invocation. In security systems, every database write at companies like Stripe goes through a "write hook" that checks compliance rules before committing. Claude Code's hooks system works identically to what you built: every tool call goes through `permissionLogging.ts` (audit log) and `interactiveHandler.ts` (user confirmation for dangerous tools). The cost hook at `hooks/costHook.py` tracks every API call's token usage — without it, a runaway agent loop could cost hundreds of dollars unnoticed.

---

## The Takeaway

Hooks are automatic checkpoints that run before and after an agent's tool calls. They enforce safety, log actions for auditing, track costs, and keep humans in the loop for high-stakes decisions. A powerful agent without hooks is a power tool without a safety guard.

---

## The Connection

Hooks check permissions. But permissions live in a larger system — the **sandbox** — which defines the boundaries of what the agent can even reach. In Chapter 15, we build the walls of the agent's playpen and understand what it means to run software in a controlled, isolated environment.

---

*→ Continue to [Chapter 15 — Permissions and Sandboxing](./ch15-permissions-and-sandboxing.md)*
