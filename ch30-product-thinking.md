# Chapter 30 — Product Thinking: Seeing Problems as Systems

*Part 7: Hands Applied — Build Something Real*

---

## The Analogy

Before the iPhone, phones had keyboards. That was just how phones were. Everyone accepted it. Nobody said "this is wrong" — because it had always been true.

Steve Jobs and his team asked a different question: *What if you didn't need a keyboard?* Not "how do we make a better keyboard phone" — but "what if the keyboard itself was the wrong answer?"

This is product thinking: the ability to see a current situation and ask whether it is *necessarily* the way things are, or just the way they have *always been*.

The MCP Registry existed because someone saw a problem — AI agents had no reliable way to discover tools — and asked: "What is the simplest system that makes this discoverable?" They did not add features to existing tools. They identified the gap and built the right thing to fill it.

---

## The Concept

**Product thinking** is the practice of:
1. Seeing a problem clearly (not its symptoms, but the root)
2. Understanding who has the problem and why it matters to them
3. Designing the minimum system that solves it
4. Validating that the solution works before building the full version

It is the architect's lens (Chapter 27) applied to human needs rather than software systems.

---

## System Diagram

```
THREE LEVELS OF JOB-TO-BE-DONE

Surface Job (what they say):
  "I need a tool that monitors soil moisture"
         │
         ▼
Deeper Job (what they really mean):
  "I want to know when plants need water
   without having to check manually"
         │
         ▼
Deepest Job (fundamental human need):
  "I want living things to thrive under my care
   without constant anxiety or effort"

The product that solves the DEEPEST job wins.
Everything else is a feature, not a solution.

MCP Registry example:
  Surface: "List MCP servers"
  Deeper:  "Let agents discover tools without custom code"
  Deepest: "Make AI useful everywhere, not just in demos"
```

---

### The Jobs-to-Be-Done Framework

People don't buy products. They hire them to do a job.

People don't buy a drill. They hire a drill to make a hole. But what they really want is a picture on the wall. A drill that could put a picture on the wall without making a hole would win the market.

Understanding the real job — not the stated one — is the key to building something people actually want.

**The MCP Registry's real job:**
- Surface job: "List MCP servers"
- Deeper job: "Let AI agents discover and use tools without custom integration work"
- Deepest job: "Make AI useful in contexts it currently can't reach"

A product team that thought only about the surface job would build a search engine for tool documentation. The team that understood the deepest job built a protocol + registry + publisher workflow that integrates into every AI agent automatically.

---

## The MCP Registry as a Product Case Study

Let's analyze the Registry using product thinking tools.

### Who has the problem?

**Primary users:**
- AI agent developers (they want their agents to use more tools)
- Tool developers (they want their tools to be discoverable)

**Secondary users:**
- End users (they want AI to do more things for them)

### What is the pain today?

Without the Registry:
- Tool developers write documentation, hoping agents find it
- Agent developers manually integrate each tool with custom code
- There is no standard — every integration is different
- Adding one new tool requires significant engineering work

### What does success look like?

With the Registry:
- A tool developer publishes once, all agents discover automatically
- An agent developer configures once, gains access to hundreds of tools
- The standard is MCP, so every tool works with every agent
- Adding a new tool takes minutes, not days

### The Minimum Viable Registry

What is the smallest version that proves the idea?

- A JSON file listing 10 MCP servers ← too minimal, no discovery mechanism
- A GitHub repo with a README ← better, but no machine-readable format
- A REST API that returns a JSON list of servers ← MVP. Anyone can query it.

The MVP is the REST API. It doesn't need authentication, validation, versioning, or a publisher CLI. It just needs to return a list that AI agents can query. Everything else is iteration.

---

## 🔬 Lab Activity — Write a Product Brief as a JSON File

**What you'll build:** A machine-readable product brief in JSON, a Python script that validates it against required fields and surface/deeper/deepest job structure, and a markdown output for sharing — applying product thinking systematically to your own project.

**Time:** ~15 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch30-product
cd C:\labs\ch30-product
```

---

**2. Create your product brief JSON.**

```powershell
notepad product_brief.json
```
Paste and fill in your own project (or use this example):
```json
{
  "product_name": "Plant Monitor MCP",
  "author": "yourname",
  "date": "2026-04-02",
  "jobs_to_be_done": {
    "surface": "Reports soil moisture percentage for houseplants",
    "deeper": "Tells users when plants need water without manual checking",
    "deepest": "Lets users keep living things healthy without constant anxiety"
  },
  "users": {
    "primary": "Plant owners who travel frequently or have busy schedules",
    "secondary": "Gardening enthusiasts who want data on plant health",
    "non_user": "Professional greenhouse operations (different scale, different tool)"
  },
  "pain_levels": {
    "primary": "high",
    "secondary": "medium"
  },
  "hypothesis": "Plant owners will water plants more reliably if given a specific, timely moisture alert",
  "mvp": "One sensor → Raspberry Pi → text message at 8am if moisture < 30%. No app.",
  "success_metrics": [
    "User waters plant within 4 hours of receiving alert (95% of cases)",
    "Zero false positives in first 7 days",
    "Setup time < 10 minutes for first plant"
  ],
  "not_in_scope": [
    "Voice control (prove notifications work first)",
    "Multiple users / sharing (personal tool for now)",
    "Automatic watering pump (add after manual alerts validated)",
    "Historical graphs dashboard (MVP is alerts only)"
  ],
  "ten_x_vision": "System waters plants automatically — user never thinks about it. Plants are always healthy."
}
```

---

**3. Create the validator and output generator.**

```powershell
notepad product_analyzer.py
```
Paste:
```python
import json

