# Chapter 17 — Skills: Pre-Packaged Superpowers

*Part 3: The AI Agent — How an AI Coding Assistant Actually Works*

---

## The Analogy

A chef knows thousands of recipes. But they also have a set of **mise en place** — preparations done in advance so that when an order comes in, they're not starting from scratch every time. Pre-chopped onions. Pre-made stock. Pre-rolled pastry.

These aren't full meals. They are building blocks — pre-packaged, tested combinations of technique that the chef can combine quickly without thinking through every step from first principles.

A doctor has the same thing: **clinical protocols**. When a patient comes in with chest pain, the doctor doesn't reason through cardiac biology from scratch. They follow a protocol — ECG, troponin test, aspirin, call cardiology — because that sequence has been established, tested, and proven to work.

**Skills in an AI agent are the mise en place and the clinical protocols combined.** They are pre-written instructions — sometimes with code, sometimes just text — that the agent can follow for common, well-understood tasks.

---

## The Concept

A **skill** is a named, reusable workflow that the agent can invoke when the user uses a specific trigger (like `/commit` or `/debug`).

When a user types `/commit`, the skill system:
1. Recognizes the `/commit` trigger
2. Loads the skill definition (a file describing exactly what to do)
3. Injects that definition into the agent's context
4. The agent follows the skill's instructions

The skill is not code the agent runs. It is instructions the agent reads, like a recipe card — and then executes using its tools.

---

## System Diagram

```
SKILL INVOCATION FLOW

User types: /debug

         │
         ▼
┌─────────────────────────────────────────────────┐
│  SKILL LOADER                                   │
│  1. Detect trigger "/debug"                     │
│  2. Look up: bundled skills + user skills       │
│  3. Find: skills/bundled/debug.ts               │
│  4. Load skill content (the instruction text)   │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  CONTEXT INJECTION                              │
│  User message is now:                           │
│  "[SKILL: debug]\n                              │
│   1. Ask for problem description                │
│   2. Read the failing file                      │
│   3. Form a hypothesis...                       │
│   [USER]: /debug — the login function crashes"  │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
         Agent loop runs as normal —
         but now following the skill's
         step-by-step instructions
```

---

### The Skills in claw-code

From the reference data at `claw-code-main/src/reference_data/subsystems/skills.json`, the skill system has 20 modules. The bundled skills reveal exactly what common workflows look like:

| Skill file | What it does |
|-----------|-------------|
| `batch.ts` | Process multiple items in parallel |
| `claudeApi.ts` | Build apps using the Claude API |
| `debug.ts` | Systematic debugging workflow |
| `keybindings.ts` | Customize keyboard shortcuts |
| `loop.ts` | Run a command repeatedly on a schedule |
| `remember.ts` | Save information to persistent memory |
| `scheduleRemoteAgents.ts` | Schedule agents to run at specific times |
| `simplify.ts` | Review and simplify changed code |
| `stuck.ts` | When the agent is stuck — how to recover |
| `updateConfig.ts` | Configure the agent's settings |
| `verify.ts` | Verify that work meets requirements |

Each of these is a `.ts` (TypeScript) file that contains detailed instructions — not logic that runs directly, but a prompt that the agent reads and follows.

### A Skill in Plain English

Here is what a `debug` skill might contain (reconstructed from the skill name and the agent architecture):

```
# Debug Skill

When invoked with /debug, follow this systematic process:

1. Ask the user to describe the problem in detail if they haven't already.

2. Read all relevant files. Start with the file that threw the error.
   Use read_file to examine it carefully.

3. Search for similar patterns. Use grep_search to find where the
   failing function is called or defined.

4. Form a hypothesis. State your hypothesis clearly before making changes.

5. Make the minimal change. Do not refactor. Only fix what is broken.

6. Run the tests. Use bash to run the test suite.

7. If tests pass, report success and explain what the root cause was.

8. If tests fail, revise your hypothesis and repeat from step 3.

Do not guess. Do not make multiple changes at once. One hypothesis, one change, one test.
```

This is instructions for the agent, not code. The agent reads this and follows it. The skill author is doing "prompt engineering" — carefully designing the instructions so the agent takes the right steps in the right order.

---

## The Real Code

The skill system loads skills from two sources:

**Bundled skills** — shipped with the agent, always available:
```
skills/bundled/debug.ts
skills/bundled/loop.ts
skills/bundled/remember.ts
...
```

**User-defined skills** — loaded from a directory you control:
```
skills/loadSkillsDir.ts  ← Finds all .md files in ~/.claude/skills/
```

This means you can write your own skills. Any `.md` file with a trigger and instructions becomes a new command the agent understands.

