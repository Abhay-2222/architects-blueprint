# Chapter 35 — Security & Threat Models: How Systems Get Attacked and Defended

*Part 8: Under the Hood*

---

## The Analogy

A medieval castle is not defended by one wall. It is defended by layers.

First, there is a **moat** — attackers cannot even reach the walls without crossing it. Then a **portcullis** — a heavy iron gate that drops instantly if the bridge is breached. Then **guards at every internal door** — even if you cross the moat and lift the portcullis, every room has a guard who checks your identity. Then a **dungeon ledger** — every person who enters or leaves is recorded, so if something goes wrong, you know exactly who was where.

If any one layer fails, the others still hold. This is called **defence in depth** — multiple independent layers of protection so that a breach of one is not a breach of all.

Software systems use exactly this principle. The MCP Registry has: TLS encryption (the moat), authentication tokens (the portcullis), middleware guards (internal doors), and audit logging (the dungeon ledger). If an attacker breaks through the TLS layer, authentication still stops them. If they steal an expired token, the validator still stops them.

Security is not one lock. It is a castle.

---

## The Concept

### The Attacker's Perspective

Before you can defend a system, you must understand how attackers think.

An attacker asks three questions:
1. **What can I send?** (Every API endpoint is a surface they can probe)
2. **What does the server trust?** (Any trusted input is a potential injection point)
3. **What is poorly guarded?** (Any assumption in the code is a potential vulnerability)

Good security means answering these questions before the attacker does, and closing every answer.

### The OWASP Top 10

OWASP (Open Web Application Security Project) maintains a list of the most common web vulnerabilities. Understanding these gives you a framework for thinking about any system's attack surface.

The five most important for backend systems like the MCP Registry:

**1. Injection (SQL Injection, Command Injection)**

An attacker puts executable code into an input field, and the server runs it.

Vulnerable code:
```python
# DANGEROUS: user input injected directly into SQL string
name = request.args.get("name")
query = "SELECT * FROM servers WHERE name = '" + name + "'"
db.execute(query)
```

If an attacker sends `name = ' OR 1=1 --`, the query becomes:
```sql
SELECT * FROM servers WHERE name = '' OR 1=1 --'
```
`1=1` is always true. The `--` comments out the rest. The attacker now sees **every record** in the database.

Worse: if `name = "'; DROP TABLE servers; --"`, the attacker **deletes your entire database**.

**2. Broken Authentication**

Weak passwords, long-lived tokens, no rate limiting on login attempts, tokens stored in browser localStorage (visible to JavaScript) — any of these allow attackers to steal or guess credentials.

The MCP Registry's defence: 5-minute JWT tokens, Ed25519 cryptographic signatures, and token permissions scoped to specific namespaces (Chapter 7). Even a stolen token is useless after 5 minutes and cannot be used to publish as someone else.

**3. Security Misconfiguration**

Default credentials left unchanged. Debug mode enabled in production. Verbose error messages that reveal internal file paths or stack traces. S3 buckets left publicly readable. These are not clever attacks — they are attackers using systems as they were accidentally left.

**4. Rate Limiting / Brute Force**

Without rate limiting, an attacker can try millions of passwords per second, or spam your API with 100,000 requests to scrape all data or cause a denial of service.

**5. Insufficient Logging and Monitoring**

If you don't log who did what, you cannot detect an attack in progress or investigate after a breach. Logging is not optional — it is the dungeon ledger.

### Defence in Depth: The Layers

