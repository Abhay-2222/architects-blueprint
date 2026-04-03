# Chapter 8 — Routing: The Postal Sorting Office

*Part 2: The MCP Registry — A Real Backend, Explained*

---

## The Analogy

Every day, a postal sorting office receives thousands of letters and packages. They arrive in a big unsorted pile. Workers read the addresses and send each piece to the right destination — this one goes to Floor 3, this one to the East Wing, this one to Building B.

No single worker handles all the mail. The system is organized so that the right specialist handles each piece — the billing department gets billing letters, the legal team gets legal notices, the customer service team gets complaints.

An HTTP server works exactly the same way. When a request arrives, the **router** reads its "address" (the URL and HTTP method) and sends it to the right handler. The handler is the specialist — the function that knows exactly how to respond to that specific type of request.

---

## The Concept

**Routing** is the process of matching an incoming request to the correct handler function.

A router is a table of rules:
- "If the request is `GET /servers`, send it to the `ListServers` function"
- "If the request is `GET /servers/:id`, send it to the `GetServer` function"
- "If the request is `POST /publish`, send it to the `PublishServer` function"
- "If nothing matches, send it to the `NotFound` function"

The router reads two things:
1. **The HTTP method** (GET, POST, PUT, DELETE — from Chapter 4)
2. **The URL path** (the address: `/servers`, `/servers/fileReader`, etc.)

Together, these two things uniquely identify what the client wants.

### Parameters: The Variable Part of the Address

Some routes have **parameters** — variable parts of the URL that carry data:

```
GET /servers/fileReader   ← "fileReader" is the parameter
GET /servers/webSearch    ← "webSearch" is the parameter
GET /servers/googleMaps   ← "googleMaps" is the parameter
```

All three use the same route: `GET /servers/:id`. The `:id` is a placeholder that the router fills in with whatever appears in that position. The handler then uses that value to look up the right record in the database.

Think of it like hotel room numbers. The rule is "go to the front desk" (the route) — but which room you're asking about is the parameter.

---

## The Real Code

The MCP Registry's routing is defined in `registry-main/internal/api/router/v0.go`. Here is the actual structure (lightly annotated):

```go
func SetupV0Routes(r *gin.RouterGroup, handlers *v0.Handlers) {
    // Public routes — no authentication required (anyone can read the catalog)
    r.GET("/servers",        handlers.ListServers)   // List all servers
    r.GET("/servers/:id",    handlers.GetServer)     // Get one server by ID

    // Health check — for monitoring systems to verify the server is alive
    r.GET("/healthz",        handlers.HealthCheck)

    // Protected routes — require a valid JWT token
    authenticated := r.Group("/", middleware.RequireAuth(jwtManager))
    {
        authenticated.POST("/publish", handlers.PublishServer)  // Register a new tool
    }
}
```

Notice the organization:
- Public routes are wide open — anyone can discover what tools exist
- The `/publish` route is inside an `authenticated` group — only verified users can register tools

This separation is deliberate. Reading the catalog is a public service. Writing to it requires accountability.

### The Middleware Layer

Between the router and the handler, there is a **middleware** layer. Think of middleware as a security checkpoint between the post office lobby and the back rooms.

For the authenticated routes, the `RequireAuth` middleware runs before the handler:

```go
// RequireAuth middleware (simplified)
func RequireAuth(jwtManager *auth.JWTManager) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 1. Read the Authorization header
        token := c.GetHeader("Authorization")

        // 2. Validate the JWT token
        claims, err := jwtManager.ValidateToken(c, token)
        if err != nil {
            c.AbortWithStatus(401) // "You are not who you claim to be"
            return
        }

        // 3. Attach the claims to the request for the handler to use
        c.Set("claims", claims)

        // 4. Pass the request through to the actual handler
        c.Next()
    }
}
```

The middleware is a gatekeeper. It runs before the handler, checks the token, and either:
- Stops the request (if the token is invalid) → returns 401 Unauthorized
- Lets it through (if the token is valid) → calls `c.Next()` to continue

---

## 🔬 Lab Activity — Build a Router with Middleware

**What you'll build:** A Python HTTP server with a routing table, URL parameters, and auth middleware — the same pattern as the MCP Registry's router.

