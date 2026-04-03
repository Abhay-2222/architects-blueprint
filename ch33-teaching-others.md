# Chapter 33 — Teaching Others: How to Use This Book in a Classroom

*Part 7: Hands Applied — Build Something Real*

---

## The Analogy

Richard Feynman — the Nobel Prize-winning physicist — had a rule: if you cannot explain something simply, you do not understand it yet.

He developed what is now called the **Feynman Technique**:
1. Explain the concept as if to a child
2. Notice where you stumble or become vague
3. Go back to the source — the stumbles reveal the gaps
4. Explain again, simpler

Teaching is not the end of learning. It is the deepest form of it.

When you teach something from this book, you will discover what you actually understand and what you only thought you understood. Both discoveries are valuable.

---

## How This Book Maps to Lessons

Each chapter is designed to be one teaching session. Below is a suggested curriculum for different contexts.

### For a One-Week Intensive (Summer Camp / Workshop)

**Day 1 — Systems Thinking:**
- Chapters 1–4 (The City Analogy through APIs)
- Project: Map a familiar system (school, restaurant, home) using the five components
- No computers required

**Day 2 — Real Backend:**
- Chapters 5–7 (Registry, Database, Authentication)
- Project: Design a database for their own registry idea
- Light coding: write SQL `CREATE TABLE` statements

**Day 3 — AI Systems:**
- Chapters 11–13 (Agent loop, Tools, Sessions)
- Project: Manually run the agent loop for a 3-step task
- Activity: Write tool descriptions; test with classmates as "AI"

**Day 4 — Deployment and Monitoring:**
- Chapters 18–21 (Docker, Kubernetes, CI/CD, Monitoring)
- Project: Draw the deployment architecture for a real service they use
- Activity: Design a monitoring dashboard for a system they choose

**Day 5 — Build Day:**
- Chapter 29 (First Architecture) + Chapter 32 (Product Designer's Chapter)
- Project: Each student presents their system design (diagram + brief)
- No code required — architecture and design are the deliverable

### For a Semester Course (16 weeks)

**Weeks 1–4:** Part 1 (Systems) + Part 2 (Registry)
- Deep dives into SQL, HTTP, REST APIs
- Build: a simple REST API for a personal registry

**Weeks 5–8:** Part 3 (AI Agent)
- Build: a simple tool-using agent
- Explore: connect to a real MCP server

**Weeks 9–12:** Part 4 (Deployment)
- Build: containerize and deploy a service
- Explore: set up a monitoring dashboard

**Weeks 13–16:** Parts 5–7 (AI + Product + Build)
- Final project: each student presents a complete system design
- Includes: problem statement, architecture diagram, MVP spec, at least one MCP tool definition

---

## Assessment Ideas

**Assessment 1: The System Map (No code required)**
Given a product (Spotify, Uber, Instagram), draw the system diagram. Identify: components, connections, bottleneck, failure modes, interfaces. No right answer — assessment is on the quality of reasoning.

**Assessment 2: The Architecture Review (Written)**
Student writes a one-page critique of an architectural decision. Why was this decision made? What are its trade-offs? What would you do differently and why?

**Assessment 3: The Tool Design (Design)**
Design an MCP server for a real-world service of the student's choice. Write: tool names, descriptions (for AI to read), input/output schemas, and one sample conversation between a user and an AI using this server.

**Assessment 4: The Product Brief (Strategy)**
Write a complete one-page product brief for an original idea. Must include: problem, solution, target user, success metrics, MVP definition, and not-in-scope list.

**Assessment 5: The Final Build (Project)**
Build the MVP of a project the student defined in Assessment 4. Assessment is on: does it solve the stated problem? Is the architecture sound? Can the student explain every decision?

---

## Running the Hands-On Sections in Groups

The "Now I Do This" sections are designed for individual work. In a classroom, adapt them:

**Solo → Pair:** Two students work through the exercise together. One is the "designer" (decides what to build), one is the "engineer" (decides how to build it). Then switch.

**Solo → Group critique:** One student presents their design. Other students apply the five questions from Chapter 27 (components, connections, bottleneck, failure modes, interfaces) as reviewers.

**Solo → Live demo:** A teacher runs through an exercise on the whiteboard in real time, making decisions out loud: "Now I add the index here because I want fast lookups on this column. I do this because without it, a search through a million records would check every row one by one — which takes seconds instead of milliseconds."

The "Now I do this" format — with its "I do this because..." explanations — is specifically designed to be spoken aloud. It models expert thinking. When you teach, talk through your reasons.

---

## Adapting for Different Ages

**Ages 12–14:**
- Focus on Parts 1, 5, 6 (systems, AI, home lab)
- Skip deep technical details; emphasize analogies
- Use the restaurant, city, and festival analogies heavily
- Project: design a smart bedroom system (no code)

**Ages 15–17:**
- Full book, but emphasize Parts 1, 2, 5, 7
- Light coding is appropriate (SQL, JSON, Python)
- Project: build a simple MCP server and connect it to a local AI

**Ages 18+ / Adults:**
- Full book
- Emphasize real-world connections (Parts 2, 4, 7)
- Project: complete a real deployment on a Raspberry Pi or cloud service

**Non-technical adults (designers, managers, executives):**
- Parts 1, 5, 6, 7 (chapters 1–4, 22–24, 27–32)
- Focus on the analogies and product thinking
- Skip the code examples; focus on diagrams and decision frameworks
- Assessment: product brief + system diagram + stakeholder presentation

---

## The Most Important Thing to Teach

Above all the content — above APIs, Docker, JWT, MCP — there is one thing that matters most:

**The confidence to try.**

Every expert built their first thing badly. Every architect drew their first diagram wrong. Every engineer wrote their first code that didn't work. The difference between an architect and someone who wishes they were one is not talent. It is the willingness to draw the box, even knowing it might be wrong, and to revise it when it is.

This book ends here. Your system does not.

---

## The Takeaway

Teaching is the deepest form of learning. This book is designed to be teachable: each chapter is one session, each hands-on section is one group exercise, each part is one unit. The most important skill to teach is not architecture or AI — it is the confidence to attempt something new, fail gracefully, and iterate.

---

*→ Continue to [Appendix A — Glossary](./appendix-a-glossary.md)*