```
                    INTERNET
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Layer 1: TLS (Ch 34)                        │
│  Encrypts all traffic. Attackers cannot      │
│  read or tamper with data in transit.        │
└──────────────────────┬───────────────────────┘
                       │ (passes through if TLS valid)
                       ▼
┌──────────────────────────────────────────────┐
│  Layer 2: Rate Limiter                       │
│  Blocks IPs sending > N requests/minute.     │
│  Stops brute force, scraping, DoS.           │
└──────────────────────┬───────────────────────┘
                       │ (passes through if under limit)
                       ▼
┌──────────────────────────────────────────────┐
│  Layer 3: Authentication (Ch 7)              │
│  Validates JWT token. Rejects expired,       │
│  forged, or missing tokens.                  │
└──────────────────────┬───────────────────────┘
                       │ (passes through if token valid)
                       ▼
┌──────────────────────────────────────────────┐
│  Layer 4: Input Validation (Ch 9)            │
│  Validates schema, types, formats.           │
│  Rejects malformed or dangerous inputs.      │
└──────────────────────┬───────────────────────┘
                       │ (passes through if input valid)
                       ▼
┌──────────────────────────────────────────────┐
│  Layer 5: Parameterised Queries              │
│  Database queries never concatenate strings. │
│  SQL injection is structurally impossible.   │
└──────────────────────┬───────────────────────┘
                       │ (passes through safely)
                       ▼
                    DATABASE
                       │
                       ▼
              AUDIT LOG (everything recorded)
```

An attacker must defeat **all five layers** simultaneously. In practice, they give up after layer 2 or 3.

### Parameterised Queries: The Fix for SQL Injection

The fix for SQL injection is to **never concatenate user input into SQL strings**. Instead, use parameterised queries — where the SQL and the data are kept strictly separate:

```python
# SAFE: user input is a separate parameter, never part of the SQL string
name = request.args.get("name")
query = "SELECT * FROM servers WHERE name = ?"
db.execute(query, (name,))
```

Even if `name` is `' OR 1=1 --`, the database treats it as a **literal string**, not SQL. It searches for a server whose name is literally `' OR 1=1 --` — finds nothing — and returns an empty result. No injection. No data breach. No dropped tables.

This is one of the most important rules in software security:

> **Never interpolate user-controlled input directly into a command string — whether SQL, shell, or otherwise.**

---

## The Real Code

The MCP Registry defends against injection through its validation layer and the Go database library. In `registry-main/internal/database/`, all queries use Go's `database/sql` package with parameterised queries:

```go
// Safe: the ? placeholder is a parameter, never SQL
row := db.QueryRow(
    "SELECT id, name, description FROM servers WHERE id = ?",
    serverID,  // ← never concatenated into the SQL string
)

// Also safe: named parameters in PostgreSQL style
rows, err := db.Query(
    "SELECT * FROM servers WHERE status = $1 AND created_at > $2",
    "active",
    since,
)
```

The Go `database/sql` driver sends the SQL and the parameters **as separate items** to PostgreSQL. PostgreSQL receives:
- SQL template: `SELECT * FROM servers WHERE id = ?`
- Parameter: `fileReader`

It never concatenates them into a single string. SQL injection is structurally impossible.

The Registry also uses `govulncheck` in its CI/CD pipeline (Chapter 20):

```yaml
# From .github/workflows/ci.yml
- name: Run govulncheck
  uses: golang/govulncheck-action@...
```

`govulncheck` scans the entire dependency tree against the Go vulnerability database. If any imported package has a known CVE (Common Vulnerabilities and Exposures), the CI pipeline fails and no deployment proceeds.

---

## 🔬 Lab Activity — SQL Injection: Attack and Defence

**What you'll build:** Two Python scripts. The first demonstrates SQL injection on a vulnerable database. The second fixes it with parameterised queries. Then you build a simple token bucket rate limiter.

**Time:** ~25 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell (no extra installs — uses Python stdlib only)

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch35-security
cd C:\labs\ch35-security
```

---

**2. Create the file `setup_db.py`.**

This creates a test database with fake user data:
```powershell
notepad setup_db.py
```
Paste:
```python
import sqlite3

conn = sqlite3.connect("vulnerable_app.db")

# Create a users table
conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id       INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email    TEXT NOT NULL,
        role     TEXT DEFAULT 'user'
    )