**Time:** ~25 minutes  
**You'll need:** Python 3.10+ · Two PowerShell windows

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch08-routing
cd C:\labs\ch08-routing
```

---

**2. Create the file `router_server.py`.**

```powershell
notepad router_server.py
```
Paste:
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
import urllib.parse

# In-memory data
SERVERS = {
    "fileReader": {"name": "FileReader MCP", "version": "1.2.0", "status": "active"},
    "webSearch":  {"name": "Web Search MCP", "version": "2.0.1", "status": "active"},
    "calendar":   {"name": "Calendar MCP",   "version": "0.9.3", "status": "inactive"},
}
VALID_TOKEN = "secret-jwt-token-123"

class RouterHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # we do custom logging below

    def send_json(self, status, data):
        body = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    # ── MIDDLEWARE ──────────────────────────────────────────────
    def check_auth(self) -> bool:
        """Returns True if request has a valid token."""
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
            return token == VALID_TOKEN
        return False

    # ── ROUTER ──────────────────────────────────────────────────
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Route: GET /healthz
        if path == "/healthz":
            print(f"[ROUTER] GET /healthz → HealthCheck")
            self.send_json(200, {"status": "ok"})

        # Route: GET /v0/servers
        elif path == "/v0/servers":
            print(f"[ROUTER] GET /v0/servers → ListServers")
            self.send_json(200, {
                "servers": list(SERVERS.values()),
                "total": len(SERVERS)
            })

        # Route: GET /v0/servers/:id  (URL parameter)
        elif match := re.match(r"^/v0/servers/([^/]+)$", path):
            server_id = match.group(1)
            print(f"[ROUTER] GET /v0/servers/{server_id} → GetServer (id='{server_id}')")
            if server_id in SERVERS:
                self.send_json(200, {"id": server_id, **SERVERS[server_id]})
            else:
                self.send_json(404, {"error": f"Server '{server_id}' not found"})

        # No match → 404
        else:
            print(f"[ROUTER] GET {path} → ??? → 404 Not Found")
            self.send_json(404, {"error": f"No endpoint at {path}"})

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        # Route: POST /v0/publish  (PROTECTED — requires auth)
        if path == "/v0/publish":
            print(f"[ROUTER] POST /v0/publish → [middleware: check auth]")

            # ← MIDDLEWARE runs here before the handler
            if not self.check_auth():
                print(f"[MIDDLEWARE] No valid token → 401 Unauthorized")
                self.send_json(401, {"error": "Unauthorized — provide Bearer token"})
                return

            print(f"[MIDDLEWARE] Token valid → PublishServer handler")
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            name = body.get("name", "unknown")
            self.send_json(201, {"message": f"Published '{name}' successfully"})
        else:
            self.send_json(404, {"error": f"No endpoint at {path}"})

print("Registry router running at http://localhost:8766")
print("Routes:")
print("  GET  /healthz")
print("  GET  /v0/servers")
print("  GET  /v0/servers/:id")
print("  POST /v0/publish  (requires: Authorization: Bearer secret-jwt-token-123)")
print("\nPress Ctrl+C to stop.\n")
HTTPServer(("localhost", 8766), RouterHandler).serve_forever()
```

**3. Start the server in one PowerShell window.**

```powershell
python router_server.py
```
✅ You should see:
```
Registry router running at http://localhost:8766
Routes:
  GET  /healthz
  ...
```

---

**4. Open a second PowerShell window and test the routes.**

```powershell
# Health check
python -c "import urllib.request,json; print(urllib.request.urlopen('http://localhost:8766/healthz').read().decode())"
```
✅ Server window shows: `[ROUTER] GET /healthz → HealthCheck`  
✅ You see: `{"status": "ok"}`

```powershell
# List all servers
python -c "import urllib.request,json; print(json.loads(urllib.request.urlopen('http://localhost:8766/v0/servers').read())['total'], 'servers')"
```
✅ You see: `3 servers`

```powershell
# Get specific server by ID (URL parameter)
python -c "import urllib.request,json; print(json.dumps(json.loads(urllib.request.urlopen('http://localhost:8766/v0/servers/webSearch').read()), indent=2))"
```
✅ You see the webSearch server detail.

```powershell
# Try a server ID that doesn't exist
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8766/v0/servers/doesnotexist')"
```
✅ You see: `urllib.error.HTTPError: HTTP Error 404` — router correctly returned 404.

```powershell
# POST /publish WITHOUT a token
python -c "
import urllib.request, json
req = urllib.request.Request('http://localhost:8766/v0/publish', data=b'{}', method='POST', headers={'Content-Type':'application/json'})
try: urllib.request.urlopen(req)
except urllib.error.HTTPError as e: print('Status:', e.code, e.reason)
"
```
✅ You see: `Status: 401 Unauthorized` — middleware blocked it.

```powershell
# POST /publish WITH a valid token
python -c "
import urllib.request, json
body = json.dumps({'name': 'io.github.me/my-tool', 'version': '1.0.0'}).encode()
req = urllib.request.Request('http://localhost:8766/v0/publish', data=body, method='POST', headers={'Content-Type':'application/json', 'Authorization':'Bearer secret-jwt-token-123'})
print(urllib.request.urlopen(req).read().decode())
"
```
✅ You see: `{"message": "Published 'io.github.me/my-tool' successfully"}` — middleware passed, handler ran.

Stop the server with Ctrl+C in the first window.

**What you just built:** A working HTTP router with URL parameters (`:id`), public routes, protected routes, and auth middleware — the same architecture as `registry-main/internal/api/router/v0.go`.

---

> **🌍 Real World**
> Express.js (Node.js), Django (Python), Gin (Go), and Rails (Ruby) are the most popular web frameworks in the world. All of them are, at their core, routers with middleware. When Netflix's API receives a request, a router instantly matches it to the right handler — in microseconds — across tens of thousands of possible routes. The middleware chain runs before every protected route: auth check, rate limit check, request logging, and abuse detection — all before the handler sees a single byte of the request body.

---

## The Takeaway

The router is the postal sorting office of every web server. It reads the address on every incoming request (method + path) and delivers it to the right handler. Middleware sits between the router and the handler, performing checks — like authentication — before the real work begins.

---

## The Connection

The request has arrived at the right handler. Now something needs to happen — usually involving the data the user sent. But before we trust that data, we check it. Chapter 9 introduces **validation** — the building inspector who refuses to approve anything that doesn't meet the code.

---

*→ Continue to [Chapter 9 — Validation: The Building Inspector](./ch09-validation.md)*
