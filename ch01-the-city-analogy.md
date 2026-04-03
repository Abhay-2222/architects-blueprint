# Chapter 1 — The City Analogy

*Part 1: What Is a System?*

---

## The Analogy

Imagine you are standing at the top of a tall building, looking down at a city.

You can see roads. Cars move along them, carrying people and goods from one place to another. You can see buildings — offices, homes, factories, warehouses. Each one has a purpose. There are water pipes underground, invisible, quietly delivering water to every tap. There are electrical cables, a power grid, keeping every light on. There is a postal system — trucks collecting letters, sorting offices routing them, postmen delivering them.

Now here is the thing: **a software system is exactly like a city.**

Every piece of technology you have ever used — a website, an app, a game, a smart speaker — is a city. It has roads, buildings, water pipes, a power grid, and a postal system. The names are different, but the ideas are identical.

This is the most important thing you will read in this book:

> **Before you ever touch a computer, you already understand how systems work — because you live in one.**

---

## The Concept

A **system** is a collection of parts that work together toward a shared goal.

A city's goal is to let people live, work, and move efficiently. A software system's goal might be to let you send a message to a friend, or to let an AI agent find the right tool to complete a task.

Every system — no matter how complicated it looks — can be broken down into the same five ingredients:

| City Component | Software Equivalent | What It Does |
|---------------|---------------------|--------------|
| Roads | Networks (the internet) | Move information from A to B |
| Buildings | Servers | Store things and do work |
| Post offices / delivery services | APIs | Handle requests and send responses |
| Filing cabinets / warehouses | Databases | Remember things permanently |
| Power grid | Cloud infrastructure | Keep everything running |

Look at those two columns and burn them into your memory. Every single chapter in this book is about one of those five things.

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              THE FIVE COMPONENTS OF ANY SYSTEM              │
├──────────────┬──────────────────────┬───────────────────────┤
│  City        │  Software            │  Example              │
├──────────────┼──────────────────────┼───────────────────────┤
│  Roads       │  Network/Internet    │  Wi-Fi, fibre cable   │
│  Buildings   │  Servers             │  registry.mcp.io      │
│  Post Office │  API                 │  GET /v0/servers      │
│  Filing Cab. │  Database            │  PostgreSQL           │
│  Power Grid  │  Cloud Infra         │  GCP / AWS            │
└──────────────┴──────────────────────┴───────────────────────┘

You (browser/agent)
      │
      │  travels the ROAD (internet)
      ▼
   API (post office) ─── forwards request ──►  SERVER (building)
                                                      │
                                               queries DATABASE
                                               (filing cabinet)
```

---

## The Real Code: Two Cities, One Book

The two codebases in this book are two halves of the same city.

**The MCP Registry** (`registry-main/`) is the city hall and the marketplace. It is the building in the center of town where people register their businesses, file their paperwork, and look up who else is in town. In software terms, it is a backend server written in Go — a fast, efficient programming language — that runs in the cloud and serves thousands of requests.

**claw-code** (`claw-code-main/`) is the citizen — specifically, a very capable citizen who uses the city's services. It is an AI coding assistant: a program that can read files, write code, search the web, and talk to tools registered in the marketplace. It is written in Python (for the main logic) and Rust (for the fast, memory-safe core).

Here is how they connect, as a simple map:

```
You (the human)
    ↓
claw-code (the AI agent / citizen)
    ↓  asks the Registry: "what tools are available?"
MCP Registry (the city hall / marketplace)
    ↓  returns a list of registered tools (MCP servers)
claw-code picks a tool and uses it
    ↓
The tool does something in the real world
   (reads a file, controls a smart device, calls an API)
```

This chain — you → agent → registry → tool → real world — is the spine of everything we will study.

---

## 🔬 Lab Activity — Map a Real System

**What you'll build:** A text file documenting the five components of a real website, plus a live trace of where your data actually travels on the internet.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell · Internet connection

---

**1. Create the project folder.**

Open PowerShell and run:
```powershell
mkdir C:\labs\ch01-systems
cd C:\labs\ch01-systems
```
✅ No output expected — the folder is created.

---

**2. Trace a real network path.**

Run this command to see every router hop between your computer and YouTube:
```powershell
tracert -d -h 15 www.youtube.com
```
(`-d` skips reverse DNS to go faster, `-h 15` limits to 15 hops)

✅ You should see output like:
```
Tracing route to www.youtube.com [172.217.x.x]
over a maximum of 15 hops:

  1    <1 ms    <1 ms    <1 ms  192.168.1.1       ← Your router
  2     8 ms     7 ms     8 ms  10.x.x.x           ← ISP gateway
  3    12 ms    11 ms    12 ms  72.x.x.x           ← ISP backbone
  ...
  9    18 ms    18 ms    19 ms  172.217.x.x        ← YouTube (Google)

Trace complete.
```
Each line is a **road** (a router) your data travelled. Count the hops — that is the number of "intersections" between your bedroom and YouTube's server.

---

**3. Find the server's address.**

```powershell
nslookup www.youtube.com
```
✅ You should see:
```
Name:    www.youtube.com
Addresses: 172.217.x.x
           142.250.x.x
