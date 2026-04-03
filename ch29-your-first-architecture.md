# Chapter 29 — Putting It All Together: Your First Architecture

*Part 7: Hands Applied — Build Something Real*

---

## The Goal

This chapter does not teach new concepts. Everything you need, you already know.

This chapter takes you through a complete architecture — from problem statement to deployed system — tracing every decision back to a specific chapter. It is the proof that the knowledge is real and transferable.

**The project: A Personal AI Dashboard**

*Problem statement:* I want one place where my AI assistant can see the state of everything that matters to me — my plants, my home, my schedule, my tasks — and help me decide what to do next. Currently, this information is scattered across 6 apps and my AI can't access any of it.

*Acceptance criteria:*
- My AI can answer "what needs my attention right now?" accurately
- All data is private — nothing leaves my home network
- New data sources can be added without rebuilding the whole system
- The system costs less than $100 to run at home

---

## The Architecture Diagram

```
My Phone / Browser (the client — Chapter 2)
        │
        ↓ HTTPS (protocol — Chapter 3)
Nginx Reverse Proxy (routing — Chapter 8)
        │
        ├──→ Home Assistant (smart home hub — Chapter 26)
        │         └──→ Sensors: plants, temp, doors, motion
        │
        ├──→ PostgreSQL (database — Chapter 6)
        │         └──→ Stores: task list, notes, history
        │
        └──→ AI Agent (Chapter 11)
                  │
                  ├──→ MCP: Plant Monitor (Chapter 23-24)
                  ├──→ MCP: Calendar (hypothetical)
                  ├──→ MCP: Task Manager (Chapter 24)
                  └──→ MCP Registry (discover new tools — Chapter 5)
```

Every box traces to a chapter. Every arrow traces to a protocol (Chapter 3). Every decision has a reason.

---

## 🔬 Lab Activity — Create the Core Files

**What you'll build:** The actual database migration, MCP server config, and docker-compose.yml for the Personal AI Dashboard — the files that make the architecture diagram real.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch29-architecture
cd C:\labs\ch29-architecture
mkdir migrations
```

---

**2. Create the database migration.**

```powershell
notepad migrations\001_create_tasks.py
```
Paste:
```python
import sqlite3  # Using SQLite instead of PostgreSQL for this lab

DB = "dashboard.db"
conn = sqlite3.connect(DB)

print("Running migration 001: create tasks table\n")

conn.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        title       TEXT NOT NULL,
        priority    TEXT CHECK (priority IN ('high', 'medium', 'low')) DEFAULT 'medium',
        due_date    TEXT,
        completed   INTEGER DEFAULT 0,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )
