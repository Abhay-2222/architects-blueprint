# Chapter 6 — The Database: Your Filing Cabinet

*Part 2: The MCP Registry — A Real Backend, Explained*

---

## The Analogy

Imagine an office from the 1950s. No computers. Just rows and rows of metal filing cabinets. Each drawer is labeled. Inside the drawers are folders. Inside the folders are papers.

Need to find a client's contract? You go to the cabinet labeled "Clients," pull open the "A–F" drawer, flip through the folders until you find "Acme Inc.," and pull out the document.

Need to update the contract? You take it out, make changes, put it back.

The office works because of three things:
1. **Organization** — everything has a specific place
2. **Labels** — so you can find things quickly
3. **Structure** — all contracts look the same, so you always know what you're looking at

A database is exactly this — but instead of paper and metal cabinets, it is organized digital storage that can hold millions of records and find any one of them in milliseconds.

---

## The Concept

A **database** is an organized collection of data that can be stored, searched, and updated reliably.

The MCP Registry uses **PostgreSQL** — one of the most trusted databases in the world, used by companies from tiny startups to Instagram and Spotify.

### Tables: The Drawers

In PostgreSQL, data is stored in **tables**. A table is like one drawer in a filing cabinet. The "servers" drawer holds all registered MCP servers. Each row in the table is one server. Each column is one piece of information about that server.

Here is the actual `servers` table from the Registry's first migration (`001_initial_schema.sql`):

```sql
CREATE TABLE servers (
    id          UUID PRIMARY KEY,    -- Unique ID for each server
    name        VARCHAR(255) NOT NULL, -- The server's name
    description TEXT NOT NULL,        -- What it does
    status      VARCHAR(50),          -- "active" or "inactive"
    version     VARCHAR(255) NOT NULL, -- Version number (e.g., "1.2.0")
    packages    JSONB,                -- Installation instructions
    created_at  TIMESTAMP,            -- When it was first added
    updated_at  TIMESTAMP             -- When it was last changed
);
```

Each column is a type of information — like the columns in a spreadsheet. Every row is one record — one MCP server.

### UUID: The Social Security Number

Notice the `id` column has type `UUID`. A UUID looks like this:

```
550e8400-e29b-41d4-a716-446655440000
```

It is a randomly generated number so large that two people generating one at the same moment will almost certainly get different values. UUIDs are used as unique identifiers because they work even when you have multiple servers creating records simultaneously — unlike simple numbers (1, 2, 3...) which would conflict.

### Indexes: The Tabs on the Folders

If you have a filing cabinet with 10,000 folders, finding one by flipping through them one by one would take forever. That's why folders have tabs — labeled markers that let you jump straight to the right section.

Databases have **indexes** for the same reason:

```sql
-- Create a fast-lookup tab on the "name" column
CREATE INDEX idx_servers_name ON servers(name);

-- Create a tab on "status" specifically for active servers
CREATE INDEX idx_servers_status ON servers(status);
```

With these indexes, searching for a server by name or status takes microseconds instead of scanning the entire table.

---

## System Diagram

```
DATABASE ANATOMY

┌─────────────────────────────────────────────┐
│  PostgreSQL / SQLite Database               │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │  TABLE: servers                       │  │
│  │  ┌──────────┬─────────┬───────────┐  │  │
│  │  │ id (PK)  │ name    │ version   │  │  │  ← columns
│  │  ├──────────┼─────────┼───────────┤  │  │
│  │  │ uuid-1   │FileRead │ 1.2.0     │  │  │  ← rows
│  │  │ uuid-2   │WebSearch│ 2.0.1     │  │  │
│  │  └──────────┴─────────┴───────────┘  │  │
│  │                                       │  │
│  │  INDEX: idx_servers_name              │  │  ← fast lookup tab
│  └───────────────────────────────────────┘  │
│                                             │
│  MIGRATIONS (change history):               │
│  001_initial_schema.sql  ← ran 2024-01-01  │
│  002_add_extensions.sql  ← ran 2024-02-15  │
│  003_add_status.sql      ← ran 2024-03-10  │
└─────────────────────────────────────────────┘
```

---

## Migrations: Renovating While Staying Open

Here is one of the most important concepts in this chapter:

**What do you do when you need to change the database structure, but the system is already running?**

This is like trying to renovate a hotel while guests are sleeping in it. You can't just tear down a wall — people are on the other side of it.

The MCP Registry solves this with **migrations** — small, numbered change scripts that update the database structure safely, one step at a time.

Look at the 13 migrations in `registry-main/internal/database/migrations/`:

```
001_initial_schema.sql          ← Build the first room
002_add_server_extensions.sql   ← Add a window
003_simplify_to_key_value.sql   ← Rearrange the furniture
004_update_meta_field_format.sql ← Change the shelf labels
005_add_server_id_rename_...    ← Rename a room
...
013_add_status_fields.sql       ← Add a new signage system
```

Each migration only runs once, in order, and never goes backward. The database keeps track of which migrations have already been run. This way, a developer in another country can get the exact same database structure by running the same migrations in the same order.

