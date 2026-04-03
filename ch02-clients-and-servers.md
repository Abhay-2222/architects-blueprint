# Chapter 2 — Clients and Servers

*Part 1: What Is a System?*

---

## The Analogy

You walk into a restaurant and sit down. A waiter appears and hands you a menu.

You decide you want pasta. You tell the waiter. The waiter walks to the kitchen, gives the order to the chef, waits while the chef cooks, then brings the pasta back to your table.

Notice what just happened:
- **You** never went into the kitchen. You never saw the chef. You never touched the stove.
- **The waiter** acted as the go-between — receiving your request and delivering the result.
- **The kitchen** did all the real work: storing the ingredients, cooking the food, plating the dish.

This is *exactly* how the internet works, every single time.

- **You** = the **client** (the one who makes requests)
- **The waiter** = the **protocol / API** (the go-between)
- **The kitchen** = the **server** (the one who does the work and holds the data)

---

## The Concept

In any software system, there are always two roles:

**The Client** — asks for things. Your phone is a client. Your web browser is a client. The AI agent in claw-code is a client. Clients do not store the main data. They request it.

**The Server** — answers requests and holds the data. The MCP Registry is a server. YouTube's computers are servers. Your school's grading system runs on a server. Servers sit quietly, waiting for clients to ask them something.

This relationship is called the **client-server model** and it is the foundation of almost everything on the internet.

Here is a crucial insight:

> **The client and the server never have to be in the same room — or even the same country.**

Your phone (client) in your bedroom can talk to a server in a data center in another continent in less than a second. They communicate over the internet, using agreed-upon languages called **protocols** (which we will cover in Chapter 3).

### One Server, Many Clients

A server can talk to thousands of clients simultaneously. Right now, millions of people are watching YouTube videos. Every one of them has a client (their browser or app) sending requests to YouTube's servers. The servers handle all of these requests at once — like a restaurant kitchen with 50 chefs all cooking different orders in parallel.

### Clients Can Be Servers Too

Here is where it gets interesting. A piece of software can be a client *and* a server at the same time, depending on who it's talking to.

Look at the chain we drew in Chapter 1:

```
You (client)
    → claw-code AI agent
        → MCP Registry (server)
```

From *your* perspective, claw-code is the server (it responds to your requests). From *claw-code's* perspective, the MCP Registry is the server (claw-code sends requests to it). claw-code is both client and server depending on which direction you look.

This is not confusing — it is just a sign that real systems have many layers. Every layer is a client to the layer above it, and a server to the layer below it.

---

## System Diagram

```
                   CLIENT–SERVER MODEL

┌──────────────┐          request          ┌──────────────┐
│              │ ────────────────────────► │              │
│   CLIENT     │   GET /v0/servers         │    SERVER    │
│              │   Host: registry.mcp.io   │              │
│ (AI Agent /  │                           │ (MCP Registry│
│  Browser /   │ ◄──────────────────────── │  PostgreSQL  │
│  Your Code)  │   200 OK {"servers":[…]}  │  inside)     │
└──────────────┘          response         └──────────────┘

CLIENT rules:          SERVER rules:
- Initiates requests   - Waits silently
- Never stores data    - Only speaks when asked
- Can be a server too  - Handles many clients at once
  (to layers below)
```

---

## The Real Code

Let's look at the actual MCP Registry server — the "kitchen" — starting up.

In `registry-main/cmd/registry/main.go`, the server announces itself to the world:

```go
// This is the entry point — the moment the server "opens for business"
func main() {
    // Load configuration (like a restaurant reading its menu)
    cfg := config.Load()

    // Connect to the database (like the kitchen stocking its fridge)
    db := database.Connect(cfg.DatabaseURL)

    // Start listening for requests (like opening the front door)
    server := api.NewServer(cfg, db)
    server.Start(cfg.Port)
}
```

*(Simplified for clarity — the actual file has more detail, but this is the shape of it.)*

Each line is a step in "opening the restaurant":
1. Read the configuration (what port to listen on, what database to use)
2. Connect to the database (where all the MCP server records are stored)
3. Start accepting requests from clients

When this runs, the MCP Registry "opens its kitchen." Any client — including AI agents like claw-code — can now send it requests.

---

## 🔬 Lab Activity — Talk to a Real Server

**What you'll build:** A Python script that acts as a client and talks to the real MCP Registry server — making requests, reading responses, and exploring the client-server relationship live.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell · Internet connection

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch02-client-server
cd C:\labs\ch02-client-server
```

---

**2. Make your first client request.**

Run this one-liner to send a real HTTP request to the MCP Registry:
```powershell
python -c "import urllib.request, json; r=urllib.request.urlopen('https://registry.modelcontextprotocol.io/v0/servers?limit=3'); print(json.dumps(json.loads(r.read()), indent=2)[:600])"
```
✅ You should see the server's response — real JSON data:
```json
{
  "servers": [
    {
      "id": "fileReader",
      "name": "FileReader MCP",
      "description": "Reads files from your local computer",
      ...
    },
    ...
  ],
  "total": 247
}
```
You are the client. The registry is the server. It only responded because you sent a request.

---

**3. Create the file `client.py`.**

```powershell
notepad client.py
```
Paste:
```python
import urllib.request
import json

