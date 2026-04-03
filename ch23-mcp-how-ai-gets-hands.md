# Chapter 23 — MCP: How AI Gets Hands

*Part 5: AI and the Real World*

---

## The Analogy

A brilliant doctor is locked in a room with only a telephone. They can hear symptoms over the phone, analyze them, form diagnoses, and give advice. They are as skilled as any doctor in the world. But they cannot examine the patient. They cannot run a blood test. They cannot prescribe — only advise.

Now give that doctor a robot assistant in the patient's room. The robot can take temperature, draw blood, check reflexes, and administer treatments. The doctor tells the robot what to do, the robot does it, the robot reports back.

The doctor still does the thinking. But now they have **hands**.

**MCP (Model Context Protocol) is the protocol that gives an AI doctor a robot assistant.**

---

## The Concept

**MCP (Model Context Protocol)** is an open standard that defines how AI agents communicate with external tools and services. It solves a fundamental problem:

Before MCP, every AI tool integration was custom. If you wanted your AI to read your calendar, you had to write custom code. If you then wanted it to also check the weather, more custom code. If you switched AI providers, you had to rewrite everything. The ecosystem was fragmented and unmaintainable.

MCP is the USB-C of AI tools.

Before USB-C: every device had a different connector. Proprietary chargers, proprietary cables, constant incompatibility. After USB-C: one standard, works with everything.

MCP does the same for AI tools:
- One protocol, any AI agent can use it
- One format, any tool can implement it
- Once a tool is MCP-compatible, any MCP-aware AI agent can use it

---

## System Diagram

```
MCP FULL PROTOCOL LIFECYCLE

AI Agent                    MCP Server
────────                    ──────────
1. connect()    ──────────► (accept connection)

2. initialize   ──────────► 
   {version,               {version, capabilities,
    capabilities}  ◄─────── serverInfo}

3. tools/list   ──────────►
                           {tools: [
                             {name: "get_events",
               ◄─────────    description: "...",
                              inputSchema: {...}}
                           ]}

4. tools/call   ──────────►
   {name: "get_events",    (executes function)
    arguments:             {content: [
      {date: "2026-04-02"}} ◄───────  {type: "text",
                              text: "Team standup..."}
                           ]}

5. close()      ──────────► (cleanup)
```

---

## How MCP Works (The Full Picture)

```
Human ──→ AI Agent ──→ MCP Client ──→ MCP Server ──→ Real World
                         (Ch 16)        (your tool)    (calendar,
                                                        files, devices)
```

**The AI Agent** (Chapter 11) understands your goal. It decides which tools to use.

**The MCP Client** (Chapter 16) speaks the MCP protocol. It connects to MCP servers.

