"""
main.py — Closira AI Customer Support Workflow
CLI entry point. Runs a full 4-stage customer conversation loop.

Usage:
    python main.py

Set your Groq API key:
    export GROQ_API_KEY=your_key_here
    OR add GROQ_API_KEY=your_key_here to a .env file in this directory.
"""

import json
import os
import sys

# .env support — graceful fallback if python-dotenv not installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from agent.session import Session
from agent.escalation import check_explicit_escalation, handle_escalation
from agent.guardrails import check_and_sanitize, DEFLECTION_MESSAGE
from agent.stages import handle_faq, handle_qualify, handle_summary


# ---------------------------------------------------------------------------
# LOAD SOP
# ---------------------------------------------------------------------------

def load_sop(path: str = "sop.json") -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] SOP file not found at '{path}'. Exiting.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# PRINT HELPERS
# ---------------------------------------------------------------------------

DIVIDER = "─" * 60

def print_header():
    print(f"\n{DIVIDER}")
    print("  🌸  BLOOM AESTHETICS CLINIC — AI Support Assistant")
    print(f"{DIVIDER}")
    print("  Type your message and press Enter.")
    print("  Type 'exit' or 'quit' to end the session.\n")

def bloom_print(message: str):
    print(f"\n  Bloom  : {message}\n")

def user_label():
    return input("  You    : ").strip()

def stage_banner(stage: str):
    labels = {
        "faq": "📋 Stage 1 — FAQ",
        "qualify": "🎯 Stage 2 — Lead Qualification",
        "escalation": "⚠️ Stage 3 — Escalation",
        "summary": "📝 Stage 4 — Conversation Summary"
    }
    print(f"\n  [{labels.get(stage, stage)}]")


# ---------------------------------------------------------------------------
# FAQ → QUALIFY TRANSITION LOGIC
# ---------------------------------------------------------------------------

STRONG_FAREWELL = [
    "that's all", "nothing else", "that's it", "no more questions",
    "all good", "i'm done", "im done", "no other questions",
]

WEAK_FAREWELL = [
    "thanks", "thank you", "cheers", "great", "perfect",
    "that helps", "helpful", "awesome", "brilliant",
]

CONTINUATION_SIGNALS = [
    "but", "also", "what about", "actually", "and", "one more", "another",
]


def should_transition_to_qualify(user_message: str, turn_count: int) -> bool:
    """
    Transition after strong farewell, OR weak farewell on a short message
    with no continuation signal, OR after 5 FAQ turns.
    """
    msg_lower = user_message.lower()

    # Never transition if user signals they want to continue
    for signal in CONTINUATION_SIGNALS:
        if signal in msg_lower:
            return False

    for kw in STRONG_FAREWELL:
        if kw in msg_lower:
            return True

    # Weak farewell only triggers on short messages (≤8 words)
    word_count = len(user_message.split())
    for kw in WEAK_FAREWELL:
        if kw in msg_lower and word_count <= 8:
            return True

    return turn_count >= 5


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------

def run():
    if not os.environ.get("GROQ_API_KEY"):
        print("\n[ERROR] GROQ_API_KEY is not set.")
        print("  Option 1: export GROQ_API_KEY=your_key_here")
        print("  Option 2: add GROQ_API_KEY=your_key_here to a .env file\n")
        sys.exit(1)

    sop = load_sop()
    session = Session()
    faq_turn_count = 0

    print_header()

    opening = (
        "Hello! Welcome to Bloom Aesthetics Clinic. 🌸 "
        "I'm Bloom, your virtual assistant. "
        "How can I help you today?"
    )
    bloom_print(opening)
    session.add_message("assistant", opening)

    while True:
        try:
            raw_input = user_label()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  [Session ended by user]")
            break

        if not raw_input:
            continue

        # ── Guardrail: injection detection + sanitization ────────────────
        is_safe, user_input = check_and_sanitize(raw_input)
        if not is_safe:
            print(f"\n  [GUARDRAIL] Prompt injection pattern detected. Deflecting.\n")
            session.add_message("user", user_input)
            session.log_escalation("guardrail", user_input, "injection_detected")
            bloom_print(DEFLECTION_MESSAGE)
            session.add_message("assistant", DEFLECTION_MESSAGE)
            continue

        # ── Exit command ─────────────────────────────────────────────────
        if user_input.lower() in ("exit", "quit", "bye", "goodbye"):
            print("\n  [Ending session — generating summary...]\n")
            session.add_message("user", user_input)
            stage_banner("summary")
            session.stage = "summary"
            reply, _ = handle_summary(session, sop, user_input)
            bloom_print(reply)
            break

        session.add_message("user", user_input)

        # ── Layer 1: Pre-API keyword escalation check ────────────────────
        should_escalate, escalation_reason = check_explicit_escalation(user_input)
        if should_escalate:
            stage_banner("escalation")
            reply = handle_escalation(session, "keyword_detection", escalation_reason, user_input)
            bloom_print(reply)
            session.add_message("assistant", reply)
            break

        # ── Stage routing ────────────────────────────────────────────────
        stage_banner(session.stage)

        if session.stage == "faq":
            faq_turn_count += 1
            reply, parsed = handle_faq(session, sop, user_input)

            if parsed.get("escalate"):
                stage_banner("escalation")
                reason = parsed.get("escalate_reason", "unknown")
                reply = handle_escalation(session, "api_response", reason, user_input)
                bloom_print(reply)
                session.add_message("assistant", reply)
                break

            bloom_print(reply)
            session.add_message("assistant", reply)

            if should_transition_to_qualify(user_input, faq_turn_count):
                session.advance_stage()
                transition_msg = (
                    "I'm glad I could help! Before I let you go, "
                    "I'd love to learn a little more about you — "
                    "it helps us serve you better. May I ask a few quick questions?"
                )
                bloom_print(transition_msg)
                session.add_message("assistant", transition_msg)

        elif session.stage == "qualify":
            reply, parsed = handle_qualify(session, sop, user_input)

            if parsed.get("escalate"):
                stage_banner("escalation")
                reason = parsed.get("escalate_reason", "unknown")
                reply = handle_escalation(session, "api_response", reason, user_input)
                bloom_print(reply)
                session.add_message("assistant", reply)
                break

            bloom_print(reply)
            session.add_message("assistant", reply)

        elif session.stage == "summary":
            reply, _ = handle_summary(session, sop, user_input)
            bloom_print(reply)
            break

    # ── End of session ───────────────────────────────────────────────────
    print(f"\n{DIVIDER}")
    print("  Session ended. Saving log...")
    saved_path = session.save_log("logs")
    if saved_path:
        print(f"  Log saved → {saved_path}")
    print(f"{DIVIDER}\n")


if __name__ == "__main__":
    run()