A user-defined skill file might look like:

```markdown
---
name: deploy-staging
trigger: /deploy-staging
description: Deploy the current branch to the staging environment
---

When invoked:

1. Run the test suite first: `npm test`. If tests fail, stop and report.
2. Build the Docker image: `docker build -t myapp:staging .`
3. Push to the registry: `docker push registry.mycompany.com/myapp:staging`
4. Deploy to staging cluster: `kubectl apply -f deploy/staging.yaml`
5. Wait 30 seconds and check: `kubectl rollout status deployment/myapp -n staging`
6. Report the result with the deployment URL.

If any step fails, stop immediately and explain what went wrong.
```

Now when you type `/deploy-staging`, the agent reads this file and follows every step — running tests, building, pushing, deploying, and verifying.

---

## 🔬 Lab Activity — Write and Run a Skill

**What you'll build:** A skill file for a `weekly-summary` workflow, a Python skill loader that detects triggers and injects skill content into the agent context, and a simulation of the agent executing the skill's steps.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder and skills directory.**

```powershell
mkdir C:\labs\ch17-skills
mkdir C:\labs\ch17-skills\skills
cd C:\labs\ch17-skills
```

---

**2. Create your skill file.**

```powershell
notepad skills\weekly-summary.md
```
Paste:
```markdown
---
name: weekly-summary
trigger: /weekly-summary
description: Generate a structured weekly summary of files changed this week
---

When invoked, follow these steps exactly:

1. Use list_files to find all files in the current folder.

2. For each file found, use read_file to check its contents.

3. Summarize the contents in one sentence per file.

4. Output a formatted weekly summary report:
   - Date: today
   - Files reviewed: [count]
   - For each file: filename, one-sentence summary
   - End with: "Review complete."

5. Do not make changes to any files. This is a read-only review.
```
Save and close.

---

**3. Create a second skill.**

```powershell
notepad skills\health-check.md
```
Paste:
```markdown
---
name: health-check
trigger: /health-check
description: Check system health and report any issues
---

When invoked:

1. Use list_files to verify the workspace is accessible.

2. Report the number of files found.

3. Check if any file is larger than expected by reading its content length.

4. Output: "Health check complete. [N] files found. No issues detected."
   or list any issues.
```
Save and close.

---

**4. Create the file `skill_runner.py`.**

```powershell
notepad skill_runner.py
```
Paste:
```python
import os
import re

SKILLS_DIR = "skills"

# ── SKILL LOADER ────────────────────────────────────────────

def load_skills():
    """Load all .md skill files from the skills directory."""
    skills = {}
    for fname in os.listdir(SKILLS_DIR):
        if not fname.endswith(".md"):
            continue
        with open(os.path.join(SKILLS_DIR, fname)) as f:
            content = f.read()
        # Parse frontmatter
        trigger_match = re.search(r"trigger:\s*(\S+)", content)
        name_match    = re.search(r"name:\s*(.+)", content)
        desc_match    = re.search(r"description:\s*(.+)", content)
        # Get body (after frontmatter ---)
        parts = content.split("---", 2)
        body = parts[2].strip() if len(parts) >= 3 else content
        if trigger_match:
            trigger = trigger_match.group(1)
            skills[trigger] = {
                "name": name_match.group(1).strip() if name_match else fname,
                "description": desc_match.group(1).strip() if desc_match else "",
                "body": body,
                "file": fname,
            }
    return skills

# ── SKILL INJECTOR ──────────────────────────────────────────

def inject_skill(user_message, skills):
    """Detect trigger in user message and inject skill content."""
    for trigger, skill in skills.items():
        if user_message.strip().startswith(trigger):
            suffix = user_message[len(trigger):].strip()
            injected = (
                f"[SKILL LOADED: {skill['name']}]\n"
                f"{skill['body']}\n\n"
                f"[USER INPUT]: {suffix or '(no additional input)'}"
            )
            return injected, skill
    return user_message, None

# ── SIMULATED AGENT ─────────────────────────────────────────

def fake_agent(context):
    """Simulate agent executing the context (skill + user input)."""
    # In real life: send context to language model
    # Here: extract steps and simulate execution
    steps = re.findall(r"^\d+\..+", context, re.MULTILINE)
    print(f"\n  Agent is following {len(steps)} skill steps:")
    for i, step in enumerate(steps, 1):
        print(f"    Step {i}: {step[:70]}")
    # Simulate final output
    print(f"\n  [Agent output]")
    print(f"  Weekly Summary — 2026-04-02")
    print(f"  Files reviewed: 3")
    print(f"  - skill_runner.py: Python skill runner with loader and agent sim")
    print(f"  - skills/weekly-summary.md: Weekly summary skill definition")
    print(f"  - skills/health-check.md: Health check skill definition")
    print(f"  Review complete.")

# ── MAIN ────────────────────────────────────────────────────

print("=== Skill Runner Demo ===\n")

skills = load_skills()
print(f"Loaded {len(skills)} skill(s):")
for trigger, skill in skills.items():
    print(f"  {trigger:25} → {skill['description'][:50]}")

# Simulate user typing a trigger
print("\n--- User types: /weekly-summary ---")
user_input = "/weekly-summary"
context, matched_skill = inject_skill(user_input, skills)

if matched_skill:
    print(f"  Skill matched: '{matched_skill['name']}' from {matched_skill['file']}")
    print(f"  Injecting skill instructions into agent context...")
    fake_agent(context)
else:
    print(f"  No skill matched — agent handles normally")

print("\n--- User types: /health-check ---")
context2, matched2 = inject_skill("/health-check", skills)
if matched2:
    print(f"  Skill matched: '{matched2['name']}'")
    steps2 = re.findall(r"^\d+\..+", context2, re.MULTILINE)
    print(f"  Skill has {len(steps2)} steps. Agent would follow them now.")

print("\n--- User types: /unknown-skill ---")
context3, matched3 = inject_skill("/unknown-skill", skills)
print(f"  No skill matched: agent handles as normal message")
```

