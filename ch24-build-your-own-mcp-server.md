# Chapter 24 — Building Your Own MCP Server

*Part 5: AI and the Real World*

---

## The Analogy

You have learned to read music. You understand the clef, the time signature, the notes, the dynamics. But reading music is not the same as playing music.

This chapter is where you sit down at the piano.

Everything from Chapters 1–23 converges here. You have a Registry that can list your server. You have an AI agent that can connect to it. You have MCP — the protocol that ties them together. Now you build the server itself.

---

## The Concept

An MCP server is a program that:
1. Listens for connections from AI agents
2. Tells agents what tools it provides
3. Executes tools when agents call them
4. Returns results

That is the entire specification. The simplicity is intentional — it is a small surface area for a large idea.

---

## System Diagram

```
YOUR MCP SERVER: FILE STRUCTURE

plant-monitor-mcp/
├── server.py          ← handles protocol (initialize, list, call)
├── sensors.py         ← tool logic (what tools actually DO)
├── server.json        ← MCP Registry entry (for discovery)
└── requirements.txt   ← dependencies (mcp, asyncio)

REQUEST FLOW:
AI Agent
  → (stdio pipe) → server.py receives "tools/call get_soil_moisture"
                 → routes to sensors.py:get_moisture("basil")
                 → returns {"moisture": 42, "status": "healthy"}
  → (stdio pipe) → AI reads result, decides next action
```

---

## Building the Plant Monitor MCP Server (Step by Step)

We will build the plant monitor server from Chapter 23. No Raspberry Pi required for this exercise — we will simulate the sensor data. The structure will be exactly what you would use with real hardware.

### Step 1 — Choose Your Language and SDK

MCP has official SDKs for TypeScript (JavaScript/Node.js), Python, and others. For a plant monitor on a Raspberry Pi, Python is the natural choice — it has excellent hardware libraries and runs everywhere.

> *Now I choose Python because my Raspberry Pi runs Raspbian (a Linux variant) and Python is already installed. I also like that Python code reads almost like English, which makes it easier to come back to after a month.*

### Step 2 — Define Your Server Structure

Create a project structure:

```
plant-monitor-mcp/
├── server.py          ← Main server code
├── sensors.py         ← Hardware interface (or simulation)
├── server.json        ← MCP Registry entry (Chapter 9)
└── requirements.txt   ← Python dependencies
```

> *Now I add a `requirements.txt` because I want anyone who installs this to get exactly the same versions I used. Without it, "it works on my machine" returns — the very problem Docker (Chapter 18) also solves.*

### Step 3 — Define Your Tools

In the MCP Python SDK, defining tools looks like this:

```python
# server.py

from mcp.server import Server
from mcp.types import Tool, TextContent
import json

# Create the server
server = Server("plant-monitor-mcp")

# Tool 1: Get moisture for one plant
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_soil_moisture",
            description=(
                "Returns current soil moisture percentage for a specific plant. "
                "Use this when the user asks about a plant's water level or "
                "whether a plant needs watering."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "plant": {
                        "type": "string",
                        "description": "The name of the plant (e.g., 'basil', 'tomato')"
                    }
                },
                "required": ["plant"]
            }
        ),
        Tool(
            name="list_plants",
            description="Returns all registered plants and their current moisture status.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
```

Notice the description quality. "Returns soil moisture" is not enough. The description tells the AI *when* to use this tool — "when the user asks about a plant's water level or whether a plant needs watering." This is the key to good tool design: write descriptions for the AI, not for humans.

> *Now I write the descriptions and I realize I am writing instructions for a reader who will decide autonomously whether to use this tool. If my description is ambiguous, the AI will make the wrong call. I spend more time on descriptions than on the code itself.*

### Step 4 — Implement the Tool Logic

```python
# sensors.py — Simulated sensor data (replace with real GPIO in production)

PLANT_MOISTURE = {
    "basil": 42,
    "tomato": 67,
    "orchid": 28,
    "mint": 55
}

def get_moisture(plant_name: str) -> dict:
    plant = plant_name.lower()
    if plant not in PLANT_MOISTURE:
        return {"error": f"Plant '{plant}' not found. Known plants: {list(PLANT_MOISTURE.keys())}"}

    moisture = PLANT_MOISTURE[plant]
    if moisture < 30:
        status = "critical — needs water immediately"
    elif moisture < 50:
        status = "low — consider watering soon"
    elif moisture < 70:
        status = "healthy"
    else:
        status = "high — do not water"

    return {
        "plant": plant,
        "moisture_percent": moisture,
        "status": status
    }
```

