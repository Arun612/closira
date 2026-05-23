# Closira AI Agent — Full Explanation Guide

> This document explains the **entire project** in plain language so you can confidently walk through it in your video and answer any evaluator questions. Read this before recording.

---

## What Is This Project?

You built an **AI-powered customer support agent** for a fictional aesthetics clinic called **Bloom Aesthetics Clinic**. It simulates what Closira's real product does — handle inbound customer conversations using AI, powered by business-specific SOPs.

The agent runs as a **Python CLI** (command-line interface). A customer types messages, and the AI responds — answering FAQs, qualifying leads, detecting when to escalate to a human, and summarizing the conversation at the end.

---

## The 4 Stages (How the Conversation Flows)

The conversation moves through **four stages** in order:

### Stage 1: FAQ Answering
- **What happens:** The customer asks questions (prices, hours, services, etc.)
- **How it works:** The AI reads the SOP data and answers ONLY from what's in there
- **Key rule:** If the answer isn't in the SOP, the AI does NOT make it up — it escalates
- **When it ends:** When the customer signals they're done ("that's all", "thanks", etc.) OR after 5 FAQ turns

### Stage 2: Lead Qualification
- **What happens:** The AI asks 3 structured questions, one at a time:
  1. "What type of business or clinic are you associated with?"
  2. "How large is your team?"
  3. "What tools do you currently use for customer communication?"
- **How it works:** Each answer is stored in `session.lead_data`
- **When it ends:** After all 3 questions are answered → auto-moves to summary

### Stage 3: Escalation Detection
- **What happens:** At ANY point during the conversation, the system checks if it should hand off to a human
- **This is NOT a sequential stage** — it's a layer that runs on every message
- **Two layers of detection:**
  - **Layer 1 (Pre-API):** Keyword matching — catches "speak to a human", "complaint", "ridiculous", etc. This is fast and costs zero API tokens
  - **Layer 2 (Post-API):** The AI itself returns `"escalate": true` in its JSON response when it detects out-of-scope questions, medical queries, low confidence, etc.

### Stage 4: Conversation Summary
- **What happens:** When the session ends, the AI generates a structured summary
- **Format:** Customer intent, details collected, SOP gaps, whether escalation happened, and recommended next action
- **When it triggers:** When the user types "exit"/"quit"/"bye", or after qualification is complete

---

## Project Files — What Each File Does

### `main.py` — The Entry Point
This is where everything starts. It:
- Loads the SOP data from `sop.json`
- Creates a new session
- Runs the main conversation loop (while True)
- For every user message:
  1. Checks guardrails (prompt injection detection)
  2. Checks for exit commands
  3. Runs Layer 1 keyword escalation
  4. Routes to the correct stage (FAQ, Qualify, or Summary)
- Saves the session log when the conversation ends

**Key function: `should_transition_to_qualify()`** — Decides when to move from FAQ to Lead Qualification. It checks for farewell signals like "that's all" or "thanks", and has a fallback of 5 turns max.

### `agent/stages.py` — The Brain
This is where the actual AI calls happen. It:
- Manages the **Groq API client** (lazy initialization — only created when first needed)
- Contains `call_llm()` — the core function that:
  - Sends the system prompt + conversation history to the API
  - Uses **retry with exponential backoff** (3 attempts)
  - Returns a parsed JSON response, or a fallback response if everything fails
- Contains stage-specific handlers:
  - `handle_faq()` — Answers questions, tracks SOP gaps, forces escalation on low confidence
  - `handle_qualify()` — Asks qualification questions one by one, stores answers
  - `handle_summary()` — Generates the structured end-of-session summary

**Key design choice:** The API is called with `response_format={"type": "json_object"}` which forces the model to return valid JSON. This makes escalation detection a simple field check (`if parsed["escalate"]`) instead of fragile text parsing.

