# Chapter 19 — Kubernetes: The Construction Site Foreman

*Part 4: Shipping It — From Your Laptop to the World*

---

## The Analogy

You are running a large construction project. You have 50 workers. Each worker has a specific job. But workers get sick. Workers quit. Workers show up late.

You hire a **foreman**. The foreman doesn't do the work — they manage the workers:
- "We need 10 bricklayers. I have 7. Find 3 more."
- "Worker 23 is sick. Assign someone to replace them."
- "The east wing is behind schedule. Move 5 workers from the west wing."
- "That crew's work doesn't meet spec. Stop them. Fix the work. Restart."

The foreman's job is to ensure the *intended state* (50 productive workers in the right positions) matches *reality* — continuously, automatically, without human intervention for every little thing.

**Kubernetes is the foreman for Docker containers.**

---

## The Concept

**Kubernetes** (often abbreviated as K8s — "K" + 8 letters + "s") is an orchestration system that manages containers at scale.

You tell Kubernetes: "I want 3 copies of the Registry container running at all times." Kubernetes makes it happen. If one copy crashes, Kubernetes starts a new one. If traffic spikes, you tell Kubernetes to run 10 copies instead of 3, and it does it within seconds.

### Core Kubernetes Concepts

**Pod** — The smallest deployable unit. Usually one container, but can be several that work together. Like one worker on the site.

**Deployment** — Manages a set of identical pods. Says "I want exactly 3 copies of this container running." Handles updates (rolling out new versions without downtime). Like the crew foreman for one type of job.

**Service** — A stable network address for a set of pods. Since pods come and go (they crash, get replaced, scale up and down), you need a fixed address that always routes to a healthy pod. Like the foreman's radio channel — workers change, the channel doesn't.

**Ingress** — The gateway that handles traffic from the outside world. It routes requests to the right internal service. Like the project site entrance with a guard who directs visitors.

**Namespace** — A virtual partition within a cluster. Like different floors in a building — each team has their own floor, but they share the building.

---

## System Diagram

```
KUBERNETES CLUSTER ARCHITECTURE

Internet traffic
      │
      ▼
┌─────────────────────────────────────────────────────┐
│  INGRESS (the front gate)                           │
│  Routes: registry.modelcontextprotocol.io → registry│
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  SERVICE: registry (stable address, load balances)  │
│  Always routes to a healthy pod                     │
└────┬──────────────────┬──────────────────┬──────────┘
     │                  │                  │
     ▼                  ▼                  ▼
┌─────────┐        ┌─────────┐        ┌─────────┐
│  Pod 1  │        │  Pod 2  │        │  Pod 3  │
│registry │        │registry │        │registry │
│:8080 ✓  │        │:8080 ✗  │        │:8080 ✓  │
│         │        │(crashed)│        │         │
└─────────┘        └────┬────┘        └─────────┘
                        │
                        │ Kubernetes detects crash
                        ▼
                   ┌─────────┐
                   │  Pod 2  │
                   │ (new)   │
                   │:8080 ✓  │
                   └─────────┘
                        │
                   Readiness probe
                   passes → rejoins pool
```

---

## The Real Code

The MCP Registry's Kubernetes configuration lives in `registry-main/deploy/`. Let's look at key pieces from the deploy package:

From `deploy/pkg/k8s/registry.go` (simplified), the Registry deployment is described in Go code that generates Kubernetes resources:

```go
// Define the Registry deployment
deployment := &appsv1.Deployment{
    Spec: appsv1.DeploymentSpec{
        Replicas: &replicas,  // How many copies to run
        Template: corev1.PodTemplateSpec{
            Spec: corev1.PodSpec{
                Containers: []corev1.Container{{
                    Name:  "registry",
                    Image: registryImage,  // Which Docker image to use
                    Ports: []corev1.ContainerPort{{
                        ContainerPort: 8080,
                    }},
                    // Health check: is this container alive?
                    ReadinessProbe: &corev1.Probe{
                        HTTPGetAction: &corev1.HTTPGetAction{
                            Path: "/healthz",  // The health endpoint (Ch 8)
                            Port: 8080,
                        },
                    },
                }},
            },
        },
    },
}
```

Notice the `ReadinessProbe`. Kubernetes repeatedly calls `/healthz` on each pod. If the pod stops responding (crashes, hangs, gets overwhelmed), Kubernetes marks it as not ready and stops sending traffic to it. It starts a new pod to replace it. You never need to intervene manually.

