# Chapter 16 — MCP Client: The Agent Calls the Registry

*Part 3: The AI Agent — How an AI Coding Assistant Actually Works*

---

## The Analogy

You are a skilled contractor — a builder who can do many things. You have your own toolkit: a hammer, a saw, a level. But sometimes a job requires a specialized tool you don't carry. A laser distance measurer. An industrial tile cutter. A concrete drill.

You could buy every tool yourself. Or you could rent from the tool library in town.

The tool library has a catalog. You look up what you need, rent it, bring it to the job site, use it, and return it when you're done. The catalog keeps growing as new tools are added by other contractors.

**The MCP Registry is the tool library.** **The AI agent is the contractor.** **The MCP client is the contractor's way of talking to the library — calling ahead, ordering the tool, and picking it up.**

---

## The Concept

The **MCP client** is the part of the agent runtime that:
1. **Connects** to MCP servers (the tools registered in the Registry)
2. **Discovers** what tools those servers provide
3. **Calls** those tools when the agent needs them
4. **Returns** results back to the agent loop

The key insight: MCP servers are separate programs. They are not built into the agent. They run independently — maybe on your computer, maybe in the cloud, maybe on a Raspberry Pi in your living room. The MCP client is the bridge.

---

## System Diagram

```
MCP CLIENT CONNECTING MULTIPLE SERVERS

┌─────────────────────────────────────────────────┐
│  AI AGENT (claw-code)                           │
│                                                 │
│  Built-in tools:                                │
│    read_file, write_file, bash, glob_search     │
│                                                 │
│  MCP Client                                     │
│  ┌───────────────────────────────────────────┐  │
│  │ calendar_mcp → stdio → node calendar.js  │  │
│  │   Tools: calendar_mcp__get_events        │  │
│  │           calendar_mcp__create_event     │  │
│  │                                          │  │
│  │ weather_mcp → http → 192.168.1.50:4000  │  │
│  │   Tools: weather_mcp__get_forecast       │  │
│  │           weather_mcp__get_current       │  │
│  │                                          │  │
│  │ registry  → sse → registry.mcp.io/sse   │  │
│  │   Tools: registry__search_servers       │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  Total available tools: 4 built-in + 5 MCP     │
└─────────────────────────────────────────────────┘
```

---

### How an MCP Server is Launched

When the agent starts up, it reads a configuration file listing which MCP servers to connect to. For each server, it launches or connects to it using one of several **transport methods**:

| Transport | What it means | Like... |
|-----------|--------------|---------|
| `stdio` | Launches a local program and talks through its input/output | Talking face-to-face |
| `sse` | Connects to a remote server via Server-Sent Events | Listening to a live radio broadcast |
| `http` | Connects via standard HTTP requests | Sending letters |
| `websocket` | A persistent two-way connection | A phone call that stays connected |

---

## The Real Code

From `claw-code-main/rust/crates/runtime/src/mcp_client.rs`:

```rust
// The four ways an agent can connect to an MCP server
pub enum McpClientTransport {
    Stdio(McpStdioTransport),         // Launch a local program
    Sse(McpRemoteTransport),          // Connect to a remote URL via SSE
    Http(McpRemoteTransport),         // Connect via HTTP
    WebSocket(McpRemoteTransport),    // Connect via WebSocket
}

// For local programs (stdio transport):
pub struct McpStdioTransport {
    pub command: String,       // The program to run (e.g., "node", "python")
    pub args: Vec<String>,     // Arguments (e.g., ["@abhay/calendar-mcp"])
    pub env: BTreeMap<String, String>, // Environment variables (API keys, etc.)
}

// For remote servers (SSE, HTTP, WebSocket):
pub struct McpRemoteTransport {
    pub url: String,           // Where the server lives
    pub headers: BTreeMap<String, String>, // Headers (auth tokens, etc.)
    pub auth: McpClientAuth,   // How to authenticate
}
```

And the bootstrap structure — what the client knows about each MCP server before connecting:

```rust
pub struct McpClientBootstrap {
    pub server_name: String,       // Human name ("calendar-mcp")
    pub normalized_name: String,   // Machine-safe name ("calendar_mcp")
    pub tool_prefix: String,       // Prefix for all tools from this server
    pub transport: McpClientTransport, // How to connect
}
```

