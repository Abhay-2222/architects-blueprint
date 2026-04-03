# Chapter 5 — What Is a Registry?

*Part 2: The MCP Registry — A Real Backend, Explained*

---

## The Analogy

In the early days of the App Store, before it existed, installing software on your phone was chaos. You had to find the developer's website, download a file, hope it wasn't a virus, figure out how to install it, and then find out — after all that — that it didn't work on your device.

Then Apple built the App Store. Suddenly, one place had everything:
- Every app you could possibly want
- Reviews telling you if it was any good
- A guarantee that it had been reviewed for safety
- One-click installation
- Automatic updates

The App Store is a **registry** — a centralized, organized, trusted list of things.

The MCP Registry is the App Store, but for **AI tools**.

---

## The Concept

A **registry** is an organized, searchable catalog of items that can be discovered and used by others.

You already know several registries without thinking of them that way:

| Registry | What it catalogs | Who uses it |
|----------|-----------------|-------------|
| App Store / Google Play | Mobile apps | Phone users |
| npm (npmjs.com) | JavaScript packages | Web developers |
| PyPI (pypi.org) | Python packages | Python developers |
| Docker Hub | Container images | DevOps engineers |
| **MCP Registry** | AI tools (MCP servers) | AI agents |

The MCP Registry was built to solve a specific problem: **AI agents had no reliable way to discover what tools were available to them.**

Without the Registry, an AI agent would need to be manually told about every tool it could use. That doesn't scale. As the number of AI tools grows into the thousands, you need a directory — a phone book — that the agent can search.

### What Gets Stored in the Registry?

Every entry in the MCP Registry represents one MCP server (one AI tool). Let's look at what information is stored, from the real model types in `registry-main/pkg/model/types.go`:

```go
type Server struct {
    ID          string    // Unique identifier (like "fileReader")
    Name        string    // Human-readable name
    Description string    // What this tool does
    Publisher   Publisher // Who made it and verified it
    Repository  *Repository // Where the source code lives
    Packages    []Package   // How to install it (npm, pip, docker, etc.)
    VersionDetail VersionDetail // What version is available
    CreatedAt   time.Time  // When it was first published
    UpdatedAt   time.Time  // When it was last updated
}
```

Each field answers a question:
- **ID**: What is this called?
- **Name**: How do humans refer to it?
- **Description**: What does it do?
- **Publisher**: Who is responsible for it?
- **Packages**: How do I install it?
- **VersionDetail**: What version am I getting?

This structure is the soul of the Registry. Everything — the API, the database, the validation — exists to create, store, and serve these records.

---

## System Diagram

```
THE REGISTRY: An App Store for AI Tools

Developer publishes:          AI Agent discovers:
  server.json                   GET /v0/servers
       │                               │
       ▼                               ▼
┌─────────────────────────────────────────────┐
│              MCP REGISTRY                   │
│  ┌──────────────────────────────────────┐  │
│  │  servers table (PostgreSQL)          │  │
│  │  ┌──────────┬───────────┬─────────┐  │  │
│  │  │ id       │ name      │ version │  │  │
│  │  ├──────────┼───────────┼─────────┤  │  │
│  │  │fileReader│FileReader │  1.2.0  │  │  │
│  │  │webSearch │Web Search │  2.0.1  │  │  │
│  │  │calendar  │Calendar   │  0.9.3  │  │  │
│  │  └──────────┴───────────┴─────────┘  │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
       │                               │
       ▼                               ▼
 POST /v0/publish               {"servers": [...],
 (requires JWT)                  "total": 247}
```

---

## The Real Code

Let's look at how the Registry handles a request to list all servers. In `registry-main/internal/api/handlers/v0/servers.go`:

```go
func ListServers(c *gin.Context) {
    // 1. Read the query parameters (filters, pagination)
    //    e.g., ?search=file&limit=10&offset=0
    query := parseListQuery(c)

    // 2. Ask the database for matching records
    servers, total, err := service.ListServers(query)

    // 3. Return the results as JSON
    c.JSON(200, ListServersResponse{
        Servers: servers,
        Total:   total,
    })
}
```

Three steps, every time:
1. Read what the client is asking for
2. Go to the database and get it
3. Send it back as JSON

This three-step pattern — **receive, retrieve, respond** — appears in almost every API handler ever written. Learn it once and you will recognize it everywhere.

---

## 🔬 Lab Activity — Query the Live Registry and Build Your Own

**What you'll build:** A Python script that queries the real MCP Registry and displays structured results. Then a mini registry backed by SQLite where you add and search your own entries.

**Time:** ~25 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell · Internet connection

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch05-registry
cd C:\labs\ch05-registry
```

---

**2. Create the file `query_registry.py`.**

This queries the real live MCP Registry:
```powershell
notepad query_registry.py
```
Paste:
```python
import urllib.request
import json

BASE = "https://registry.modelcontextprotocol.io/v0"

def list_servers(limit=10, search=None):
    url = f"{BASE}/servers?limit={limit}"
    if search:
        url += f"&search={search}"
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read())

# Show the registry overview
print("=== MCP Registry Overview ===\n")
data = list_servers(5)
print(f"Total MCP servers registered: {data['total']}\n")
print("First 5 servers:")
print(f"{'ID':<20} {'Name':<30} {'Description'}")
print("-" * 80)
for s in data.get("servers", []):
    name = s.get("name", "N/A")
    desc = s.get("description", "")[:40]
    sid  = s.get("id", "N/A")[:18]
    print(f"{sid:<20} {name:<30} {desc}")

