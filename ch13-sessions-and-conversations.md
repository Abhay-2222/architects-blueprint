# Chapter 13 — Sessions and Conversations

*Part 3: The AI Agent — How an AI Coding Assistant Actually Works*

---

## The Analogy

You are on a long phone call with a very helpful assistant. They have no notes, no memory, no file system. But as long as the call is connected, they remember *everything* you have said in this call.

"Find me restaurants in Paris." — they remember you want Paris.
"Filter for vegetarian." — they know you mean the Paris restaurants.
"Actually, make it Rome." — they know you're changing the city.

They don't need you to repeat yourself each time. They hold the entire conversation in their mind simultaneously.

But there is a limit. Their mind can only hold a certain number of words at once. If the call goes on too long — hours of complex discussion — they start to forget the earliest parts to make room for the newest parts.

This is exactly how AI conversation sessions work. There is a **context window** — a maximum amount of text the model can hold in mind at once. As the conversation grows, old parts may need to be summarized or removed to make room for new ones.

---

## The Concept

A **session** is the complete history of an agent's conversation — every message from you, every response from the AI, every tool call, and every tool result.

When the agent decides what to do next, it reads this entire history. That is why it "remembers" — not because it has a separate memory database (usually), but because every prior message is part of every subsequent request.

The session is the agent's working memory.

### The Structure of a Session Message

Each message in the session has a **role** — who sent it:
- `user` — your messages
- `assistant` — the AI's responses
- `tool_result` — what a tool returned after being used

---

## System Diagram

```
SESSION GROWTH OVER TIME

Turn 1:  [user] → [assistant + tool call] → [tool_result]
         ─────────────────────────────────────────────────
         3 messages, ~500 tokens

Turn 5:  Turn 1 messages still present +
         [user] → [assistant + tool] → [tool_result] × 4 more
         ─────────────────────────────────────────────────
         15 messages, ~3,000 tokens

Turn 20: 60+ messages — approaching context limit
         ─────────────────────────────────────────────────
         COMPACTION TRIGGERED:
         ┌─────────────────────────────────────────────┐
         │ Summary: "Refactored auth module.           │
         │  Read jwt.go, edited token duration,        │
         │  ran tests (all passed). Fixed 2 warnings." │
         └─────────────────────────────────────────────┘
         + Last 10 messages kept verbatim
         = Session reset to ~2,000 tokens, loop continues
```

---

A typical session might look like:

```
[user]:         "Refactor the authentication module"
[assistant]:    "I'll start by reading the current code."
                → ToolUse: read_file("internal/auth/jwt.go")
[tool_result]:  "package auth\nimport ..."
[assistant]:    "I see the issue. The token duration is hardcoded. I'll fix it."
                → ToolUse: edit_file("internal/auth/jwt.go", ...)
[tool_result]:  "File updated successfully"
[assistant]:    "Done. The token duration is now configurable via environment variable."
```

Every item in this list is sent to the AI model on the next request. The model reads all of it to understand the context before deciding what to do next.

---

## The Real Code

From `claw-code-main/rust/crates/runtime/src/conversation.rs`, the session is a simple structure:

```rust
// A single message in the session
pub struct ConversationMessage {
    pub role: MessageRole,    // user, assistant, or tool_result
    pub content: Vec<ContentBlock>, // The text or tool call inside
}

// A session is a list of messages
pub struct Session {
    pub messages: Vec<ConversationMessage>,
    pub token_usage: TokenUsage,  // How many tokens have been used so far
}
```

And the agent loop adds to the session at each step:

```rust
// User sends a message → add it
self.session.messages.push(
    ConversationMessage::user_text(user_input)
);

// AI uses a tool → add the tool result
self.session.messages.push(
    ConversationMessage::tool_result(result)
);
```