> *Now I add the status interpretation directly in the sensor layer — not in the server layer, not in the tool layer. I want the data coming back from the sensor to already tell the AI what to think about it. If I just return "42%", the AI has to know what 42% means for plants. If I return "healthy", the AI can act immediately. Good data design saves reasoning steps.*

### Step 5 — Connect the Handler

```python
# Back in server.py — handle the actual tool call

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_soil_moisture":
        plant = arguments.get("plant", "")
        result = get_moisture(plant)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "list_plants":
        all_plants = [get_moisture(p) for p in PLANT_MOISTURE.keys()]
        return [TextContent(type="text", text=json.dumps(all_plants, indent=2))]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
```

### Step 6 — Start the Server

```python
# At the bottom of server.py

import asyncio
from mcp.server.stdio import stdio_server

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

> *Now I choose `stdio_server` because I want to launch this as a local process that an AI agent (like the one in Chapter 16) can start on demand. The agent runs `python server.py`, pipes messages through stdin/stdout, and gets responses back. No network port needed. No firewall rules. No separate service to keep running.*

### Step 7 — Write the server.json

Now register your server so the MCP Registry can list it (Chapter 10):

```json
{
  "$schema": "https://registry.modelcontextprotocol.io/schema/2025-12-11.json",
  "name": "io.github.yourname/plant-monitor-mcp",
  "description": "Monitor soil moisture for houseplants using a Raspberry Pi sensor array. Supports reading moisture levels and watering status for up to 8 plants.",
  "version": "0.1.0",
  "packages": [
    {
      "registry": "pypi",
      "name": "plant-monitor-mcp",
      "version": "0.1.0",
      "runtimeArguments": ["python", "-m", "plant_monitor_mcp.server"]
    }
  ]
}
```

---

## 🔬 Lab Activity — Build a Complete MCP Server

**What you'll build:** A fully working MCP server for a study timer (Pomodoro-style) using only Python stdlib — no external MCP SDK required. An AI agent connecting to it can start timers, check status, and get session history.

**Time:** ~25 minutes  
**You'll need:** Python 3.10+ · Two PowerShell windows

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch24-mcp-server
cd C:\labs\ch24-mcp-server
```

---

**2. Create the `sensors.py` (timer logic).**

```powershell
notepad sensors.py
```
Paste:
```python
import time

# Study timer state
_state = {
    "active": False,
    "start_time": None,
    "duration_minutes": 0,
    "sessions_completed": 0,
    "history": []
}

def start_timer(duration_minutes=25, label="Study session"):
    if _state["active"]:
        return {"error": "Timer already running. Stop it first."}
    _state["active"] = True
    _state["start_time"] = time.time()
    _state["duration_minutes"] = duration_minutes
    _state["label"] = label
    return {
        "started": True,
        "label": label,
        "duration_minutes": duration_minutes,
        "message": f"Timer started: {label} ({duration_minutes} min)"
    }

def stop_timer():
    if not _state["active"]:
        return {"error": "No timer is running."}
    elapsed = (time.time() - _state["start_time"]) / 60
    _state["active"] = False
    _state["sessions_completed"] += 1
    _state["history"].append({
        "label": _state.get("label", "Unknown"),
        "duration_planned": _state["duration_minutes"],
        "duration_actual": round(elapsed, 1)
    })
    return {
        "stopped": True,
        "elapsed_minutes": round(elapsed, 1),
        "sessions_completed": _state["sessions_completed"]
    }

def get_status():
    if not _state["active"]:
        return {
            "active": False,
            "sessions_completed": _state["sessions_completed"],
            "message": "No timer running."
        }
    elapsed = (time.time() - _state["start_time"]) / 60
    remaining = _state["duration_minutes"] - elapsed
    return {
        "active": True,
        "label": _state.get("label", "Unknown"),
        "elapsed_minutes": round(elapsed, 1),
        "remaining_minutes": round(max(0, remaining), 1),
        "complete": remaining <= 0
    }

def get_history():
    return {"sessions": _state["history"], "total": _state["sessions_completed"]}
```

---

**3. Create the MCP server: `server.py`.**

```powershell
notepad server.py
```
Paste:
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sensors

TOOLS = [
    {"name": "start_timer",
     "description": "Start a study timer (Pomodoro-style). Use when user wants to focus or start a work session. Default 25 minutes.",
     "inputSchema": {"type": "object", "properties": {
         "duration_minutes": {"type": "integer", "description": "Duration in minutes (default 25)"},
         "label": {"type": "string", "description": "What you're working on"}
     }}},
    {"name": "stop_timer",
     "description": "Stop the currently running timer. Use when user says they're done or wants to take a break.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "get_status",
     "description": "Check current timer status. Use when user asks how much time is left or if a timer is running.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "get_history",
     "description": "Get all completed study sessions. Use when user asks about their study history or progress today.",
     "inputSchema": {"type": "object", "properties": {}}},
]

