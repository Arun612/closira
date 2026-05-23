# Closira AI Customer Support Workflow

An AI-powered customer support agent for **Bloom Aesthetics Clinic**

Handles a simulated end-to-end customer conversation across four stages — FAQ answering, lead qualification, escalation detection, and conversation summary — via a Python CLI using the **Groq API (LLaMA 3.3 70B)**.

---

## Architecture

```
Customer Input
      │
      ▼
┌──────────────────────────────────┐
│  Guardrail Layer                 │  ← Injection detection + input sanitization
│  (guardrails.py)                 │     Runs before any API call
└──────────────────────────────────┘
      │ (clean input)
      ▼
┌──────────────────────────────────┐
│  Layer 1: Keyword Escalation     │  ← Pre-API, catches explicit requests/complaints
│  (escalation.py)                 │
└──────────────────────────────────┘
      │ (no escalation)
      ▼
┌──────────────────────────────────┐
│  Stage Router                    │  ← Routes to FAQ / Qualify / Summary
│  (main.py)                       │
└──────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────┐
│  Groq API Call                   │  ← Stage-specific system prompt + SOP
│  LLaMA 3.3 70B · JSON mode       │     Retry with exponential backoff
│  (stages.py)                     │     History windowing (last 20 messages)
└──────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────┐
│  Layer 2: Schema Escalation      │  ← Checks escalate + confidence fields
└──────────────────────────────────┘
      │
      ▼
   Reply + Timestamped Session Log
```

---

## Project Structure

```
closira/
│
├── main.py                        # CLI entry point and conversation loop
├── sop.json                       # Extended SOP for Bloom Aesthetics Clinic
├── .env.example                   # Environment variable template
├── requirements.txt               # Python dependencies
│
├── agent/
│   ├── __init__.py
│   ├── prompts.py                 # System prompts for all stages
│   ├── stages.py                  # Stage logic + Groq API calls (retry/backoff)
│   ├── escalation.py              # Two-layer escalation detection + logging
│   ├── guardrails.py              # Prompt injection detection + sanitization
│   └── session.py                 # Session state management
│
├── logs/                          # Auto-generated timestamped session logs
│
├── test_transcripts/
│   ├── 01_in_scope_faq.md
│   ├── 02_out_of_scope.md
│   ├── 03_escalation_sentiment.md
│   ├── 04_lead_qualification.md
│   └── 05_conversation_summary.md
│
├── prompt_design.md               # Full prompt design and reasoning
└── README.md
```

---

## Setup

### Prerequisites
- Python 3.10+
- A free Groq API key — [get one at console.groq.com](https://console.groq.com)

### 1. Clone

```bash
git clone https://github.com/Arun612/closira.git
cd closira
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set API Key

**Option A — .env file (recommended):**
```bash
cp .env.example .env
# Edit .env and add your key:
# GROQ_API_KEY=your_groq_api_key_here
```

**Option B — Environment variable:**
```bash
export GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run

```bash
python main.py
```

---

## The Four Stages

| # | Stage | Trigger | What happens |
|---|---|---|---|
| 1 | FAQ | Session start | Answers from SOP only; flags gaps |
| 2 | Lead Qualification | After FAQ stage | Asks 3 structured questions one at a time |
| 3 | Escalation | Any trigger | Logs reason + ends with handoff message |
| 4 | Summary | `exit` or end of qualify | Structured session summary |

---

## Escalation Triggers

| Trigger | Detection Method |
|---|---|
| Explicit human request | Keyword layer (pre-API) |
| Complaint / negative sentiment | Keyword layer (pre-API) |
| Out-of-scope question | `escalate: true` in API JSON |
| Medical or health question | `escalate: true` in API JSON |
| Pricing negotiation | `escalate: true` in API JSON |
| Low AI confidence | `confidence: "low"` in API JSON |
| More than 2 unanswered questions | Session counter in `session.py` |
| API total failure | Fallback response → escalation |
| Prompt injection detected | Guardrail layer (pre-API) |

All escalations logged to `logs/session_YYYYMMDD_HHMMSS.json`.

---

## Reliability Features

| Feature | Where |
|---|---|
| Retry with exponential backoff (3 attempts) | `stages.py → call_llm()` |
| Graceful fallback on API failure (no crash) | `stages.py → FALLBACK_RESPONSE` |
| History windowing (last 20 messages to API) | `stages.py → call_llm()` |
| Lazy Groq client initialization | `stages.py → _get_client()` |
| Prompt injection detection (14+ patterns) | `guardrails.py` |
| Input sanitization (control chars, whitespace) | `guardrails.py → sanitize()` |
| Timestamped session logs (no overwrites) | `session.py → save_log()` |
| Confidence → escalation wired in code | `stages.py → handle_faq/qualify()` |
| .env file support | `main.py` |

---

## SOP Coverage

The SOP (`sop.json`) covers:
- **Hours:** Per-day schedule including Saturday/bank holidays
- **8 Services:** Botox, Dermal Fillers, Consultation, Anti-Wrinkle, Skin Boosters, Chemical Peels, Microneedling, IV Drips — each with pricing, duration, result timelines
- **Booking Policy:** Cancellation fees, deposit requirements, patch test policy, minimum age
- **FAQs:** 6 pre-approved Q&A pairs
- **Escalation Rules:** 7 defined triggers
- **Privacy:** Staff names and clinic address intentionally withheld from AI — escalated to human

---

## Trade-offs and Limitations

| Limitation | Notes |
|---|---|
| Groq instead of OpenAI/Claude | API-agnostic design; one line to switch provider |
| Binary confidence (high/low) | More stable than float; loses granularity |
| No RAG | Appropriate for this SOP size; wouldn't scale to 100+ pages |
| Keyword escalation is surface-level | Fast, but may miss sarcasm or complex phrasing |
| Regex-based injection detection | Catches known patterns; novel injections may slip through |
| File-based session logs | Production would use a database |
| CLI only | No frontend/UI, per assignment requirements |

---

## Evaluation Criteria Mapping

| Criterion | Where addressed |
|---|---|
| AI workflow structure | `main.py` stage router + `agent/stages.py` |
| Prompt quality | `agent/prompts.py` + `prompt_design.md` |
| Reliability & safety | Retry/backoff, guardrails, JSON schema, fallback responses |
| Escalation logic | `agent/escalation.py` + two-layer detection |
| SOP understanding | Extended `sop.json` + verbatim injection in system prompt |
| Clarity of reasoning | `prompt_design.md` |
