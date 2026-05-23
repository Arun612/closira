# Test Transcript 01 — In-SOP FAQ Question

**Scenario:** Customer asks questions that are covered by the SOP. The AI answers accurately from the SOP data only, without hallucinating any information.

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

  You    : What are your Botox prices?

  [📋 Stage 1 — FAQ]

  Bloom  : Botox prices at Bloom Aesthetics Clinic start from £200. The final price
           depends on the area treated and the number of units required, which will
           be discussed during your consultation. Is there anything else I can help
           you with?

  You    : How long does Botox last?

  [📋 Stage 1 — FAQ]

  Bloom  : Botox results typically last 3 to 6 months, depending on the individual
           and the area treated. Regular maintenance helps results last longer over
           time. Would you like to know anything else?

  You    : Can I book online?

  [📋 Stage 1 — FAQ]

  Bloom  : Yes! You can book via WhatsApp or through our website. We'll confirm your
           appointment and send a reminder 24 hours before. Is there anything else
           I can help with?

  You    : What are your opening hours?

  [📋 Stage 1 — FAQ]

  Bloom  : We're open Monday to Friday from 9:00 AM to 7:00 PM, and Saturday from
           9:00 AM to 5:00 PM. We're closed on Sundays and bank holidays. Would you
           like to book an appointment?

  You    : What's the cancellation policy?

  [📋 Stage 1 — FAQ]

  Bloom  : We require 24 hours' notice for cancellations. Late cancellations are
           charged at 50% of the treatment cost, and no-shows are charged the full
           treatment cost. Can I help with anything else?

  You    : exit

  [Ending session — generating summary...]

  [📝 Stage 4 — Conversation Summary]

  Bloom  : CUSTOMER INTENT     : General enquiry about Botox pricing, duration, booking,
                                 hours, and cancellation policy
           DETAILS COLLECTED   : None
           SOP GAPS IDENTIFIED : None
           ESCALATED           : No
           RECOMMENDED ACTION  : No follow-up required — all questions answered from SOP

────────────────────────────────────────────────────────
  Session ended. Saving log...
  Log saved → logs/session_20250523_143012.json
────────────────────────────────────────────────────────
```

---

## Expected Behaviour Verified

| Check | Result |
|---|---|
| AI answers from SOP data only | ✅ All prices, hours, and policies match `sop.json` exactly |
| No hallucinated information | ✅ No invented staff names, addresses, or unsupported claims |
| Pre-approved FAQ answers used | ✅ Botox duration and booking answers match the FAQs section verbatim |
| Tone is warm and professional | ✅ Concise, friendly, and invites follow-up questions |
| Responses ≤ 3 sentences | ✅ All responses are within the 3-sentence limit |
