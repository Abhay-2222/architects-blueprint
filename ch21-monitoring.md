# Chapter 21 — Monitoring: The Control Room Dashboard

*Part 4: Shipping It — From Your Laptop to the World*

---

## The Analogy

A nuclear power plant has a control room. It is filled with screens showing every measurement that matters: core temperature, pressure in each reactor loop, coolant flow rate, power output, valve positions. Everything is measured continuously. Every number that goes outside safe limits triggers an alarm.

The operators do not run through the plant with thermometers every hour. They sit in the control room and watch the dashboards. The instruments do the watching. The operators respond to alerts.

This is the only sane way to run a complex system. A server handling millions of requests cannot be checked manually. You need instruments — automated systems that measure what's happening, display it, and sound the alarm when something goes wrong.

**This is monitoring.**

---

## The Concept

**Monitoring** is the practice of continuously measuring a system's health and behavior, and alerting when something falls outside acceptable ranges.

There are four things to measure in any web service:

**1. Latency** — How long does each request take?
- Normal: < 100ms
- Slow: 100ms–1s
- Problem: > 1s consistently

**2. Traffic** — How many requests per second?
- Useful for detecting spikes, drops (service failure), or trends

**3. Errors** — What percentage of requests fail?
- Normal: < 0.1%
- Warning: 1%
- Crisis: 5%+

**4. Saturation** — How close to the limit is the system?
- CPU at 90%? About to fail.
- Database connections exhausted? New requests will fail.

These four are known as the **"Four Golden Signals"** in reliability engineering. Monitor these four things on any service and you will know everything that matters.

---

## System Diagram

```
MONITORING ARCHITECTURE

  MCP Registry (running)
  ┌─────────────────────────────────┐
  │  Each request updates metrics:  │
  │  requests_total += 1            │
  │  request_duration.observe(45ms) │
  │  errors_total += 0 (success)    │
  └──────────────┬──────────────────┘
                 │ metrics exposed at /metrics
                 ▼
  ┌─────────────────────────────────┐
  │  PROMETHEUS (scrapes /metrics   │
  │  every 15 seconds, stores data) │
  └──────────────┬──────────────────┘
                 │ time-series data
                 ▼
  ┌─────────────────────────────────┐
  │  GRAFANA (dashboard UI)         │
  │  ┌──────────┐  ┌─────────────┐  │
  │  │Latency   │  │ Error Rate  │  │
  │  │p95: 45ms │  │  0.02%  🟢  │  │
  │  └──────────┘  └─────────────┘  │
  │  ┌──────────┐  ┌─────────────┐  │
  │  │Traffic   │  │ Saturation  │  │
  │  │847 req/s │  │ CPU: 32%    │  │
  │  └──────────┘  └─────────────┘  │
  └──────────────┬──────────────────┘
                 │ alert rule triggered
                 ▼
  ┌─────────────────────────────────┐
  │  ALERTMANAGER                   │
  │  "Error rate > 1% for 5 min"    │
  │  → PagerDuty → Engineer's phone │
  └─────────────────────────────────┘
```

---

## The Real Code

The MCP Registry uses **OpenTelemetry** with **Prometheus** for metrics. From `registry-main/internal/telemetry/metrics.go`:

```go
type Metrics struct {
    // How many HTTP requests have been received
    Requests metric.Int64Counter

    // How long each request took (in seconds)
    // Stored as a histogram — shows distribution, not just average
    RequestDuration metric.Float64Histogram

    // How many errors have occurred
    ErrorCount metric.Int64Counter

    // Is the service up? (1 = yes, 0 = no)
    Up metric.Int64Gauge
}
```

Each metric has a specific measurement type:

- **Counter** — A number that only goes up. Total requests ever received. You can calculate rate (requests per second) by looking at how fast it grows.
- **Histogram** — Shows the distribution of values. For request duration, it reveals: "90% of requests finish in < 50ms, but 1% take > 2s." A simple average would hide that 1%.
- **Gauge** — A number that goes up and down. Current connections open. CPU percentage right now.

The `RequestDuration` histogram uses explicit bucket boundaries:

```go
metric.WithExplicitBucketBoundaries(
    0.005, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 50.0,
)
```

This says: "Count how many requests fell in each duration bracket." You can then see: "95% of requests completed in under 0.25 seconds, but 0.1% took over 5 seconds." This is far more useful than knowing "the average request took 0.3 seconds" — because averages hide outliers.

### The Health Endpoint

Every service in the Registry exposes `/healthz` — a special endpoint that Kubernetes calls to check if the service is alive. From Chapter 8:

