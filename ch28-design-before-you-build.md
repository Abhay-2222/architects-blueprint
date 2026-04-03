# Chapter 28 — Your First Project: Design It Before You Build It

*Part 6: The Home Architect*

---

## The Analogy

No architect draws blueprints and then figures out what the building is for. No engineer designs a bridge before studying the river.

The design process always starts with **questions**, not answers:

- Who will use this?
- What problem does it solve?
- What does success look like?
- What could go wrong?
- What is the simplest version that proves the idea works?

Only after answering these questions do you pick up a pencil — let alone start building.

The Japanese have a concept called **nemawashi** — carefully preparing the ground before planting. Before a decision is made, you consult everyone affected. You understand all perspectives. You build consensus slowly. Then you act quickly, because the preparation has already been done.

Good system design is nemawashi for software. When it is done well, the actual building is almost anticlimactic — because every decision has already been made.

---

## System Diagram

```
THE FIVE-STEP DESIGN PROCESS

Step 1: PROBLEM STATEMENT
  "I want to know when plants need water
   without checking manually every day."
   (No solution yet — only the problem)
         │
         ▼
Step 2: ACCEPTANCE CRITERIA
  ✓ Notified at 8am if moisture < 30%
  ✓ 95% sensor accuracy
  ✓ Setup < 5 minutes per plant
  ✓ Cost < $50
         │
         ▼
Step 3: SYSTEM DIAGRAM
  [Sensor]──reading──→[Pi]──stores──→[DB]
                        └──serves──→[MCP]
                                     └──→[AI]──→[Phone]
         │
         ▼
Step 4: RISK TABLE
  Sensor offline → use last-known value + alert
  Pi power out   → accept downtime (UPS optional)
  AI API down    → fall back to rule-based check
         │
         ▼
Step 5: MVP DEFINITION
  Full vision: 8 plants, auto-watering, voice control
  MVP:         1 plant → Pi → text log → manual check
  (Prove core idea works. Then expand.)
```

---

## The Blueprint Process

### Step 1: Define the Problem (Not the Solution)

Bad: "I want to build an app that monitors my plants."

Good: "I want to know when my plants need water without having to check them manually every day. Currently I forget, the plants die, I feel bad, I buy new ones. I want this to happen automatically."

Notice: the good version says nothing about what you will build. It describes the problem, the current situation, the desired outcome. The solution might be an app. Or an alarm. Or a better habit. Or someone else's product. You don't know yet.

> *Now I write the problem statement for my project in the "good" format. I resist the urge to jump to solutions. I ask: "What would have to be true for this problem to not exist?" That question often reveals solutions I never considered.*

### Step 2: Define Success

How will you know when it is working? Be specific. Unmeasurable goals are unachievable goals.

Bad: "Plants are healthy."

Good:
- "I am notified at 8am every day only if any plant is below 30% moisture"
- "Notifications are accurate 95% of the time (sensor is reliable)"
- "I can set up a new plant in less than 5 minutes"
- "The system costs less than $50 to build"

These are your **acceptance criteria** — the test you will run when you think you are done.

### Step 3: Sketch the Components

Take a blank piece of paper. Draw boxes and arrows. This is your **system diagram** — the visual language of architecture.

Rules for a good system diagram:
- Every box is one thing that does one job
- Every arrow is one type of information or control
- Label every arrow with what flows through it
- If a box has more than 3 arrows, it is probably doing too many things

For the plant monitor:

```
[Soil sensor] ──moisture reading──→ [Raspberry Pi]
                                         │
                                    stores to
                                         ↓
                              [Local database (SQLite)]
                                         │
                                    reads from
                                         ↓
                              [MCP Server (Python)]
                                         │
                                    responds to
                                         ↓
                              [AI Agent (claw-code)]
                                         │
                                  reads context and decides
                                         ↓
                              [Notification to phone]
```

This diagram took 5 minutes to draw and communicates the entire architecture. Anyone reading it immediately understands the data flow.

### Step 4: Identify the Risks

For each component, ask: "What if this breaks?"

| Component | Failure mode | Mitigation |
|-----------|-------------|------------|
| Soil sensor | Offline / gives wrong reading | Store last-known-good value. Alert if no reading for > 2 hours |
| Raspberry Pi | Power outage | UPS (uninterruptible power supply) or accept downtime |
| AI Agent | Model API down | Fall back to rule-based threshold check |
| Phone notification | Phone offline | Also send email as backup |

You will not fix all risks before you start. But naming them means you are not surprised when they happen.

### Step 5: Build the Minimum Viable Version

The **MVP (Minimum Viable Product)** is the smallest possible version that proves your core idea works.

For the plant monitor:
- **Full vision:** 8 plants, automatic watering, AI notifications, historical graphs, voice control
- **MVP:** 1 plant sensor → Raspberry Pi → text file log → manual check

The MVP is not the final product. It is the test. It answers: "Does the core idea work?" If yes, build more. If no, adjust the idea — before you spent months building the wrong thing.

---

## 🔬 Lab Activity — Write Your Project Blueprint

**What you'll build:** A complete project blueprint as a real markdown file: problem statement, acceptance criteria, ASCII architecture diagram, risk table, and MVP definition — the actual deliverable that a professional architect produces before writing any code.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell · A project idea (use one from Chapter 24 or your own)

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch28-blueprint
cd C:\labs\ch28-blueprint
```

---

**2. Create the blueprint generator.**

```powershell
notepad blueprint.py
```
Paste:
```python
import os

print("=== Project Blueprint Generator ===")
print("This creates a design document before you write any code.\n")

