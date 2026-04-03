# Chapter 11 — What Is an AI Agent?

*Part 3: The AI Agent — How an AI Coding Assistant Actually Works*

---

## The Analogy

You hire an intern for the summer. They are smart, eager, and fast. You say:

> "I need you to prepare a report on our top 5 customers. Their purchase histories are in the shared drive. Check last year's data, calculate their totals, find their email addresses in the contacts sheet, and write up a summary."

The intern doesn't do all of this in one second. They:
1. Open the shared drive
2. Find the purchase history files
3. Read through them
4. Do the calculations
5. Switch to the contacts sheet
6. Look up the emails
7. Open a document
8. Write the summary

Each step uses a different "tool" — the file system, a calculator, a spreadsheet, a word processor. The intern picks the right tool for each step, uses it, reads the result, and decides what to do next.

**An AI agent is this intern** — but it never sleeps, works in milliseconds, and its tools are software programs.

---

## The Concept

An **AI agent** is a program that:
1. Receives a goal from a human
2. Breaks the goal into steps
3. Uses tools to complete each step
4. Reads the results
5. Decides what to do next
6. Repeats until the goal is complete (or until it's stuck)

This cycle — think, act, observe, repeat — is called the **agent loop**. It is not magic. It is a `while` loop in code.

Here is the agent loop in its simplest form:

```
WHILE goal not complete:
    1. Look at the current state (what have I done so far?)
    2. Decide what to do next (which tool? with what input?)
    3. Execute the tool
    4. Observe the result
    5. Update my understanding of the situation
    6. Check: am I done?
```

That's it. The "intelligence" is in step 2 — deciding what to do next. Everything else is machinery.

---

## System Diagram

```
THE AGENT LOOP

User: "Find all Python files and count lines of code"
                │
                ▼
┌───────────────────────────────────────────────┐
│  ITERATION 1                                  │
│  AI sees: goal + no prior tool results        │
│  Decides: use glob_search("**/*.py")          │
│  Tool runs → ["main.py", "utils.py", ...]     │
└──────────────────────┬────────────────────────┘
                       │ result added to history
                       ▼
┌───────────────────────────────────────────────┐
│  ITERATION 2                                  │
│  AI sees: goal + file list from iteration 1   │
│  Decides: use bash("wc -l *.py")              │
│  Tool runs → "main.py: 142\nutils.py: 87\n..." │
└──────────────────────┬────────────────────────┘
                       │ result added to history
                       ▼
┌───────────────────────────────────────────────┐
│  ITERATION 3                                  │
│  AI sees: goal + file list + line counts      │
│  Decides: I have all the info → respond       │
│  Sends: "Found 3 Python files: 312 lines total"│
│  MessageStop → loop exits                     │
└───────────────────────────────────────────────┘
```

---

## The Real Code

In `claw-code-main/rust/crates/runtime/src/conversation.rs`, the core agent loop is called `run_turn`:

```rust
pub fn run_turn(
    &mut self,
    user_input: impl Into<String>,
) -> Result<TurnSummary, RuntimeError> {

    // Add the user's message to the conversation history
    self.session.messages.push(
        ConversationMessage::user_text(user_input.into())
    );

    loop {
        // Step 1: Send the full conversation to the AI model
        // The AI reads all previous messages and tool results
        let events = self.api_client.stream(self.build_request())?;

        // Step 2: Process what the AI decided to do
        for event in events {
            match event {
                // The AI wants to use a tool
                AssistantEvent::ToolUse { name, input, .. } => {
                    // Step 3: Execute the tool
                    let result = self.tool_executor.execute(&name, &input);

                    // Step 4: Add the result back to the conversation
                    self.session.messages.push(
                        ConversationMessage::tool_result(result)
                    );
                }

                // The AI is done — it sent a final text message
                AssistantEvent::MessageStop => {
                    return Ok(summary); // Exit the loop
                }
            }
        }
        // Loop again — the AI might need more tools
    }
}
```

Notice the structure:
- It is literally a `loop`
- The AI model is called repeatedly, not once
- Each time, it sees *all previous messages and tool results*
- It continues until it sends `MessageStop` — saying "I'm done"

This is the heartbeat of every AI agent system in existence.

---

## 🔬 Lab Activity — Build an Agent Loop in Python

**What you'll build:** A working Python agent loop that uses three tools (list files, count lines, respond), runs multiple iterations, and prints its reasoning at each step — just like `claw-code-main/rust/crates/runtime/src/conversation.rs`.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch11-agent
cd C:\labs\ch11-agent
```

---

**2. Create some sample files for the agent to work with.**

```powershell
notepad notes.txt
```
Paste any text you like, then save. Then:
```powershell
notepad report.py
```
Paste:
```python
# This is a sample Python report
x = 42
print(x)
```
Save and close.

---

**3. Create the file `agent.py`.**

```powershell
notepad agent.py
```
Paste:
```python
import os
import glob

# ---- TOOLS (the agent's hands) ----

def list_files(folder="."):
    """List files in a folder."""
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    return {"files": files, "count": len(files)}

def count_lines(filename):
    """Count lines in a file."""
    try:
        with open(filename) as f:
            lines = f.readlines()
        return {"filename": filename, "lines": len(lines)}
    except FileNotFoundError:
        return {"error": f"File '{filename}' not found"}

def respond(message):
    """Send final answer to user."""
    return {"done": True, "answer": message}

TOOLS = {
    "list_files": list_files,
    "count_lines": count_lines,
    "respond": respond,
}

# ---- SIMULATED AI DECISION MAKING ----
# In a real agent, this is the language model.
# Here, we hard-code the decisions to demonstrate the loop structure.

def ai_decide(goal, history):
    """Simulate the AI deciding what to do next."""
    step = len(history)

    if step == 0:
        # First iteration: start by listing files
        return ("list_files", {"folder": "."})
    elif step == 1:
        # Second iteration: count lines in first .py file found
        result = history[0]["result"]
        py_files = [f for f in result.get("files", []) if f.endswith(".py")]
        if py_files:
            return ("count_lines", {"filename": py_files[0]})
        else:
            return ("respond", {"message": "No Python files found in this folder."})
    elif step == 2:
        # Third iteration: we have all info — respond
        file_result = history[0]["result"]
        line_result = history[1]["result"]
        total_files = file_result.get("count", 0)
        filename = line_result.get("filename", "unknown")
        lines = line_result.get("lines", "unknown")
        return ("respond", {
            "message": (
                f"Found {total_files} files in the folder. "
                f"The Python file '{filename}' has {lines} lines of code."
            )
        })
    else:
        return ("respond", {"message": "Done."})

# ---- AGENT LOOP ----

def run_agent(goal):
    print(f"Goal: {goal}\n")
    history = []
    iteration = 0

    while True:
        iteration += 1
        print(f"{'='*50}")
        print(f"Iteration {iteration}")
        print(f"History so far: {len(history)} tool result(s)")

        # AI decides what to do
        tool_name, tool_input = ai_decide(goal, history)
        print(f"AI decides: use '{tool_name}' with {tool_input}")

        # Execute the tool
        tool_fn = TOOLS[tool_name]
        result = tool_fn(**tool_input)
        print(f"Tool result: {result}")

        # Add to history
        history.append({"tool": tool_name, "input": tool_input, "result": result})

        # Check if done
        if result.get("done"):
            print(f"\nFINAL ANSWER: {result['answer']}")
            print(f"\nCompleted in {iteration} iterations.")
            break

        if iteration > 10:
            print("Safety stop: too many iterations.")
            break

run_agent("Find files in this folder and count lines in any Python file")
```

**4. Run it.**

```powershell
python agent.py
```
✅ You should see:
```
Goal: Find files in this folder and count lines in any Python file

==================================================
Iteration 1
History so far: 0 tool result(s)
AI decides: use 'list_files' with {'folder': '.'}
Tool result: {'files': ['agent.py', 'notes.txt', 'report.py'], 'count': 3}
==================================================
Iteration 2
History so far: 1 tool result(s)
AI decides: use 'count_lines' with {'filename': 'agent.py'}
Tool result: {'filename': 'agent.py', 'lines': 78}
==================================================
Iteration 3
History so far: 2 tool result(s)
AI decides: use 'respond' with {...}
Tool result: {'done': True, 'answer': 'Found 3 files...'}

FINAL ANSWER: Found 3 files in the folder. The Python file 'agent.py' has 78 lines of code.

Completed in 3 iterations.
```

**5. Test the error path.**

Delete `report.py` and run again to see what happens when no `.py` file is found:
```powershell
del report.py
python agent.py
```
✅ The agent adapts: on iteration 2 it finds no `.py` files and goes straight to `respond` with "No Python files found."

**What you just built:** A working 3-iteration agent loop with tool dispatch, history tracking, and conditional decision-making — the same pattern as `run_turn` in `claw-code-main/rust/crates/runtime/src/conversation.rs`.

---

> **🌍 Real World**
> Google's Gemini, OpenAI's GPT-4o, and Anthropic's Claude all use the same agent loop pattern you just built. When you ask GitHub Copilot to "fix the bug in this file," Copilot runs a multi-iteration loop: read the file, analyze the error, write the fix, verify the syntax, respond. AutoGPT (2023) was the first popular open-source agent that ran this loop autonomously — it shocked the world when it started using Google Search, writing files, and executing code without any human in the loop. The loop itself is decades old. What changed in 2023 is that the AI inside the loop became capable enough to make useful decisions.

---

## Research Spotlight

> **"Deep learning for AI"** — Bengio, Y., LeCun, Y., & Hinton, G. (2021). *Communications of the ACM, 64*(7), 58–65.

This review paper, written by three of the most influential figures in AI, describes how deep learning enables systems to learn complex behaviors from examples — without being explicitly programmed. The "deciding what to do next" step in an agent (step 2 in our loop) is powered by a large language model trained on billions of examples of human reasoning. The model is not following a script — it has learned patterns of thought from the collected writing of humanity.

The paper is accessible through Hinton's archive at: https://www.cs.toronto.edu/~hinton/pages/publications.html

---

## The Takeaway

An AI agent is a loop that thinks, acts, observes, and repeats. The "thinking" is a language model. The "acting" is tool use. The "observing" is reading the tool's output. There is no magic — only a well-engineered cycle, repeated until the job is done.

---

## The Connection

The agent can loop. But what does it loop with? What tools does it have? In Chapter 12, we open the toolbox — and see how tools are defined, registered, and executed in the claw-code agent system.

---

*→ Continue to [Chapter 12 — Tools: The Agent's Hands](./ch12-tools.md)*
