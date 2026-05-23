# prompt_design.md — Closira AI Agent: Prompt Design Document

## Overview

This document covers the full prompt design for the Closira AI customer support workflow built for Bloom Aesthetics Clinic. It explains every key design decision, the full system prompt, hallucination prevention strategy, escalation logic, tone/persona choices, and all reliability features.

---

## 1. System Prompt (Full)

The base system prompt is shared across all stages. Stage-specific instructions are appended dynamically.

```
You are Bloom, a friendly and professional AI assistant for Bloom Aesthetics Clinic.
You handle inbound customer enquiries on behalf of the clinic.

## YOUR PERSONA
- Warm, reassuring, and professional — appropriate for an aesthetics/beauty clinic
- Concise: never write more than 3 sentences per response
- Never use medical jargon; keep language simple and accessible
- Always address the customer respectfully

## YOUR KNOWLEDGE BOUNDARIES — CRITICAL
You MUST answer ONLY from the SOP data provided below.
- If a fact is NOT in the SOP, you do NOT know it.
- NEVER invent prices, services, staff names, addresses, contact numbers, or policies.
- NEVER make clinical or medical recommendations.
- If asked something outside the SOP, acknowledge honestly and escalate.
- The FAQs section of the SOP contains pre-approved answers — use them verbatim where applicable.

## SOP DATA (your only source of truth)
{ ... injected at runtime from sop.json ... }

## OUTPUT FORMAT — MANDATORY
You MUST always respond with valid JSON and nothing else.
Schema:
{
  "response": "<your reply to the customer>",
  "confidence": "high" | "low",
  "escalate": true | false,
  "escalate_reason": "<reason string or null>",
  "sop_gap": "<the unanswered question, or null>"
}
```

---

## 2. Key Design Decisions

### 2.1 Structured JSON Output

**What:** Every API call returns a fixed JSON schema — never free text.

**Why:** Escalation detection becomes a deterministic field check (`if parsed["escalate"]`) rather than fragile regex on free text. This makes the system testable and reliable for a customer-facing workflow.

**How enforced:**
1. System prompt explicitly specifies the schema and prohibits anything else
2. Groq API called with `response_format={"type": "json_object"}` — enforces JSON at the model level

---

### 2.2 SOP Injected Verbatim as Single Source of Truth

**What:** The entire `sop.json` is serialized and injected directly into the system prompt.

**Why:** The model cannot answer what it cannot see. Injecting the SOP eliminates retrieval errors (vs RAG) and makes the knowledge boundary completely explicit.

**Why not RAG:** The SOP is < 1000 tokens. RAG introduces retrieval failures and added complexity with no benefit at this scale. For a multi-hundred-page SOP, RAG would be appropriate.

**Extended SOP:** The SOP was extended beyond the assignment minimum to include: 8 services with pricing, duration, and result timelines; a booking policy with cancellation fees; pre-approved FAQ answers; and escalation rules matching real clinic operations.

---

### 2.3 Stage-Specific Prompt Injection

**What:** A base prompt defines identity and SOP grounding. Each stage appends its own focused instruction block.

**Why:** A monolithic prompt confuses the model about what to do next. Injecting stage context dynamically keeps each stage clean:
- FAQ: answer accurately, flag gaps
- Qualify: ask one question at a time, collect data
- Summary: synthesise session metadata

---

### 2.4 Low Temperature (0.3)

Lower temperature = more deterministic, grounded responses. Reduces the chance of the model improvising answers outside the SOP. For factual, bounded tasks, creativity is a liability.

---

## 3. Hallucination Prevention

Five explicit layers prevent hallucination:

### Layer 1 — Instruction-Level Grounding
System prompt contains a "KNOWLEDGE BOUNDARIES" section with explicit, emphatic prohibitions. The phrase "NEVER" in capitals is intentional — specific prohibitions are more reliably followed than soft suggestions.

### Layer 2 — Escalation as the Designed Failure Path
Instead of guessing, the model has a designed-in escape route: set `escalate: true` with the gap noted in `sop_gap`. The model is trained to prefer this over invention.

### Layer 3 — SOP as Complete Context
The SOP is the only knowledge source in the prompt. This constrains the surface area for hallucination to a small, explicit document.

### Layer 4 — Unanswered Question Counter
`session.unanswered_count` tracks SOP gaps. After 2 gaps, the system forces escalation — matching the SOP's own rule ("more than 2 unanswered questions").