From `deploy/pkg/k8s/postgres.go`, the database gets similar treatment:

```go
// PostgreSQL gets persistent storage (pods are ephemeral, data is not)
volumeClaimTemplates: []corev1.PersistentVolumeClaim{{
    Spec: corev1.PersistentVolumeClaimSpec{
        AccessModes: []corev1.PersistentVolumeAccessMode{
            corev1.ReadWriteOnce,
        },
        Resources: corev1.ResourceRequirements{
            Requests: corev1.ResourceList{
                corev1.ResourceStorage: resource.MustParse("10Gi"),
            },
        },
    },
}}
```

This creates a 10-gigabyte storage volume that persists even if the PostgreSQL pod restarts. The pod can die and be replaced — the data survives because it lives in the volume, not in the pod.

---

## 🔬 Lab Activity — Write Kubernetes YAML Files

**What you'll build:** A Kubernetes Deployment YAML with 3 replicas and a readiness probe, a Service YAML, and a Python script that simulates the Kubernetes control loop — detecting drift between intended and actual state, just like `registry-main/deploy/pkg/k8s/registry.go`.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch19-kubernetes
cd C:\labs\ch19-kubernetes
```

---

**2. Create the Deployment manifest.**

```powershell
notepad registry-deployment.yaml
```
Paste:
```yaml
# This mirrors registry-main/deploy/pkg/k8s/registry.go
apiVersion: apps/v1
kind: Deployment
metadata:
  name: registry
  namespace: mcp-registry
spec:
  replicas: 3                          # Desired pod count
  selector:
    matchLabels:
      app: registry
  template:
    metadata:
      labels:
        app: registry
    spec:
      containers:
        - name: registry
          image: registry.modelcontextprotocol.io/registry:latest
          ports:
            - containerPort: 8080
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: registry-secrets
                  key: database-url
          readinessProbe:              # Health check — must pass before receiving traffic
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5     # Wait 5s before first check
            periodSeconds: 10          # Check every 10s
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
```

---

**3. Create the Service manifest.**

```powershell
notepad registry-service.yaml
```
Paste:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: registry
  namespace: mcp-registry
spec:
  selector:
    app: registry           # Routes to pods with this label
  ports:
    - protocol: TCP
      port: 80              # External port
      targetPort: 8080      # Internal pod port
  type: ClusterIP           # Internal only — Ingress handles external traffic
```

---

**4. Create the control loop simulator.**

```powershell
notepad k8s_simulator.py
```
Paste:
```python
import time
import random

# ── SIMULATED KUBERNETES CLUSTER ──────────────────────────

class Pod:
    def __init__(self, name):
        self.name = name
        self.status = "Running"  # Running, Crashed, Starting
        self.ready = True

    def check_health(self):
        """Simulate random pod crashes."""
        if random.random() < 0.15:  # 15% chance of crash per check
            self.status = "Crashed"
            self.ready = False

class Deployment:
    def __init__(self, name, desired_replicas):
        self.name = name
        self.desired = desired_replicas
        self.pods = [Pod(f"{name}-pod-{i+1}") for i in range(desired_replicas)]

    def actual_running(self):
        return [p for p in self.pods if p.status == "Running"]

    def crashed_pods(self):
        return [p for p in self.pods if p.status == "Crashed"]

    def reconcile(self):
        """The Kubernetes control loop: compare desired vs actual, fix drift."""
        running = len(self.actual_running())
        crashed = self.crashed_pods()

        # Fix crashed pods
        for pod in crashed:
            new_name = pod.name.replace("-pod-", "-pod-new-")
            new_pod = Pod(new_name)
            new_pod.status = "Starting"
            new_pod.ready = False
            self.pods.remove(pod)
            self.pods.append(new_pod)
            print(f"    [K8s] {pod.name} crashed → Starting replacement {new_name}")
            # Simulate startup time
            new_pod.status = "Running"
            new_pod.ready = True
            print(f"    [K8s] {new_name} passed readiness probe → Added to pool")

        # Scale up if needed
        while len(self.actual_running()) < self.desired:
            idx = len(self.pods) + 1
            p = Pod(f"{self.name}-pod-scale-{idx}")
            self.pods.append(p)
            print(f"    [K8s] Scaled up: started {p.name}")

        # Scale down if needed
        while len(self.actual_running()) > self.desired:
            p = self.actual_running()[-1]
            self.pods.remove(p)
            print(f"    [K8s] Scaled down: terminated {p.name}")

# ── SIMULATION ─────────────────────────────────────────────

print("=== Kubernetes Control Loop Simulation ===\n")

deployment = Deployment("registry", desired_replicas=3)
print(f"Deployment 'registry' created with {deployment.desired} desired replicas\n")

for tick in range(5):
    print(f"{'─'*50}")
    print(f"Tick {tick+1}: Checking cluster state...")

    # Simulate random failures
    for pod in deployment.pods:
        pod.check_health()

    running = deployment.actual_running()
    crashed = deployment.crashed_pods()
    print(f"  Running: {len(running)}/{deployment.desired}")
    for p in deployment.pods:
        status_icon = "✓" if p.status == "Running" else "✗"
        print(f"  {status_icon} {p.name}: {p.status}")

    if crashed or len(running) != deployment.desired:
        print(f"  ⚠ Drift detected! Reconciling...")
        deployment.reconcile()
    else:
        print(f"  ✓ All {deployment.desired} pods healthy. No action needed.")

    # Simulate scale event on tick 3
    if tick == 2:
        print(f"\n  📈 Traffic spike! Scaling to 6 replicas...")
        deployment.desired = 6
        deployment.reconcile()

    if tick == 3:
        print(f"\n  📉 Traffic normal. Scaling back to 3 replicas...")
        deployment.desired = 3
        deployment.reconcile()

print(f"\n{'='*50}")
print(f"Final state: {len(deployment.actual_running())}/{deployment.desired} pods running")
```

