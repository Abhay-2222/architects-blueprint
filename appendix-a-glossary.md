# Appendix A — Glossary

*Every term used in this book, defined in plain language.*

---

**Agent Loop** — The repeated cycle of an AI agent: receive goal → choose tool → execute tool → read result → decide next step → repeat. See Chapter 11.

**API (Application Programming Interface)** — The front door of a server. A defined set of endpoints that clients can call to interact with a system. See Chapter 4.

**Authentication** — The process of proving who you are. "I am Abhay" + proof. See Chapter 7.

**Authorization** — The process of checking what you are allowed to do. "Abhay can publish, but cannot delete others' servers." Different from authentication. See Chapter 7.

**Backpropagation** — An algorithm that allows neural networks to learn by calculating how much each connection contributed to an error, then adjusting all connections slightly. The foundational discovery of modern AI. (Rumelhart, Hinton, Williams, 1986)

**CI/CD (Continuous Integration/Continuous Deployment)** — Automated pipelines that build, test, and deploy code every time a change is pushed. The assembly line of software. See Chapter 20.

**Client** — Any program that sends requests to a server. Your browser, your phone app, an AI agent. See Chapter 2.

**Container** — A self-contained, isolated package of code and everything it needs to run. Created with Docker. See Chapter 18.

**Context Window** — The maximum amount of text an AI model can "hold in mind" at once. When a conversation exceeds this limit, old messages must be compressed or removed. See Chapter 13.

**Database** — Organized, persistent storage for data. In this book, PostgreSQL. See Chapter 6.

**Deep Learning** — A type of machine learning using neural networks with many layers. Each layer learns increasingly abstract features. See Chapter 22 and the Hinton publications.

**Docker** — A tool for creating, running, and managing containers. See Chapter 18.

**Docker Compose** — A tool for defining and running multiple Docker containers together. See Chapter 18.

**Ed25519** — A modern cryptographic algorithm for creating digital signatures. Used in the MCP Registry's JWT system. See Chapter 7.

**Endpoint** — A specific URL in an API that the client can send requests to. Like a room in a building. See Chapter 4.

**Hook** — A piece of code that runs automatically before or after a specific event (like a tool call). Safety checkpoints in an AI agent. See Chapter 14.

**HTTP (HyperText Transfer Protocol)** — The language of the web. The protocol used for sending requests and receiving responses between clients and servers. See Chapter 3.

**Index (database)** — A data structure that makes database searches faster. Like tabs on a filing cabinet. See Chapter 6.

**Ingress (Kubernetes)** — The gateway that routes external traffic to the right internal service. See Chapter 19.

**JSON (JavaScript Object Notation)** — A human-readable format for structured data. Used everywhere: APIs, databases, configuration files. See Chapter 3.

**JWT (JSON Web Token)** — A signed token that proves identity and permissions. Used like a festival wristband. See Chapter 7.

**Kubernetes (K8s)** — An orchestration system that manages containers at scale. Self-heals crashed services, scales up and down automatically. See Chapter 19.

**Latency** — How long a request takes to complete. One of the Four Golden Signals of monitoring. See Chapter 21.

**MCP (Model Context Protocol)** — An open protocol that defines how AI agents communicate with external tools. The USB-C of AI integrations. See Chapters 23–24.

**MCP Client** — The part of an AI agent that connects to and communicates with MCP servers. See Chapter 16.

**MCP Registry** — The official directory of MCP servers — the App Store for AI tools. See Chapter 5.

**MCP Server** — A program that exposes tools, resources, or prompts to AI agents via the MCP protocol. See Chapters 23–24.

**Migration (database)** — A numbered script that makes a specific, reversible change to the database structure. Allows safe evolution of the database over time. See Chapter 6.

**Middleware** — Code that runs between the router and the handler, performing checks like authentication. See Chapter 8.

**Monitoring** — Continuously measuring a system's health and alerting when something goes wrong. See Chapter 21.

**MVP (Minimum Viable Product)** — The smallest version of a product that tests the core hypothesis. See Chapter 31.

**Neural Network** — A mathematical model loosely inspired by the brain, composed of layers of interconnected numerical parameters (weights). Trained by adjusting weights to reduce errors.

**OpenTelemetry** — An open-source observability framework for collecting metrics, logs, and traces. Used by the MCP Registry. See Chapter 21.

**Permission Mode** — The level of access granted to an AI agent's tools. ReadOnly, WorkspaceWrite, DangerFullAccess. See Chapters 12, 15.

**Pod (Kubernetes)** — The smallest deployable unit in Kubernetes. Usually one container. See Chapter 19.

**PostgreSQL** — A powerful open-source relational database. Used by the MCP Registry. See Chapter 6.

**Protocol** — A set of agreed-upon rules for how two systems communicate. HTTP, JSON, and MCP are all protocols. See Chapter 3.

**Prometheus** — An open-source monitoring system that collects and stores metrics. See Chapter 21.

**Reverse Proxy** — A server that sits in front of other servers and routes requests. Nginx is a common reverse proxy. See Chapters 8, 25.

**Router** — The component that matches incoming requests to the correct handler function. The postal sorting office. See Chapter 8.

**Sandbox** — An isolated environment that restricts what a program can access. The digital playpen for AI agents. See Chapter 15.

**Schema** — A formal definition of what data must look like. Used for validation and documentation. See Chapter 9.

**Server** — Any program that answers requests from clients. The kitchen in the restaurant analogy. See Chapter 2.

**Session** — The complete history of an AI conversation — every message, tool call, and result. The agent's working memory. See Chapter 13.

**Skill** — A named, reusable workflow that an AI agent can invoke with a trigger command. Pre-packaged instructions. See Chapter 17.

**SQL (Structured Query Language)** — The language used to interact with relational databases. See Chapter 6.

**Transport** — How an MCP client connects to an MCP server. Options: stdio, HTTP, SSE, WebSocket. See Chapter 16.

**UUID (Universally Unique Identifier)** — A randomly generated identifier so unique that two independently generated UUIDs will almost certainly differ. See Chapter 6.

**Validation** — Checking that incoming data meets a set of rules before accepting it. The building inspector. See Chapter 9.

**YAML** — A human-readable format for configuration files. Used in Docker Compose, Kubernetes, and CI/CD pipelines.
