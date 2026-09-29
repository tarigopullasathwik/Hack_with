"""
RecallDesk Support Agent

Pipeline per request:
  1. Identify customer
  2. Recall relevant Hindsight memories
  3. Build system prompt with memory context
  4. Call LLM with tools
  5. Detect outcomes (resolution, failure, escalation)
  6. Retain useful outcome memories
  7. Return response + metadata for UI

Memory mode:
  "with_memory"    — normal operation (uses Hindsight)
  "without_memory" — demo mode: agent receives NO memory context (for before/after comparison)
"""

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Customer, Ticket, TicketStatus, Message, MessageRole
from app import hindsight as mem
from app.tools.support_tools import (
    lookup_customer,
    get_ticket_history,
    lookup_subscription,
    get_billing_status,
    search_knowledge_base,
    create_ticket,
    update_ticket,
    escalate_ticket,
    recall_customer_memory,
)
from app.agents.llm_client import call_llm

logger = logging.getLogger(__name__)
settings = get_settings()


# ─────────────────────────────────────────────────────────────────────────────
# System prompt builder
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """You are RecallDesk, an AI customer support agent for {company} ({product}).

You are helping customer: {customer_name} ({customer_email})
Plan: {plan} | Status: {status}
Environment: {environment}

{memory_section}

AVAILABLE TOOLS (call as JSON in your response when needed):
- lookup_customer: Get customer profile details
- get_ticket_history: Retrieve previous support tickets  
- lookup_subscription: Check subscription/plan details
- get_billing_status: Get billing account status
- search_knowledge_base: Search support articles (arg: query)
- create_ticket: Create a new support ticket (args: title, description, category, priority)
- update_ticket: Update ticket status or resolution (args: ticket_id, status, resolution, successful_step, failed_steps)
- escalate_ticket: Escalate to human agent (args: ticket_id, reason, history_summary, what_worked, what_failed)

To call a tool, include it as:
<tool_call>{{"tool": "tool_name", "args": {{}}}}</tool_call>

INSTRUCTIONS:
1. Acknowledge the customer's issue empathetically.
2. Use your memory context to avoid repeating failed solutions.
3. Recommend solutions based on what previously worked for this customer.
4. If troubleshooting, suggest steps ONE AT A TIME and confirm before continuing.
5. If a solution works, say explicitly: "Glad that resolved it" so the outcome is captured.
6. If multiple attempts fail, escalate with full context.
7. NEVER recommend a troubleshooting step that memory shows already failed for this customer.
8. Be concise, professional, and human — not robotic.

ESCALATION TRIGGERS:
- Billing disputes > $100
- Repeated failed troubleshooting (3+ attempts)
- Security-sensitive account changes
- High-priority enterprise issues
- Suspected account compromise

After tool results are returned, incorporate them naturally into your response.
Do NOT expose raw tool JSON to the customer — only your natural language response.
"""

MEMORY_WITH_TEMPLATE = """
━━━ HINDSIGHT MEMORY CONTEXT (recalled from {count} relevant memories) ━━━
{memories}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USE THIS MEMORY to:
• Reference previous issues by approximate date
• Skip troubleshooting steps that already failed
• Start with what previously worked
• Show the customer you remember their history
"""

MEMORY_WITHOUT_TEMPLATE = """
[MEMORY DISABLED — Generic support mode, no customer history available]
"""


def _build_memory_section(memories: list[dict], mode: str) -> str:
    if mode == "without_memory" or not memories:
        return MEMORY_WITHOUT_TEMPLATE

    formatted = []
    for i, m in enumerate(memories, 1):
        formatted.append(f"  {i}. [{m.get('type', 'memory')}] {m.get('text', '')}")

    return MEMORY_WITH_TEMPLATE.format(
        count=len(memories),
        memories="\n".join(formatted),
    )


def _build_environment_string(customer: Customer) -> str:
    parts = []
    if customer.browser:
        parts.append(customer.browser)
    if customer.operating_system:
        parts.append(customer.operating_system)
    if customer.product_version:
        parts.append(f"Nexora v{customer.product_version}")
    if customer.workspace_size:
        parts.append(f"Workspace: {customer.workspace_size}")
    return " / ".join(parts) if parts else "Unknown"


# ─────────────────────────────────────────────────────────────────────────────
# Outcome detection
# ─────────────────────────────────────────────────────────────────────────────

RESOLUTION_SIGNALS = [
    r"glad that (resolved|worked|fixed|solved)",
    r"great.*resolved",
    r"issue.*resolved",
    r"problem.*fixed",
    r"that (worked|fixed it|solved it|did the trick)",
    r"successfully (resolved|fixed|completed)",
]

