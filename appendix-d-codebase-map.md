# Appendix D — The Two Codebases: Map to Source Files

*Every chapter, mapped to the real file that grounds it.*

---

## How to Use This Map

When a chapter references real code, find the exact file here. Open it. Read it. The chapter tells you what to look for — this map tells you where to find it.

Both codebases are at:
- `D:\Someinfo\registry-main\registry-main\` (the MCP Registry — Go)
- `D:\Someinfo\claw-code-main\claw-code-main\` (the AI agent — Python + Rust)

---

## Part 1 — What Is a System?

| Chapter | Key concept | Source file |
|---------|------------|-------------|
| Ch 1: The City Analogy | Overall system structure | `registry-main/README.md` |
| Ch 2: Clients and Servers | Server entry point | `registry-main/cmd/registry/main.go` |
| Ch 3: Protocols | JSON schema | `registry-main/internal/validators/schemas/2025-12-11.json` |
| Ch 4: APIs | All endpoints | `registry-main/internal/api/router/v0.go` |

---

## Part 2 — The MCP Registry

| Chapter | Key concept | Source file |
|---------|------------|-------------|
| Ch 5: What Is a Registry? | Data model | `registry-main/pkg/model/types.go` |
| Ch 5: What Is a Registry? | API types | `registry-main/pkg/api/v0/types.go` |
| Ch 6: The Database | Initial schema | `registry-main/internal/database/migrations/001_initial_schema.sql` |
| Ch 6: The Database | All migrations | `registry-main/internal/database/migrations/` (001–013) |
| Ch 6: The Database | Database connection | `registry-main/internal/database/postgres.go` |
| Ch 6: The Database | Migration runner | `registry-main/internal/database/migrate.go` |
| Ch 7: Authentication | JWT manager | `registry-main/internal/auth/jwt.go` |
| Ch 7: Authentication | Block list | `registry-main/internal/auth/blocks.go` |
| Ch 7: Authentication | Auth types | `registry-main/internal/auth/types.go` |
| Ch 8: Routing | All v0 routes | `registry-main/internal/api/router/v0.go` |
| Ch 8: Routing | API server setup | `registry-main/internal/api/server.go` |
| Ch 8: Routing | List servers handler | `registry-main/internal/api/handlers/v0/servers.go` |
| Ch 9: Validation | Main validator | `registry-main/internal/validators/validators.go` |
| Ch 9: Validation | Validation types | `registry-main/internal/validators/validation_types.go` |
| Ch 9: Validation | Latest schema | `registry-main/internal/validators/schemas/2025-12-11.json` |
| Ch 9: Validation | Constants | `registry-main/internal/validators/constants.go` |
| Ch 10: The Publisher | Publish command | `registry-main/cmd/publisher/commands/publish.go` |
| Ch 10: The Publisher | Login command | `registry-main/cmd/publisher/commands/login.go` |
| Ch 10: The Publisher | Validate command | `registry-main/cmd/publisher/commands/validate.go` |
| Ch 10: The Publisher | Publisher CLI entry | `registry-main/cmd/publisher/main.go` |

---

## Part 3 — The AI Agent

| Chapter | Key concept | Source file |
|---------|------------|-------------|
| Ch 11: What Is an AI Agent? | Agent loop | `claw-code-main/rust/crates/runtime/src/conversation.rs` |
| Ch 11: What Is an AI Agent? | Core types | `claw-code-main/rust/crates/runtime/src/lib.rs` |
| Ch 12: Tools | Tool registry | `claw-code-main/rust/crates/tools/src/lib.rs` |
| Ch 12: Tools | Tool snapshot (reference) | `claw-code-main/src/tools.py` |
| Ch 12: Tools | Tool reference data | `claw-code-main/src/reference_data/tools_snapshot.json` |
| Ch 13: Sessions | Session structure | `claw-code-main/rust/crates/runtime/src/session.rs` |
| Ch 13: Sessions | Compaction | `claw-code-main/rust/crates/runtime/src/compact.rs` |
| Ch 13: Sessions | Usage tracking | `claw-code-main/rust/crates/runtime/src/usage.rs` |
| Ch 14: Hooks | Hook reference data | `claw-code-main/src/reference_data/subsystems/hooks.json` |
| Ch 14: Hooks | Hook placeholder | `claw-code-main/src/hooks/__init__.py` |
| Ch 15: Sandboxing | Sandbox config | `claw-code-main/rust/crates/runtime/src/sandbox.rs` |
| Ch 15: Sandboxing | Permissions | `claw-code-main/rust/crates/runtime/src/permissions.rs` |
| Ch 16: MCP Client | Client types | `claw-code-main/rust/crates/runtime/src/mcp_client.rs` |
| Ch 16: MCP Client | MCP utilities | `claw-code-main/rust/crates/runtime/src/mcp.rs` |
| Ch 16: MCP Client | Config types | `claw-code-main/rust/crates/runtime/src/config.rs` |
| Ch 17: Skills | Skills reference data | `claw-code-main/src/reference_data/subsystems/skills.json` |
| Ch 17: Skills | Skills placeholder | `claw-code-main/src/skills/__init__.py` |

---

## Part 4 — Shipping It

| Chapter | Key concept | Source file |
|---------|------------|-------------|
| Ch 18: Docker | ko config | `registry-main/.ko.yaml` |
| Ch 18: Docker | Docker ignore | `registry-main/.ko.dockerignore` |
| Ch 18: Docker | Makefile (dev-compose) | `registry-main/Makefile` |
| Ch 19: Kubernetes | K8s registry deployment | `registry-main/deploy/pkg/k8s/registry.go` |
| Ch 19: Kubernetes | K8s PostgreSQL | `registry-main/deploy/pkg/k8s/postgres.go` |
| Ch 19: Kubernetes | K8s ingress | `registry-main/deploy/pkg/k8s/ingress.go` |
| Ch 19: Kubernetes | K8s monitoring | `registry-main/deploy/pkg/k8s/monitoring.go` |
| Ch 19: Kubernetes | Deploy main | `registry-main/deploy/main.go` |
| Ch 20: CI/CD | CI pipeline | `registry-main/.github/workflows/ci.yml` |
| Ch 20: CI/CD | Staging deploy | `registry-main/.github/workflows/deploy-staging.yml` |
| Ch 20: CI/CD | Production deploy | `registry-main/.github/workflows/deploy-production.yml` |
| Ch 20: CI/CD | Release pipeline | `registry-main/.github/workflows/release.yml` |
| Ch 21: Monitoring | Metrics definitions | `registry-main/internal/telemetry/metrics.go` |
| Ch 21: Monitoring | Metrics tests | `registry-main/internal/telemetry/metrics_test.go` |

---

## Part 5 — AI and the Real World

| Chapter | Key concept | Source file |
|---------|------------|-------------|
| Ch 22: What AI Is | Agent runtime (loop) | `claw-code-main/rust/crates/runtime/src/conversation.rs` |
| Ch 23: MCP Protocol | MCP client types | `claw-code-main/rust/crates/runtime/src/mcp_client.rs` |
| Ch 23: MCP Protocol | MCP schema validation | `registry-main/internal/validators/validators.go` |
| Ch 24: Build MCP Server | Publisher workflow | `registry-main/cmd/publisher/commands/publish.go` |
| Ch 24: Build MCP Server | Server JSON schema | `registry-main/internal/validators/schemas/2025-12-11.json` |

---

## External References

**MCP Registry Live API:** https://registry.modelcontextprotocol.io

**Geoffrey Hinton's Publications:** https://www.cs.toronto.edu/~hinton/pages/publications.html

**MCP Specification:** https://modelcontextprotocol.io

**Go Documentation:** https://go.dev/doc/

**Rust Book:** https://doc.rust-lang.org/book/

**Home Assistant:** https://www.home-assistant.io/

**Ollama (local AI):** https://ollama.ai/

---

## File Naming Convention

In the MCP Registry Go codebase:
- `cmd/` → Entry points (runnable programs)
- `internal/` → Private packages (not intended for external use)
- `pkg/` → Public packages (shared types, usable externally)
- `deploy/` → Infrastructure code
- `.github/workflows/` → CI/CD pipelines

In the claw-code codebase:
- `rust/crates/` → Rust implementation (the performance core)
- `src/` → Python implementation (the porting workspace)
- `src/reference_data/` → Snapshots of the original system's surface area
- `rust/crates/runtime/` → The agent loop, sessions, MCP, sandbox
- `rust/crates/tools/` → Tool definitions