This is how production databases evolve over months and years — not by rebuilding from scratch, but by carefully, incrementally renovating.

---

## 🔬 Lab Activity — Create a Real Database with Migrations

**What you'll build:** A SQLite database modelling the MCP Registry's schema, with two migrations, indexes, and real data — all controlled by Python scripts you create and run.

**Time:** ~25 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell (SQLite3 is built into Python — no extra install)

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch06-database
cd C:\labs\ch06-database
```

---

**2. Create the file `migration_001.py`.**

This is your first migration — building the initial schema:
```powershell
notepad migration_001.py
```
Paste:
```python
import sqlite3

DB = "registry.db"
conn = sqlite3.connect(DB)

print("Running migration 001: initial schema\n")

# Create the servers table
conn.execute("""
    CREATE TABLE IF NOT EXISTS servers (
        id          TEXT PRIMARY KEY,
        name        TEXT NOT NULL,
        description TEXT NOT NULL,
        status      TEXT DEFAULT 'active',
        version     TEXT NOT NULL,
        packages    TEXT,              -- JSON string (SQLite has no JSONB)
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )
""")
print("  ✓ Created table: servers")

# Create indexes for fast lookup
conn.execute("CREATE INDEX IF NOT EXISTS idx_servers_name   ON servers(name)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_servers_status ON servers(status)")
print("  ✓ Created index: idx_servers_name")
print("  ✓ Created index: idx_servers_status")