FAILURE_SIGNALS = [
    r"(didn.t|did not|hasn.t|have not) (work|resolve|fix|help)",
    r"still (not working|having issues|experiencing)",
    r"(same|same) (problem|issue|error)",
    r"escalat(e|ing|ed)",
]

def _detect_outcome(text: str) -> str:
    """Returns 'resolved', 'failed', 'escalated', or 'ongoing'."""
    t = text.lower()
    for pattern in RESOLUTION_SIGNALS:
        if re.search(pattern, t):
            return "resolved"
    if "escalat" in t:
        return "escalated"
    for pattern in FAILURE_SIGNALS:
        if re.search(pattern, t):
            return "failed"
    return "ongoing"


# ─────────────────────────────────────────────────────────────────────────────
# Memory extraction
# ─────────────────────────────────────────────────────────────────────────────

def _extract_memory_content(
    customer: Customer,
    user_message: str,
    agent_response: str,
    outcome: str,
    tool_results: list[dict],
) -> Optional[str]:
    """
    Determine what is worth retaining.
    Returns a formatted memory string or None if nothing meaningful to store.
    """
    lines = []

    # Always record the issue category if inferable
    issue_lower = user_message.lower()
    category = "support interaction"
    for kw, cat in [
        ("payment", "billing"), ("billing", "billing"), ("invoice", "billing"),
        ("login", "login"), ("password", "login"), ("sso", "login"),
        ("integration", "integration"), ("api", "api"),
        ("sync", "file_sync"), ("file", "file_sync"),
        ("notification", "notifications"),
        ("permission", "permissions"),
        ("subscription", "subscription"), ("upgrade", "subscription"),
    ]:
        if kw in issue_lower:
            category = cat
            break

    lines.append(f"Support interaction — category: {category}")
    lines.append(f"Customer message: {user_message[:300]}")
    lines.append(f"Outcome: {outcome}")

    # Extract tool call info (successful/failed steps)
    for tr in tool_results:
        if tr.get("tool") == "update_ticket" and tr.get("result", {}).get("success"):
            ticket = tr["result"].get("ticket", {})
            if ticket.get("successful_step"):
                lines.append(f"SUCCESSFUL RESOLUTION STEP: {ticket['successful_step']}")
            if ticket.get("failed_steps"):
                try:
                    fs = json.loads(ticket["failed_steps"])
                    lines.append(f"FAILED STEPS (do not retry): {', '.join(fs)}")
                except Exception:
                    pass
        if tr.get("tool") == "escalate_ticket":
            lines.append(f"Issue was ESCALATED. Reason: {tr.get('args', {}).get('reason', '')}")

    # If resolution confirmed, record it clearly
    if outcome == "resolved":
        lines.append("STATUS: Fully resolved — customer confirmed fix worked.")
    elif outcome == "failed":
        lines.append("STATUS: Unresolved — troubleshooting step did NOT work for this customer.")
    elif outcome == "escalated":
        lines.append("STATUS: Escalated to human support team.")

    # Minimum length to be worth retaining
    content = "\n".join(lines)
    if len(content.strip()) < 50:
        return None
    return content


# ─────────────────────────────────────────────────────────────────────────────
# Tool execution dispatcher
# ─────────────────────────────────────────────────────────────────────────────

def _execute_tool(db: Session, customer_id: str, tool_name: str, args: dict) -> dict:
    try:
        if tool_name == "lookup_customer":
            return lookup_customer(db, customer_id)
        elif tool_name == "get_ticket_history":
            return get_ticket_history(db, customer_id)
        elif tool_name == "lookup_subscription":
            return lookup_subscription(db, customer_id)
        elif tool_name == "get_billing_status":
            return get_billing_status(db, customer_id)
        elif tool_name == "search_knowledge_base":
            return search_knowledge_base(db, args.get("query", ""), args.get("category"))
        elif tool_name == "create_ticket":
            return create_ticket(
                db, customer_id,
                title=args.get("title", "Support Request"),
                description=args.get("description", ""),
                category=args.get("category", "other"),
                priority=args.get("priority", "medium"),
            )
        elif tool_name == "update_ticket":
            return update_ticket(
                db,
                ticket_id=args.get("ticket_id", ""),
                status=args.get("status"),
                resolution=args.get("resolution"),
                successful_step=args.get("successful_step"),
                failed_steps=args.get("failed_steps"),
            )
        elif tool_name == "escalate_ticket":
            return escalate_ticket(
                db,
                ticket_id=args.get("ticket_id", ""),
                customer_id=customer_id,
                reason=args.get("reason", ""),
                customer_name=args.get("customer_name", ""),
                history_summary=args.get("history_summary", ""),
                what_worked=args.get("what_worked", ""),
                what_failed=args.get("what_failed", ""),
                environment=args.get("environment", ""),
            )
        elif tool_name == "recall_customer_memory":
            return recall_customer_memory(customer_id, args.get("query", ""))
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        logger.error(f"Tool {tool_name} failed: {e}")
        return {"error": str(e)}


