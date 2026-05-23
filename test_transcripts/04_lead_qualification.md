# Test Transcript 04 — Lead Qualification

**Scenario:** After the FAQ stage, the AI transitions to lead qualification and asks 3 structured questions one at a time. The customer's responses are collected and stored in `session.lead_data`.

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

  You    : What services do you offer?

  [📋 Stage 1 — FAQ]

  Bloom  : We offer a range of treatments including Botox (from £200), Dermal Fillers
           (from £250), Anti-Wrinkle Treatment (from £180), Skin Boosters (from £300),
           Chemical Peels (from £120), Microneedling (from £150), and Vitamin Infusion
           Drips (from £150). We also offer free initial consultations. Would you like
           to know more about any specific treatment?

  You    : No thanks, that's all I needed

  [📋 Stage 1 — FAQ]

  Bloom  : You're welcome! Happy to help anytime.

  Bloom  : I'm glad I could help! Before I let you go, I'd love to learn a little
           more about you — it helps us serve you better. May I ask a few quick
           questions?

  You    : Sure, go ahead

  [🎯 Stage 2 — Lead Qualification]

  Bloom  : Thank you! Could you tell me what type of business or clinic you're
           associated with?

  You    : I run a small beauty salon in Manchester

  [🎯 Stage 2 — Lead Qualification]

  Bloom  : That's great! How large is your team, or how many staff members do you have?

  You    : We have 4 therapists and 1 receptionist, so 5 in total

  [🎯 Stage 2 — Lead Qualification]

  Bloom  : Lovely! One last question — what tools or platforms are you currently using
           to manage customer communication?

  You    : We mostly use WhatsApp and a shared Google Calendar for bookings

  [📝 Stage 4 — Conversation Summary]

  Bloom  : CUSTOMER INTENT     : Enquiry about available services at Bloom Aesthetics
                                 Clinic
           DETAILS COLLECTED   : Business type: small beauty salon in Manchester |
                                 Team size: 5 staff (4 therapists + 1 receptionist) |
                                 Current tools: WhatsApp and Google Calendar
           SOP GAPS IDENTIFIED : None
           ESCALATED           : No
           RECOMMENDED ACTION  : Follow up with a tailored consultation proposal
                                 highlighting how Bloom's services could complement
                                 their salon offerings

────────────────────────────────────────────────────────
  Session ended. Saving log...
  Log saved → logs/session_20250523_143722.json
────────────────────────────────────────────────────────
```

---

## Lead Data Collected

```json
{
  "business_type": "I run a small beauty salon in Manchester",
  "team_size": "We have 4 therapists and 1 receptionist, so 5 in total",
  "current_tools": "We mostly use WhatsApp and a shared Google Calendar for bookings"
}
```

---

## Expected Behaviour Verified

| Check | Result |
|---|---|
| FAQ → Qualify transition triggered | ✅ "that's all I needed" matched `STRONG_FAREWELL` keywords |
| Transition message is warm | ✅ Natural, conversational — not abrupt |
| Questions asked one at a time | ✅ Each turn asks exactly one question |
| All 3 qualification questions asked | ✅ Business type → team size → current tools |
| Responses collected and stored | ✅ `session.lead_data` populated with all 3 answers |
| Auto-transition to summary after Q3 | ✅ After the third answer, summary is generated |
| Summary includes lead data | ✅ All collected details appear in the summary |