with open("product_brief.json") as f:
    brief = json.load(f)

print(f"=== Product Brief: {brief['product_name']} ===\n")

# Validate structure
required = ["jobs_to_be_done", "users", "hypothesis", "mvp", "success_metrics", "not_in_scope"]
missing = [r for r in required if r not in brief]
if missing:
    print(f"INCOMPLETE BRIEF — missing: {missing}")
else:
    print("✓ Brief is complete\n")

# Display three-level job
print("JOBS TO BE DONE:")
for level in ["surface", "deeper", "deepest"]:
    label = {"surface": "Surface (what they say)",
             "deeper":  "Deeper  (what they mean)",
             "deepest": "Deepest (fundamental need)"}[level]
    print(f"  {label}:")
    print(f"    \"{brief['jobs_to_be_done'][level]}\"")

# User analysis
print(f"\nUSERS:")
print(f"  Primary   ({brief['pain_levels']['primary']} pain):   {brief['users']['primary']}")
print(f"  Secondary ({brief['pain_levels']['secondary']} pain): {brief['users']['secondary']}")
print(f"  Not targeting yet: {brief['users']['non_user']}")

# Hypothesis
print(f"\nHYPOTHESIS TO TEST:")
print(f"  \"{brief['hypothesis']}\"")

# MVP
print(f"\nMVP (smallest version that tests hypothesis):")
print(f"  {brief['mvp']}")

# Success
print(f"\nSUCCESS METRICS:")
for i, m in enumerate(brief["success_metrics"], 1):
    print(f"  {i}. {m}")

# Not in scope
print(f"\nNOT IN SCOPE (discipline required):")
for item in brief["not_in_scope"]:
    print(f"  ✗ {item}")

# 10x vision
print(f"\n10X VISION (the north star, not the MVP):")
print(f"  \"{brief['ten_x_vision']}\"")

# Write markdown output
md = f"""# Product Brief: {brief["product_name"]}
*Written: {brief.get("date", "?")} by {brief.get("author", "?")}*

## Jobs to Be Done
- **Surface**: {brief["jobs_to_be_done"]["surface"]}
- **Deeper**: {brief["jobs_to_be_done"]["deeper"]}
- **Deepest**: {brief["jobs_to_be_done"]["deepest"]}

## Users
- Primary ({brief["pain_levels"]["primary"]} pain): {brief["users"]["primary"]}
- Secondary: {brief["users"]["secondary"]}

## Hypothesis
{brief["hypothesis"]}

## MVP
{brief["mvp"]}

## Success Metrics
{chr(10).join(f"- [ ] {m}" for m in brief["success_metrics"])}

## Not In Scope
{chr(10).join(f"- ~~{item}~~" for item in brief["not_in_scope"])}

## 10x Vision
*{brief["ten_x_vision"]}*
"""

with open("product_brief_output.md", "w") as f:
    f.write(md)
print(f"\nMarkdown saved to: product_brief_output.md")
```

**4. Run it.**

```powershell
python product_analyzer.py
```
✅ You see the full product analysis and a markdown file is created.

**What you built:** A machine-validated, human-readable product brief applying the Jobs-to-Be-Done framework — the same thinking process used by product teams at Anthropic, Notion, and Figma before they write a single line of code.

---

> **🌍 Real World**
> The "Jobs to Be Done" framework was developed by Harvard Business School professor Clayton Christensen and is used by Apple, Intercom, and Basecamp as their primary product framework. When Intercom interviewed customers asking "why do you use our messaging tool?" the surface answer was "to talk to customers." The deeper answer was "to convert website visitors." The deepest was "to grow revenue without hiring a sales team." That insight led them to build revenue-generation features, not just better chat. The MCP Registry team at Anthropic understood the deepest job — "make AI capable everywhere, not just in demos" — and built a protocol, not just a list.

---

## Research Spotlight

> **"Learning multiple layers of representation"**
> Hinton, G. E. (2007). *Trends in Cognitive Sciences*, 11(10), 428–434.

In this paper, Hinton describes how the brain (and deep neural networks) build understanding by stacking representations — each layer making sense of the layer below. A product that achieves the deepest job is doing the same thing: it understands not just what the user asked for (the surface), but why they need it (the deeper layers of meaning).

A great product is built on multiple layers of user understanding, just as a deep learning model is built on multiple layers of learned representations.

Available at: https://www.cs.toronto.edu/~hinton/pages/publications.html

---

## The Takeaway

Product thinking is seeing a problem at all three levels — surface, deeper, deepest — and designing the minimum system that addresses the deepest one. The MCP Registry exists because someone understood that the deepest job wasn't "list servers" but "make AI universally capable." Your deepest job is always more interesting than your surface job. Find it, and your product becomes inevitable.

---

## The Connection

You can see the problem. Now you need a plan — a strategy that turns insight into a roadmap, and a roadmap into something built. Chapter 31 is about moving from idea to architecture, and from architecture to action.

---

*→ Continue to [Chapter 31 — Product Strategy: From Idea to Architecture](./ch31-product-strategy.md)*
