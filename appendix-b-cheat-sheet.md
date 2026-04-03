# Appendix B — Cheat Sheet

*One-page reference for the entire book.*

---

## The Five Components of Any System

| Component | Software | Analogy |
|-----------|---------|---------|
| Roads | Network / Internet | Cars carrying packages |
| Buildings | Servers | Kitchens doing work |
| Post Office | API | Waiter taking orders |
| Filing Cabinet | Database | Organized storage |
| Power Grid | Cloud / Infrastructure | Keeps everything running |

---

## HTTP Methods

| Method | Meaning | Example |
|--------|---------|---------|
| GET | Read something | GET /servers → list all servers |
| POST | Create something | POST /publish → register a server |
| PUT/PATCH | Update something | PATCH /servers/1 → edit a server |
| DELETE | Remove something | DELETE /servers/1 → remove a server |

---

## HTTP Status Codes

| Code | Meaning | When you see it |
|------|---------|-----------------|
| 200 | OK | Everything worked |
| 201 | Created | POST succeeded, new thing was made |
| 400 | Bad Request | You sent invalid data |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Valid token, but no permission |
| 404 | Not Found | That endpoint / resource doesn't exist |
| 500 | Server Error | Something broke on the server side |

---

## The AI Agent Loop

```
1. Receive user message
2. Read full session history
3. Decide: what tool to use next?
4. Pre-tool hooks check permissions
5. Execute the tool
6. Add result to session
7. Read result → decide if done or loop again
8. If done → send final message
```

---

## Tool Permission Levels

| Level | Can do | Risk |
|-------|--------|------|
| ReadOnly | Read files and data only | Low |
| WorkspaceWrite | Read and write project files | Medium |
| DangerFullAccess | Run any shell command | High |

---

## Sandbox Modes

| Mode | Filesystem access |
|------|------------------|
| workspace-only | Only the current project folder |
| allow-list | Specific paths you explicitly permit |
| off | No restrictions |

---

## Database Quick Reference

```sql
-- Create a table
CREATE TABLE plants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    moisture INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create an index (fast search)
CREATE INDEX idx_plants_name ON plants(name);

-- Insert a row
INSERT INTO plants (name, moisture) VALUES ('basil', 42);

-- Query rows
SELECT * FROM plants WHERE moisture < 30;

-- Update a row
UPDATE plants SET moisture = 55 WHERE name = 'basil';
```

---

## JWT Token Structure

```
HEADER.PAYLOAD.SIGNATURE

Header:  { "alg": "EdDSA" }
Payload: { "user": "abhay", "permissions": [...], "exp": 1234567890 }
Signature: [signed with server's private key — cannot be forged]
```

---

## MCP Server Tools — Minimum Required Fields

```json
{
  "name": "get_soil_moisture",
  "description": "Returns current moisture level. Use when user asks about plant water needs.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "plant": { "type": "string", "description": "Plant name" }
    },
    "required": ["plant"]
  }
}
```

---

## MCP Registry server.json — Required Fields

```json
{
  "name": "io.github.yourname/your-tool",
  "description": "What this tool does",
  "version": "1.0.0",
  "packages": [
    { "registry": "npm|pypi|docker", "name": "package-name", "version": "1.0.0" }
  ]
}
```

---

## Docker Quick Reference

```bash
# Run a container
docker run -d --name myapp -p 8080:8080 myimage:latest

# Run multiple containers together
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker logs myapp

# Enter a running container
docker exec -it myapp bash
```

---

## The Four Golden Signals (Monitoring)

| Signal | What it measures | Alert when |
|--------|-----------------|------------|
| Latency | How long requests take | p99 > 1 second |
| Traffic | Requests per second | Drops unexpectedly |
| Errors | % of requests failing | > 1% error rate |
| Saturation | How close to limits | CPU/memory > 80% |

---

## The Architect's Five Questions

1. What are the **components**?
2. How do they **connect**?
3. Where is the **bottleneck**?
4. What are the **failure modes**?
5. What are the **interfaces**?

---

## The One-Page Product Brief

```
PRODUCT: _______________ DATE: _______________

PROBLEM:
[2-3 sentences: What is broken? Who experiences it?]

SOLUTION:
[2-3 sentences: What will you build?]

TARGET USER:
[Specific. Not "everyone."]

SUCCESS METRICS:
1. _______________
2. _______________
3. _______________

MVP:
[Smallest version that tests the hypothesis]

NOT IN SCOPE:
1. _______________
2. _______________
3. _______________
```

---

## Key Research Papers (Hinton et al.)

| Paper | Year | Why it matters |
|-------|------|---------------|
| "Learning representations by back-propagating errors" | 1986 | Invented backpropagation — the foundation of all neural network training |
| "Reducing the dimensionality of data with neural networks" | 2006 | Proved deep networks could be trained — started the deep learning era |
| "ImageNet Classification with Deep CNNs" (AlexNet) | 2012 | Proved deep learning was categorically better — transformed the field |
| "Deep Learning" (review) | 2015 | The definitive summary of what deep learning is and why it works |
| "Distilling the knowledge in a neural network" | 2015 | How to compress a large model into a small one without losing capability |
| "Deep learning for AI" | 2021 | The state of the art and the path forward |

All available at: https://www.cs.toronto.edu/~hinton/pages/publications.html