**5. Run the simulator.**

```powershell
python k8s_simulator.py
```
✅ You should see the control loop detecting crashes, replacing pods, scaling up on tick 3, and scaling back down on tick 4:
```
=== Kubernetes Control Loop Simulation ===

Deployment 'registry' created with 3 desired replicas

──────────────────────────────────────────────────
Tick 1: Checking cluster state...
  Running: 2/3
  ✓ registry-pod-1: Running
  ✗ registry-pod-2: Crashed
  ✓ registry-pod-3: Running
  ⚠ Drift detected! Reconciling...
    [K8s] registry-pod-2 crashed → Starting replacement registry-pod-new-2
    [K8s] registry-pod-new-2 passed readiness probe → Added to pool
...
  📈 Traffic spike! Scaling to 6 replicas...
    [K8s] Scaled up: started registry-pod-scale-4
    [K8s] Scaled up: started registry-pod-scale-5
    [K8s] Scaled up: started registry-pod-scale-6
```

**What you just built:** A working Kubernetes Deployment YAML and Service YAML matching `registry-main/deploy/pkg/k8s/registry.go`, plus a Python simulation of the Kubernetes reconciliation control loop — the same loop that runs every 15 seconds in every real Kubernetes cluster in the world.

---

> **🌍 Real World**
> Kubernetes was open-sourced by Google in 2014, based on their internal system called Borg which had managed their infrastructure for a decade. Today, over 70% of Fortune 500 companies run Kubernetes. The MCP Registry runs on Google Kubernetes Engine (GKE) — the same managed Kubernetes service used by Spotify, Twitter, and The New York Times. When the MCP Registry got featured on Hacker News in 2025 and received a sudden traffic spike, Kubernetes auto-scaled within 30 seconds — no human intervention required. The health probe at `/healthz` you learned in Chapter 8 is not just for testing: it is the signal Kubernetes uses to decide whether to route traffic to a pod.

---

## The Takeaway

Kubernetes is the foreman for containers — it ensures the desired state (X copies of Y container) matches reality at all times. It self-heals crashed containers, scales up and down on demand, performs zero-downtime rolling updates, and manages persistent storage. The MCP Registry uses Kubernetes on GCP to run reliably in production.

---

## The Connection

Kubernetes manages what is running. But how does new code get deployed automatically? How does the Registry team push code and have it live in production within minutes? In Chapter 20, we follow the CI/CD pipeline — the automated factory that builds, tests, and deploys every change.

---

*→ Continue to [Chapter 20 — CI/CD: The Factory Assembly Line](./ch20-cicd.md)*
