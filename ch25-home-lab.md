# Chapter 25 — The Home Lab: Your Personal Data Center

*Part 6: The Home Architect*

---

## The Analogy

Every great chef has a home kitchen. It is not the restaurant's industrial kitchen — no commercial gas range, no walk-in fridge, no line of sous-chefs. But it is theirs. It is where they experiment. Where they try new recipes without consequences. Where they learn by cooking, not by watching.

The chef's home kitchen is not a lesser version of the restaurant kitchen. It is the same skills applied at a smaller scale. Everything learned in the home kitchen applies directly to the restaurant — and vice versa.

A **home lab** is the engineer's home kitchen.

It is a small cluster of computers — maybe one Raspberry Pi, maybe a repurposed laptop, maybe an old desktop PC — where you run real services. Your own database. Your own server. Your own DNS. Your own AI. At home. On your network. Under your control.

This is not playing. It is the same thing that Google, Netflix, and Anthropic do — just smaller.

---

## The Concept

A **home lab** (short for home laboratory) is a personal infrastructure environment where you:
- Learn how production systems work by running them yourself
- Host services for your own use (file server, media server, smart home hub)
- Experiment safely without touching anything real or important
- Build skills that transfer directly to professional infrastructure

### What You Need

**Minimum setup:**
- 1 Raspberry Pi 4 (4GB RAM) — ~$55
- A microSD card (32GB or larger) — ~$10
- A USB power supply — ~$10
- A network cable (connect directly to your router)

**Expanded setup:**
- 1 Raspberry Pi 5 as the main server
- 1 old laptop or PC as a secondary server
- An external hard drive for storage
- A small switch (to connect multiple devices)

**Total cost of a functional home lab:** $75–$300 depending on what you already have

---

## System Diagram

```
HOME LAB NETWORK ARCHITECTURE

Internet
    │
    ▼
Router (192.168.1.1)
    │
    ├── Your laptop (192.168.1.100)
    │
    └── Raspberry Pi (192.168.1.50)  ← your server
         │
         ├── Docker: Pi-hole      :53    (DNS + ad blocking)
         ├── Docker: Home Assist  :8123  (smart home hub)
         ├── Docker: Nginx        :80    (reverse proxy)
         ├── Docker: PostgreSQL   :5432  (database)
         └── Docker: Ollama       :11434 (local AI)

Nginx routes by hostname:
  pihole.home      → 127.0.0.1:8080
  home.local       → 127.0.0.1:8123
  ollama.home      → 127.0.0.1:11434

Pi-hole custom DNS:
  *.home → 192.168.1.50  (all home services go to the Pi)
```

---

### What You Can Run

