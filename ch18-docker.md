# Chapter 18 — Docker: Shipping Containers for Code

*Part 4: Shipping It — From Your Laptop to the World*

---

## The Analogy

Before standardized shipping containers were invented in the 1950s, loading a cargo ship was a nightmare. Every item was a different shape and size. Boxes of bananas. Crates of machinery. Drums of chemicals. Each required different handling, different storage conditions, different loading techniques. Ships spent more time in port loading and unloading than at sea.

In 1956, Malcolm McLean invented the standardized shipping container — a uniform steel box that could carry anything inside. The same crane picks it up. The same ship carries it. The same truck delivers it. What's inside doesn't matter — the container is always the same shape.

This transformed global trade. Before: weeks in port. After: hours.

**Docker is the shipping container for software.**

Before Docker, deploying software was a nightmare. "It works on my machine" was the most feared phrase in software development. The code ran perfectly on the developer's laptop. On the server? Crashes, errors, missing files, wrong version of Python, wrong library version, different operating system. Chaos.

Docker solves this by packaging the code *together with everything it needs to run*: the exact version of Python, the exact libraries, the configuration files, the runtime environment. All sealed in one container. Same container runs everywhere.

---

## The Concept

A **Docker container** is a self-contained, isolated package that includes:
- Your application code
- The exact runtime it needs (Python 3.11, Go 1.24, Node.js 20, etc.)
- All libraries and dependencies
- Configuration and environment variables
- A defined way to start the application

A **Docker image** is the blueprint — the template for creating containers. Like a cookie cutter. The image is the cutter; the container is the cookie.

You build an image once. You can run thousands of containers from the same image. Every container is identical.

---

## System Diagram

```
FROM CODE TO RUNNING CONTAINER

  source code + Dockerfile
         │
         ▼
  docker build
  ┌─────────────────────────────────────────────┐
  │  DOCKER IMAGE LAYERS                        │
  │  Layer 1: FROM golang:1.24-alpine  (cached) │
  │  Layer 2: COPY go.mod              (cached) │
  │  Layer 3: RUN go mod download      (cached) │
  │  Layer 4: COPY . .                 (changed)│
  │  Layer 5: RUN go build             (rebuilt)│
  │  └─→ image: registry:latest                 │
  └─────────────────────────────────────────────┘
         │
         ▼
  docker run (or Kubernetes schedules it)
  ┌─────────────────────────────────────────────┐
  │  CONTAINER (running instance)               │
  │  ┌───────────────┐  ┌───────────────┐       │
  │  │ registry:8080 │  │ postgres:5432 │       │
  │  │  (your code)  │──│  (database)   │       │
  │  └───────────────┘  └───────────────┘       │
  │  Both isolated. Same network. Same machine. │
  └─────────────────────────────────────────────┘
         │
  localhost:8080 exposed to your computer
```

---

### The Dockerfile: The Recipe

A `Dockerfile` is a text file that describes how to build an image. Here is a simplified version of what the MCP Registry's Dockerfile would look like:

```dockerfile
# Start from an official Go image (provides the Go compiler)
FROM golang:1.24-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the Go dependency files first (for caching)
COPY go.mod go.sum ./

# Download dependencies (this layer is cached if go.mod doesn't change)
RUN go mod download

# Copy all source code
COPY . .

# Build the application
RUN go build -o registry ./cmd/registry

# Define what runs when the container starts
CMD ["./registry"]
```

Each line is a layer. Docker caches layers — if nothing changed in your `go.mod` file, it doesn't re-download all dependencies. Only changed layers are rebuilt. This makes builds fast.

### The MCP Registry Uses ko

The MCP Registry uses a special tool called **ko** (from Google) instead of a traditional Dockerfile. ko is designed specifically for Go applications — it builds a minimal container image without needing Docker itself. From `.ko.yaml` in the registry:

```yaml
# The base image — the smallest possible starting point
defaultBaseImage: gcr.io/distroless/static-debian12
```

`distroless` images contain only what is absolutely necessary to run the application. No shell. No utilities. No package manager. This is a security practice: the fewer things in the container, the fewer things that can go wrong or be exploited.

---

## 🔬 Lab Activity — Write a Dockerfile and docker-compose.yml

**What you'll build:** A working Dockerfile for a Python API, a docker-compose.yml connecting two services, and the actual files that model the MCP Registry's container setup — so you understand every line of the real `registry-main/docker-compose.yml`.