**5. Run it.**

```powershell
python skill_runner.py
```
✅ You should see:
```
=== Skill Runner Demo ===

Loaded 2 skill(s):
  /weekly-summary           → Generate a structured weekly summary...
  /health-check             → Check system health and report any issues

--- User types: /weekly-summary ---
  Skill matched: 'weekly-summary' from weekly-summary.md
  Injecting skill instructions into agent context...

  Agent is following 5 skill steps:
    Step 1: 1. Use list_files to find all files...
    Step 2: 2. For each file found, use read_file...
    Step 3: 3. Summarize the contents in one sentence per file.
    Step 4: 4. Output a formatted weekly summary report:
    Step 5: 5. Do not make changes to any files.

  [Agent output]
  Weekly Summary — 2026-04-02
  Files reviewed: 3
  ...
  Review complete.

--- User types: /unknown-skill ---
  No skill matched: agent handles as normal message
```

**6. Add your own skill.**

```powershell
notepad skills\my-skill.md
```
Write a skill for any repeated task you do. Give it a trigger like `/my-skill`. Run `skill_runner.py` again — it auto-discovers the new file.

**What you just built:** A working skill loader, trigger detector, context injector, and skill runner — matching the `loadSkillsDir.ts` and bundled skill architecture in `claw-code-main/src/reference_data/subsystems/skills.json`.

---

> **🌍 Real World**
> Claude Code's `/commit` skill is a real-world example: type `/commit` and it reads your git diff, summarizes the changes, writes a conventional commit message, stages files, and creates the commit — all from a single typed trigger. The skill is a markdown file with detailed instructions for each step. GitHub Copilot's `/fix`, `/explain`, and `/tests` commands work the same way: a trigger loads a pre-written instruction set that guides the AI through a structured workflow. Anthropic publishes the Claude Code skills in the open-source repository — you can read the exact instructions that power `/commit` and write your own skills using the same format.

---

## Connecting Part 3

You now understand the complete AI agent system:

```
User sends a message (goal)
    → Agent loop starts (Ch 11)
    → Agent may invoke a skill for structured workflows (Ch 17)
    → Agent selects tools (Ch 12)
    → Pre-tool hooks check permissions (Ch 14)
    → Sandbox enforces access limits (Ch 15)
    → Tool executes (built-in or via MCP client, Ch 16)
    → Result is added to the session (Ch 13)
    → Agent reads the result and decides next step
    → Loop continues until done
```

This is how an AI coding assistant actually works. No magic. A loop with safety guards.

---

## The Takeaway

Skills are pre-packaged workflows — detailed instruction sets that the agent reads and follows for common, well-defined tasks. They convert expert knowledge ("how to debug systematically," "how to deploy safely") into reusable recipes that any user can invoke with a single command. Anyone can write a skill — it is just a carefully worded text file.

---

## The Connection

We have the agent. We have the Registry. We understand both sides of the system. Now: how does all of this get deployed to the world? In Part 4, we follow the journey from "code on a developer's laptop" to "running in production, serving thousands of users."

---

*→ Continue to [Chapter 18 — Docker: Shipping Containers for Code](./ch18-docker.md)*