HANDLERS = {
    "start_timer": lambda a: sensors.start_timer(**{k: v for k, v in a.items() if k in ["duration_minutes","label"]}),
    "stop_timer":  lambda a: sensors.stop_timer(),
    "get_status":  lambda a: sensors.get_status(),
    "get_history": lambda a: sensors.get_history(),
}

class McpHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        method = body.get("method", "")
        print(f"[MCP] ← {method}")

        if method == "initialize":
            self.send_json({
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "study-timer-mcp", "version": "0.1.0"}
            })
        elif method == "tools/list":
            self.send_json({"tools": TOOLS})
        elif method == "tools/call":
            params = body.get("params", {})
            name = params.get("name", "")
            args = params.get("arguments", {})
            if name in HANDLERS:
                result = HANDLERS[name](args)
                self.send_json({"content": [{"type": "text", "text": json.dumps(result, indent=2)}]})
            else:
                self.send_json({"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True})

print("Study Timer MCP Server at http://localhost:8772")
print("Tools: start_timer, stop_timer, get_status, get_history")
HTTPServer(("localhost", 8772), McpHandler).serve_forever()
```

---

**4. Create the `server.json`.**

```powershell
notepad server.json
```
Paste:
```json
{
  "name": "io.github.yourname/study-timer-mcp",
  "description": "Pomodoro-style study timer MCP server. Helps AI agents track focus sessions, check remaining time, and review study history.",
  "version": "0.1.0",
  "packages": [
    {
      "registry": "pypi",
      "name": "study-timer-mcp",
      "version": "0.1.0"
    }
  ]
}
```

---

**5. Start the server.**

```powershell
python server.py
```

---

**6. In a second window, run the client test.**

```powershell
notepad test_client.py
```
Paste:
```python
import urllib.request, json, time

def mcp(method, params=None):
    body = {"method": method}
    if params: body["params"] = params
    req = urllib.request.Request("http://localhost:8772",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req).read())

print("=== Study Timer MCP Test ===\n")
print("Tools:", [t["name"] for t in mcp("tools/list")["tools"]])

print("\nStarting 1-minute timer...")
r = mcp("tools/call", {"name": "start_timer", "arguments": {"duration_minutes": 1, "label": "Chapter reading"}})
print(r["content"][0]["text"])

print("\nChecking status...")
r = mcp("tools/call", {"name": "get_status", "arguments": {}})
print(r["content"][0]["text"])

print("\nWaiting 2 seconds...")
time.sleep(2)

print("Stopping timer...")
r = mcp("tools/call", {"name": "stop_timer", "arguments": {}})
print(r["content"][0]["text"])

print("\nHistory:")
r = mcp("tools/call", {"name": "get_history", "arguments": {}})
print(r["content"][0]["text"])
```

```powershell
python test_client.py
```
✅ You should see the complete MCP lifecycle including tool discovery, timer start, status check, stop, and history.

**What you just built:** A complete MCP server with 4 tools, a `server.json` for the Registry, and a working client — ready to be connected to Claude Code or any MCP-compatible AI agent.

---

> **🌍 Real World**
> The MCP Python SDK (pip install mcp) was released by Anthropic in late 2024. Within 3 months, over 500 MCP servers had been published on GitHub — weather servers, database servers, browser automation servers, email servers, calendar servers. The fastest-growing category is personal productivity: study timers, task managers, habit trackers — exactly what you just built. Zapier (which connects 6,000+ web apps) announced MCP support in 2025, making every Zapier integration instantly available as an MCP tool. A developer at Anthropic built a fully working MCP server for controlling a Philips Hue smart lighting system in 4 hours — the same structure you just learned.

---

## The Takeaway

Building an MCP server is simpler than it sounds. Define your tools (name, description, schema), implement the logic (what they actually do), handle the calls (route tool names to functions), and start the server. The MCP SDK handles the protocol. You handle the capability. The Registry handles discovery. The AI agent handles the thinking. Your job is just to build the hands.

---

## The Connection

You can now build tools for AI. You know how to deploy them (Part 4). You know how agents use them (Part 3). The final frontier: building it at home, literally. In Part 6, we design the home lab — your personal infrastructure, starting with a Raspberry Pi on a shelf.

---

*→ Continue to [Chapter 25 — The Home Lab: Your Personal Data Center](./ch25-home-lab.md)*
