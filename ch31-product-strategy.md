# Chapter 31 — Product Strategy: From Idea to Architecture

*Part 7: Hands Applied — Build Something Real*

---

## The Analogy

A general planning a military campaign does not walk to the battlefield and start fighting. They study maps. They assess their forces and their opponent's. They identify terrain advantages. They choose the right moment. They plan supply lines. Only then do they move.

The campaign plan is not the battle. But without it, the battle is chaos.

**A product strategy is the campaign plan.**

It does not build the product. It decides:
- Which problem to solve first (and why not the others)
- Who the first users will be (and why not everyone)
- What success looks like in 3 months (not 3 years)
- What you will NOT build (the most underrated strategic decision)

Without strategy, builders build interesting things that nobody needs in the order that felt exciting rather than the order that matters.

---

## The One-Page Product Brief

Every product should fit on one page before it is built. If you cannot explain it on one page, you do not understand it well enough yet.

Here is the format:

```
PRODUCT: [Name]
DATE: [When written]

PROBLEM
[2-3 sentences: What is happening now that shouldn't be? Who experiences this?]

SOLUTION
[2-3 sentences: What will you build? How does it solve the problem?]

TARGET USER
[1 sentence: Who is this for? Be specific — not "everyone."]

SUCCESS METRICS
[3-5 measurable criteria that would tell you the product works]

MVP
[What is the smallest version that tests the core hypothesis?]

NOT IN SCOPE
[At least 3 things you will NOT build, even if they seem useful]
```

The "Not in Scope" section is the most important. Every product dies from trying to do too much. Deciding what NOT to build is harder than deciding what to build — and more important.

---

## System Diagram

```
FROM PRODUCT BRIEF TO ARCHITECTURE

Product Requirement          Architectural Decision
────────────────────         ──────────────────────
"Publish once, discover      → REST API + Registry DB
 from anywhere"                (Chapters 4, 5, 6)

"Only valid entries"         → Schema validation
                               (Chapter 9)

"Track who published what"   → JWT auth + publisher identity
                               (Chapter 7)

"Reliable in production"     → Kubernetes + monitoring
                               (Chapters 19, 21)

"Standard format"            → JSON schemas in /schemas/
                               (Chapters 3, 9)

"Publisher workflow"         → publisher CLI tool
                               (Chapter 10)

One product brief → 
  Six architectural decisions →
    Six chapters of implementation
```

---

## Strategy Applied: The MCP Registry

Let's reverse-engineer the Registry's strategy from what we know:

**PROBLEM:** AI agents have no reliable, standard way to discover what tools are available to them. Every integration is custom. There is no App Store equivalent for AI tools.

**SOLUTION:** A REST API registry where tool developers publish server metadata, and AI agents can query to discover available tools.

**TARGET USER:** First: developers of AI coding assistants. Second: developers of MCP-compatible tools.

**SUCCESS METRICS:**
1. AI agents can query the API and discover tools without custom code
2. Tool developers can publish in < 30 minutes
3. At least 100 real MCP servers listed within 90 days of launch

**MVP:** A REST API (`GET /servers`) that returns a JSON list. No authentication. No validation. No publisher CLI. Just a list.

**NOT IN SCOPE (initially):**
- Mobile apps
- Reviews or ratings
- Usage analytics
- Billing or monetization
- Webhooks or real-time updates

The Registry team launched a working system precisely because they were clear about what they were not building.

---

## Mapping Idea to Architecture

Once the product brief is clear, you translate it into architecture using the tools from Chapter 27 and 28.

### The Translation Matrix

| Product requirement | Architectural decision | Chapter |
|--------------------|----------------------|---------|
| "Tool developers can publish" | Need a publisher CLI + publish API endpoint | Ch 10 |
| "AI agents can query tools" | Need a GET /servers API | Ch 4, 8 |
| "Who published what" | Need authentication + publisher identity | Ch 7 |
| "Only valid entries" | Need schema validation | Ch 9 |
| "Reliable in production" | Need Kubernetes + monitoring | Ch 19, 21 |
| "Standard format" | Need JSON schemas | Ch 3, 9 |

Every product requirement translates to an architectural decision. The architecture serves the product. The product serves the user.

---

## 🔬 Lab Activity — Write Your One-Page Strategy Document

**What you'll build:** A complete one-page product strategy document as a Python-generated markdown file — covering problem, solution, users, metrics, MVP, not-in-scope, and a 90-day phase plan, then a translation matrix connecting product requirements to architectural components.

**Time:** ~15 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch31-strategy
cd C:\labs\ch31-strategy
```

---

**2. Create the strategy generator.**

```powershell
notepad strategy.py
```
Paste:
```python
# Fill in your project details below, then run this script
# to generate a professional one-page strategy document.