# Step 1: Problem Statement
print("STEP 1: Problem Statement")
print("Describe the problem (not the solution). Include: current situation, pain point, desired outcome.")
print("Example: 'I forget to water my plants. They die. I want automatic moisture monitoring.'")
print()
project_name = input("Project name: ").strip() or "my-project"
problem      = input("Problem statement (1-3 sentences): ").strip() or "Problem TBD"
print()

# Step 2: Acceptance Criteria
print("STEP 2: Acceptance Criteria (what does 'done' look like?)")
print("Enter 3-5 specific, measurable criteria. Press Enter after each. Empty line to finish.")
criteria = []
while len(criteria) < 10:
    c = input(f"  Criterion {len(criteria)+1}: ").strip()
    if not c:
        break
    criteria.append(c)
if not criteria:
    criteria = ["System works as intended", "Cost within budget", "Setup takes < 10 minutes"]
print()

# Step 3: Components
print("STEP 3: System Components (what are the distinct parts?)")
print("Enter each component name. Empty line to finish.")
components = []
while True:
    c = input(f"  Component {len(components)+1}: ").strip()
    if not c:
        break
    components.append(c)
if not components:
    components = ["Sensor", "Raspberry Pi", "Database", "MCP Server", "AI Agent", "Phone"]
print()

# Step 4: Risks
print("STEP 4: Risk Analysis (what could break?)")
print("Enter: component, failure, mitigation (one per line). Empty to finish.")
risks = []
while True:
    component = input(f"  Risk {len(risks)+1} - Component: ").strip()
    if not component:
        break
    failure   = input(f"  Risk {len(risks)+1} - Failure:   ").strip()
    mitigation= input(f"  Risk {len(risks)+1} - Fix:       ").strip()
    risks.append((component, failure, mitigation))
if not risks:
    risks = [
        ("Database", "Goes offline", "Use last-known-good values"),
        ("API", "Crashes", "Kubernetes restarts it automatically"),
    ]
print()

# Step 5: MVP
print("STEP 5: MVP — Minimum Viable Product")
mvp = input("What is the SMALLEST version that proves your idea works? ").strip()
if not mvp:
    mvp = "Single sensor → read value → print to screen"
full_vision = input("What is the full vision (for later)? ").strip()
if not full_vision:
    full_vision = "Fully automated system with AI and notifications"

# Build the ASCII diagram
component_boxes = " → ".join(f"[{c}]" for c in components[:5])
if len(components) > 5:
    component_boxes += " → ..."

# Write the blueprint
blueprint = f"""# Project Blueprint: {project_name}

## Problem Statement
{problem}

## Acceptance Criteria
{chr(10).join(f'- [ ] {c}' for c in criteria)}

## System Architecture
```
{component_boxes}
```

### Components
{chr(10).join(f'- **{c}**' for c in components)}

## Risk Analysis

| Component | Failure | Mitigation |
|-----------|---------|------------|
{chr(10).join(f'| {r[0]} | {r[1]} | {r[2]} |' for r in risks)}

## MVP Definition
**Minimum Viable Product:** {mvp}

**Full Vision (Phase 2+):** {full_vision}

**Decision:** Build MVP first. Prove the core idea works. Then expand.

---
*Blueprint created before writing any code.*
"""

filename = f"{project_name.lower().replace(' ', '-')}-blueprint.md"
with open(filename, "w") as f:
    f.write(blueprint)
print(f"\nBlueprint saved to: {filename}")
print("\nContents:")
print(blueprint)
```

**3. Run the generator.**

```powershell
python blueprint.py
```
Follow the prompts. Enter your project idea from Chapter 24 (or use the plant monitor). Press Enter for defaults if you want to see a quick example.

✅ After running, you'll have a real project blueprint file:
```powershell
type my-project-blueprint.md
```

**4. Read your own blueprint.**

Before writing any code for your project:
- Does the problem statement describe the problem — not the solution?
- Are your acceptance criteria measurable? (Not "it works" — but "it completes in < 200ms 95% of the time")
- Can you draw your architecture as boxes and arrows?
- Have you named what will break and how to handle it?
- Is your MVP truly minimal?

If yes to all five: you are ready to build.

**What you just built:** A real project blueprint document using the same 5-step process used at Google, Amazon, and every engineering team that builds systems that last.

---

> **🌍 Real World**
> Amazon writes "Working Backwards" press releases before starting any project — the team writes the press release announcing the finished product as if it's complete, then works backward to figure out how to build it. Google uses "Design Docs" — 2-10 page documents covering problem, goals, non-goals, detailed design, and risks — before any code is written. The infamous "Netscape 6 rewrite" disaster (2001) happened because engineers were allowed to rewrite the entire browser without a design phase. They threw away 3 years of browser history, bug fixes, and optimizations, and produced something worse. The lesson — still cited in software engineering — is: design before you build, always.

---

## Connecting Part 6

You now have the full toolkit of the home architect:

- A home lab running real services (Chapter 25)
- A smart home with proper layered architecture (Chapter 26)
- The architect's lens for seeing systems (Chapter 27)
- A design process for building them (Chapter 28)

This is not theoretical knowledge. Every professional architect, engineer, and system designer uses exactly these tools — at every scale, from bedrooms to data centers.

---

## The Takeaway

Design before you build. Define the problem before the solution. Write acceptance criteria before writing code. Draw the diagram before touching the keyboard. Identify risks before they become emergencies. Build the MVP before the full vision. These practices are not bureaucracy — they are the difference between building the right thing and building the wrong thing very thoroughly.

---

## The Connection

You have all the knowledge. Now it is time to use it. Part 7 is where everything converges — we take everything from every chapter and apply it to building something real.

---

*→ Continue to [Chapter 29 — Putting It All Together: Your First Architecture](./ch29-your-first-architecture.md)*
