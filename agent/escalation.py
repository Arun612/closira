"""
escalation.py — Two-layer escalation detection and logging.

Layer 1: Keyword-based (pre-API) — fast, no token cost
Layer 2: Schema-based (post-API) — catches subtle cases via model judgment
"""

EXPLICIT_ESCALATION_KEYWORDS = [
    "speak to a human", "talk to a human", "speak to someone",
    "talk to someone", "human agent", "real person", "customer service",
    "speak to a person", "talk to a person", "agent please",
    "transfer me", "escalate", "speak to a manager", "talk to a manager",
]

NEGATIVE_SENTIMENT_KEYWORDS = [
    "unacceptable", "ridiculous", "terrible", "awful", "disgusting",
    "furious", "outraged", "scam", "fraud", "complaint", "complain",
    "lawsuit", "horrible", "worst", "rude", "incompetent", "disgusted",
    "appalling", "shocking", "nightmare", "useless",
]


def check_explicit_escalation(user_message: str) -> tuple[bool, str]:
    """
    Pre-API keyword check. Returns (should_escalate, reason).
    """
    msg_lower = user_message.lower()
    for keyword in EXPLICIT_ESCALATION_KEYWORDS:
        if keyword in msg_lower:
            return True, "explicit_request"
    for keyword in NEGATIVE_SENTIMENT_KEYWORDS:
        if keyword in msg_lower:
            return True, "negative_sentiment"
    return False, None


def handle_escalation(session, trigger: str, reason: str, customer_message: str) -> str:
    session.log_escalation(trigger=trigger, customer_message=customer_message, reason=reason)

    reason_display = {
        "explicit_request": "Customer requested a human agent",
        "negative_sentiment": "Negative sentiment or complaint detected",
        "out_of_scope": "Question outside SOP knowledge base",
        "medical_question": "Medical or health-related question",
        "pricing_negotiation": "Pricing negotiation or discount request",
        "low_confidence": "AI confidence too low to answer reliably",
        "unanswered_limit": "More than 2 questions could not be answered from SOP",
        "api_failure": "AI service temporarily unavailable",
        "injection_detected": "Suspicious input detected"
    }.get(reason, reason)

    print(f"\n  [ESCALATION TRIGGERED]")
    print(f"  Reason  : {reason_display}")
    print(f"  Logged  : Yes → logs/\n")

    return (
        "I'd like to connect you with one of our team members who can assist you better. "
        "Please hold on and someone from Bloom Aesthetics Clinic will be with you shortly."
    )
