# Appendix C — What to Learn Next

*You finished the book. Now what?*

---

## The Learning Map

This book gave you the map. Now you need to travel.

Each section below is a road you can take. You don't need to take all of them. Pick the one that connects to where you want to go.

---

## If you want to build backends and APIs

**Learn: Go**
The MCP Registry is written in Go. Go is fast, simple, and built for servers. It compiles to a single binary — no runtime required, no dependency headaches.

Start with: *A Tour of Go* — the official interactive tutorial at go.dev/tour

**Then:** Build a REST API. Use the Gin framework (same one the Registry uses). Connect it to PostgreSQL. Write a migration. Deploy it in Docker.

**Go deeper:** Read the MCP Registry's code. Start at `cmd/registry/main.go`. Follow every function call. You now know enough to understand all of it.

---

## If you want to build AI agents and tools

**Learn: Python**
Python is the dominant language for AI. The MCP SDK, Anthropic's API client, and most AI libraries are Python-first.

Start with: *Automate the Boring Stuff with Python* by Al Sweigart (free at automatetheboringstuff.com)

**Then:** Build your first MCP server (Chapter 24 shows the structure). Connect it to a local AI model using Ollama.

**Go deeper:** Study the Anthropic API documentation. Build an agent from scratch — not using a framework, but implementing the loop yourself (Chapter 11).

---

## If you want to build fast, safe systems

**Learn: Rust**
The claw-code project has a Rust implementation. Rust is the language of the future for systems that need to be both fast and safe. It has no garbage collector and no runtime crashes from null pointers.

Start with: *The Rust Book* — the official, free textbook at doc.rust-lang.org/book

**Then:** Read the `claw-code` Rust source. Start at `rust/crates/runtime/src/conversation.rs`. You already understand the loop — now you see it in Rust.

---

## If you want to run infrastructure and DevOps

**Learn: Docker + Kubernetes + Terraform**

Start with Docker (Chapter 18 is your foundation). Then:
1. Learn to write a `Dockerfile` and `docker-compose.yml`
2. Deploy a multi-service app using Docker Compose
3. Move to Kubernetes: `kubectl`, deployments, services, ingress
4. Learn Terraform for infrastructure-as-code (describing infrastructure in files, the same way the Registry uses Pulumi)

**Certification path:** Cloud Native Computing Foundation (CNCF) offers the CKA (Certified Kubernetes Administrator) exam. Respected in industry.

---

## If you want to understand AI deeply

**Read the papers.** They are more accessible than you think.

Start here (in order):

1. **"How neural networks learn from experience"** — Hinton (1992). Short, readable, no equations.

2. **"Deep Learning"** — LeCun, Bengio, Hinton (2015). *Nature*. The definitive overview.

3. **"Attention Is All You Need"** — Vaswani et al. (2017). The paper that introduced the Transformer — the architecture behind every modern language model including Claude.

4. **"Deep learning for AI"** — Bengio, LeCun, Hinton (2021). The state of the field.

Hinton's full archive: https://www.cs.toronto.edu/~hinton/pages/publications.html

---

## If you want to build smart homes and IoT

**Start with:** Home Assistant (home-assistant.io). Install it on a Raspberry Pi. Connect one device. Write one automation.

**Hardware path:**
1. Raspberry Pi 4 or 5 (your home server)
2. Zigbee USB stick (ConBee II or SONOFF Zigbee 3.0)
3. Zigbee sensors (temperature, motion, contact)
4. Zigbee smart plugs (energy monitoring)

**Software path:**
1. Home Assistant for the hub
2. Node-RED for complex automations
3. Mosquitto (MQTT broker) for custom sensors
4. InfluxDB + Grafana for historical data and dashboards

**Community:** r/homeassistant on Reddit. 900,000+ members. Answers to every question.

---

## If you want to be a product designer in the AI era

**Read:**
- *The Lean Startup* — Eric Ries. The foundational text on MVPs and validated learning.
- *Thinking in Systems* — Donella Meadows. Systems thinking at its clearest.
- *The Innovator's Dilemma* — Clayton Christensen. Why great companies fail, and how disruptors win.

**Practice:**
- Write a product brief for something you use every day. Pretend you're building it from scratch.
- Read one technical blog post per week about a system you use. How does it work? How could it fail?
- Talk to engineers. Learn their constraints. Build your vocabulary.

---

## The Most Important Thing

Start something. Anything.

The gap between reading about systems and building one is enormous. Cross it with the smallest possible project — not a plan for a project, not a design for a project, but a thing that runs.

A Python script that reads a sensor. A REST API with one endpoint. A Docker container with one service. A database with one table.

Start there. Everything else follows.

---

*The book is over. The building has begun.*