""")

# Insert test data
conn.executemany(
    "INSERT OR IGNORE INTO users (id, username, email, role) VALUES (?, ?, ?, ?)",
    [
        (1, "alice",  "alice@example.com",  "admin"),
        (2, "bob",    "bob@example.com",    "user"),
        (3, "charlie","charlie@example.com","user"),
    ]
)
conn.commit()
conn.close()
print("Test database created: vulnerable_app.db")
print("Users: alice (admin), bob (user), charlie (user)")
```

**3. Run the setup.**

```powershell
python setup_db.py
```
✅ You should see:
```
Test database created: vulnerable_app.db
Users: alice (admin), bob (user), charlie (user)
```

---

**4. Create the file `attack_demo.py`.**

This shows the SQL injection attack:
```powershell
notepad attack_demo.py
```
Paste:
```python
import sqlite3

conn = sqlite3.connect("vulnerable_app.db")

def vulnerable_login(username_input):
    """DANGEROUS: never do this in real code."""
    # Attacker controls username_input
    query = "SELECT * FROM users WHERE username = '" + username_input + "'"
    print(f"\n[QUERY] {query}")
    results = conn.execute(query).fetchall()
    return results

# --- Normal use ---
print("=== Normal login ===")
results = vulnerable_login("alice")
print(f"[RESULT] Found {len(results)} user(s): {[r[1] for r in results]}")

# --- Attack 1: Read all users ---
print("\n=== ATTACK 1: Read all users ===")
results = vulnerable_login("' OR 1=1 --")
print(f"[RESULT] Found {len(results)} user(s): {[r[1] for r in results]}")
print("[!] Attacker now has ALL usernames and emails")

# --- Attack 2: Target admin specifically ---
print("\n=== ATTACK 2: Find admin accounts ===")
results = vulnerable_login("' OR role='admin' --")
print(f"[RESULT] Found {len(results)} admin(s): {[(r[1], r[2]) for r in results]}")
print("[!] Attacker knows exactly which account is admin")

# --- Attack 3: Extract data via UNION ---
print("\n=== ATTACK 3: UNION injection (extract email + role) ===")
results = vulnerable_login("x' UNION SELECT id, email, role, role FROM users --")
print(f"[RESULT] Extracted {len(results)} rows:")
for row in results:
    print(f"         {row}")
print("[!] Attacker now has all emails and roles")

conn.close()
print("\n[SUMMARY] The vulnerable function leaked the entire database.")
print("[SUMMARY] None of these inputs should have returned any results.")
```

**5. Run the attack demo.**

```powershell
python attack_demo.py
```
✅ You should see:
```
=== Normal login ===
[QUERY] SELECT * FROM users WHERE username = 'alice'
[RESULT] Found 1 user(s): ['alice']

=== ATTACK 1: Read all users ===
[QUERY] SELECT * FROM users WHERE username = '' OR 1=1 --'
[RESULT] Found 3 user(s): ['alice', 'bob', 'charlie']
[!] Attacker now has ALL usernames and emails

=== ATTACK 2: Find admin accounts ===
[QUERY] SELECT * FROM users WHERE username = '' OR role='admin' --'
[RESULT] Found 1 admin(s): [('alice', 'alice@example.com')]
[!] Attacker knows exactly which account is admin

=== ATTACK 3: UNION injection (extract email + role) ===
[RESULT] Extracted 3 rows:
         (1, 'alice@example.com', 'admin', 'admin')
         ...
[!] Attacker now has all emails and roles

[SUMMARY] The vulnerable function leaked the entire database.
```

Look at those queries. The attacker broke out of the string with `'` and wrote their own SQL. The database had no way to tell user input from SQL commands.

---

**6. Create the file `safe_login.py`.**

This fixes it with parameterised queries:
```powershell
notepad safe_login.py
```
Paste:
```python
import sqlite3

conn = sqlite3.connect("vulnerable_app.db")

def safe_login(username_input):
    """SAFE: user input is always a parameter, never part of the SQL."""
    query = "SELECT * FROM users WHERE username = ?"  # ? is a placeholder
    print(f"\n[QUERY] {query}")
    print(f"[PARAM] {repr(username_input)}")
    # The driver sends SQL and parameter SEPARATELY to the database engine
    results = conn.execute(query, (username_input,)).fetchall()
    return results

# --- Normal use (still works) ---
print("=== Normal login ===")
results = safe_login("alice")
print(f"[RESULT] Found {len(results)} user(s): {[r[1] for r in results]}")

# --- Same attack strings — now they fail safely ---
print("\n=== ATTACK 1: OR injection (defeated) ===")
results = safe_login("' OR 1=1 --")
print(f"[RESULT] Found {len(results)} user(s): {[r[1] for r in results]}")
print("[OK] The attack string is treated as a literal username. No match found.")

print("\n=== ATTACK 2: Admin extraction (defeated) ===")
results = safe_login("' OR role='admin' --")
print(f"[RESULT] Found {len(results)} user(s)")
print("[OK] No results. The attack string is just a username that doesn't exist.")

print("\n=== ATTACK 3: UNION injection (defeated) ===")
results = safe_login("x' UNION SELECT id, email, role, role FROM users --")
print(f"[RESULT] Found {len(results)} user(s)")
print("[OK] No results. The entire injection string is treated as one username string.")

conn.close()
print("\n[SUMMARY] Parameterised queries defeat all three attacks.")
print("[SUMMARY] The fix was a single character: ? instead of string concatenation.")
```

**7. Run the safe version.**

```powershell
python safe_login.py
```
✅ You should see:
```
=== Normal login ===
[QUERY] SELECT * FROM users WHERE username = ?
[PARAM] 'alice'
[RESULT] Found 1 user(s): ['alice']

=== ATTACK 1: OR injection (defeated) ===
[RESULT] Found 0 user(s): []
[OK] The attack string is treated as a literal username. No match found.

=== ATTACK 2: Admin extraction (defeated) ===
[RESULT] Found 0 user(s)
[OK] No results.

=== ATTACK 3: UNION injection (defeated) ===
[RESULT] Found 0 user(s)
[OK] No results.

[SUMMARY] Parameterised queries defeat all three attacks.
[SUMMARY] The fix was a single character: ? instead of string concatenation.
```

The fix was exactly one character — `?` instead of `+ username +`. The attack strings are now harmless.

---

**8. Create the file `rate_limiter.py`.**

Rate limiting is the second line of defence. This implements a simple token bucket:
```powershell
notepad rate_limiter.py
```
Paste:
```python
import time
from collections import defaultdict

class TokenBucketRateLimiter:
    """
    Token bucket algorithm:
    - Each IP gets a bucket with MAX_TOKENS tokens.
    - Each request costs 1 token.
    - Tokens refill at REFILL_RATE per second (up to MAX_TOKENS).
    - If bucket is empty, request is rejected (429 Too Many Requests).
    """
    MAX_TOKENS = 10         # max requests in a burst
    REFILL_RATE = 2.0       # tokens added per second

    def __init__(self):
        self.buckets = defaultdict(lambda: {"tokens": self.MAX_TOKENS, "last_refill": time.time()})

    def _refill(self, ip):
        """Add tokens based on time elapsed since last refill."""
        now = time.time()
        bucket = self.buckets[ip]
        elapsed = now - bucket["last_refill"]
        new_tokens = elapsed * self.REFILL_RATE
        bucket["tokens"] = min(self.MAX_TOKENS, bucket["tokens"] + new_tokens)
        bucket["last_refill"] = now

    def allow(self, ip: str) -> bool:
        """Return True if request is allowed, False if rate limit exceeded."""
        self._refill(ip)
        bucket = self.buckets[ip]
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        return False


# --- Simulate requests ---
limiter = TokenBucketRateLimiter()

print("=== Simulating normal traffic (one request) ===")
result = limiter.allow("192.168.1.100")
print(f"IP 192.168.1.100 → {'ALLOWED ✓' if result else 'BLOCKED ✗'}")
print(f"Tokens remaining: {limiter.buckets['192.168.1.100']['tokens']:.1f}")

print("\n=== Simulating a burst of 15 requests from an attacker ===")
attacker_ip = "10.0.0.1"
for i in range(1, 16):
    allowed = limiter.allow(attacker_ip)
    status = "ALLOWED ✓" if allowed else "BLOCKED ✗ (429 Too Many Requests)"
    print(f"Request {i:2d}: {status}")

print("\n=== After 2 seconds, tokens refill ===")
print("Waiting 2 seconds...")
time.sleep(2)
result = limiter.allow(attacker_ip)
print(f"Request after wait → {'ALLOWED ✓' if result else 'BLOCKED ✗'}")
print(f"Tokens now: {limiter.buckets[attacker_ip]['tokens']:.1f}")

print("\n=== Two different IPs have independent buckets ===")
for ip in ["user_a", "user_b"]:
    for i in range(3):
        limiter.allow(ip)
print(f"user_a tokens: {limiter.buckets['user_a']['tokens']:.1f}")
print(f"user_b tokens: {limiter.buckets['user_b']['tokens']:.1f}")
print("user_a's usage does not affect user_b.")
```

**9. Run the rate limiter.**

```powershell
python rate_limiter.py
```
✅ You should see:
```
=== Simulating normal traffic (one request) ===
IP 192.168.1.100 → ALLOWED ✓
Tokens remaining: 9.0

=== Simulating a burst of 15 requests from an attacker ===
Request  1: ALLOWED ✓
Request  2: ALLOWED ✓
...
Request 10: ALLOWED ✓
Request 11: BLOCKED ✗ (429 Too Many Requests)
Request 12: BLOCKED ✗ (429 Too Many Requests)
...
Request 15: BLOCKED ✗ (429 Too Many Requests)

=== After 2 seconds, tokens refill ===
Waiting 2 seconds...
Request after wait → ALLOWED ✓
Tokens now: 4.0

=== Two different IPs have independent buckets ===
user_a tokens: 7.0
user_b tokens: 7.0
user_a's usage does not affect user_b.
```

The attacker is limited to 10 requests before being blocked. Normal users are unaffected.

---

**What you just built:** A working SQL injection attack and its defence (parameterised queries), plus a token bucket rate limiter. These are not toy examples — production systems like the MCP Registry use parameterised queries in every single database call, and rate limiters with the same token-bucket algorithm in every API endpoint.

---

> **🌍 Real World**
> The MCP Registry uses Go's `database/sql` package which makes parameterised queries the default — string concatenation requires extra effort, so developers rarely do it accidentally. Its CI pipeline runs `govulncheck` on every commit, checking all Go dependencies against the National Vulnerability Database. In 2021, a vulnerability in the `log4j` Java library (CVE-2021-44228) affected millions of systems worldwide — systems with automated vulnerability scanning detected it within hours; systems without it took weeks. The Registry's approach — validate early, scan automatically, parameterise everything — reflects lessons learned from high-profile breaches.

---

## The Takeaway

Security is a castle, not a lock. Defence in depth means that a breach of one layer (TLS, authentication, rate limiting, validation, parameterised queries) does not mean a breach of all. SQL injection — one of the most common vulnerabilities in existence — is completely prevented by a single habit: never concatenate user input into command strings. Use parameterised queries. Rate limiting stops brute force and denial-of-service attacks at the perimeter, before they reach your application logic.

---

## The Connection

You can now build secure systems and understand how attacks work. Chapter 36 takes a different kind of intelligence question: how do you communicate with AI effectively? Prompt engineering is the skill of writing instructions the AI can actually follow — and RAG is how you give AI access to knowledge it was never trained on.

---

*→ Continue to [Chapter 36 — Prompt Engineering & RAG](./ch36-prompt-engineering-and-rag.md)*
