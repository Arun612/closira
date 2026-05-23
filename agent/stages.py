"""
stages.py — Per-stage logic handlers using Groq API.

Key reliability features:
- Retry with exponential backoff (3 attempts)
- Graceful fallback on total API failure → escalation instead of crash
- Confidence-based escalation wired up (low confidence → escalate)
- History windowing: only last 20 messages sent to API
- Lazy client initialization: client created only on first call
"""

import json
import os
import time

from groq import Groq, APIConnectionError, APITimeoutError, RateLimitError, APIError

from agent.prompts import build_system_prompt

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

MODEL = "llama-3.3-70b-versatile"
MAX_RETRIES = 3
MAX_HISTORY_MESSAGES = 20   # Windowing: only last N messages sent to API

_client = None  # Lazy initialization


def _get_client() -> Groq:
    """Initialize Groq client on first call (lazy init)."""
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. "
                "Set it via environment variable or in a .env file."
            )
        _client = Groq(api_key=api_key)
    return _client


# ---------------------------------------------------------------------------
# CORE LLM CALL  (with retry + exponential backoff)
# ---------------------------------------------------------------------------

FALLBACK_RESPONSE = {
    "response": (
        "I'm sorry, I'm having trouble connecting right now. "
        "Let me get a team member to assist you."
    ),
    "confidence": "low",
    "escalate": True,
    "escalate_reason": "api_failure",
    "sop_gap": None
}


def call_llm(system_prompt: str, history: list) -> dict:
    """
    Call Groq API with retry and exponential backoff.
    Returns parsed JSON dict. On total failure, returns FALLBACK_RESPONSE.

    History windowing: only last MAX_HISTORY_MESSAGES sent to API.
    Full history is preserved in the session object.
    """
    client = _get_client()
    windowed_history = history[-MAX_HISTORY_MESSAGES:]
    messages = [{"role": "system", "content": system_prompt}] + windowed_history

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            raw = completion.choices[0].message.content.strip()

            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                # Model returned non-JSON — treat as low-confidence
                return {**FALLBACK_RESPONSE, "escalate_reason": "api_failure"}

            # Ensure all required keys present with safe defaults
            parsed.setdefault("response", FALLBACK_RESPONSE["response"])
            parsed.setdefault("confidence", "low")
            parsed.setdefault("escalate", False)
            parsed.setdefault("escalate_reason", None)
            parsed.setdefault("sop_gap", None)
            return parsed

        except RateLimitError as e:
            last_error = e
            wait = (2 ** attempt)   # Rate limit: longer backoff
            print(f"\n  Rate limited on attempt {attempt}/{MAX_RETRIES}. Retrying in {wait}s...")
            time.sleep(wait)

        except (APIConnectionError, APITimeoutError) as e:
            last_error = e
            wait = (2 ** (attempt - 1))
            print(f"\n  Connection error on attempt {attempt}/{MAX_RETRIES}. Retrying in {wait}s...")
            time.sleep(wait)

        except APIError as e:
            last_error = e
            wait = (2 ** (attempt - 1))
            print(f"\n  API error on attempt {attempt}/{MAX_RETRIES}. Retrying in {wait}s...")
            time.sleep(wait)

    print(f"\n  API call failed after {MAX_RETRIES} attempts. Last error: {last_error}")
    return FALLBACK_RESPONSE


# ---------------------------------------------------------------------------
# STAGE 1 — FAQ
# ---------------------------------------------------------------------------

def handle_faq(session, sop: dict, user_message: str) -> tuple[str, dict]:
    system_prompt = build_system_prompt("faq", sop)
    parsed = call_llm(system_prompt, session.history)

    # Track SOP gaps
    if parsed.get("sop_gap"):
        session.log_sop_gap(parsed["sop_gap"])

    # Low confidence → force escalation
    if parsed.get("confidence") == "low" and not parsed.get("escalate"):
        parsed["escalate"] = True
        parsed["escalate_reason"] = "low_confidence"

    # SOP rule: > 2 unanswered questions → escalate
    if session.unanswered_count > 2:
        parsed["escalate"] = True
        parsed["escalate_reason"] = "unanswered_limit"

    return parsed["response"], parsed


# ---------------------------------------------------------------------------
# STAGE 2 — LEAD QUALIFICATION
# ---------------------------------------------------------------------------

QUALIFY_KEYS = {0: "business_type", 1: "team_size", 2: "current_tools"}


def handle_qualify(session, sop: dict, user_message: str) -> tuple[str, dict]:
    q_index = session.qualify_question_index

    # Store previous answer
    if q_index > 0:
        answer_key = QUALIFY_KEYS.get(q_index - 1)
        if answer_key:
            session.lead_data[answer_key] = user_message.strip()

    # All 3 questions done → move to summary
    if q_index >= 3:
        session.lead_data[QUALIFY_KEYS[2]] = user_message.strip()
        session.advance_stage()
        return handle_summary(session, sop, user_message)

    system_prompt = build_system_prompt("qualify", sop)
    system_prompt += f"\n\nNow ask qualification question number {q_index + 1} of 3."
    parsed = call_llm(system_prompt, session.history)

    # Low confidence → escalate
    if parsed.get("confidence") == "low" and not parsed.get("escalate"):
        parsed["escalate"] = True
        parsed["escalate_reason"] = "low_confidence"

    session.qualify_question_index += 1
    return parsed["response"], parsed


# ---------------------------------------------------------------------------
# STAGE 4 — SUMMARY
# ---------------------------------------------------------------------------

def handle_summary(session, sop: dict, user_message: str) -> tuple[str, dict]:
    system_prompt = build_system_prompt("summary", sop)
    context_block = f"""

## SESSION CONTEXT FOR SUMMARY
Lead data collected: {json.dumps(session.lead_data) if session.lead_data else 'None'}
SOP gaps identified: {session.sop_gaps if session.sop_gaps else 'None'}
Escalated: {'Yes — ' + session.escalation_log[-1]['reason'] if session.escalated else 'No'}
Total turns: {len([m for m in session.history if m['role'] == 'user'])}
"""
    system_prompt += context_block
    parsed = call_llm(system_prompt, session.history)
    session.summary = parsed["response"]
    return parsed["response"], parsed
