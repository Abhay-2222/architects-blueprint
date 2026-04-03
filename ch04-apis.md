# Chapter 4 — APIs: The Front Door

*Part 1: What Is a System?*

---

## The Analogy

You want to order a pizza. You don't walk into the kitchen and start telling the chef what to do. You don't open the fridge yourself and grab ingredients. You call a phone number, or tap a button in an app.

That phone number — that single point of contact — is the **API**.

An API (Application Programming Interface) is the front door of a server. It is the only place where the outside world is allowed to knock. Everything behind the door — the database, the business logic, the internal systems — is hidden. You only ever interact with the front door.

The front door has specific rules:
- You must ring the bell in a specific way (send requests in the right format)
- The door opens only for certain requests (not everything is accessible to everyone)
- The door responds in a predictable way (the same request always gets the same type of response)

This is what makes APIs powerful: **predictability and control.** The server decides exactly what the outside world can ask for and exactly how it will respond.

---

## The Concept

An API is a defined set of **endpoints** — specific addresses you can send requests to — and the rules for those requests.

Think of endpoints like rooms in a building:
- Room `/servers` → "Show me all registered MCP servers"
- Room `/servers/fileReader` → "Show me details about the FileReader server"
- Room `/publish` → "I want to register a new server"

Each room has a door policy:
- Some rooms anyone can enter (public)
- Some rooms require ID (authenticated)
- Some rooms let you look but not touch (read-only)
- Some rooms let you leave things behind (write)

### HTTP Methods — The Four Types of Knocks

When you approach a door (endpoint), you knock in one of four ways:

| Method | What it means | Restaurant analogy |
|--------|--------------|-------------------|
| `GET` | "Show me something" | "What's on the menu?" |
| `POST` | "Create something new" | "I'd like to order a pizza" |
| `PUT` / `PATCH` | "Update something existing" | "Actually, make it extra large" |
| `DELETE` | "Remove something" | "Cancel my order" |

These four methods cover almost everything you would ever want to do with data.

---

## System Diagram

```
API = The front door. Only way in. You never see what's inside.

OUTSIDE THE DOOR (public)          INSIDE THE DOOR (hidden)
        │                                    │
        │   GET /servers                     │  Database queries
        │ ──────────────────────────────►    │  Business logic
        │                                    │  Other services
        │   200 OK { "servers": [...] }      │  Internal state
        │ ◄──────────────────────────────    │
        │                                    │
        │   POST /publish                    │  Validation
        │ ──────────────────────────────►    │  Auth check
        │   + JWT token + server.json body   │  DB write
        │                                    │
        │   201 Created / 400 Bad Request    │
        │ ◄──────────────────────────────    │

HTTP Method guide:
  GET    → Read something  (safe, repeatable)
  POST   → Create something new
  PUT    → Replace something entirely
  PATCH  → Update part of something
  DELETE → Remove something
```

---

## The Real Code

The MCP Registry's API is defined in `registry-main/internal/api/router/v0.go`. Let's look at what doors it opens to the world:

```go
// These are the endpoints — the rooms in the Registry's building
r.GET("/servers",           handlers.ListServers)      // See all servers
r.GET("/servers/:id",       handlers.GetServer)        // See one server
r.POST("/servers/publish",  handlers.PublishServer)    // Register a new server
r.GET("/healthz",           handlers.HealthCheck)      // "Are you alive?"
```

Each line is a door with:
- A method (`GET`, `POST`) — the type of knock
- A path (`/servers`, `/servers/:id`) — which room
- A handler (`handlers.ListServers`) — the person who answers the door

The `:id` in `/servers/:id` is a **variable** — like a hotel room number. `/servers/fileReader` and `/servers/googleMaps` both use the same door, but you get a different room depending on the ID you give.

### A Real API Request and Response

When an AI agent like claw-code wants to know what tools are available, it sends this request:

```
GET https://registry.modelcontextprotocol.io/v0/servers
```