| Service | What it does | Production equivalent |
|---------|-------------|----------------------|
| Home Assistant | Smart home hub | Commercial IoT platforms |
| Pi-hole | Network-wide ad blocking + custom DNS | Corporate DNS |
| Nextcloud | Personal cloud storage | Dropbox/Google Drive |
| Gitea | Personal Git server | GitHub |
| PostgreSQL | Your own database (like the Registry's) | AWS RDS |
| Ollama | Run AI models locally | OpenAI API |
| Nginx | Web server / reverse proxy | Load balancers |

Running any of these at home teaches you exactly what operations teams do in production — at zero cost.

---

## The Real Connection: From Registry to Home Lab

Everything you learned about the MCP Registry (Part 2) applies to your home lab:

**Database (Chapter 6):** PostgreSQL runs on a Raspberry Pi. The same commands. The same migrations. The same SQL. Your home database IS a PostgreSQL server — smaller, but identical in every important way.

**Docker (Chapter 18):** Every service listed above can be run in Docker. One command: `docker run`. No installation, no conflicts, no dependency hell.

**Monitoring (Chapter 21):** You can run Prometheus + Grafana on a Raspberry Pi. The same dashboards. The same alerts. Your home lab teaches you to read production monitoring because it IS the same system at smaller scale.

---

## 🔬 Lab Activity — Write a Home Lab docker-compose.yml

**What you'll build:** A complete `docker-compose.yml` for a 3-service home lab (Nginx reverse proxy, a custom API, and PostgreSQL), plus an Nginx config file, and a Python health checker that pings all services and reports their status.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Docker Desktop · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch25-homelab
mkdir C:\labs\ch25-homelab\nginx
cd C:\labs\ch25-homelab
```

---

**2. Create the Nginx config.**

```powershell
notepad nginx\default.conf
```
Paste:
```nginx
# Nginx reverse proxy config
# Routes requests to the right backend service by hostname path

server {
    listen 80;

    # Route /api/* to the API service
    location /api/ {
        proxy_pass http://api:8080/;
        proxy_set_header Host $host;
    }

    # Route /health to Nginx's own health
    location /health {
        return 200 '{"service":"nginx","status":"ok"}';
        add_header Content-Type application/json;
    }

    # Default: show a welcome page
    location / {
        return 200 '{"message":"Home Lab running","services":["nginx","api","postgres"]}';
        add_header Content-Type application/json;
    }
}
```

---

**3. Create the API app.**

```powershell
notepad app.py
```
Paste:
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass
    def do_GET(self):
        if self.path in ["/", "/healthz"]:
            body = json.dumps({"service": "home-api", "status": "ok",
                               "db_url": os.environ.get("DATABASE_URL","not set")[:40]}).encode()
            self.send_response(200)
        else:
            body = b'{"error":"not found"}'
            self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
```

---

**4. Create the Dockerfile for the API.**

```powershell
notepad Dockerfile
```
Paste:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
EXPOSE 8080
CMD ["python", "app.py"]
```

---

**5. Create the `docker-compose.yml`.**

```powershell
notepad docker-compose.yml
```
Paste:
```yaml
# Home Lab — 3-service stack
# Mirrors the MCP Registry's docker-compose.yml structure

services:
  # Service 1: Nginx reverse proxy (the front door)
  nginx:
    image: nginx:alpine
    ports:
      - "8080:80"                         # Expose on port 8080 of your computer
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - api

  # Service 2: Custom API (your application)
  api:
    build: .
    environment:
      DATABASE_URL: "postgres://homelab:secret@postgres:5432/homelab"
    depends_on:
      - postgres

  # Service 3: PostgreSQL database
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: homelab
      POSTGRES_USER: homelab
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

**6. Start the home lab.**

```powershell
docker compose up -d --build
```
✅ You should see all 3 services start:
```
✔ Container ch25-homelab-postgres-1  Started
✔ Container ch25-homelab-api-1       Started
✔ Container ch25-homelab-nginx-1     Started
```

---

**7. Create and run the health checker.**

```powershell
notepad health_check.py
```
Paste:
```python
import urllib.request, json

SERVICES = [
    ("Nginx (reverse proxy)", "http://localhost:8080/health"),
    ("API via Nginx",          "http://localhost:8080/api/healthz"),
    ("API direct",             "http://localhost:8080/api/"),
]

print("=== Home Lab Health Check ===\n")
for name, url in SERVICES:
    try:
        r = urllib.request.urlopen(url, timeout=3)
        data = json.loads(r.read())
        print(f"  ✓ {name}: {data}")
    except Exception as e:
        print(f"  ✗ {name}: UNREACHABLE — {e}")
```

```powershell
python health_check.py
```
✅ You should see all services responding:
```
=== Home Lab Health Check ===

  ✓ Nginx (reverse proxy): {'service': 'nginx', 'status': 'ok'}
  ✓ API via Nginx: {'service': 'home-api', 'status': 'ok', 'db_url': 'postgres://homelab:secret@postgres'}
  ✓ API direct: {'service': 'home-api', 'status': 'ok', ...}
```

Stop everything:
```powershell
docker compose down
```

**What you just built:** A 3-service home lab stack with a reverse proxy, custom API, and PostgreSQL — the same architecture as the MCP Registry's production stack, runnable on a Raspberry Pi with one command.

---

> **🌍 Real World**
> The "home lab" community is one of the most active in technology — r/homelab on Reddit has over 600,000 members sharing their setups. Jeff Geerling (jeffgeerling.com) has spent years testing Raspberry Pis and building home labs on YouTube, inspiring tens of thousands of engineers. The skills learned in a home lab are directly applicable to cloud infrastructure: AWS, GCP, and Azure all use the same Docker, Kubernetes, and Nginx configurations you just ran. Many engineers credit their home lab as the most important learning tool in their career — it costs $100 and teaches what years of coursework cannot.

---

## The Takeaway

A home lab is a professional-grade learning environment that costs under $100 to set up. Every skill from Parts 1–5 of this book applies directly: Docker containers, databases, APIs, monitoring, routing. Your Raspberry Pi IS a production server — just personal-scale. Start small. One device. Three services. Then grow.

---

## The Connection

You have a home lab running services. Now let's wire them together intelligently. In Chapter 26, we design the smart home — not as a collection of gadgets, but as a properly architected system with sensors, a hub, automations, and an AI layer.

---

*→ Continue to [Chapter 26 — Smart Home Architecture](./ch26-smart-home-architecture.md)*