**Time:** ~25 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell · Docker Desktop (install from docker.com if not present)

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch18-docker
cd C:\labs\ch18-docker
```

---

**2. Create the application: `app.py`.**

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
        if self.path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "env": os.environ.get("APP_ENV", "unknown")}).encode())
        else:
            self.send_response(404)
            self.end_headers()

port = int(os.environ.get("PORT", 8080))
print(f"Starting on port {port}")
HTTPServer(("0.0.0.0", port), Handler).serve_forever()
```

---

**3. Create the `Dockerfile`.**

```powershell
notepad Dockerfile
```
Paste:
```dockerfile
# Layer 1: Start from an official Python runtime
FROM python:3.11-slim

# Layer 2: Set the working directory inside the container
WORKDIR /app

# Layer 3: Copy the application code
COPY app.py .

# Layer 4: Expose the port the app listens on
EXPOSE 8080

# Layer 5: Set default environment variable
ENV APP_ENV=production

# Layer 6: Define what runs when the container starts
CMD ["python", "app.py"]
```

---

**4. Create the `docker-compose.yml`.**

```powershell
notepad docker-compose.yml
```
Paste:
```yaml
services:
  # Service 1: The API server (our app.py)
  api:
    build: .                        # Build from current folder's Dockerfile
    ports:
      - "8080:8080"                 # Expose port 8080 to your computer
    environment:
      PORT: "8080"
      APP_ENV: "development"
    depends_on:
      - db                          # Wait for db service to start first

  # Service 2: A simple "database" placeholder (just echoes a hostname)
  db:
    image: alpine:3.19              # Tiny Linux image — no real DB needed for demo
    command: sh -c "echo 'DB ready' && sleep infinity"
    ports:
      - "5432:5432"                 # Reserved as if it were PostgreSQL
```

---

**5. Build and run with Docker.**

First verify Docker is installed:
```powershell
docker --version
```
✅ You should see: `Docker version 27.x.x, build ...`

Build the image:
```powershell
docker build -t my-registry-app .
```
✅ You should see each layer build in sequence:
```
[1/6] FROM python:3.11-slim
[2/6] WORKDIR /app
[3/6] COPY app.py .
...
Successfully built abc123
Successfully tagged my-registry-app:latest
```

Run the container:
```powershell
docker run -d -p 8080:8080 --name myapp my-registry-app
```

Test it:
```powershell
python -c "import urllib.request,json; print(json.loads(urllib.request.urlopen('http://localhost:8080/healthz').read()))"
```
✅ You should see: `{'status': 'ok', 'env': 'production'}`

Stop and remove:
```powershell
docker stop myapp && docker rm myapp
```

---

**6. Run with Docker Compose (two services together).**

```powershell
docker compose up -d
```
✅ You should see both services start:
```
✔ Container ch18-docker-db-1   Started
✔ Container ch18-docker-api-1  Started
```

Test:
```powershell
python -c "import urllib.request,json; print(json.loads(urllib.request.urlopen('http://localhost:8080/healthz').read()))"
```
✅ You see: `{'status': 'ok', 'env': 'development'}` — note "development" from docker-compose env vars.

Stop everything:
```powershell
docker compose down
```

**What you just built:** A working Dockerfile with layered build, a docker-compose.yml with two dependent services, and a running containerized app — matching the exact structure of `registry-main/Dockerfile` and `registry-main/docker-compose.yml`.

---

> **🌍 Real World**
> Docker was released in 2013 and transformed the industry within two years. Before Docker, a server team might spend a full week setting up a new production environment. After Docker: minutes. Netflix runs all of its microservices in Docker containers — over 700 different services that handle 200 million subscribers. The MCP Registry uses `ko` (Google's Go container builder) instead of a Dockerfile because ko produces smaller, faster images with no shell or OS utilities — reducing the attack surface to almost zero. When you run `docker pull` on Docker Hub, you're downloading layers — each one cached and reusable, exactly as you experienced in this lab.

---

## The Takeaway

Docker packages your application and everything it needs into a standardized container. This eliminates "it works on my machine" forever — because the container runs identically everywhere. Docker Compose orchestrates multiple containers, defining how they connect and depend on each other. The MCP Registry uses Docker Compose for development and a minimal distroless image for production security.

---

## The Connection

One container is easy to manage. But production systems need many copies — for redundancy, for scale, for zero-downtime updates. In Chapter 19, we meet **Kubernetes**, the system that manages a fleet of containers the way a construction site foreman manages a team of workers.

---

*→ Continue to [Chapter 19 — Kubernetes: The Construction Site Foreman](./ch19-kubernetes.md)*