def _parse_tool_calls(text: str) -> list[dict]:
    """Extract <tool_call>...</tool_call> blocks from LLM response."""
    pattern = r"<tool_call>(.*?)</tool_call>"
    matches = re.findall(pattern, text, re.DOTALL)
    calls = []
    for m in matches:
        try:
            obj = json.loads(m.strip())
            if "tool" in obj:
                calls.append(obj)
        except Exception:
            pass
    return calls


def _strip_tool_calls(text: str) -> str:
    """Remove <tool_call> blocks from agent response for customer display."""
    return re.sub(r"<tool_call>.*?</tool_call>", "", text, flags=re.DOTALL).strip()


# ─────────────────────────────────────────────────────────────────────────────
# Activity log helpers
# ─────────────────────────────────────────────────────────────────────────────

def _activity(log: list, action: str):
    log.append({
        "time": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        "action": action,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Main agent entry point
# ─────────────────────────────────────────────────────────────────────────────

def process_message(
    db: Session,
    customer_id: str,
    session_id: str,
    user_message: str,
    memory_mode: str = "with_memory",  # "with_memory" | "without_memory"
    active_ticket_id: Optional[str] = None,
) -> dict:
    """
    Full agent pipeline. Returns:
    {
        "response": str,
        "memories_recalled": list,
        "memory_count": int,
        "memory_retained": bool,
        "tool_calls": list,
        "activity": list,
        "outcome": str,
        "ticket_id": str | None,
        "escalated": bool,
        "handoff_summary": str | None,
        "hindsight_status": dict,
    }
    """
    activity: list[dict] = []
    tool_calls_log: list[dict] = []
    recalled_memories: list[dict] = []
    current_ticket_id = active_ticket_id
    handoff_summary = None

    # ── Step 1: Identify customer ──────────────────────────────────────────
    _activity(activity, "Received customer message")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return {
            "response": "I'm sorry, I couldn't locate your account. Please contact support directly.",
            "memories_recalled": [],
            "memory_count": 0,
            "memory_retained": False,
            "tool_calls": [],
            "activity": activity,
            "outcome": "error",
            "ticket_id": None,
            "escalated": False,
            "handoff_summary": None,
            "hindsight_status": mem.get_status(),
        }

    _activity(activity, f"Identified customer: {customer.name} ({customer.plan} plan)")

    # ── Step 2: Recall memories ────────────────────────────────────────────
    # With memory enabled we always attempt recall. When a live Hindsight server is
    # not connected the manager serves from its in-process fallback store and the
    # response still carries hindsight_status so the UI labels the degraded mode.
    if memory_mode == "with_memory":
        memory_source = "Hindsight" if mem.is_available() else "fallback memory store"
        if mem.is_available():
            _activity(activity, "Querying Hindsight memory bank…")
        else:
            _activity(activity, "Hindsight unavailable — querying in-process fallback memory store")

        recall_result = mem.recall(
            customer_id=customer_id,
            query=user_message,
            budget="mid",
        )
        if recall_result["success"]:
            recalled_memories = recall_result["memories"]
            if recalled_memories:
                _activity(activity, f"Recalled {len(recalled_memories)} relevant memories from {memory_source}")
            else:
                _activity(activity, "No prior memories found — first interaction")
        else:
            _activity(activity, f"Memory recall unavailable: {recall_result.get('error', 'unknown')}")
    else:
        _activity(activity, "Memory mode: without memory (generic support)")

    # ── Step 3: Build system prompt ────────────────────────────────────────
    memory_section = _build_memory_section(recalled_memories, memory_mode)
    env_str = _build_environment_string(customer)

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        company=settings.COMPANY_NAME,
        product=settings.PRODUCT_NAME,
        customer_name=customer.name,
        customer_email=customer.email,
        plan=customer.plan,
        status=customer.status,
        environment=env_str,
        memory_section=memory_section,
    )

    # ── Step 4: LLM call (with tool loop) ──────────────────────────────────
    _activity(activity, "Generating response with LLM…")
    messages = [{"role": "user", "content": user_message}]

    # Load recent conversation context (last 6 messages)
    recent = (
        db.query(Message)
        .filter(Message.customer_id == customer_id, Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(6)
        .all()
    )
    conversation_history = []
    for msg in reversed(recent):
        conversation_history.append({
            "role": "user" if msg.role == MessageRole.USER else "assistant",
            "content": msg.content,
        })
    conversation_history.append({"role": "user", "content": user_message})

    llm_response = call_llm(system_prompt, conversation_history)

    # Tool loop — max 3 iterations
    for _iteration in range(3):
        tool_calls_found = _parse_tool_calls(llm_response)
        if not tool_calls_found:
            break

        tool_results_text = []
        for tc in tool_calls_found:
            tool_name = tc.get("tool", "")
            tool_args = tc.get("args", {})
            _activity(activity, f"Calling tool: {tool_name}")

            result = _execute_tool(db, customer_id, tool_name, tool_args)
            tool_calls_log.append({
                "tool": tool_name,
                "args": tool_args,
                "result": result,
            })
            # Track ticket IDs from create_ticket
            if tool_name == "create_ticket" and result.get("success"):
                current_ticket_id = result["ticket"]["id"]
                _activity(activity, f"Created ticket {current_ticket_id}")
            if tool_name == "escalate_ticket" and result.get("success"):
                handoff_summary = result.get("handoff_summary")
                _activity(activity, "Generated human handoff summary")

            tool_results_text.append(
                f"<tool_result tool=\"{tool_name}\">\n{json.dumps(result, indent=2, default=str)}\n</tool_result>"
            )

        # Feed tool results back to LLM
        follow_up = "\n\n".join(tool_results_text)
        follow_up_messages = conversation_history + [
            {"role": "assistant", "content": llm_response},
            {"role": "user", "content": f"Tool results:\n{follow_up}\n\nNow provide your response to the customer."},
        ]
        llm_response = call_llm(system_prompt, follow_up_messages)

    # Clean tool calls from final customer-facing response
    clean_response = _strip_tool_calls(llm_response)
    _activity(activity, "Response generated")

    # ── Step 5: Detect outcome ─────────────────────────────────────────────
    # Check both user message and agent response for signals
    combined = user_message + " " + clean_response
    outcome = _detect_outcome(combined)
    _activity(activity, f"Outcome detected: {outcome}")

    # ── Step 6: Retain memory ──────────────────────────────────────────────
    memory_retained = False
    if memory_mode == "with_memory":
        content = _extract_memory_content(
            customer, user_message, clean_response, outcome, tool_calls_log
        )
        if content:
            retain_result = mem.retain(
                customer_id=customer_id,
                content=content,
                context=f"support_session:{session_id}",
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "customer_name": customer.name,
                    "plan": str(customer.plan),
                    "outcome": outcome,
                    "ticket_id": current_ticket_id or "",
                    "session_id": session_id,
                },
                document_id=f"session-{session_id}",
            )
            memory_retained = retain_result.get("success", False)
            if memory_retained:
                target = "Hindsight" if mem.is_available() else "fallback memory store"
                _activity(activity, f"Retained new memory in {target}")
            else:
                _activity(activity, f"Memory retention failed: {retain_result.get('error')}")

    # ── Step 7: Save messages to DB ────────────────────────────────────────
    user_msg = Message(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        ticket_id=current_ticket_id,
        session_id=session_id,
        role=MessageRole.USER,
        content=user_message,
        memory_mode=memory_mode,
    )
    db.add(user_msg)

    agent_msg = Message(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        ticket_id=current_ticket_id,
        session_id=session_id,
        role=MessageRole.AGENT,
        content=clean_response,
        memories_recalled=json.dumps(recalled_memories),
        memories_retained=content if (memory_retained and "content" in dir()) else None,
        memory_count=str(len(recalled_memories)),
        tool_calls=json.dumps(tool_calls_log, default=str),
        memory_mode=memory_mode,
    )
    db.add(agent_msg)
    db.commit()

    return {
        "response": clean_response,
        "memories_recalled": recalled_memories,
        "memory_count": len(recalled_memories),
        "memory_retained": memory_retained,
        "tool_calls": tool_calls_log,
        "activity": activity,
        "outcome": outcome,
        "ticket_id": current_ticket_id,
        "escalated": any(tc.get("tool") == "escalate_ticket" for tc in tool_calls_log),
        "handoff_summary": handoff_summary,
        "hindsight_status": mem.get_status(),
    }