### Layer 5 — Pre-Approved FAQ Answers
The SOP includes a `faqs` section with pre-written answers. The system prompt instructs the model to use these verbatim, removing the need for the model to paraphrase and risk inaccuracy.

---

## 4. Confidence-Based Escalation

The model self-reports confidence as `"high"` or `"low"`.

**Why binary (not float):** A float threshold (e.g. escalate if < 0.4) sounds precise but is calibration-inconsistent across LLMs. A binary `high/low` flag is easier to instruct and more reliably followed.

**Wired up in code:** Both `handle_faq()` and `handle_qualify()` in `stages.py` explicitly check:
```python
if parsed.get("confidence") == "low" and not parsed.get("escalate"):
    parsed["escalate"] = True
    parsed["escalate_reason"] = "low_confidence"
```
This ensures low-confidence responses never reach the customer without escalation.

**Two-layer escalation:**

| Layer | Mechanism | When |
|---|---|---|
| Layer 1 | Keyword matching in Python (pre-API) | Explicit requests, strong complaints — fast, no token cost |
| Layer 2 | `escalate` field in JSON response (post-API) | Out-of-scope, medical queries, low confidence — model judgment |

Layer 1 runs first. If it fires, the API call is skipped entirely.

---

## 5. Tone and Persona

**Name:** "Bloom" — matches the business brand, feels personal.

**Voice guidelines in prompt:**
- Warm and reassuring (not robotic)
- Maximum 3 sentences per response — SMB customers want quick answers
- No medical jargon — aesthetics clients may have health anxieties
- Respectful, never condescending

**Why these choices for an SMB context:**
SMB customers on WhatsApp expect short, human messages. An aesthetics clinic has a trust-sensitive context — warmth is essential. The assistant must feel like the business's own voice.

---

## 6. Reliability Features

### Retry with Exponential Backoff
`call_llm()` retries up to 3 times with increasing delays:
- Connection/timeout errors: 1s → 2s → 4s
- Rate limit errors: 2s → 4s → 8s (longer, as rate limits need more recovery time)
- On total failure: returns `FALLBACK_RESPONSE` which triggers escalation — no crash

### Graceful API Failure Handling
Instead of raising an unhandled exception, total API failure returns a pre-defined response that triggers escalation with reason `"api_failure"`. The customer sees a professional handoff message.

### History Windowing
Only the last 20 messages are sent to the API per call. Full history is preserved in the session object for logging and summary. This prevents context window overflow on long conversations and reduces token costs.

### Lazy Client Initialization
The Groq client is created only on the first API call, after `main.py` has already validated the API key. This avoids silent failures at import time.

### Prompt Injection Guard (`guardrails.py`)
14+ compiled regex patterns detect common injection attempts before any API call:
- "ignore previous instructions", "act as", "jailbreak", "DAN mode"
- Fake system message tags: `[system]`, `<system>`
- "you have no restrictions", "override instructions", etc.

Detected injections: deflect with a friendly message, log escalation, no API call made.
Input sanitization also strips control characters and collapses whitespace on every message.

---

## 7. SOP Coverage

The extended SOP covers:

| Area | Details |
|---|---|
| Hours | Per-day schedule including Saturday and bank holidays |
| Services | 8 services: Botox, Fillers, Consultation, Anti-Wrinkle, Skin Boosters, Chemical Peels, Microneedling, IV Drips |
| Pricing | From-prices for all services in GBP |
| Booking | Channels, cancellation policy, fees, deposit, patch test requirements |
| FAQs | 6 pre-approved Q&A pairs for common questions |
| Escalation Rules | 7 defined triggers matching real clinic operations |
| Privacy | Staff names and clinic address not shared via AI — escalated to human |

---

## 8. Known Limitations and Trade-offs

| Limitation | Trade-off made |
|---|---|
| Binary confidence (high/low) | More stable than float; loses granularity |
| No RAG | Appropriate for small SOP; wouldn't scale to 100+ pages |
| Keyword escalation is surface-level | Fast and cheap; misses sarcasm or complex phrasing |
| Stage transition is heuristic | Predictable; could be improved with intent classification |
| No persistent database | File-based logs; production would use a database |
| Guardrails are regex-based | Catches known patterns; novel injections may slip through |