### `agent/prompts.py` — The System Prompts
Contains all the prompt text that tells the AI how to behave:
- **`BASE_PROMPT`** — Shared across all stages. Defines the persona ("Bloom"), knowledge boundaries, and the mandatory JSON output schema
- **Stage-specific additions** — Appended to the base prompt depending on the current stage:
  - FAQ: "Answer from SOP only, flag gaps"
  - Qualify: "Ask one question at a time"
  - Summary: "Generate structured summary in this exact format"

**Key design choice:** The entire `sop.json` is injected into the system prompt as a string. This means the AI can ONLY answer from what's physically in the prompt — no retrieval errors, no RAG complexity.

### `agent/escalation.py` — Escalation Detection
Handles the two-layer escalation system:
- **`check_explicit_escalation()`** — Layer 1. Scans the user message for keywords like "speak to a human", "complaint", "ridiculous", "lawsuit", etc. Runs BEFORE any API call
- **`handle_escalation()`** — Logs the escalation event with timestamp, trigger type, reason, and customer message. Returns a professional handoff message

### `agent/guardrails.py` — Security
Protects against prompt injection attacks:
- **14+ regex patterns** detect attempts like "ignore previous instructions", "act as if you are", "jailbreak", "DAN mode", `[system]` tags, etc.
- **Input sanitization** strips control characters and collapses whitespace
- **`check_and_sanitize()`** runs both checks and returns `(is_safe, clean_message)`

If injection is detected: the AI does NOT call the API. It returns a generic deflection message and logs the event.