The Registry responds with something like:

```json
{
  "servers": [
    {
      "id": "fileReader",
      "name": "FileReader MCP",
      "description": "Reads files from your local computer",
      "version": "1.2.0"
    },
    {
      "id": "webSearch",
      "name": "Web Search MCP",
      "description": "Searches the internet",
      "version": "2.0.1"
    }
  ],
  "total": 247
}
```

The agent reads this JSON, picks the tool it needs, and uses it. The entire conversation happened through the front door — the API — without the agent ever touching the Registry's internals.

---

## 🔬 Lab Activity — Call a Real API and Build a Mini One

**What you'll build:** First, call the live MCP Registry API using different HTTP methods and see real responses. Then build a tiny Python HTTP server with two API endpoints.

**Time:** ~25 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell · Two PowerShell windows

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch04-apis
cd C:\labs\ch04-apis
```

---

**2. Call the real API with different methods.**

```powershell
notepad explore_api.py
```
Paste:
```python
import urllib.request
import json

BASE = "https://registry.modelcontextprotocol.io/v0"

print("=== Exploring the MCP Registry API ===\n")

# GET /servers — list all servers
print("GET /servers?limit=3")
with urllib.request.urlopen(f"{BASE}/servers?limit=3") as r:
    data = json.loads(r.read())
    print(f"  Status: 200 OK")
    print(f"  Total servers in registry: {data['total']}")
    print(f"  First server: {data['servers'][0]['name']}\n")

# GET /servers/:id — get one specific server
first_id = data["servers"][0]["id"]
print(f"GET /servers/{first_id}")
with urllib.request.urlopen(f"{BASE}/servers/{first_id}") as r:
    server = json.loads(r.read())
    print(f"  Status: 200 OK")
    print(f"  Name:    {server.get('name')}")
    print(f"  ID:      {server.get('id')}")
    print()

# GET /servers/nonexistent — should return 404
print("GET /servers/this-does-not-exist-xyz")
try:
    urllib.request.urlopen(f"{BASE}/servers/this-does-not-exist-xyz")
except urllib.error.HTTPError as e:
    print(f"  Status: {e.code} {e.reason}")
    print(f"  This is the 'room doesn't exist' response.\n")

