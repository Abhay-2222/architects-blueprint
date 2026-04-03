# Chapter 26 — Smart Home Architecture

*Part 6: The Home Architect*

---

## The Analogy

A concert is not a collection of musicians playing simultaneously. It is a **system**. The conductor coordinates. The musicians follow scores — structured, timed instructions. The sound engineer controls the mix. The lighting technician responds to the music. The stage manager tracks entrances and exits.

Every person has a role. Every role connects to others. Remove the conductor and the musicians diverge. Remove the sound engineer and the acoustics fail. The concert is only beautiful because the system works.

A smart home is the same. It is not a collection of gadgets. It is a **system** — sensors that sense, a hub that coordinates, automations that respond, and (increasingly) an AI that understands.

When the system is designed well, it is invisible. The lights are always right. The temperature is always comfortable. The door locks when it should. It just works.

When it is designed poorly, it is a collection of apps that don't talk to each other.

---

## The Four Layers of Smart Home Architecture

---

## System Diagram

```
FOUR-LAYER SMART HOME ARCHITECTURE

Layer 4: AI LAYER (understanding)
  Claude / AI Agent
  ← connects via MCP to hub
  "Make the house ready for guests"
  → reads state, decides actions, executes

Layer 3: AUTOMATIONS (rules)
  Home Assistant automations:
  "If front_door.open AND time > 23:00 → notify phone"
  "If person.abhay = away → turn_off all lights"
  Runs locally — works without internet

Layer 2: HUB (coordinator)
  Home Assistant (Raspberry Pi)
  Maintains state of every device:
  light.living_room: on, 60%
  sensor.front_door: closed
  person.abhay: home
  climate.thermostat: 21°C

Layer 1: SENSORS & DEVICES (physical world)
  Motion sensors  → "motion in kitchen"
  Contact sensors → "front door opened"
  Temp sensors    → "bedroom: 19.5°C"
  Smart lights    ← "turn on, 40% brightness"
  Smart locks     ← "lock the door"
  Thermostats     ← "set to 22°C"
```

---

Every well-designed smart home has four layers, from bottom to top:

### Layer 1: Sensors (The Nervous System)

Sensors detect the physical world and translate it into data.

| Sensor type | What it detects | Data it produces |
|------------|----------------|-----------------|
| Motion sensor | Movement in a room | `{room: "living_room", motion: true, timestamp: ...}` |
| Contact sensor | Door/window open or closed | `{device: "front_door", state: "open"}` |
| Temperature/humidity | Temperature and moisture | `{temp: 21.5, humidity: 48, unit: "celsius"}` |
| Light level | How bright a room is | `{lux: 320}` |
| Power monitor | How much energy a device uses | `{device: "fridge", watts: 45.2}` |
| Soil moisture | Plant watering needs | `{plant: "basil", moisture: 42}` |

Sensors do not think. They only report. The intelligence is in the layers above.

> *Now I think about sensor placement strategically. I want motion in every room so the hub knows if anyone is home. I want contact sensors on the front and back door for security. I want temperature in the bedroom because that's where sleep quality matters most. I don't need sensors everywhere at once — I start with the highest-value locations and expand.*

### Layer 2: The Hub (The Brain)

The hub is the central coordinator. Every sensor reports to the hub. Every device is controlled by the hub. The hub speaks all the different languages (Zigbee, Z-Wave, Wi-Fi, Bluetooth, Matter) and translates them into a unified system.

**Home Assistant** (running on your Raspberry Pi from Chapter 25) is the leading open-source hub. It connects to 3,000+ device types and runs completely locally — your data never leaves your home.

The hub maintains the **state** of your entire home:
```yaml
# Home Assistant's state at a moment in time
light.living_room:     { state: "on", brightness: 180, color_temp: 3000K }
binary_sensor.front_door: { state: "closed" }
sensor.bedroom_temp:   { state: 19.5, unit: "°C" }
person.abhay:          { state: "home" }
climate.thermostat:    { state: "heat", target_temp: 21 }
```

This is the ground truth of your home — every device, every sensor, every person, every moment.

### Layer 3: Automations (The Rules Engine)

Automations are "if this, then that" rules that run when specific conditions are met.

