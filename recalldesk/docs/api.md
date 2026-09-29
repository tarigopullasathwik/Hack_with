# RecallDesk — API Reference

Base URL: `http://localhost:8000/api/v1`
Interactive schema (Swagger UI): `http://localhost:8000/docs`
Health (outside the versioned prefix): `GET /health`

All request/response bodies are JSON. **No API keys are ever accepted from or returned to the
client** — the browser talks only to this backend, which holds the secrets.

---

## Chat

### `POST /chat`
Run one agent turn: identify → recall → reason → tools → respond → detect outcome → retain.

```json
{
  "customer_id": "cust-001",
  "message": "My payment failed again when upgrading.",
  "session_id": "demo-abc",
  "memory_mode": "with_memory",
  "active_ticket_id": null
}
```

| Field | Notes |
|---|---|
| `message` | required, 1–4000 chars |
| `memory_mode` | `with_memory` (default) or `without_memory` — the latter skips recall **and** retain |
| `session_id` | optional; generated if omitted |
| `active_ticket_id` | optional ticket to attach messages to |

Response:

```json
{
  "response": "Cache clearing didn't resolve your previous billing issue — updating your billing profile did. Let's check that first…",
  "session_id": "demo-abc",
  "memories_recalled": [
    { "text": "…cache clearing FAILED…billing profile WORKED…", "type": "experience", "score": 0.83 }
  ],
  "memory_count": 3,
  "memory_retained": true,
  "tool_calls": [ { "tool": "get_billing_status", "args": {}, "result": { "plan": "business" } } ],
  "activity": [ { "time": "10:42:04", "action": "Recalled 3 relevant memories from Hindsight" } ],
  "outcome": "resolved",
  "ticket_id": "TKT-1A2B3C4D",
  "escalated": false,
  "handoff_summary": null,
  "hindsight_status": { "available": true, "error": null, "server_url": "http://127.0.0.1:61234", "mode": "hindsight" }
}
```

`outcome` ∈ `resolved` | `failed` | `escalated` | `ongoing` | `error`.
`activity` is operational only — it never contains hidden chain-of-thought.

### `GET /chat/history/{customer_id}/{session_id}`
Messages for one session, oldest first: `{ "messages": [...], "count": n }`

### `GET /chat/sessions/{customer_id}`
`{ "sessions": ["demo-abc", "…"] }`

---

## Customers

| Method | Path | Description |
|---|---|---|
| `GET` | `/customers` | all customers, sorted by name |
| `GET` | `/customers/{customer_id}` | one profile (`404` if unknown) |
| `POST` | `/customers` | create a customer **and initialise their Hindsight bank** |

```json
// POST /customers
{ "name": "Dana Reed", "email": "dana@example.com", "company": "Acme", "plan": "business" }
```

`409` if the email already exists. `plan` ∈ `free` | `starter` | `business` | `enterprise`.

---

## Tickets

| Method | Path | Description |
|---|---|---|
| `GET` | `/tickets?customer_id=&status=&limit=` | list (default limit 20), newest first |
| `GET` | `/tickets/{ticket_id}` | one ticket (`404` if unknown) |
| `POST` | `/tickets` | create |
| `PATCH` | `/tickets/{ticket_id}` | update status / resolution / successful_step / failed_steps |
| `POST` | `/tickets/{ticket_id}/escalate` | escalate and generate a human handoff summary |

```json
// POST /tickets
{ "customer_id": "cust-001", "title": "Payment failure", "description": "…", "category": "billing", "priority": "high" }
```

```json
// PATCH /tickets/TKT-1A2B3C4D
{ "status": "resolved", "successful_step": "updated billing profile", "failed_steps": ["cleared browser cache"] }
```

`POST /tickets/{id}/escalate` response includes `handoff_summary` — a formatted human-readable block
(customer, issue, reason, history, what was tried, what worked, what failed, recommended next step).

`status` ∈ `open` · `in_progress` · `pending_customer` · `escalated` · `resolved` · `closed`

---

## Memory (Hindsight)

| Method | Path | Description |
|---|---|---|
| `GET` | `/memory/status` | `{ available, error, server_url, mode }` — `mode` is `hindsight` or `fallback` |
| `GET` | `/memory/{customer_id}?memory_type=&limit=` | list a customer's memories |
| `POST` | `/memory/{customer_id}/recall` | `{ "query": "…", "budget": "mid" }` |
| `POST` | `/memory/{customer_id}/retain` | `{ "content": "…", "context": "…" }` |
| `POST` | `/memory/{customer_id}/reflect` | `{ "query": "…" }` — deeper synthesis |

When Hindsight is unavailable these endpoints return `hindsight_available: false` with the message
`"Memory unavailable for this request."` (list/recall) or `503` (retain/reflect) — they never fake a
successful memory operation.

---

## Knowledge base

| Method | Path | Description |
|---|---|---|
| `GET` | `/knowledge?category=` | list articles (11 seeded) |
| `GET` | `/knowledge/search?q=&category=` | keyword search, top 5 scored |
| `GET` | `/knowledge/{article_id}` | one article (`404` if unknown) |

The knowledge base is **general product documentation**; it is not customer memory. See
[memory-design.md](memory-design.md#1-memory-vs-knowledge--an-explicit-split).

---

## Demo

| Method | Path | Description |
|---|---|---|
| `GET` | `/demo/scenarios` | the 3 seeded scenarios with customer name/plan |
| `GET` | `/demo/scenarios/{scenario_id}` | one scenario (incl. scripted `turns`) |
| `GET` | `/demo/customers` | featured demo customers with their tickets |
| `GET` | `/demo/memory-timeline/{customer_id}` | ticket + memory timeline, `hindsight_memories`, availability |
| `POST` | `/demo/compare/{customer_id}` | run the same message **without** and **with** memory |
| `GET` | `/demo/stats` | counts + `hindsight_status` |

```json
// POST /demo/compare/cust-001
{ "message": "I'm having another billing problem." }
```

```json
{
  "message": "I'm having another billing problem.",
  "without_memory": { "response": "…clear your cache…", "memories_recalled": [], "memory_count": 0 },
  "with_memory":    { "response": "…billing profile worked before…", "memories_recalled": [ … ], "memory_count": 3 }
}
```

---

## Health

### `GET /health`
`{ "status": "ok", "app": "RecallDesk", "version": "1.0.0", "hindsight": { … } }`

---

## Error handling

| Status | When |
|---|---|
| `400` | invalid body (e.g. compare without `message`) |
| `404` | unknown customer / ticket / article / scenario |
| `409` | duplicate customer email |
| `422` | Pydantic validation failure (e.g. empty `message`) |
| `500` | unexpected error — returns a generic message, never internals |
| `503` | Hindsight-only operation attempted while memory is unavailable |