""")
print("  ✓ Created table: tasks")

conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_incomplete ON tasks(completed) WHERE completed = 0")
print("  ✓ Created index: idx_tasks_incomplete")

# Track migrations
conn.execute("CREATE TABLE IF NOT EXISTS migrations (id INTEGER PRIMARY KEY, name TEXT, applied_at TEXT DEFAULT CURRENT_TIMESTAMP)")
conn.execute("INSERT OR IGNORE INTO migrations (id, name) VALUES (1, '001_create_tasks')")
print("  ✓ Migration 001 recorded\n")

conn.commit()

# Seed with sample data
conn.execute("INSERT OR IGNORE INTO tasks (id, title, priority, due_date) VALUES (1, 'Review contract', 'high', date('now'))")
conn.execute("INSERT OR IGNORE INTO tasks (id, title, priority, due_date) VALUES (2, 'Water the orchid', 'medium', date('now'))")
conn.execute("INSERT OR IGNORE INTO tasks (id, title, priority) VALUES (3, 'Read chapter 30', 'low')")
conn.commit()

tasks = conn.execute("SELECT id, title, priority, due_date FROM tasks ORDER BY priority").fetchall()
print("Sample data:")
for task in tasks:
    print(f"  [{task[0]}] {task[1]:30} priority={task[2]:6}  due={task[3] or 'none'}")

conn.close()
print(f"\nDatabase saved to: {DB}")
```

**3. Run the migration.**

```powershell
python migrations\001_create_tasks.py
```
✅ You should see:
```
Running migration 001: create tasks table

  ✓ Created table: tasks
  ✓ Created index: idx_tasks_incomplete
  ✓ Migration 001 recorded

Sample data:
  [1] Review contract            priority=high   due=2026-04-02
  [2] Water the orchid           priority=medium  due=2026-04-02
  [3] Read chapter 30            priority=low    due=none
```

---

**4. Create the MCP server config.**

```powershell
notepad mcp_config.json
```
Paste:
```json
{
  "mcpServers": {
    "tasks": {
      "transport": "stdio",
      "command": "python",
      "args": ["task_server.py"],
      "description": "Personal task manager — connects to dashboard.db"
    },
    "plants": {
      "transport": "http",
      "url": "http://localhost:8771",
      "description": "Plant monitor from Chapter 23 lab"
    }
  },
  "comment": "Copy this to ~/.claude/settings.json to use with Claude Code"
}
```

---

**5. Create the AI query simulator.**

```powershell
notepad ai_query.py
```
Paste:
```python
import sqlite3, json

def get_tasks(priority_filter=None):
    conn = sqlite3.connect("dashboard.db")
    if priority_filter:
        tasks = conn.execute("SELECT title, priority, due_date FROM tasks WHERE completed=0 AND priority=? ORDER BY priority", (priority_filter,)).fetchall()
    else:
        tasks = conn.execute("SELECT title, priority, due_date FROM tasks WHERE completed=0 ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END").fetchall()
    conn.close()
    return [{"title": t[0], "priority": t[1], "due": t[2]} for t in tasks]

# Simulate the AI answering: "What needs my attention right now?"
print('=== AI Query: "What needs my attention right now?" ===\n')
print("AI checking tasks database...")
tasks = get_tasks()

print(f"\nAI response:")
print(f"You have {len(tasks)} pending tasks:")
for task in tasks:
    due_str = f" (due {task['due']})" if task['due'] else ""
    urgency = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
    print(f"  {urgency} [{task['priority'].upper()}] {task['title']}{due_str}")

if any(t['priority'] == 'high' for t in tasks):
    print("\nMost urgent: high-priority tasks due today. I recommend starting with those.")
```

**6. Run the AI query.**

```powershell
python ai_query.py
```
✅ You should see:
```
=== AI Query: "What needs my attention right now?" ===

AI checking tasks database...

AI response:
You have 3 pending tasks:
  🔴 [HIGH] Review contract (due 2026-04-02)
  🟡 [MEDIUM] Water the orchid (due 2026-04-02)
  🟢 [LOW] Read chapter 30

Most urgent: high-priority tasks due today. I recommend starting with those.
```

**What you just built:** The database migration (with CHECK constraint), MCP config, and AI query layer for the Personal AI Dashboard — every component traced to its chapter, every decision reasoned explicitly.

---

## Building It: Step by Step

### Step 1 — The Home Lab (Chapter 25)

> *Now I set up the Raspberry Pi 5 as my home server. I install Docker and Docker Compose. I run `docker-compose up` and within 10 minutes I have a PostgreSQL database and a local Nginx reverse proxy running. I verify by opening a browser on my laptop and navigating to `http://192.168.1.50/`. I see the Nginx welcome page. Foundation is solid.*

### Step 2 — The Database Schema (Chapter 6)

I need to store tasks. I write my first migration:

```sql
-- 001_create_tasks_table.sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    priority VARCHAR(10) CHECK (priority IN ('high', 'medium', 'low')),
    due_date DATE,
    completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast lookup of incomplete tasks
CREATE INDEX idx_tasks_incomplete ON tasks(completed) WHERE completed = false;
```

> *Now I add the `CHECK` constraint on `priority`. I do this because I learned in Chapter 6 that the database is a second line of defense. Even if my application has a bug and tries to create a task with priority "urgent," the database will refuse. Only "high," "medium," or "low" are allowed. The constraint enforces data integrity at the storage level.*

### Step 3 — The MCP Server (Chapter 24)

I build a task manager MCP server. It exposes three tools:

```
get_tasks()          → returns incomplete tasks sorted by priority
add_task(title, priority, due_date)  → creates a new task
complete_task(id)    → marks a task as done
```

> *Now I write the tool descriptions. For `get_tasks`, I write: "Returns all incomplete tasks sorted by priority (high first). Use this when the user asks 'what do I need to do' or 'what's on my list' or 'what's my highest priority right now'." I include multiple phrasings because I know from Chapter 12 that the AI matches tool descriptions to user intent — more phrasings mean more reliable matching.*

### Step 4 — Authentication (Chapter 7)

My dashboard is accessible from the internet (so I can check it from anywhere). This means I need authentication.

> *Now I add JWT authentication to my task API. I generate an Ed25519 key pair (the same method the MCP Registry uses). My personal API client gets a long-lived token. The token expires after 24 hours. If it's stolen, the thief has at most 24 hours of access. I set this rather than 5 minutes (like the Registry) because I am the only user and re-authenticating every 5 minutes is annoying for a personal tool.*

This is an architectural decision: security vs. convenience. I am making the tradeoff explicitly, not accidentally.

### Step 5 — The AI Agent Connection (Chapters 11, 16)

I configure my local AI agent (running Ollama with a local model) to connect to my MCP servers:

```json
{
  "mcpServers": {
    "tasks": {
      "transport": "stdio",
      "command": "python",
      "args": ["/home/pi/task-mcp/server.py"]
    },
    "plants": {
      "transport": "http",
      "url": "http://localhost:3001",
      "headers": { "Authorization": "Bearer my-home-token" }
    },
    "home": {
      "transport": "http",
      "url": "http://localhost:8123/api/mcp",
      "headers": { "Authorization": "Bearer home-assistant-token" }
    }
  }
}
```

> *Now I test by asking my AI: "What needs my attention right now?" The agent calls `get_tasks`, `list_plants`, and reads the Home Assistant state. It responds: "Three things need your attention: 1. The orchid is critically dry (21% moisture). 2. You have a high-priority task 'Review contract' due today. 3. The front door has been open for 20 minutes." This is exactly what I wanted. Three data sources. One intelligent answer. Everything private — no data left my home network.*

### Step 6 — Monitoring (Chapter 21)

> *Now I add monitoring. I run Prometheus and Grafana in Docker. I add a probe that checks `/healthz` on every service every 30 seconds. I add an alert: if any service fails to respond for 3 minutes, send a message to my phone. I set up one dashboard showing: uptime for each service, response time for the AI, number of tasks completed per day, plant moisture over 7 days.*

### Step 7 — CI/CD (Chapter 20)

> *Now I set up a simple CI pipeline using GitHub Actions. When I push changes to my MCP server code, the pipeline runs tests and deploys to the Raspberry Pi automatically via SSH. I no longer need to manually copy files — I just push to GitHub and my home server updates itself within 2 minutes.*

---

## The Completed System

Look back at the architecture diagram. Every box is running. Every arrow carries data. The system does what it was designed to do.

But more importantly: you understand every part of it. If something breaks, you know where to look. If you want to add a new data source, you know how to build a new MCP server and connect it. If traffic grows (unlikely for a personal tool, but possible if you share it), you know how to scale with Kubernetes.

**You are no longer a user of systems. You are an architect of them.**

---

> **🌍 Real World**
> Every successful tech product started as exactly this: a small personal system built by someone who had a problem. Flickr started as a feature in an online game. Instagram was a pivot from a location check-in app. Slack started as a game studio's internal communication tool. The Personal AI Dashboard you just designed — task manager + plant monitor + home state + AI — is a real product category. Several YC-funded startups in 2025 are building exactly this ("personal AI OS"). The difference between your version and theirs: scale, polish, and distribution. The architecture is identical.

---

## The Takeaway

Architecture is not magic. It is a sequence of decisions, each traceable to a principle. This chapter traced every decision to its chapter, its concept, and its reasoning. Your first architecture will be smaller and messier than this one — and that is completely correct. Start small. Make decisions explicitly. Trace every choice back to a principle. Build it, run it, break it, fix it. That is how architects are made.

---

## The Connection

You built a system for yourself. Now — how do you turn that skill into a product? Into a strategy? Into something that serves people you've never met? Chapter 30 teaches product thinking: how to see problems as systems, and systems as products.

---

*→ Continue to [Chapter 30 — Product Thinking: Seeing Problems as Systems](./ch30-product-thinking.md)*
