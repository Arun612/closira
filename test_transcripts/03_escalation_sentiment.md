# Test Transcript 03 — Escalation via Negative Sentiment

**Scenario:** Customer expresses frustration or makes a complaint. The AI detects the negative sentiment via the pre-API keyword escalation layer and hands off to a human agent with a clear reason logged.

---

## Transcript

```
────────────────────────────────────────────────────────
  🌸  BLOOM AESTHETICS CLINIC — AI Support Assistant
────────────────────────────────────────────────────────
  Type your message and press Enter.
  Type 'exit' or 'quit' to end the session.

  Bloom  : Hello! Welcome to Bloom Aesthetics Clinic. 🌸 I'm Bloom, your virtual
           assistant. How can I help you today?

  You    : How much do fillers cost?

  [📋 Stage 1 — FAQ]

  Bloom  : Dermal filler prices start from £250. The final cost depends on the area
           treated and the volume of filler used, which will be discussed at your
           consultation. Would you like to know anything else?

  You    : This is ridiculous, I was charged way more than that last time. I want to
           make a complaint.

  [⚠️ Stage 3 — Escalation]

  [ESCALATION TRIGGERED]
  Reason  : Negative sentiment or complaint detected
  Logged  : Yes → logs/

  Bloom  : I'd like to connect you with one of our team members who can assist you
           better. Please hold on and someone from Bloom Aesthetics Clinic will be
           with you shortly.

────────────────────────────────────────────────────────
  Session ended. Saving log...
  Log saved → logs/session_20250523_143501.json
────────────────────────────────────────────────────────
```

---

## How Escalation Was Triggered

This escalation was caught by **Layer 1 (pre-API keyword detection)** in `escalation.py`:

- The word **"ridiculous"** matched the `NEGATIVE_SENTIMENT_KEYWORDS` list
- The word **"complaint"** also matched
- Since Layer 1 fires before any API call, no tokens were consumed for this escalation

The API call is skipped entirely when Layer 1 triggers — this is faster and more cost-effective than relying on the model's sentiment analysis.

---

## Expected Behaviour Verified

| Check | Result |
|---|---|
| Negative sentiment detected | ✅ "ridiculous" and "complaint" trigger keyword escalation |
| Escalation reason logged | ✅ `negative_sentiment` reason with timestamp |
| Handoff message is professional | ✅ Warm, reassuring — not robotic or dismissive |
| No API call wasted | ✅ Layer 1 (keyword) fires before the API is called |
| Session log captures the event | ✅ Escalation logged with trigger, reason, customer message, and stage |