The **tool prefix** is important. If you connect to both a `calendar-mcp` and a `weather-mcp`, they might both have a tool named `get_events`. The prefix makes them unique: `calendar_mcp__get_events` vs `weather_mcp__get_events`. The agent always knows which server it is talking to.

### The Connection Sequence

1. Agent starts → reads config → finds MCP server entries
2. For each entry → creates a `McpClientBootstrap`
3. Connects using the specified transport (launches the process or opens a connection)
4. **Handshake**: "What tools do you provide?" → Server returns a list of tool specs
5. Agent adds those tools to its toolbox alongside its built-in tools
6. When the agent calls `calendar_mcp__get_events`, the MCP client routes the call to the calendar server and returns the result

This is how an agent that ships with 6 built-in tools can work with hundreds of tools — by connecting to external MCP servers at runtime.

---

## 🔬 Lab Activity — Build an MCP Client Simulator

**What you'll build:** A Python MCP client simulator that connects to two "servers" (simulated locally), discovers their tools, routes tool calls, and handles connection failures — mirroring `claw-code-main/rust/crates/runtime/src/mcp_client.rs`.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch16-mcp-client
cd C:\labs\ch16-mcp-client
```

---

**2. Create the file `mcp_client.py`.**

```powershell
notepad mcp_client.py
```
Paste:
```python
import json

# ── SIMULATED MCP SERVERS ──────────────────────────────────
# In real life, each server is a separate running process.
# Here we simulate them as Python classes.

class CalendarServer:
    def list_tools(self):
        return [
            {"name": "get_events", "description": "Get calendar events for a date range",
             "params": {"start": "string", "end": "string"}},
            {"name": "create_event", "description": "Create a new calendar event",
             "params": {"title": "string", "date": "string", "time": "string"}},
        ]

    def call(self, tool_name, **kwargs):
        if tool_name == "get_events":
            return {"events": [
                {"title": "Team standup", "date": kwargs.get("start"), "time": "09:00"},
                {"title": "Lunch with Priya", "date": kwargs.get("start"), "time": "12:30"},
            ]}
        elif tool_name == "create_event":
            return {"created": True, "event": kwargs}
        return {"error": "unknown tool"}

class WeatherServer:
    def list_tools(self):
        return [
            {"name": "get_current", "description": "Get current weather for a city",
             "params": {"city": "string"}},
            {"name": "get_forecast", "description": "Get 3-day forecast for a city",
             "params": {"city": "string"}},
        ]

    def call(self, tool_name, **kwargs):
        city = kwargs.get("city", "unknown")
        if tool_name == "get_current":
            return {"city": city, "temp_c": 22, "condition": "Partly cloudy"}
        elif tool_name == "get_forecast":
            return {"city": city, "days": [
                {"day": "Today",    "high": 22, "low": 15},
                {"day": "Tomorrow", "high": 19, "low": 13},
                {"day": "Day 3",    "high": 24, "low": 16},
            ]}
        return {"error": "unknown tool"}

# ── MCP CLIENT ─────────────────────────────────────────────

class McpClient:
    def __init__(self):
        self.connections = {}   # server_name → server instance
        self.tool_registry = {} # prefixed_tool_name → (server_name, tool_name)

    def connect(self, server_name, server_instance):
        """Connect to an MCP server and discover its tools."""
        print(f"[MCP] Connecting to '{server_name}'...")
        try:
            tools = server_instance.list_tools()
            self.connections[server_name] = server_instance
            for tool in tools:
                prefixed = f"{server_name}__{tool['name']}"
                self.tool_registry[prefixed] = (server_name, tool['name'])
                print(f"  ✓ Registered: {prefixed}")
        except Exception as e:
            print(f"  ✗ Connection failed: {e}")

    def connect_failed(self, server_name):
        """Simulate a failed connection (server offline)."""
        print(f"[MCP] Connecting to '{server_name}'...")
        print(f"  ✗ Connection refused: server may be offline")

    def call_tool(self, prefixed_name, **kwargs):
        """Call a tool via the MCP client."""
        if prefixed_name not in self.tool_registry:
            return {"error": f"Unknown tool: '{prefixed_name}'"}

        server_name, tool_name = self.tool_registry[prefixed_name]
        server = self.connections.get(server_name)
        if not server:
            return {"error": f"Server '{server_name}' not connected"}

        print(f"[MCP] Routing: {prefixed_name} → {server_name}.{tool_name}({kwargs})")
        result = server.call(tool_name, **kwargs)
        return result

    def list_all_tools(self):
        """List all tools from all connected servers."""
        return list(self.tool_registry.keys())


