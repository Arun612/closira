# Test Transcript 05 — Conversation Summary

**Scenario:** At the end of a session, the AI generates a structured summary including: customer intent, key details collected, SOP gaps identified, and recommended next action. This transcript demonstrates a session with mixed signals — some SOP gaps and an escalation — to show how the summary captures everything.

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

  You    : Hi, I'm interested in Botox. How much does it cost?

  [📋 Stage 1 — FAQ]

  Bloom  : Botox prices at Bloom Aesthetics Clinic start from £200. The final price
           depends on the area treated and the number of units required, which we'll
           discuss during your consultation. Would you like to know anything else?

  You    : Is there any downtime after the treatment?

  [📋 Stage 1 — FAQ]

  Bloom  : Most clients experience minimal downtime after Botox. Results become
           visible within 3 to 7 days and typically last 3 to 6 months. We recommend
           maintenance every 3 to 6 months. Anything else I can help with?

  You    : Do you offer financing or monthly payment plans?

  [📋 Stage 1 — FAQ]

  Bloom  : Payment plan options are discussed during consultation. Please speak with
           our team directly for details. Is there anything else you'd like to know?

  You    : What's the nearest parking to your clinic?

  [📋 Stage 1 — FAQ]

  Bloom  : I don't have parking information available, but our team will provide
           directions and parking details when you book your appointment. Would you
           like to book a consultation?

  You    : That's all, thanks

  [📋 Stage 1 — FAQ]

  Bloom  : You're welcome! Happy to help.

  Bloom  : I'm glad I could help! Before I let you go, I'd love to learn a little
           more about you — it helps us serve you better. May I ask a few quick
           questions?

  You    : Actually I need to go, bye

  [Ending session — generating summary...]

  [📝 Stage 4 — Conversation Summary]

  Bloom  : CUSTOMER INTENT     : Interest in Botox treatment — asked about pricing,
                                 downtime, payment plans, and parking
           DETAILS COLLECTED   : None (customer left before qualification)
           SOP GAPS IDENTIFIED : Parking information near the clinic
           ESCALATED           : No
           RECOMMENDED ACTION  : Follow up via WhatsApp to offer a free consultation
                                 booking. Consider adding parking information to the
                                 SOP for future enquiries.

────────────────────────────────────────────────────────
  Session ended. Saving log...
  Log saved → logs/session_20250523_144001.json
────────────────────────────────────────────────────────
```

---

## Summary Structure Breakdown

| Field | Content | Source |
|---|---|---|
| **Customer Intent** | Interest in Botox — pricing, downtime, payment plans, parking | Derived from conversation history |
| **Details Collected** | None | Customer exited before lead qualification |
| **SOP Gaps Identified** | Parking information | `sop_gap` field captured this during FAQ stage |
| **Escalated** | No | No escalation triggers fired |
| **Recommended Action** | Follow up, add parking info to SOP | AI-generated next step for human team |

---

## Expected Behaviour Verified

| Check | Result |
|---|---|
| Summary is structured (not free text) | ✅ Uses the exact format specified in the summary prompt |
| Customer intent captured | ✅ Accurately summarises the conversation topics |
| SOP gaps identified | ✅ Parking information flagged as a gap |
| Lead data status noted | ✅ Notes that customer left before qualification |
| Recommended action is actionable | ✅ Specific next steps for the human team |
| Session log saved | ✅ Full session with history, metadata, and summary saved to JSON |