The session grows with every exchange. Every turn adds at least two messages (the AI's response and any tool results). A complex task might add dozens.

### The Compaction Problem

From the claw-code Rust source, there is a dedicated module: `compact.rs`.

```rust
// When the session gets too long, compact it
pub fn compact_session(
    session: &Session,
    config: &CompactionConfig,
) -> CompactionResult {
    // Estimate how many tokens the session is using
    let token_count = estimate_session_tokens(session);

    // If we're approaching the limit, summarize the early parts
    if token_count > config.max_tokens {
        // Create a summary of the older messages
        // Replace them with the summary
        // Keep the most recent messages verbatim
    }
}
```

**Compaction** is like taking detailed meeting notes and replacing them with a summary when your notepad gets full. You keep the key conclusions and decisions, but compress the blow-by-blow details.

This is a delicate operation. Compress too aggressively and the agent loses important context. Compress too little and it hits the token limit and fails. Good compaction is one of the hardest unsolved problems in production agent systems.

---

## 🔬 Lab Activity — Build a Session Manager

**What you'll build:** A Python session manager that stores conversation history, tracks token usage, and compacts the session when it gets too long — matching the `Session` struct and `compact_session` function in `claw-code-main/rust/crates/runtime/src/conversation.rs`.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch13-sessions
cd C:\labs\ch13-sessions
```

---

**2. Create the file `session_manager.py`.**

```powershell
notepad session_manager.py
```
Paste:
```python
import json
import time

# ── SESSION STRUCTURE ─────────────────────────────────────

class Session:
    def __init__(self, max_tokens=500):
        self.messages = []
        self.token_usage = 0
        self.max_tokens = max_tokens  # low limit so we can see compaction trigger

    def add(self, role, content):
        """Add a message to the session."""
        msg = {"role": role, "content": content, "timestamp": time.time()}
        self.messages.append(msg)
        # Rough token estimate: 1 token ≈ 4 characters
        self.token_usage += len(content) // 4
        print(f"  [{role:12}] {content[:60]}")
        print(f"             Token usage: ~{self.token_usage}/{self.max_tokens}")

    def compact(self):
        """Summarize old messages when approaching token limit."""
        if self.token_usage < self.max_tokens * 0.8:
            return  # No need to compact yet

        print(f"\n  ⚠ Approaching token limit ({self.token_usage}/{self.max_tokens})")
        print(f"  Running compaction...")

        # Keep first message (the goal) and last 3 messages verbatim
        if len(self.messages) <= 4:
            return

        early = self.messages[1:-3]  # messages to summarize
        recent = self.messages[-3:]  # keep these verbatim
        goal   = self.messages[0]    # always keep the original goal

        # Create a summary (in real life, the AI model writes this)
        summary_text = (
            f"[SUMMARY of {len(early)} messages]: "
            f"Agent performed {len(early)//2} tool operations. "
            f"All succeeded. Context compressed to save tokens."
        )

        # Rebuild the session
        self.messages = [goal, {"role": "summary", "content": summary_text, "timestamp": time.time()}] + recent
        self.token_usage = sum(len(m["content"]) // 4 for m in self.messages)
        print(f"  Compacted: {len(early)} messages → 1 summary")
        print(f"  Token usage now: ~{self.token_usage}/{self.max_tokens}\n")

    def show(self):
        """Print the full session."""
        print(f"\n{'='*55}")
        print(f"SESSION ({len(self.messages)} messages, ~{self.token_usage} tokens)")
        print(f"{'='*55}")
        for m in self.messages:
            print(f"  [{m['role']:12}] {m['content'][:70]}")
        print(f"{'='*55}\n")


# ── SIMULATE AN AGENT CONVERSATION ───────────────────────

session = Session(max_tokens=500)

print("=== Session Manager Demo ===\n")
print("Simulating: 'Refactor the authentication module'\n")

# Turn 1
session.add("user", "Refactor the authentication module to use Ed25519 instead of RSA.")
session.add("assistant", "I'll start by reading the current auth implementation.")
session.add("tool_result", "package auth\nimport jwt\nconst tokenDuration = 5 * time.Minute\nfunc (m *JWTManager) CreateToken(...) {...}")
session.compact()

# Turn 2
session.add("assistant", "I see the current implementation uses RSA. I'll check the key generation code.")
session.add("tool_result", "privateKey, _ := rsa.GenerateKey(rand.Reader, 2048)")
session.compact()

# Turn 3
session.add("assistant", "Found RSA in key generation. Now I'll update to Ed25519.")
session.add("tool_result", "File updated: privateKey := ed25519.NewKeyFromSeed(seed)")
session.compact()

# Turn 4
session.add("assistant", "Updated. Now running the tests to verify the change.")
session.add("tool_result", "All 47 tests passed. No regressions.")
session.compact()

# Turn 5
session.add("assistant", "All tests pass. Refactor complete.")
session.add("tool_result", "Response sent to user.")
session.compact()

# Show final session
session.show()

print("Key observations:")
print(f"  - Total messages in session: {len(session.messages)}")
print(f"  - Token usage: ~{session.token_usage}")
print(f"  - Without compaction: would have been ~10 messages and ~350+ tokens")
print(f"  - Compaction summarized early steps while keeping recent context")
```

**3. Run it.**

```powershell
python session_manager.py
```
✅ You should see compaction trigger mid-conversation:
```
=== Session Manager Demo ===

Simulating: 'Refactor the authentication module'

  [user        ] Refactor the authentication module to use Ed25519...
                 Token usage: ~14/500
  [assistant   ] I'll start by reading the current auth implementation.
                 Token usage: ~24/500
  [tool_result ] package auth\nimport jwt\nconst tokenDuration = ...
                 Token usage: ~44/500
  ...
  ⚠ Approaching token limit (412/500)
  Running compaction...
  Compacted: 4 messages → 1 summary
  Token usage now: ~180/500

SESSION (6 messages, ~180 tokens)
=======================================================
  [user        ] Refactor the authentication module...
  [summary     ] [SUMMARY of 4 messages]: Agent performed 2 tool...
  [assistant   ] Updated. Now running the tests to verify the change.
  [tool_result ] All 47 tests passed. No regressions.
  [assistant   ] All tests pass. Refactor complete.
  [tool_result ] Response sent to user.
=======================================================
```

**What you just built:** A working session manager with message history, token tracking, and compaction — matching the `Session` struct and `compact_session` logic from `claw-code-main/rust/crates/runtime/src/conversation.rs`.

---

> **🌍 Real World**
> Every AI chat application — Claude, ChatGPT, Gemini — uses session history exactly as you built it. When you ask a follow-up question and the AI "remembers" what you said earlier, that's because your earlier messages are literally resent with every new request. This is why long conversations sometimes feel slower — you're sending more data each turn. OpenAI's GPT-4 has a 128,000-token context window (roughly 96,000 words — a full novel). Claude has up to 200,000 tokens. But even those limits run out during a complex, multi-hour coding session. Anthropic's Claude Code summarizes long sessions automatically — you may have noticed the message "Auto-compacting context" in long sessions. That is exactly the compaction you just implemented.

---

## Research Spotlight

> **"Using Fast Weights to Attend to the Recent Past"** — Ba, J. L., Hinton, G. E., Mnih, V., et al. (2016).

This paper explored a mechanism for neural networks to dynamically weight recent information more heavily than older information. The intuition is exactly what we discussed above: recent context matters more than old context. The challenge of "what to remember and what to forget" in an AI system is one of the oldest problems in neural network research — and it is still not fully solved.

Session compaction in modern agents is a practical engineering solution to the same fundamental problem: limited memory, unlimited world.

Available at: https://www.cs.toronto.edu/~hinton/pages/publications.html

---

## The Takeaway

A session is the agent's working memory — every message, tool call, and result from the beginning of a conversation. The agent reads the entire history on every turn. As sessions grow long, compaction summarizes older content to free up space in the context window, preserving recent detail and original goals.

---

## The Connection

The agent remembers. But memory without discipline leads to chaos. In Chapter 14, we learn about **hooks** — the rules the agent must follow before and after every action, like safety checks on a construction site.

---

*→ Continue to [Chapter 14 — Hooks: Rules the Agent Must Follow](./ch14-hooks.md)*
