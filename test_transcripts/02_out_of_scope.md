# Test Transcript 02 — Out-of-Scope Question

**Scenario:** Customer asks questions that are NOT covered by the SOP. The AI acknowledges the gap honestly and escalates to a human agent rather than guessing or hallucinating.

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

  You    : What is your clinic's exact address?

  [📋 Stage 1 — FAQ]

  Bloom  : I don't have the clinic address details available, but one of our team
           members will be happy to provide directions when you book. Would you like
           to book a consultation?

  You    : Who is the lead doctor at your clinic?

  [📋 Stage 1 — FAQ]

  Bloom  : I'm not able to share individual staff details, but I can assure you that
           all our treatments are carried out by qualified medical professionals.
           Would you like me to connect you with someone who can tell you more?

  You    : Can I get laser hair removal done at your clinic?

  [📋 Stage 1 — FAQ]

  [⚠️ Stage 3 — Escalation]

  [ESCALATION TRIGGERED]
  Reason  : Question outside SOP knowledge base
  Logged  : Yes → logs/

  Bloom  : I'd like to connect you with one of our team members who can assist you
           better. Please hold on and someone from Bloom Aesthetics Clinic will be
           with you shortly.

────────────────────────────────────────────────────────
  Session ended. Saving log...
  Log saved → logs/session_20250523_143245.json
────────────────────────────────────────────────────────
```

---

## Expected Behaviour Verified

| Check | Result |
|---|---|
| AI does NOT invent an address | ✅ SOP says address is provided by human on booking — AI follows this |
| AI does NOT invent staff names | ✅ SOP says staff names are not shared via AI — AI follows this |
| Out-of-scope service triggers escalation | ✅ Laser hair removal is not in the SOP → AI escalates |
| Escalation reason is logged | ✅ `out_of_scope` reason flagged and logged |
| AI acknowledges the gap honestly | ✅ Does not guess or fabricate — admits limitation |
| SOP gap tracking | ✅ `sop_gap` field captures the unanswered question |