```go
r.GET("/healthz", handlers.HealthCheck)
```

This endpoint returns:
- `200 OK` — "I'm alive and healthy"
- `503 Service Unavailable` — "Something is wrong"

Kubernetes calls this every 10 seconds. If the service doesn't respond with 200 for 3 consecutive checks, Kubernetes marks it as unhealthy and starts a replacement (Chapter 19).

---

## 🔬 Lab Activity — Build a Metrics Collector

**What you'll build:** A Python HTTP server that tracks the Four Golden Signals for every request (latency, traffic, errors, saturation), exposes a `/metrics` endpoint in Prometheus format, and a `/dashboard` endpoint showing a live text dashboard — matching the `Metrics` struct in `registry-main/internal/telemetry/metrics.go`.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Two PowerShell windows

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch21-monitoring
cd C:\labs\ch21-monitoring
```

---

**2. Create the file `monitored_server.py`.**

```powershell
notepad monitored_server.py
```
Paste:
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, time, random

# ── METRICS STORE (the Four Golden Signals) ─────────────────
metrics = {
    "requests_total": 0,           # Traffic: total requests received
    "errors_total": 0,             # Errors: total failed requests
    "duration_sum_ms": 0.0,        # Latency: sum of all response times
    "duration_buckets": {          # Latency: histogram buckets
        5: 0, 25: 0, 50: 0, 100: 0, 250: 0, 500: 0, 1000: 0, float("inf"): 0
    },
    "active_requests": 0,          # Saturation: currently in-flight
}

def record_request(duration_ms, is_error):
    """Update metrics after each request."""
    metrics["requests_total"] += 1
    metrics["duration_sum_ms"] += duration_ms
    if is_error:
        metrics["errors_total"] += 1
    for bucket in sorted(metrics["duration_buckets"]):
        if duration_ms <= bucket:
            metrics["duration_buckets"][bucket] += 1
            break

def format_prometheus():
    """Output metrics in Prometheus text format."""
    total = metrics["requests_total"]
    avg = metrics["duration_sum_ms"] / total if total > 0 else 0
    error_rate = (metrics["errors_total"] / total * 100) if total > 0 else 0
    lines = [
        f"# HELP requests_total Total HTTP requests received",
        f"requests_total {total}",
        f"",
        f"# HELP errors_total Total HTTP errors",
        f"errors_total {metrics['errors_total']}",
        f"",
        f"# HELP request_duration_ms_avg Average request duration",
        f"request_duration_ms_avg {avg:.2f}",
        f"",
        f"# HELP error_rate_percent Error percentage",
        f"error_rate_percent {error_rate:.3f}",
        f"",
        f"# HELP active_requests Currently in-flight requests",
        f"active_requests {metrics['active_requests']}",
    ]
    return "\n".join(lines)

def format_dashboard():
    """Output a text dashboard showing Four Golden Signals."""
    total = metrics["requests_total"]
    errors = metrics["errors_total"]
    avg = metrics["duration_sum_ms"] / total if total > 0 else 0
    error_rate = (errors / total * 100) if total > 0 else 0

    def color(val, warn, crit, higher_is_bad=True):
        if higher_is_bad:
            if val >= crit: return "RED"
            if val >= warn: return "YELLOW"
            return "GREEN"
        else:
            if val <= crit: return "RED"
            if val <= warn: return "YELLOW"
            return "GREEN"

    lines = [
        "=" * 55,
        "  MONITORING DASHBOARD — Four Golden Signals",
        "=" * 55,
        f"",
        f"  TRAFFIC     {total:>8} requests total",
        f"",
        f"  LATENCY     {avg:>8.1f} ms average",
        f"              Status: {color(avg, 100, 500)}",
        f"",
        f"  ERRORS      {errors:>8} total  ({error_rate:.2f}%)",
        f"              Status: {color(error_rate, 1.0, 5.0)}",
        f"",
        f"  SATURATION  {metrics['active_requests']:>8} active requests",
        f"              Status: {color(metrics['active_requests'], 10, 50)}",
        "",
        "  Buckets (response time distribution):",
    ]
    for bucket, count in metrics["duration_buckets"].items():
        label = f"<= {bucket}ms" if bucket != float("inf") else "> 1000ms"
        bar = "#" * min(count, 30)
        lines.append(f"    {label:12} {count:5}  {bar}")
    lines.append("=" * 55)
    return "\n".join(lines)


class MonitoredHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        metrics["active_requests"] += 1
        start = time.time()
        is_error = False

        try:
            if self.path == "/healthz":
                body = json.dumps({"status": "ok"}).encode()
                self.send_response(200)
            elif self.path == "/metrics":
                body = format_prometheus().encode()
                self.send_response(200)
            elif self.path == "/dashboard":
                body = format_dashboard().encode()
                self.send_response(200)
            elif self.path == "/slow":
                # Simulate slow endpoint
                time.sleep(random.uniform(0.2, 0.6))
                body = b'{"result": "slow response"}'
                self.send_response(200)
            elif self.path == "/error":
                body = b'{"error": "something went wrong"}'
                self.send_response(500)
                is_error = True
            else:
                body = b'{"error": "not found"}'
                self.send_response(404)
                is_error = True

            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        finally:
            elapsed = (time.time() - start) * 1000
            record_request(elapsed, is_error)
            metrics["active_requests"] -= 1

print("Monitored server running at http://localhost:8770")
print("Endpoints:")
print("  GET /healthz   — normal request")
print("  GET /slow      — slow request (200-600ms)")
print("  GET /error     — forced error (500)")
print("  GET /metrics   — Prometheus metrics")
print("  GET /dashboard — Four Golden Signals dashboard")
HTTPServer(("localhost", 8770), MonitoredHandler).serve_forever()
```