# Show what one full entry looks like
print(f"\n=== Full Entry: '{data['servers'][0]['id']}' ===\n")
server_id = data["servers"][0]["id"]
with urllib.request.urlopen(f"{BASE}/servers/{server_id}") as r:
    full = json.loads(r.read())

for key, value in full.items():
    if isinstance(value, (dict, list)):
        print(f"  {key}: {json.dumps(value)[:80]}")
    else:
        print(f"  {key}: {value}")

print("\n=== Registry Fields We Found ===")
print(f"  id, name, description, version, packages, repository, createdAt, updatedAt")
print("  → These are the same fields as the Server struct in registry-main/pkg/model/types.go")
```

Run it:
```powershell
python query_registry.py
```
✅ You should see the live registry data printed as a formatted table.

---

**3. Create the file `my_registry.py`.**

Build your own registry using SQLite:
```powershell
notepad my_registry.py
```
Paste:
```python
import sqlite3
import json
from datetime import datetime

DB = "my_registry.db"

def setup():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            description TEXT NOT NULL,
            category    TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def add(conn, id, name, description, category):
    conn.execute(
        "INSERT OR REPLACE INTO entries VALUES (?, ?, ?, ?, ?)",
        (id, name, description, category, datetime.now().isoformat())
    )
    conn.commit()
    print(f"  Added: '{name}'")

def list_all(conn):
    rows = conn.execute(
        "SELECT id, name, description, category FROM entries ORDER BY name"
    ).fetchall()
    return rows

def search(conn, query):
    rows = conn.execute(
        "SELECT id, name, description, category FROM entries "
        "WHERE name LIKE ? OR description LIKE ? OR category LIKE ?",
        (f"%{query}%", f"%{query}%", f"%{query}%")
    ).fetchall()
    return rows

# --- Build and use your own registry ---
conn = setup()

print("=== Building My Recipe Registry ===\n")
print("Adding entries:")
add(conn, "pasta-bolognese", "Pasta Bolognese",
    "Classic Italian meat sauce with spaghetti. Serves 4.", "italian")
add(conn, "greek-salad", "Greek Salad",
    "Fresh cucumber, tomato, feta, olives. Ready in 10 minutes.", "salad,vegetarian")
add(conn, "chicken-curry", "Chicken Curry",
    "Spiced coconut milk curry with basmati rice. Medium heat.", "curry")
add(conn, "banana-bread", "Banana Bread",
    "Moist loaf with overripe bananas. Baking time: 60 minutes.", "baking,vegetarian")
add(conn, "stir-fry-veg", "Vegetable Stir Fry",
    "Quick 15-minute stir fry with tofu and seasonal vegetables.", "vegetarian,quick")

print(f"\n=== All {len(list_all(conn))} Entries ===")
print(f"{'ID':<20} {'Name':<25} {'Category'}")
print("-" * 60)
for row in list_all(conn):
    print(f"{row[0]:<20} {row[1]:<25} {row[3] or ''}")

print("\n=== Search: 'vegetarian' ===")
results = search(conn, "vegetarian")
print(f"Found {len(results)} matches:")
for row in results:
    print(f"  - {row[1]}: {row[2][:50]}")

print("\n=== Search: 'quick' ===")
results = search(conn, "quick")
print(f"Found {len(results)} matches:")
for row in results:
    print(f"  - {row[1]}: {row[2][:50]}")

conn.close()
print("\nRegistry saved to: my_registry.db")
print("The MCP Registry is this same structure, but for AI tools instead of recipes.")
```

**4. Run it.**

```powershell
python my_registry.py
```
✅ You should see:
```
=== Building My Recipe Registry ===

Adding entries:
  Added: 'Pasta Bolognese'
  Added: 'Greek Salad'
  Added: 'Chicken Curry'
  Added: 'Banana Bread'
  Added: 'Vegetable Stir Fry'

=== All 5 Entries ===
ID                   Name                      Category
------------------------------------------------------------
banana-bread         Banana Bread              baking,vegetarian
chicken-curry        Chicken Curry             curry
...

=== Search: 'vegetarian' ===
Found 3 matches:
  - Greek Salad: Fresh cucumber, tomato, feta, olives...
  - Banana Bread: Moist loaf with overripe bananas...
  - Vegetable Stir Fry: Quick 15-minute stir fry...
```

**What you just built:** A live query of the MCP Registry showing real production data, and your own SQLite-backed registry with add/list/search — the same three operations the real Registry provides, just for recipes instead of AI tools.

---

> **🌍 Real World**
> npm (Node Package Manager) is the world's largest software registry with over 2 million packages and 3 billion daily downloads. When a JavaScript developer runs `npm install express`, npm queries its registry (at `registry.npmjs.org`), finds the Express package entry, downloads it, and installs it. The MCP Registry follows the same model — publish once, discover anywhere. The difference is that instead of human developers using a package manager, AI agents query the registry automatically at runtime to discover what tools they can use.

---

## The Takeaway

A registry is an organized, searchable catalog — like an App Store, but for whatever you need to catalog. The MCP Registry is the App Store for AI tools. Every field it stores answers a question that an AI agent (or a human developer) would ask when looking for the right tool.

---

## The Connection

The Registry stores data. But where does that data actually live? In Chapter 6, we go underground — into the database — and see how the filing cabinet works: what it stores, how it is organized, and what happens when you need to change its structure without losing anything.

---

*→ Continue to [Chapter 6 — The Database: Your Filing Cabinet](./ch06-the-database.md)*
