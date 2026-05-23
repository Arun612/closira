"""
guardrails.py — Prompt injection detection and input sanitization.

Detects common prompt injection patterns before any API call is made.
Sanitizes raw user input to strip control characters and collapse whitespace.
"""

import re

# ---------------------------------------------------------------------------
# COMPILED INJECTION PATTERNS  (checked once at module load for performance)
# ---------------------------------------------------------------------------

_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"forget\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"you\s+are\s+now\s+(a|an)\s+\w+",
    r"act\s+as\s+(a|an|if)\s+",
    r"pretend\s+(you\s+are|to\s+be)\s+",
    r"roleplay\s+as\s+",
    r"jailbreak",
    r"dan\s+mode",
    r"developer\s+mode",
    r"\[system\]",
    r"<system>",
    r"new\s+instructions?:",
    r"override\s+(previous\s+)?(instructions?|prompt|system)",
    r"you\s+have\s+no\s+restrictions?",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]

# Matches non-printable control characters (except newline/tab)
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

DEFLECTION_MESSAGE = (
    "I'm here to help with questions about Bloom Aesthetics Clinic. "
    "What can I assist you with today?"
)


def sanitize(text: str) -> str:
    """Strip control characters and collapse excessive whitespace."""
    text = _CONTROL_CHARS.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_injection(text: str) -> bool:
    """Return True if the message matches any known injection pattern."""
    for pattern in _COMPILED:
        if pattern.search(text):
            return True
    return False


def check_and_sanitize(user_message: str) -> tuple[bool, str]:
    """
    Full guardrail check.
    Returns (is_safe, sanitized_message).
    If injection detected, is_safe=False.
    """
    clean = sanitize(user_message)
    if is_injection(clean):
        return False, clean
    return True, clean