```
These are the IP addresses of YouTube's **servers** (buildings). Multiple addresses mean YouTube has servers in many locations — your request goes to the nearest one.

---

**4. Create the file `system-map.txt`.**

Open Notepad:
```powershell
notepad system-map.txt
```
Fill in this template for YouTube (or any product you use daily). Use the `tracert` and `nslookup` results you just collected:

```
SYSTEM MAP: YouTube
==================

ROADS (Network)
  Protocol: HTTPS (TCP/IP)
  My path: [paste your tracert hops count here] router hops
  Example: Data travels from 192.168.1.1 → 10.x.x.x → ... → 172.217.x.x

BUILDINGS (Servers)
  IP addresses found: [paste your nslookup results here]
  Purpose: Store videos, user accounts, watch history
  Location: Google data centers worldwide

POST OFFICE (API)
  Example endpoint: GET /watch?v=VIDEO_ID
  Purpose: Receives your "play this video" request, returns the video stream

FILING CABINET (Database)
  Stores: Your watch history, subscriptions, likes, comments
  Type: Google's internal databases (Bigtable, Spanner)

POWER GRID (Cloud Infrastructure)
  Provider: Google Cloud Platform
  Purpose: Keeps all servers running 24/7

FAILURE ANALYSIS:
  If ROADS fail (internet down): You see "No connection"
  If BUILDINGS fail (server crash): You see "503 Service Unavailable"
  If FILING CABINET fails (DB down): Your history and subscriptions disappear
  If POST OFFICE fails (API down): Requests never reach the servers
```

Save the file.

---

**5. Verify your file was saved.**

```powershell
type system-map.txt
```
✅ You should see the content you typed printed to the terminal.

---

**6. Create the file `five_components.py`.**

This script queries the real MCP Registry and identifies all five components in action:
```powershell
notepad five_components.py
```
Paste:
```python
import urllib.request
import json
import socket

URL = "https://registry.modelcontextprotocol.io/v0/servers?limit=1"

print("=== Five Components of the MCP Registry ===\n")

# ROAD: DNS + Network
hostname = "registry.modelcontextprotocol.io"
ip = socket.gethostbyname(hostname)
print(f"ROAD (Network):     {hostname} → {ip}")
print(f"                    Data travels via HTTPS (TCP/IP) to reach this IP\n")

# POST OFFICE + BUILDING: API Request
req = urllib.request.Request(URL, headers={"Accept": "application/json"})
with urllib.request.urlopen(req, timeout=10) as resp:
    status = resp.status
    data = json.loads(resp.read())

print(f"POST OFFICE (API):  GET /v0/servers  →  HTTP {status} OK")
print(f"BUILDING (Server):  Response received from {ip}\n")

# FILING CABINET: Data returned from database
total = data.get("total", 0)
server = data.get("servers", [{}])[0]
print(f"FILING CABINET (DB): {total} servers stored in PostgreSQL")
print(f"                     First record: '{server.get('name', 'N/A')}'")
print(f"                     ID: {server.get('id', 'N/A')}\n")

print("POWER GRID (Cloud):  Server is running on GCP (Google Cloud Platform)")
print("                     Kept online 24/7 by Kubernetes (Chapter 19)\n")
print("All five components working. Every request you make goes through all of them.")
```

**7. Run it.**

```powershell
python five_components.py
```
✅ You should see:
```
=== Five Components of the MCP Registry ===

ROAD (Network):     registry.modelcontextprotocol.io → 104.21.47.33
                    Data travels via HTTPS (TCP/IP) to reach this IP

POST OFFICE (API):  GET /v0/servers  →  HTTP 200 OK
BUILDING (Server):  Response received from 104.21.47.33

FILING CABINET (DB): 247 servers stored in PostgreSQL
                     First record: 'FileReader MCP'
                     ID: fileReader

POWER GRID (Cloud):  Server is running on GCP (Google Cloud Platform)
                     Kept online 24/7 by Kubernetes (Chapter 19)

All five components working. Every request you make goes through all of them.
```

**What you just built:** A real network trace showing your data's physical path, and a Python script that identifies all five system components by talking to a live production API.

---

> **🌍 Real World**
> WhatsApp handles over 100 billion messages per day using exactly these five components. The "roads" are undersea fibre-optic cables spanning continents. The "buildings" are data centers in multiple countries. The "post office" is WhatsApp's API layer handling billions of requests. The "filing cabinet" is their distributed database storing message history. The "power grid" is Meta's private cloud infrastructure. The architecture you just mapped for YouTube or WhatsApp is the same architecture behind every app on your phone.

---

## The Takeaway

Every software system is a city. Roads move data. Buildings store and process it. Post offices handle requests. Filing cabinets remember things. And you already understood all of this before you opened this book — because you live in a city every day.

---

## The Connection

Now that you see software as a city, the next question is: *who are the citizens?* In Chapter 2, we meet the two most important characters in any system — the **client** (the one who asks) and the **server** (the one who answers). They are everywhere, and once you see them, you cannot unsee them.

---

*→ Continue to [Chapter 2 — Clients and Servers](./ch02-clients-and-servers.md)*