```yaml
# Automation: Morning routine
trigger:
  - time: "07:00"
  - condition: person.abhay.state == "home"

actions:
  - turn_on: light.bedroom (brightness: 30%, color: warm)
  - wait: 5 minutes
  - set: climate.thermostat.target = 22°C
  - play: media.bedroom_speaker (playlist: "morning focus")
```

```yaml
# Automation: Security — door left open
trigger:
  - binary_sensor.front_door.state == "open"
  - for: 5 minutes

condition:
  - time_after: "23:00"

actions:
  - notify.phone: "Front door has been open for 5 minutes after 11pm"
```

Automations are the rules your home follows automatically. They run on the hub — locally, instantly, even if the internet is down.

### Layer 4: AI Layer (The Understanding)

Automations are powerful but rigid. "If motion in the kitchen at 7am, turn on the kitchen light" — but what if you're on holiday? What if it's a holiday? What if there's a guest?

The AI layer adds **understanding** — context-aware reasoning that rigid rules cannot provide.

With an AI agent connected to your home via MCP (Chapter 23):

```
You: "Make the house comfortable for movie night."

AI: (reads current state via MCP)
    - Checks: who is home, what time is it, what's currently playing
    - Decides: dim all lights except the TV area, set temperature to 21°C,
      close all blinds, enable "do not disturb" on all phones
    - Executes: 6 tool calls in sequence
    - Reports: "Movie night mode activated. Lights dimmed, temperature set to 21°C,
      blinds closed. Enjoy the film!"
```

The AI doesn't follow a rule someone wrote in advance. It reads the situation and responds appropriately.

---

## 🔬 Lab Activity — Build a Smart Home State Machine

**What you'll build:** A Python smart home simulator with a state store (mimicking Home Assistant's entity registry), 5 automations that fire on state changes, and an AI command interface that handles natural language actions — all without real hardware.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch26-smarthome
cd C:\labs\ch26-smarthome
```

---

**2. Create the file `smart_home.py`.**

```powershell
notepad smart_home.py
```
Paste:
```python
import time
import json

# ── LAYER 2: STATE STORE (the hub) ────────────────────────

state = {
    "light.living_room":      {"state": "off", "brightness": 0},
    "light.bedroom":          {"state": "off", "brightness": 0},
    "light.kitchen":          {"state": "off", "brightness": 0},
    "sensor.front_door":      {"state": "closed"},
    "sensor.bedroom_temp":    {"state": 20.0, "unit": "C"},
    "sensor.living_room_motion": {"state": "clear"},
    "person.abhay":           {"state": "home"},
    "climate.thermostat":     {"state": "idle", "target_temp": 21},
}

# ── LAYER 3: AUTOMATIONS (rules engine) ───────────────────

def run_automations(changed_entity, old_val, new_val):
    """Check all automation rules after a state change."""
    triggered = []

    # Automation 1: Away mode — lights off when person leaves
    if changed_entity == "person.abhay" and new_val["state"] == "away":
        for light in ["light.living_room", "light.bedroom", "light.kitchen"]:
            state[light] = {"state": "off", "brightness": 0}
        state["climate.thermostat"]["target_temp"] = 18
        triggered.append("Away mode: lights off, heat lowered to 18°C")

    # Automation 2: Welcome home — lights on when person arrives
    if changed_entity == "person.abhay" and new_val["state"] == "home":
        state["light.living_room"] = {"state": "on", "brightness": 70}
        state["climate.thermostat"]["target_temp"] = 21
        triggered.append("Welcome home: living room light on, heat to 21°C")

    # Automation 3: Security — front door opened after "night"
    if changed_entity == "sensor.front_door" and new_val["state"] == "open":
        hour = time.localtime().tm_hour
        if hour >= 22 or hour < 6:
            triggered.append("SECURITY ALERT: Front door opened after 10pm!")

    # Automation 4: Morning light — bedroom light on at 7am (simulated)
    # (In real life: triggered by time. Here: demonstrate concept)
    if changed_entity == "climate.thermostat" and new_val.get("target_temp", 0) >= 22:
        state["light.bedroom"]["state"] = "on"
        state["light.bedroom"]["brightness"] = 30
        triggered.append("Morning hint: bedroom light dimly on (warm temp requested)")

    return triggered