# Attempt POST /publish without auth — should return 401
print("POST /publish  (without JWT token)")
try:
    req = urllib.request.Request(
        f"{BASE.replace('/v0','')}/v0/publish",
        data=b'{}',
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(f"  Status: {e.code} {e.reason}")
    print(f"  The front door requires a JWT token. No token = no entry.\n")

print("Summary of HTTP status codes seen:")
print("  200 OK           — request succeeded")
print("  404 Not Found    — that endpoint/resource doesn't exist")
print("  401 Unauthorized — authentication required")
```

Run it:
```powershell
python explore_api.py
```
✅ You should see:
```
=== Exploring the MCP Registry API ===

GET /servers?limit=3
  Status: 200 OK
  Total servers in registry: 247
  First server: FileReader MCP

GET /servers/fileReader
  Status: 200 OK
  Name:    FileReader MCP
  ID:      fileReader

GET /servers/this-does-not-exist-xyz
  Status: 404 Not Found
  This is the 'room doesn't exist' response.

POST /publish  (without JWT token)
  Status: 401 Unauthorized
  The front door requires a JWT token. No token = no entry.
```

---

**3. Build your own mini API server.**

Create `mini_api.py`:
```powershell
notepad mini_api.py
```
Paste:
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

# In-memory "database"
LIGHTS = {
    "living_room": {"status": "off", "brightness": 0},
    "bedroom":     {"status": "off", "brightness": 0},
    "kitchen":     {"status": "on",  "brightness": 80},
}

class HomeAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress default logging

    def send_json(self, status, data):
        body = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/lights":
            print(f"[API] GET /lights → 200 OK")
            self.send_json(200, {"lights": LIGHTS})

        elif path.startswith("/lights/"):
            room = path.split("/")[2]
            if room in LIGHTS:
                print(f"[API] GET /lights/{room} → 200 OK")
                self.send_json(200, {room: LIGHTS[room]})
            else:
                print(f"[API] GET /lights/{room} → 404 Not Found")
                self.send_json(404, {"error": f"Room '{room}' not found"})

        elif path == "/temperature":
            print(f"[API] GET /temperature → 200 OK")
            self.send_json(200, {"celsius": 21.5, "status": "comfortable"})

        else:
            self.send_json(404, {"error": f"No endpoint at {path}"})

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        if path.startswith("/lights/") and path.endswith("/on"):
            room = path.split("/")[2]
            if room in LIGHTS:
                LIGHTS[room]["status"] = "on"
                LIGHTS[room]["brightness"] = 100
                print(f"[API] POST /lights/{room}/on → 200 OK")
                self.send_json(200, {"message": f"{room} light turned on", **LIGHTS[room]})
            else:
                self.send_json(404, {"error": f"Room '{room}' not found"})
        else:
            self.send_json(404, {"error": "Endpoint not found"})

print("Home API server running at http://localhost:8765")
print("Endpoints:")
print("  GET  /lights")
print("  GET  /lights/:room")
print("  GET  /temperature")
print("  POST /lights/:room/on")
print("\nPress Ctrl+C to stop.\n")
HTTPServer(("localhost", 8765), HomeAPIHandler).serve_forever()
```

**4. Start the server in one PowerShell window.**

```powershell
python mini_api.py
```
✅ You should see:
```
Home API server running at http://localhost:8765
```
Leave this window open.

---

**5. Open a second PowerShell window and call your API.**

```powershell
# List all lights
python -c "import urllib.request,json; print(json.dumps(json.loads(urllib.request.urlopen('http://localhost:8765/lights').read()), indent=2))"
```
✅ You should see:
```json
{
  "lights": {
    "living_room": { "status": "off", "brightness": 0 },
    ...
  }
}
```

```powershell
# Turn on the bedroom light
python -c "import urllib.request; r=urllib.request.Request('http://localhost:8765/lights/bedroom/on',data=b'',method='POST'); print(urllib.request.urlopen(r).read().decode())"
```
✅ You should see:
```json
{"message": "bedroom light turned on", "status": "on", "brightness": 100}
```

```powershell
# Check a room that doesn't exist
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8765/lights/garage')" 
```
✅ You should see a 404 error — the API enforces its contract.

In the first window, you'll see your API logging each request it received.

Stop the server with Ctrl+C in the first window.

**What you just built:** You called a real production API (MCP Registry) using GET, POST, and saw 200/404/401 responses. Then you built your own two-endpoint HTTP API server from scratch using Python's standard library — the same model as every production API in this book.

---

> **🌍 Real World**
> Stripe processes over $1 trillion in payments per year entirely through an API. Every payment your online store makes is a `POST /charges` request to Stripe's API. Every refund is a `POST /refunds`. Stripe's API has been so carefully designed that it has barely changed in 15 years — the same endpoints work today as they did in 2010. This stability is intentional: thousands of companies built products on Stripe's API contract, and breaking that contract would break all of them. Good API design is a promise you keep forever.

---

## The Takeaway

An API is the front door of a server — the only place the outside world can communicate with what's inside. It defines what can be asked, how to ask it, and what the answer will look like. Every app you use talks to one or more APIs constantly, without you knowing.

---

## The Connection

You now understand the skeleton of any software system. In Part 2, we stop looking at diagrams and start looking at a real building — the MCP Registry. We will walk through its actual rooms, examine its filing cabinets, and read the rules posted on its front door. Chapter 5 starts at the beginning: what is the Registry, and why does it exist?

---

*→ Continue to [Chapter 5 — What Is a Registry?](./ch05-what-is-a-registry.md)*