STRATEGY = {
    "product": "Plant Monitor MCP",
    "date": "2026-04-02",
    "problem": (
        "Plant owners who travel or have busy schedules frequently forget to water houseplants, "
        "causing them to die. There is no reliable way to monitor plant moisture without manually "
        "checking — which requires remembering to check."
    ),
    "solution": (
        "A Raspberry Pi-based soil moisture monitor that sends a daily notification at 8am "
        "if any plant needs water. An AI agent connected via MCP can also query plant status "
        "on demand and recommend actions."
    ),
    "target_user": (
        "People who travel 5+ days per month and own 3-10 houseplants, "
        "who have lost plants before due to forgetting to water while away."
    ),
    "success_metrics": [
        "User waters plant within 4 hours of alert in 9 out of 10 cases",
        "Zero sensor false positives in first 14 days",
        "System setup takes < 10 minutes per plant",
        "Zero plants die due to under-watering in Month 1",
    ],
    "mvp": (
        "One soil sensor → Raspberry Pi → reads moisture every hour → "
        "sends text message at 8am if moisture < 30%. "
        "No app. No dashboard. No AI. Just a reliable alert."
    ),
    "not_in_scope": [
        "Automatic watering pump (validate alerts first, then automate)",
        "Voice control input (core job is monitoring, not interaction)",
        "Multi-user sharing (personal tool for now)",
        "Historical graphs or dashboard (alerts only for MVP)",
        "Mobile app (SMS is sufficient for MVP)",
    ],
    "phase_plan": {
        "Month 1 (MVP)": [
            "Buy Raspberry Pi + soil moisture sensor",
            "Write Python script to read sensor",
            "Set up SMS notifications via free API",
            "Test with 1 plant for 2 weeks",
            "Validate: do alerts lead to watering?",
        ],
        "Month 2 (Full Journey)": [
            "Build MCP server (Chapter 24 pattern)",
            "Connect Claude Code as the AI agent",
            "Add 2-3 more plants",
            "Build query interface ('which plants need water now?')",
        ],
        "Month 3 (Polish + 2x Feature)": [
            "Add Home Assistant integration (Chapter 26)",
            "Create automations for morning plant checks",
            "Add the one feature that makes it 2x better: watering reminder calendar",
            "Write server.json, publish to MCP Registry",
        ],
    },
    "translation_matrix": [
        ("Alerts when moisture < 30%", "Raspberry Pi + Python + SMS API"),
        ("AI can query plant status", "MCP Server (Chapter 24)"),
        ("Only your agent can connect", "JWT Authentication (Chapter 7)"),
        ("Runs at home, private",    "Home Lab on Pi (Chapter 25)"),
        ("Discoverable by any agent", "MCP Registry entry (Chapters 5, 10)"),
        ("Reliable uptime",          "Docker + auto-restart (Chapter 18)"),
    ],
}

# Generate the document
lines = [
    f"# One-Page Product Strategy: {STRATEGY['product']}",
    f"*Written: {STRATEGY['date']}*\n",
    "## Problem",
    STRATEGY["problem"] + "\n",
    "## Solution",
    STRATEGY["solution"] + "\n",
    "## Target User",
    STRATEGY["target_user"] + "\n",
    "## Success Metrics",
    *[f"- [ ] {m}" for m in STRATEGY["success_metrics"]],
    "",
    "## MVP",
    STRATEGY["mvp"] + "\n",
    "## Not In Scope",
    *[f"- ~~{item}~~" for item in STRATEGY["not_in_scope"]],
    "",
    "## 90-Day Phase Plan",
]
for phase, tasks in STRATEGY["phase_plan"].items():
    lines.append(f"\n### {phase}")
    lines.extend(f"- {t}" for t in tasks)

lines += [
    "",
    "## Product → Architecture Translation Matrix",
    "",
    "| Product Requirement | Architectural Component |",
    "|---------------------|------------------------|",
    *[f"| {r} | {a} |" for r, a in STRATEGY["translation_matrix"]],
]

doc = "\n".join(lines)

print(doc)
print()

with open("product_strategy.md", "w") as f:
    f.write(doc)
print("Saved to: product_strategy.md")
```

**3. Run it.**

```powershell
python strategy.py
```
✅ You see the full strategy document printed and saved. Read it:
```powershell
type product_strategy.md
```

**4. Customize for your own project.**

Open `strategy.py` and replace the STRATEGY dictionary values with your own project. Re-run — you now have a professional strategy document for your project.

**What you just built:** A complete one-page strategy document with problem statement, user definition, success metrics, MVP, phase plan, and architecture translation matrix — the deliverable that engineering and product teams produce before any development starts.

---

## The Takeaway

A product strategy is the campaign plan — it decides what to build, who for, in what order, and what not to build. The one-page product brief forces clarity before complexity. The translation matrix connects product requirements to architectural decisions. A 90-day phased plan stages complexity — proving the simple before building the sophisticated.

---

## The Connection

You have a strategy. You have an architecture. You can build it. But the biggest chapter still awaits — for the designers, the dreamers, and the people who have ideas worth building but don't know how to start. Chapter 32 is the most important chapter in this book for that person.

---

*→ Continue to [Chapter 32 — The Product Designer's Chapter](./ch32-product-designer.md)*