# ── DEMO ───────────────────────────────────────────────────

print("=== MCP Client Demo ===\n")
client = McpClient()

# Connect to two MCP servers
client.connect("calendar", CalendarServer())
client.connect("weather", WeatherServer())
client.connect_failed("plant_monitor")  # simulate offline server

print(f"\nAll available MCP tools: {len(client.list_all_tools())}")
for t in client.list_all_tools():
    print(f"  {t}")

# Call tools via the MCP client
print("\n--- Agent calls: calendar__get_events ---")
result = client.call_tool("calendar__get_events", start="2026-04-02", end="2026-04-02")
print(json.dumps(result, indent=2))

print("\n--- Agent calls: weather__get_current ---")
result = client.call_tool("weather__get_current", city="London")
print(json.dumps(result, indent=2))

print("\n--- Agent calls: plant_monitor__get_moisture (server offline) ---")
result = client.call_tool("plant_monitor__get_moisture", plant="basil")
print(json.dumps(result, indent=2))

print("\n--- Agent calls: unknown__tool ---")
result = client.call_tool("unknown__tool")
print(json.dumps(result, indent=2))
```

**3. Run it.**

```powershell
python mcp_client.py
```
✅ You should see:
```
=== MCP Client Demo ===

[MCP] Connecting to 'calendar'...
  ✓ Registered: calendar__get_events
  ✓ Registered: calendar__create_event
[MCP] Connecting to 'weather'...
  ✓ Registered: weather__get_current
  ✓ Registered: weather__get_forecast
[MCP] Connecting to 'plant_monitor'...
  ✗ Connection refused: server may be offline

All available MCP tools: 4
  calendar__get_events
  calendar__create_event
  weather__get_current
  weather__get_forecast

--- Agent calls: calendar__get_events ---
[MCP] Routing: calendar__get_events → calendar.get_events(...)
{"events": [{"title": "Team standup", ...}, ...]}

--- Agent calls: plant_monitor__get_moisture (server offline) ---
{"error": "Unknown tool: 'plant_monitor__get_moisture'"}
```

**What you just built:** A working MCP client that connects to multiple servers, discovers tools with prefixed names, routes calls to the right server, and handles failures — matching the `McpClientBootstrap` and `McpClientTransport` structures from `claw-code-main/rust/crates/runtime/src/mcp_client.rs`.

---

> **🌍 Real World**
> Claude Code uses this exact MCP client architecture. When you add an MCP server to your Claude Code config (in `.claude/settings.json`), the MCP client connects on startup, discovers tools, and prefixes them. A tool called `search` from a server called `brave` becomes `brave__search` in Claude's toolbox. The stdio transport you learned about is how Claude Code runs local MCP servers like `@anthropic/mcp-server-filesystem` — it literally launches the Node.js process and communicates via stdin/stdout. The same pattern is used by Cursor, Continue, and Windsurf — all AI coding tools use MCP clients to connect to external tool servers.

---

## The Takeaway

The MCP client is the agent's connection to the outside world of tools. It supports multiple transport methods — local programs, remote HTTP, SSE streams, WebSockets — and handles the entire lifecycle of connecting, discovering tools, routing calls, and returning results. It is what turns the MCP Registry from a catalog into a functioning tool ecosystem.

---

## The Connection

The agent can discover and use any tool in the Registry. But some tasks are so common — or so complex — that you don't want the agent to figure them out from scratch every time. In Chapter 17, we meet **skills**: pre-packaged, named workflows that the agent can invoke with a single command.

---

*→ Continue to [Chapter 17 — Skills: Pre-Packaged Superpowers](./ch17-skills.md)*