def set_state(entity, **kwargs):
    """Update an entity's state and run automations."""
    old = dict(state[entity])
    state[entity].update(kwargs)
    new = dict(state[entity])
    triggered = run_automations(entity, old, new)
    print(f"\n  [HUB] {entity}: {old} → {new}")
    for t in triggered:
        print(f"  [AUTO] {t}")

# ── LAYER 4: AI INTERFACE ──────────────────────────────────

def ai_command(command):
    """Simple AI command parser — maps natural language to state changes."""
    cmd = command.lower()
    print(f"\n[AI] Command: '{command}'")

    if "movie" in cmd or "film" in cmd:
        set_state("light.living_room", state="on", brightness=15)
        set_state("light.kitchen", state="off", brightness=0)
        set_state("climate.thermostat", target_temp=21)
        print("  [AI] Movie night mode activated.")

    elif "morning" in cmd or "wake" in cmd:
        set_state("light.bedroom", state="on", brightness=20)
        set_state("climate.thermostat", target_temp=22)
        print("  [AI] Morning mode activated.")

    elif "i'm leaving" in cmd or "away" in cmd:
        set_state("person.abhay", state="away")

    elif "i'm home" in cmd or "home" in cmd:
        set_state("person.abhay", state="home")

    elif "status" in cmd or "show" in cmd:
        print("  [AI] Current state:")
        for entity, val in state.items():
            print(f"    {entity}: {val}")

    else:
        print("  [AI] Unknown command. Try: 'movie night', 'morning', 'I'm leaving', 'status'")

# ── DEMO ───────────────────────────────────────────────────

print("=== Smart Home Simulator ===\n")
print("Initial state:")
for entity, val in state.items():
    print(f"  {entity}: {val}")

print("\n--- Simulating events ---")

ai_command("movie night")
ai_command("I'm leaving")
ai_command("I'm home")

# Simulate door opened late (manual state change)
print("\n--- Manual: front door opened ---")
set_state("sensor.front_door", state="open")

ai_command("show status")
```

**3. Run it.**

```powershell
python smart_home.py
```
✅ You should see automations fire on state changes:
```
=== Smart Home Simulator ===

--- Simulating events ---

[AI] Command: 'movie night'
  [HUB] light.living_room: {'state': 'off', ...} → {'state': 'on', 'brightness': 15}
  [HUB] climate.thermostat: {...} → {'target_temp': 21}
  [AI] Movie night mode activated.

[AI] Command: 'I'm leaving'
  [HUB] person.abhay: {'state': 'home'} → {'state': 'away'}
  [AUTO] Away mode: lights off, heat lowered to 18°C
...
```

**What you just built:** A 4-layer smart home simulator — state store, automation engine, and AI command interface — the same architecture used by Home Assistant with 3,000+ integrations and 500,000+ active installations.

---

> **🌍 Real World**
> Home Assistant has over 500,000 active installations worldwide and is the most popular open-source smart home platform. It runs on Raspberry Pi, old laptops, NAS devices — anything with Linux. The state store you simulated is real: Home Assistant's entity registry stores the live state of every device in a local SQLite database, updated in real time. Matter (formerly Project CHIP), backed by Apple, Google, Amazon, and Samsung, is the industry standard protocol that Layer 2 (the hub) speaks — ensuring any smart device can connect to any hub. When you connect an AI agent to Home Assistant via MCP, you get exactly the 4-layer system you built: sensor → hub → automation → AI.

---

## The Takeaway

A smart home is a four-layer system: sensors (detect), hub (coordinate), automations (rules), AI (understand). Each layer adds capability that the layer below it cannot provide alone. The result — when designed properly — is a home that understands your life and adapts to it, rather than one that requires constant manual control.

---

## The Connection

Your home is now a system. Chapter 27 zooms out further — how do you think about ANY system the same way? The architect's lens is not just for software or for homes. It is a way of seeing the world.

---

*→ Continue to [Chapter 27 — Thinking Like an Architect](./ch27-thinking-like-an-architect.md)*