# Track that this migration ran
conn.execute("""
    CREATE TABLE IF NOT EXISTS migrations (
        id         INTEGER PRIMARY KEY,
        name       TEXT NOT NULL,
        applied_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.execute("INSERT OR IGNORE INTO migrations (id, name) VALUES (1, '001_initial_schema')")
print("  ✓ Migration 001 recorded\n")

conn.commit()
conn.close()
print("Migration 001 complete. Database: registry.db")
```

**3. Run migration 001.**

```powershell
python migration_001.py
```
✅ You should see:
```
Running migration 001: initial schema

  ✓ Created table: servers
  ✓ Created index: idx_servers_name
  ✓ Created index: idx_servers_status
  ✓ Migration 001 recorded

Migration 001 complete. Database: registry.db
```
✅ Confirm the file exists:
```powershell
dir C:\labs\ch06-database
```
✅ You should see `registry.db` listed.

---

**4. Create the file `seed_data.py`.**

Insert real records into your database:
```powershell
notepad seed_data.py
```
Paste:
```python
import sqlite3
import json

DB = "registry.db"
conn = sqlite3.connect(DB)

print("Inserting seed data...\n")

servers = [
    {
        "id": "fileReader",
        "name": "FileReader MCP",
        "description": "Reads files from your local computer. Supports .txt, .pdf, .md formats.",
        "status": "active",
        "version": "1.2.0",
        "packages": json.dumps([{"registry": "npm", "name": "@tools/file-reader", "version": "1.2.0"}])
    },
    {
        "id": "webSearch",
        "name": "Web Search MCP",
        "description": "Searches the internet using multiple search engines.",
        "status": "active",
        "version": "2.0.1",
        "packages": json.dumps([{"registry": "npm", "name": "@tools/web-search", "version": "2.0.1"}])
    },
    {
        "id": "calendarMcp",
        "name": "Calendar MCP",
        "description": "Read and write Google Calendar events. Supports recurring events.",
        "status": "active",
        "version": "0.9.3",
        "packages": json.dumps([{"registry": "pypi", "name": "calendar-mcp", "version": "0.9.3"}])
    },
    {
        "id": "legacyTool",
        "name": "Old Legacy Tool",
        "description": "Deprecated tool, kept for backward compatibility.",
        "status": "inactive",
        "version": "0.1.0",
        "packages": json.dumps([])
    },
]

conn.executemany(
    "INSERT OR IGNORE INTO servers (id, name, description, status, version, packages) "
    "VALUES (:id, :name, :description, :status, :version, :packages)",
    servers
)
conn.commit()

count = conn.execute("SELECT COUNT(*) FROM servers").fetchone()[0]
print(f"Inserted {len(servers)} servers. Total in database: {count}")
conn.close()
```

**5. Run the seed.**

```powershell
python seed_data.py
```
✅ You should see:
```
Inserted 4 servers. Total in database: 4
```

---

**6. Create the file `query_db.py`.**

Query your database and see the results:
```powershell
notepad query_db.py
```
Paste:
```python
import sqlite3
import json

DB = "registry.db"
conn = sqlite3.connect(DB)

print("=== All Servers ===")
rows = conn.execute(
    "SELECT id, name, status, version FROM servers ORDER BY name"
).fetchall()
print(f"{'ID':<15} {'Name':<20} {'Status':<10} {'Version'}")
print("-" * 55)
for row in rows:
    print(f"{row[0]:<15} {row[1]:<20} {row[2]:<10} {row[3]}")

print("\n=== Active Servers Only ===")
rows = conn.execute(
    "SELECT id, name FROM servers WHERE status = 'active'"
).fetchall()
print(f"Found {len(rows)} active servers:")
for row in rows:
    print(f"  - {row[1]} ({row[0]})")

print("\n=== Full Detail: fileReader ===")
row = conn.execute(
    "SELECT * FROM servers WHERE id = ?", ("fileReader",)
).fetchone()
col_names = [d[0] for d in conn.execute("SELECT * FROM servers LIMIT 0").description]
for col, val in zip(col_names, row):
    if col == "packages":
        print(f"  {col}: {json.dumps(json.loads(val), indent=4)}")
    else:
        print(f"  {col}: {val}")

print("\n=== Migration History ===")
rows = conn.execute("SELECT id, name, applied_at FROM migrations").fetchall()
for row in rows:
    print(f"  Migration {row[0]}: {row[1]} (applied: {row[2]})")

conn.close()
```

**7. Run the queries.**

```powershell
python query_db.py
```
✅ You should see:
```
=== All Servers ===
ID              Name                 Status     Version
-------------------------------------------------------
calendarMcp     Calendar MCP         active     0.9.3
fileReader      FileReader MCP       active     1.2.0
legacyTool      Old Legacy Tool      inactive   0.1.0
webSearch       Web Search MCP       active     2.0.1

=== Active Servers Only ===
Found 3 active servers:
  - FileReader MCP (fileReader)
  - Web Search MCP (webSearch)
  - Calendar MCP (calendarMcp)

=== Full Detail: fileReader ===
  id: fileReader
  name: FileReader MCP
  description: Reads files from your local computer...
  packages: [{"registry": "npm", "name": "@tools/file-reader", "version": "1.2.0"}]

=== Migration History ===
  Migration 1: 001_initial_schema (applied: 2026-04-02 ...)
```

---

**8. Create and run migration 002.**

Add a `publisher` column after the fact — a real schema migration:
```powershell
notepad migration_002.py
```
Paste:
```python
import sqlite3

DB = "registry.db"
conn = sqlite3.connect(DB)

# Check if migration already ran
already_ran = conn.execute(
    "SELECT COUNT(*) FROM migrations WHERE id = 2"
).fetchone()[0]

if already_ran:
    print("Migration 002 already applied. Skipping.")
else:
    print("Running migration 002: add publisher column\n")
    conn.execute("ALTER TABLE servers ADD COLUMN publisher TEXT DEFAULT 'unknown'")
    print("  ✓ Added column: publisher")

    # Update existing records
    conn.execute("UPDATE servers SET publisher = 'Acme Tools' WHERE id = 'fileReader'")
    conn.execute("UPDATE servers SET publisher = 'SearchCo' WHERE id = 'webSearch'")
    print("  ✓ Updated existing records")

    conn.execute("INSERT INTO migrations (id, name) VALUES (2, '002_add_publisher')")
    print("  ✓ Migration 002 recorded\n")
    conn.commit()
    print("Migration 002 complete.")

# Confirm
rows = conn.execute("SELECT id, name, publisher FROM servers").fetchall()
print("\nServers with publisher field:")
for row in rows:
    print(f"  {row[0]}: {row[1]} — published by '{row[2]}'")

conn.close()
```

```powershell
python migration_002.py
```
✅ You should see:
```
Running migration 002: add publisher column

  ✓ Added column: publisher
  ✓ Updated existing records
  ✓ Migration 002 recorded

Migration 002 complete.

Servers with publisher field:
  fileReader: FileReader MCP — published by 'Acme Tools'
  webSearch: Web Search MCP — published by 'SearchCo'
  ...
```

Run it a second time to see idempotency in action:
```powershell
python migration_002.py
```
✅ You should see: `Migration 002 already applied. Skipping.` — the migration system prevents double-applying.

**What you just built:** A real SQLite database with the same schema as the MCP Registry's PostgreSQL database, two sequential migrations, indexes, seed data, and queries. You can open `registry.db` in any SQLite browser (DB Browser for SQLite is free) to explore it visually.

---

> **🌍 Real World**
> Instagram uses PostgreSQL as its primary database. In 2012, Instagram had 13 employees and 30 million users — all running on PostgreSQL. When Facebook acquired them, the database was one of their most valuable assets. The MCP Registry uses the exact same engine you just used: PostgreSQL with numbered migrations. Migration files are checked into source control, so every developer on the team runs the same migrations in the same order. When a new developer joins, they clone the repo and run `make migrate` — one command sets up their database identically to production.

---

## The Takeaway

A database is an organized, durable filing cabinet that can hold millions of records and find any of them instantly. Tables organize data into rows and columns. Indexes make searches fast. Migrations let you change the structure safely over time, without throwing away what already exists.

---

## The Connection

The data is stored safely. But not everyone should be allowed to read or write it. What if someone tries to publish a malicious MCP server? What if someone tries to delete someone else's entry? In Chapter 7, we install the security system — **authentication** — the mechanism that checks your ID before letting you through the door.

---

*→ Continue to [Chapter 7 — Authentication: The ID Card at the Door](./ch07-authentication.md)*