**The MCP Server** is a program you write (or use someone else's). It exposes tools via MCP. It could control a file system, talk to an API, read a sensor, manage a database — anything.

**The Real World** is what the MCP server connects to. Files on disk. Your Google Calendar. The temperature sensor in your living room. The inventory system at a warehouse.

### The Three Primitives of MCP

MCP defines three things that a server can expose to an AI agent:

**1. Tools** — Functions the AI can call.
```
Tool: get_events(date: string) → returns calendar events for that date
Tool: create_event(title, date, time) → creates a new event
Tool: delete_event(event_id) → removes an event
```

**2. Resources** — Data the AI can read.
```
Resource: /calendar/today → today's agenda as text
Resource: /contacts/alice → Alice's contact information
```

**3. Prompts** — Pre-written instructions the AI can use.
```
Prompt: "summarize-week" → a template for summarizing the week's events
```

Tools are actions. Resources are data. Prompts are instructions. Together, they give the AI a complete interface to whatever the server controls.

---

## The MCP Lifecycle

When an AI agent connects to an MCP server, a specific sequence happens:

**1. Connect** — The agent opens a connection to the server (via stdio, HTTP, SSE, or WebSocket — Chapter 16).

**2. Initialize** — The agent says: "Hello, I am Claude v3.7, I support MCP version 1.0." The server responds: "Hello, I support MCP version 1.0."

**3. Discover** — The agent asks: "What tools do you have?" The server responds with a list of tool definitions (name, description, input schema).

**4. Use** — When the agent wants to use a tool: "Call `get_events` with `{date: '2026-04-01'}`." The server executes the function and responds: `[{"title": "Team meeting", "time": "10:00 AM"}, ...]`

**5. Disconnect** — When the agent is done, it closes the connection.

This protocol is designed to be simple. A competent developer can implement a basic MCP server in an afternoon.

---

## 🔬 Lab Activity — Implement the MCP Protocol

**What you'll build:** A Python MCP server that implements the full protocol lifecycle (connect → initialize → tools/list → tools/call → close) over HTTP, and a client that connects and calls tools — demonstrating exactly how Claude connects to any MCP server.

**Time:** ~25 minutes  
**You'll need:** Python 3.10+ · Two PowerShell windows

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch23-mcp
cd C:\labs\ch23-mcp
```

---

**2. Create the MCP server: `mcp_server.py`.**

```powershell
notepad mcp_server.py
```
Paste:
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# ── TOOL IMPLEMENTATIONS ──────────────────────────────────

PLANTS = {
    "basil":    {"moisture": 28, "status": "needs watering"},
    "tomato":   {"moisture": 52, "status": "healthy"},
    "orchid":   {"moisture": 75, "status": "overwatered"},
}

def tool_list_plants():
    return [{"name": n, **v} for n, v in PLANTS.items()]

def tool_get_soil_moisture(plant):
    if plant in PLANTS:
        return {"plant": plant, "moisture": PLANTS[plant]["moisture"], "unit": "percent"}
    return {"error": f"Plant '{plant}' not found"}

def tool_water_plant(plant, duration_seconds=10):
    if plant in PLANTS:
        PLANTS[plant]["moisture"] = min(100, PLANTS[plant]["moisture"] + 15)
        PLANTS[plant]["status"] = "watered"
        return {"success": True, "message": f"Watered {plant} for {duration_seconds}s"}
    return {"error": f"Plant '{plant}' not found"}

TOOL_HANDLERS = {
    "list_plants": lambda args: tool_list_plants(),
    "get_soil_moisture": lambda args: tool_get_soil_moisture(**args),
    "water_plant": lambda args: tool_water_plant(**args),
}

TOOL_DEFINITIONS = [
    {"name": "list_plants",
     "description": "Returns all registered plants and their current moisture and status.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "get_soil_moisture",
     "description": "Returns current soil moisture percentage for a specific plant.",
     "inputSchema": {"type": "object", "properties": {"plant": {"type": "string"}}, "required": ["plant"]}},
    {"name": "water_plant",
     "description": "Activates watering for a plant. Use only when moisture < 30%.",
     "inputSchema": {"type": "object", "properties": {
         "plant": {"type": "string"},
         "duration_seconds": {"type": "integer"}
     }, "required": ["plant"]}},
]

# ── MCP HTTP HANDLER ──────────────────────────────────────

class McpHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_POST(self):
        body = self.read_body()
        method = body.get("method", "")
        print(f"[MCP] ← {method}")

        if method == "initialize":
            self.send_json(200, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "plant-monitor-mcp", "version": "0.1.0"}
            })

        elif method == "tools/list":
            self.send_json(200, {"tools": TOOL_DEFINITIONS})

        elif method == "tools/call":
            params = body.get("params", {})
            tool_name = params.get("name", "")
            arguments  = params.get("arguments", {})
            if tool_name in TOOL_HANDLERS:
                result = TOOL_HANDLERS[tool_name](arguments)
                self.send_json(200, {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                })
            else:
                self.send_json(200, {
                    "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                    "isError": True
                })
        else:
            self.send_json(400, {"error": f"Unknown method: {method}"})

print("Plant Monitor MCP Server at http://localhost:8771")
print("Implements: initialize, tools/list, tools/call")
HTTPServer(("localhost", 8771), McpHandler).serve_forever()
```

**3. Start the server.**

```powershell
python mcp_server.py
```

---

**4. In a second window, create and run the MCP client.**

```powershell
cd C:\labs\ch23-mcp
notepad mcp_client.py
```
Paste:
```python
import urllib.request
import json

BASE = "http://localhost:8771"

def mcp_call(method, params=None):
    body = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params:
        body["params"] = params
    req = urllib.request.Request(
        BASE, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST"
    )
    response = urllib.request.urlopen(req)
    return json.loads(response.read())

print("=== MCP Client Demo ===\n")

# Step 1: Initialize
print("[1] Initializing connection...")
result = mcp_call("initialize", {"protocolVersion": "2024-11-05",
                                  "clientInfo": {"name": "demo-agent", "version": "1.0"}})
info = result.get("serverInfo", {})
print(f"  Server: {info.get('name')} v{info.get('version')}")
print(f"  Protocol: {result.get('protocolVersion')}\n")

# Step 2: List tools
print("[2] Discovering tools...")
result = mcp_call("tools/list")
tools = result.get("tools", [])
print(f"  {len(tools)} tools available:")
for tool in tools:
    print(f"    - {tool['name']}: {tool['description'][:60]}")

# Step 3: Call tools
print("\n[3] Calling list_plants...")
result = mcp_call("tools/call", {"name": "list_plants", "arguments": {}})
plants = json.loads(result["content"][0]["text"])
print(f"  Plants: {json.dumps(plants, indent=4)}")

print("\n[4] Calling get_soil_moisture for basil...")
result = mcp_call("tools/call", {"name": "get_soil_moisture", "arguments": {"plant": "basil"}})
print(f"  {result['content'][0]['text']}")

print("\n[5] Watering basil (moisture was 28% — needs water)...")
result = mcp_call("tools/call", {"name": "water_plant",
                                   "arguments": {"plant": "basil", "duration_seconds": 15}})
print(f"  {result['content'][0]['text']}")

print("\n[6] Checking basil moisture after watering...")
result = mcp_call("tools/call", {"name": "get_soil_moisture", "arguments": {"plant": "basil"}})
print(f"  {result['content'][0]['text']}")
```

```powershell
python mcp_client.py
```
✅ You should see the full MCP lifecycle:
```
=== MCP Client Demo ===

[1] Initializing connection...
  Server: plant-monitor-mcp v0.1.0
  Protocol: 2024-11-05

[2] Discovering tools...
  3 tools available:
    - list_plants: Returns all registered plants...
    - get_soil_moisture: Returns current soil moisture...
    - water_plant: Activates watering for a plant...

[3] Calling list_plants...
  Plants: [{"name": "basil", "moisture": 28, ...}, ...]

[4] Calling get_soil_moisture for basil...
  {"plant": "basil", "moisture": 28, "unit": "percent"}

[5] Watering basil...
  {"success": true, "message": "Watered basil for 15s"}

[6] Checking basil moisture after watering...
  {"plant": "basil", "moisture": 43, "unit": "percent"}
```

Stop the server with Ctrl+C.

**What you just built:** A working MCP server implementing `initialize`, `tools/list`, and `tools/call` — and a client that runs the full MCP protocol lifecycle. This is exactly what Claude does when it connects to any MCP server.

---

> **🌍 Real World**
> MCP was created by Anthropic and open-sourced in November 2024. Within 6 months, over 1,000 MCP servers had been published to various registries. Microsoft integrated MCP into VS Code's GitHub Copilot in early 2025. Google added MCP support to Gemini. The protocol is now supported by nearly every major AI assistant. When you use Claude to read a PDF, browse the web, or control your computer, it's using MCP servers. The `initialize` handshake you implemented is exactly what happens when Claude Code starts up — it connects to all configured MCP servers, discovers their tools, and adds them to its toolbox.

---

## The Takeaway

MCP is the USB-C of AI tools — a single open standard that lets any AI agent talk to any compatible tool. It defines three primitives (tools, resources, prompts) and a simple connection lifecycle. Once implemented, an MCP server makes your capability available to any AI agent in the world. The MCP Registry (Part 2 of this book) is the directory that makes those servers discoverable.

---

## The Connection

You understand MCP conceptually. Now let's build something real. In Chapter 24, we walk through creating your own MCP server from scratch — not just designing it, but understanding every decision that goes into making it work.

---

*→ Continue to [Chapter 24 — Building Your Own MCP Server](./ch24-build-your-own-mcp-server.md)*
