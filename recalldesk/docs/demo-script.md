# RecallDesk — Demo Script (≈3 minutes)

**Setup before you start:** backend on `:8000`, frontend on `:5173`, and the Hindsight badge in the
top-right shows either **Hindsight Connected** or **Fallback Memory Mode**. Mention which one it is
out loud — see the honesty note at the end.

Open **http://localhost:5173** → you land on **Demo Mode**.

---

## 0:00–0:20 — The problem

> "Support bots are stateless. Every conversation starts from zero, so customers repeat their
> history, get told to try fixes that already failed, and never benefit from a fix that worked last
> month. Human agents take notes — but those notes are never recalled at the right moment."

Point at the tagline: **"Support that remembers what happened."**

---

## 0:20–0:45 — What a normal bot does

Stay on **Demo Mode**. Scroll to the **Before / After** panel at the bottom. Send:

> `My payment keeps failing when I try to upgrade.`

> "This is the current message sent to the model with **no** memory. The generic answer is: clear
> your cache and retry. That is exactly the wrong advice for this customer — and in a second you'll
> see why."

---

## 0:45–1:30 — First interaction (memory gets written)

Click the **Scenario 1: Recurring Billing Memory** card (customer **Sarah Mitchell**, Vertex Labs,
Business plan). On the left you can see her **Memory Timeline**.

> "Sarah already had a billing incident. Cache clearing **failed** for her. Updating her billing
> profile is what actually fixed it."

Send in the conversation box:

> `I'm having another billing problem — my payment failed again.`

While it streams, narrate the **Agent Activity** feed on the right — this is the architecture made
visible:

```
10:42:03  Received customer message
10:42:04  Identified customer: Sarah Mitchell (business plan)
10:42:04  Recalled 3 relevant memories from Hindsight
10:42:05  Calling tool: get_billing_status
10:42:07  Response generated
10:42:09  Retained new memory in Hindsight
```

> "Notice the agent did **not** tell her to clear her cache. Memory says that already failed, so it
> leads with the billing-profile fix instead."

---

## 1:30–2:20 — Second interaction (memory gets read)

Now scroll to **Before / After** and send the *same* message through both modes. Keep both answers
on screen.

> "Same question, same customer, same model. The only difference is whether the recalled memories
> were injected into the prompt."

- **Without memory:** generic cache-clearing advice.
- **With Hindsight:** "cache clearing didn't resolve your previous billing issue; updating your
  billing profile did — let's start there."

Click **Recalled 3 memories** to expand the exact memories used, each with type and date.

---

## 2:20–2:45 — Memory recall + personalized response

Switch to **Scenario 3: Escalation with Memory Handoff** (customer **James Okonkwo**, FinBridge
Capital) — a billing *dispute*, which the agent must not resolve itself.

> "Watch it escalate — and watch what it hands to the human."

Open the ticket in **Tickets** (or the response panel) and show the generated
**Human Handoff Summary**: customer, issue, history, what was tried, **what failed**, what worked,
environment, and recommended next action.

> "The human agent never has to ask the customer to repeat themselves. That is the memory doing
> real work."

---

## 2:45–3:00 — Why Hindsight changes the experience

> "RecallDesk isn't storing chat history and calling it memory. Hindsight is the memory: one bank
> per customer, with explicit `retain` and `recall` operations. The agent remembers **outcomes** —
> which fixes worked and which failed — and it changes its recommendation because of them. That
> before/after gap is the whole product."

---

## Honesty note (say this if asked)

- All customers, tickets, knowledge articles and history are **synthetic demo data**.
- If the badge reads **Fallback Memory Mode**, the Hindsight server did not start (for example the
  local ML stack could not load, or no LLM key with credits is configured). The app says so on
  screen and falls back to an in-process store so the flow still runs — it never pretends Hindsight
  succeeded. To see the real thing, start Hindsight via `docker compose up` (see README) or point
  `HINDSIGHT_BASE_URL` at a running server.

## Suggested prompts per scenario

| Scenario | Customer | Suggested message |
|---|---|---|
| 1 — Recurring billing | Sarah Mitchell | `I'm having another billing problem — my payment failed again.` |
| 2 — Integration failure | Marcus Chen | `Our Slack and API integrations broke again after the workspace change.` |
| 3 — Escalation | James Okonkwo | `I've been double-charged again and want a refund for this billing period.` |