### `agent/session.py` — State Management
Tracks everything about the conversation:
- `history` — Full message history (used for API context)
- `lead_data` — Collected qualification answers
- `escalation_log` — All escalation events with timestamps
- `sop_gaps` — Questions the AI couldn't answer from the SOP
- `unanswered_count` — Counter for SOP gaps (>2 forces escalation, matching the SOP's own rule)
- `save_log()` — Dumps everything to a timestamped JSON file in `logs/`

### `sop.json` — The SOP Data
This is the AI's **only source of truth**. Contains:
- 8 services with pricing, duration, and treatment details
- Opening hours (per day)
- Booking policy (cancellation fees, deposits, patch test requirements)
- 6 pre-approved FAQ answers
- 7 escalation rules
- Privacy rules (staff names and address not shared via AI)

### `prompt_design.md` — Design Reasoning
A detailed document explaining WHY every design decision was made. Covers:
- Why structured JSON output instead of free text
- Why SOP is injected verbatim instead of using RAG
- The 5 layers of hallucination prevention
- Why binary confidence (high/low) instead of a float
- Tone and persona choices for SMB context
- Known limitations and trade-offs

---

## Key Design Decisions (What to Explain in Your Video)

### 1. "Why structured JSON output?"
> Every API response is a JSON object with fields: `response`, `confidence`, `escalate`, `escalate_reason`, `sop_gap`. This means escalation detection is a simple `if parsed["escalate"]` check — not fragile regex on free text. It's deterministic and testable.

### 2. "How do you prevent hallucination?"
> Five layers:
> 1. **Instruction-level** — System prompt has explicit "NEVER invent" prohibitions
> 2. **Escalation as failure path** — Instead of guessing, the model can say "I don't know" via the `escalate` field
> 3. **SOP as complete context** — The entire SOP is in the prompt; the model can't reference anything outside it
> 4. **Gap counter** — After 2 unanswered questions, the system forces escalation (matching the SOP's own rule)
> 5. **Pre-approved FAQs** — The SOP has verbatim answers the model uses directly

### 3. "Why two-layer escalation?"
> Layer 1 (keywords) is fast, free (no API tokens), and catches obvious cases like "speak to a human" or "this is ridiculous". Layer 2 (model judgment) catches subtle cases like medical questions or out-of-scope queries that need AI reasoning. Layer 1 runs first — if it triggers, the API is never called.

### 4. "Why Groq instead of OpenAI/Claude?"
> The assignment says OpenAI or Claude, but the architecture is API-agnostic. Groq is used as a free alternative running LLaMA 3.3 70B. Switching to OpenAI requires changing only the client initialization in `stages.py` — all prompt logic, stage routing, and escalation detection stay identical.

### 5. "Why inject the full SOP instead of using RAG?"
> The SOP is small (~1000 tokens). RAG would add complexity (embeddings, vector DB, retrieval failures) with zero benefit at this scale. For a 100+ page SOP, RAG would make sense — but for this size, direct injection is simpler and more reliable.

### 6. "Why low temperature (0.3)?"
> This is a factual, grounded task — not a creative one. Lower temperature means more deterministic responses, reducing the chance of the model improvising answers outside the SOP.

---

## Reliability Features (What Makes This Production-Grade)

| Feature | Why It Matters |
|---|---|
| **Retry with exponential backoff** | If the API is temporarily down, the system retries 3 times with increasing delays instead of crashing |
| **Graceful fallback** | If all retries fail, the customer sees a professional handoff message — never a stack trace |
| **History windowing** | Only last 20 messages sent to the API — prevents context window overflow and reduces token costs |
| **Lazy client init** | The Groq client is only created on the first API call, after the API key has been validated |
| **Prompt injection guard** | 14+ regex patterns block common attacks before any API call is made |
| **Input sanitization** | Control characters stripped, whitespace collapsed on every input |
| **Timestamped logs** | Every session saved with full history, escalation events, and lead data |

---

## How to Run a Demo (for Your Video)

```bash
# 1. Make sure you're in the project directory
cd closira-agent-v2

# 2. Make sure your .env file has the Groq API key
# GROQ_API_KEY=your_key_here

# 3. Run the agent
python main.py
```

### Demo Script — Show These Scenarios:

1. **Ask an in-SOP question:** "What are your Botox prices?" → Shows FAQ answering
2. **Ask an out-of-scope question:** "Can I get laser hair removal?" → Shows escalation
3. **Express frustration:** "This is ridiculous, I want to complain" → Shows sentiment escalation
4. **Complete a full flow:** Answer a question, say "that's all", then answer the 3 qualification questions → Shows the full 4-stage pipeline
5. **Type "exit":** → Shows the structured conversation summary

### What to Say While Demoing:

- Point out the **stage banners** changing (Stage 1 → 2 → 4)
- Show the **[ESCALATION TRIGGERED]** output with the reason
- Open the **session log file** in `logs/` and show the structured JSON
- Briefly show `sop.json` and explain it's the AI's only knowledge source
- Open `prompt_design.md` and highlight the hallucination prevention section

---

## Quick Answers for Evaluator Questions

**Q: "How does the AI know when to escalate?"**
> Two layers. Layer 1 is keyword-based — runs before the API call, catches explicit requests and complaints. Layer 2 is model-based — the AI returns an `escalate: true` field in its JSON response when it detects low confidence, out-of-scope, or medical questions. Both are logged with timestamps and reasons.

**Q: "What happens if the API goes down?"**
> The system retries 3 times with exponential backoff. If all retries fail, it returns a pre-defined fallback response that triggers escalation with reason "api_failure". The customer sees a professional message, never an error.

**Q: "How do you prevent the AI from making things up?"**
> Five layers: explicit instruction-level prohibitions, escalation as the designed failure path, SOP as the only context source, unanswered question counter, and pre-approved FAQ answers. The model physically cannot reference information that isn't in the system prompt.

**Q: "Why didn't you use OpenAI or Claude as specified?"**
> The design is API-agnostic. Groq is a free alternative running LLaMA 3.3 70B. Switching to OpenAI requires changing only the client initialization — all prompts, logic, and escalation remain identical. I chose this to avoid API costs while demonstrating the same capabilities.

**Q: "What would you improve for production?"**
> A persistent database instead of file-based logs, RAG for larger SOPs, a proper frontend (the assignment only required CLI), more sophisticated sentiment analysis beyond keywords, and session resumption across restarts.