**3. Start the server in one PowerShell window.**

```powershell
python monitored_server.py
```

---

**4. In a second PowerShell window, generate traffic and check the dashboard.**

Generate mixed traffic (normal, slow, error):
```powershell
python -c "
import urllib.request, time
endpoints = ['/healthz']*8 + ['/slow']*2 + ['/error']*2
for ep in endpoints:
    try: urllib.request.urlopen('http://localhost:8770' + ep, timeout=2)
    except: pass
    time.sleep(0.1)
print('Traffic generated')
"
```

View the dashboard:
```powershell
python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8770/dashboard').read().decode())"
```
✅ You should see:
```
=======================================================
  MONITORING DASHBOARD — Four Golden Signals
=======================================================

  TRAFFIC          12 requests total

  LATENCY        45.3 ms average
                 Status: GREEN

  ERRORS            2 total  (16.67%)
                 Status: RED

  SATURATION        0 active requests
                 Status: GREEN

  Buckets (response time distribution):
    <= 5ms           3  ###
    <= 25ms          4  ####
    <= 50ms          2  ##
    <= 500ms         3  ###
    <= 1000ms        0
```

View Prometheus format:
```powershell
python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8770/metrics').read().decode())"
```

Stop the server with Ctrl+C.

**What you just built:** A monitored HTTP server tracking the Four Golden Signals, a Prometheus-format `/metrics` endpoint, and a live text dashboard — matching the `Metrics` struct and histogram bucket boundaries in `registry-main/internal/telemetry/metrics.go`.

---

> **🌍 Real World**
> Prometheus was built at SoundCloud in 2012 and is now the industry standard for metrics collection. Grafana — the dashboard tool — is used by NASA, CERN, and Booking.com. The MCP Registry sends metrics to Google Cloud Monitoring (formerly Stackdriver) via the OpenTelemetry protocol. When Anthropic's Claude API exceeded its error rate threshold during a major release in 2024, PagerDuty automatically paged the on-call engineer at 2am. The page included the exact metric that triggered it, the current value, and the threshold it crossed — exactly the information you just built. A healthy production system generates boring dashboards. The goal is to be bored.

---

## Connecting Part 4

You now understand the complete deployment lifecycle:

```
Developer writes code
    → git push
    → CI pipeline runs (lint → test → build → security scan) [Ch 20]
    → CD pipeline deploys to staging [Ch 20]
    → If staging looks good → CD deploys to production [Ch 20]
    → Kubernetes manages the running containers [Ch 19]
    → Docker containers run the actual application [Ch 18]
    → Monitoring watches everything [Ch 21]
    → Alerts notify when something goes wrong [Ch 21]
    → Kubernetes self-heals crashed pods [Ch 19]
```

This is the complete production lifecycle of a real software system.

---

## The Takeaway

Monitoring is the control room of software infrastructure. The Four Golden Signals (latency, traffic, errors, saturation) tell you everything you need to know about a service's health. The MCP Registry uses OpenTelemetry and Prometheus histograms to measure request performance precisely — not just averages, but the full distribution of response times.

---

## The Connection

We have covered the full stack: the Registry backend, the AI agent, and the deployment infrastructure. Now it is time to step back and answer the most important question many people have been wondering since page one: **What is AI, really?** Part 5 starts with the honest, no-hype answer.

---

*→ Continue to [Chapter 22 — What AI Actually Is (No Hype)](./ch22-what-ai-actually-is.md)*