BASE_URL = "https://registry.modelcontextprotocol.io/v0"

def get_servers(limit=5):
    """Client request: Ask server for a list of MCP servers."""
    url = f"{BASE_URL}/servers?limit={limit}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())

def get_server(server_id):
    """Client request: Ask server for details about ONE specific server."""
    url = f"{BASE_URL}/servers/{server_id}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "message": str(e)}

def health_check():
    """Client request: Ask the server if it is alive."""
    url = f"{BASE_URL.replace('/v0','')}/healthz"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return f"Server is UP — HTTP {resp.status}"
    except Exception as e:
        return f"Server is DOWN — {e}"

# ---- Run the client conversation ----
print("=== Client-Server Conversation ===\n")

print("Client: Are you alive?")
print(f"Server: {health_check()}\n")

print("Client: Show me 3 MCP servers.")
data = get_servers(3)
print(f"Server: Here are {data['total']} total servers. First 3:")
for s in data.get("servers", []):
    print(f"        - {s.get('name', s.get('id'))}: {s.get('description','')[:50]}")
print()

# Get the first server ID from the list
first_id = data["servers"][0]["id"] if data.get("servers") else "fileReader"
print(f"Client: Tell me about '{first_id}'.")
detail = get_server(first_id)
if "error" not in detail:
    print(f"Server: Name:    {detail.get('name', 'N/A')}")
    print(f"        ID:      {detail.get('id', 'N/A')}")
    pkg = (detail.get("packages") or [{}])[0]
    print(f"        Install: {pkg.get('registry','?')} package '{pkg.get('name','?')}'")
else:
    print(f"Server: Error {detail['error']}")
print()

print("Client: [no more requests — client goes silent]")
print("Server: [waiting for next request — server never initiates]\n")

print("Key insight: The server sent 0 bytes until the client asked.")
print("Every response above was triggered by a client request, never by the server itself.")
```

**4. Run it.**

```powershell
python client.py
```
✅ You should see:
```
=== Client-Server Conversation ===

Client: Are you alive?
Server: Server is UP — HTTP 200

Client: Show me 3 MCP servers.
Server: Here are 247 total servers. First 3:
        - FileReader MCP: Reads files from your local computer
        - Web Search MCP: Searches the internet
        - ...

Client: Tell me about 'fileReader'.
Server: Name:    FileReader MCP
        ID:      fileReader
        Install: npm package '@filetools/file-reader'

Client: [no more requests — client goes silent]
Server: [waiting for next request — server never initiates]

Key insight: The server sent 0 bytes until the client asked.
```

---

**5. Test server unavailability.**

Now change the URL to a non-existent endpoint and see what happens:
```powershell
python -c "import urllib.request; urllib.request.urlopen('https://registry.modelcontextprotocol.io/v0/doesnotexist')"
```
✅ You should see an error like:
```
urllib.error.HTTPError: HTTP Error 404: Not Found
```
The server is still alive — but it said "404 Not Found" because that path doesn't exist. The server controlled what it shared.

**What you just built:** A Python client that had a real multi-turn conversation with a production server. Every line of server output above was triggered by a client request. The server was silent until asked — that is the fundamental rule of the client-server model.

---

> **🌍 Real World**
> YouTube serves over 500 hours of video uploaded per minute and over 1 billion hours watched per day. Every single play button click is a client request. YouTube's servers never push video to you uninvited — they wait. When you click play, your browser (client) sends `GET /watch?v=VIDEO_ID` to YouTube (server). The server responds with the video stream. The server itself initiates nothing. This reactive model — "only speak when spoken to" — is why the internet scales to billions of simultaneous users. Proactive servers would create infinite noise; reactive servers only work when asked.

---

## The Takeaway

Every interaction on the internet is a conversation between a client (the one who asks) and a server (the one who answers). The client never sees the server's kitchen — it only sees the waiter's responses. Once you recognize this pattern, you will see it in every piece of software you ever use.

---

## The Connection

Now you know *who* is talking. But how do they talk? Two people who don't share a language cannot communicate, no matter how close they are. Machines have the same problem. In Chapter 3, we learn about **protocols** — the agreed-upon languages that let machines understand each other.

---

*→ Continue to [Chapter 3 — Protocols: The Language of Machines](./ch03-protocols.md)*
