"""
HindsightManager — wraps the Hindsight SDK for RecallDesk.

One memory bank per customer.  Bank ID format: "recalldesk-customer-{customer_id}"

Operations:
  retain(customer_id, content, context, timestamp, metadata)  → store a memory
  recall(customer_id, query, budget)                          → retrieve memories
  reflect(customer_id, query)                                 → deep analysis
  create_bank(customer_id, name, plan)                        → initialise bank
  list_memories(customer_id)                                  → all raw memories

Modes:
  1. hindsight-client connecting to a running Hindsight server (local or Cloud)
  2. Graceful fallback with in-process mock memory (SQLite-backed) when server unavailable.
     The mock mode stores/retrieves memories using simple semantic search so the
     application remains fully functional for demos without a live Hindsight server.
"""

import logging
import json
import os
from datetime import datetime, timezone
from typing import Optional, Any

logger = logging.getLogger(__name__)

_client = None
_hindsight_available = False
_init_error: Optional[str] = None
_server_url: Optional[str] = None

# In-process fallback memory store (used when Hindsight server is not running)
_fallback_store: dict[str, list[dict]] = {}


def _get_bank_id(customer_id: str) -> str:
    return f"recalldesk-customer-{customer_id}"


def _missing_local_ml_deps(embeddings_provider: str, reranker_provider: str) -> list[str]:
    """
    Return the local ML modules required by the configured providers that cannot be imported.

    The embedded server cannot start without them, and the SDK's own start() waits the
    full timeout when the background thread dies — so check up front and fail fast with a
    clear reason instead of stalling startup.
    """
    import importlib

    required: set[str] = set()
    if embeddings_provider == "local":
        required.add("sentence_transformers")
    elif embeddings_provider == "onnx":
        required.update({"onnxruntime", "transformers"})
    if reranker_provider == "local":
        required.add("sentence_transformers")

    missing: list[str] = []
    for module in sorted(required):
        try:
            importlib.import_module(module)
        except Exception as exc:  # noqa: BLE001 — any import failure means it is unusable
            missing.append(f"{module} ({type(exc).__name__})")
    return missing


def _configure_hindsight_env(
    llm_provider: str,
    llm_model: str,
    llm_api_key: str,
    llm_base_url: str,
    embeddings_provider: str,
    reranker_provider: str,
) -> None:
    """
    The embedded Hindsight server reads its configuration from HINDSIGHT_API_*
    environment variables (see https://hindsight.vectorize.io/developer/configuration).
    Mirror the app settings there before starting it so a single .env drives both.
    """
    os.environ["HINDSIGHT_API_LLM_API_KEY"] = llm_api_key
    os.environ.setdefault("HINDSIGHT_API_LLM_PROVIDER", llm_provider)
    os.environ.setdefault("HINDSIGHT_API_LLM_MODEL", llm_model)
    if llm_base_url:
        os.environ.setdefault("HINDSIGHT_API_LLM_BASE_URL", llm_base_url)

    # Embedding/reranker backends. "local" needs sentence-transformers + PyTorch;
    # "openai" + reranker "none" avoids the local ML stack entirely.
    os.environ.setdefault("HINDSIGHT_API_EMBEDDINGS_PROVIDER", embeddings_provider)
    os.environ.setdefault("HINDSIGHT_API_RERANKER_PROVIDER", reranker_provider)
    if embeddings_provider == "openai":
        os.environ.setdefault("HINDSIGHT_API_EMBEDDINGS_OPENAI_API_KEY", llm_api_key)
        if llm_base_url:
            os.environ.setdefault("HINDSIGHT_API_EMBEDDINGS_OPENAI_BASE_URL", llm_base_url)


async def init_hindsight(
    llm_provider: str,
    llm_model: str,
    llm_api_key: str,
    embedded: bool = True,
    base_url: str = "http://localhost:8888",
    hindsight_api_key: str = "",
    llm_base_url: str = "",
    embeddings_provider: str = "local",
    reranker_provider: str = "local",
    start_timeout: float = 45.0,
) -> bool:
    """
    Try to connect to a Hindsight server.
    Falls back gracefully if unavailable.
    """
    global _client, _hindsight_available, _init_error, _server_url

    # First try: embedded HindsightServer (hindsight-all)
    if embedded:
        # Fail fast: the Hindsight server cannot start without an LLM key. Without
        # this guard the SDK retries for ~90s before we fall back.
        if not llm_api_key:
            _init_error = "No LLM API key configured (set LLM_API_KEY or HINDSIGHT_LLM_API_KEY)"
            logger.warning(
                "Skipping embedded Hindsight — no LLM API key configured. "
                "Add LLM_API_KEY to .env for full persistent memory."
            )
        else:
            missing = _missing_local_ml_deps(embeddings_provider, reranker_provider)
            if missing:
                _init_error = (
                    "Embedded Hindsight needs the local ML stack, but these modules are "
                    f"unavailable: {', '.join(missing)}. Set HINDSIGHT_EMBEDDINGS_PROVIDER "
                    "(e.g. openai) and HINDSIGHT_RERANKER_PROVIDER=rrf, or run Hindsight "
                    "via docker compose."
                )
                logger.warning(
                    f"Skipping embedded Hindsight — {_init_error}"
                )
            else:
                _configure_hindsight_env(
                    llm_provider, llm_model, llm_api_key, llm_base_url,
                    embeddings_provider, reranker_provider,
                )
                try:
                    from hindsight import HindsightServer
                    from hindsight_client import Hindsight

                    logger.info("Attempting to start embedded Hindsight server…")
                    import app.hindsight._embedded_server as _es
                    _es.server = HindsightServer(
                        llm_provider=llm_provider,
                        llm_model=llm_model,
                        llm_api_key=llm_api_key,
                        llm_base_url=llm_base_url or None,
                    )
                    _es.server.start(timeout=start_timeout)
                    _server_url = _es.server.url
                    _client = Hindsight(base_url=_server_url)
                    _hindsight_available = True
                    logger.info(f"Embedded Hindsight server started at {_server_url}")
                    return True
                except ImportError:
                    logger.info("hindsight-all not installed; trying external hindsight-client…")
                except Exception as e:
                    _init_error = str(e)
                    logger.warning(f"Embedded Hindsight failed: {e}")

    # Second try: external client (sync version check — non-async)
    try:
        from hindsight_client import Hindsight

        _server_url = base_url
        kwargs: dict[str, Any] = {"base_url": base_url}
        if hindsight_api_key:
            kwargs["api_key"] = hindsight_api_key

        test_client = Hindsight(**kwargs)
        # Use a quick HTTP probe instead of get_version() to avoid async issues
        import httpx
        probe = httpx.get(f"{base_url.rstrip('/')}/version", timeout=3.0)
        if probe.status_code < 500:
            _client = test_client
            _hindsight_available = True
            logger.info(f"Connected to Hindsight at {base_url} (status {probe.status_code})")
            return True
        else:
            raise Exception(f"Hindsight probe returned {probe.status_code}")

    except ImportError:
        _init_error = "hindsight-client not installed"
        logger.warning("hindsight-client not installed")
    except Exception as e:
        _init_error = str(e)
        logger.warning(
            f"Hindsight server not reachable at {base_url}: {e}\n"
            "Running in FALLBACK memory mode — memories stored in-process. "
            "Start a Hindsight server for full persistent memory."
        )

    # Fallback mode: use in-process store
    _hindsight_available = False
    logger.info("Using in-process fallback memory store.")
    return False


def shutdown_hindsight():
    """Clean up the embedded server on app shutdown."""
    try:
        import app.hindsight._embedded_server as _es
        if getattr(_es, "server", None) is not None:
            _es.server.__exit__(None, None, None)
            logger.info("Hindsight embedded server shut down.")
    except Exception:
        pass


def is_available() -> bool:
    """Returns True when a real Hindsight server is connected."""
    return _hindsight_available


def is_usable(customer_id: Optional[str] = None) -> bool:
    """
    True when memory recall/retain can return something meaningful — i.e. a real
    Hindsight server is connected, OR the in-process fallback store holds data.

    Callers should gate memory features on this rather than is_available(), so the
    seeded demo memories still flow through recall/retain when running in fallback
    mode (no Hindsight server). The UI keeps showing the honest mode via get_status().
    """
    if _hindsight_available:
        return True
    if customer_id is not None:
        return bool(_fallback_store.get(_get_bank_id(customer_id)))
    return any(_fallback_store.values())


def get_status() -> dict:
    return {
        "available": _hindsight_available,
        "error": _init_error,
        "server_url": _server_url,
        "mode": "hindsight" if _hindsight_available else "fallback",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Fallback in-process memory store
# ─────────────────────────────────────────────────────────────────────────────

def _fallback_retain(bank_id: str, content: str, context: Optional[str], metadata: dict) -> dict:
    if bank_id not in _fallback_store:
        _fallback_store[bank_id] = []
    _fallback_store[bank_id].append({
        "id": f"mem-{len(_fallback_store[bank_id])+1}",
        "text": content,
        "type": "experience",
        "context": context,
        "metadata": metadata,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"success": True, "bank_id": bank_id, "error": None}


def _fallback_recall(bank_id: str, query: str) -> dict:
    memories = _fallback_store.get(bank_id, [])
    if not memories:
        return {"success": True, "memories": [], "count": 0, "error": None}

    # Simple keyword scoring
    query_words = set(query.lower().split())
    scored = []
    for m in memories:
        text_words = set(m["text"].lower().split())
        score = len(query_words & text_words)
        if score > 0:
            scored.append((score, m))

    scored.sort(key=lambda x: -x[0])
    top = [m for _, m in scored[:6]]

    return {"success": True, "memories": top, "count": len(top), "error": None}


def _fallback_reflect(bank_id: str, query: str) -> dict:
    result = _fallback_recall(bank_id, query)
    memories = result["memories"]
    if not memories:
        return {"success": True, "answer": "No relevant memories found.", "error": None}
    summary = "\n".join(f"- {m['text'][:200]}" for m in memories[:3])
    return {"success": True, "answer": f"Based on memory:\n{summary}", "error": None}


# ─────────────────────────────────────────────────────────────────────────────
# Core memory operations
# ─────────────────────────────────────────────────────────────────────────────

def retain(
    customer_id: str,
    content: str,
    context: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    metadata: Optional[dict] = None,
    document_id: Optional[str] = None,
) -> dict:
    """Store a memory in the customer's Hindsight bank."""
    bank_id = _get_bank_id(customer_id)
    ts = timestamp or datetime.now(timezone.utc)
    meta = metadata or {}

    if not _hindsight_available or _client is None:
        return _fallback_retain(bank_id, content, context, meta)

    try:
        _client.retain(
            bank_id=bank_id,
            content=content,
            context=context,
            timestamp=ts,
            document_id=document_id,
            metadata=meta,
            retain_async=True,
        )
        logger.debug(f"[Hindsight] retain → {bank_id}: {content[:80]}…")
        return {"success": True, "bank_id": bank_id, "error": None}
    except Exception as e:
        logger.error(f"retain() failed for {bank_id}: {e}")
        # Write to fallback as well so nothing is lost
        _fallback_retain(bank_id, content, context, meta)
        return {"success": False, "bank_id": bank_id, "error": str(e)}


def recall(
    customer_id: str,
    query: str,
    budget: str = "mid",
    types: Optional[list[str]] = None,
    max_tokens: int = 3000,
) -> dict:
    """Retrieve relevant memories from the customer's bank."""
    bank_id = _get_bank_id(customer_id)

    if not _hindsight_available or _client is None:
        return _fallback_recall(bank_id, query)

    try:
        kwargs: dict[str, Any] = {
            "bank_id": bank_id,
            "query": query,
            "budget": budget,
            "max_tokens": max_tokens,
        }
        if types:
            kwargs["types"] = types

        response = _client.recall(**kwargs)
        memories = []
        for r in response.results:
            memories.append({
                "text": r.text,
                "type": getattr(r, "type", "unknown"),
                "score": float(getattr(r, "score", 0.0)),
                "chunk_id": getattr(r, "chunk_id", None),
            })
        logger.debug(f"[Hindsight] recall → {len(memories)} memories for {bank_id}")
        return {"success": True, "memories": memories, "count": len(memories), "error": None}
    except Exception as e:
        logger.error(f"recall() failed for {bank_id}: {e}")
        return _fallback_recall(bank_id, query)


def reflect(
    customer_id: str,
    query: str,
    budget: str = "mid",
    context: Optional[str] = None,
) -> dict:
    """Deep reasoning over memory bank."""
    bank_id = _get_bank_id(customer_id)

    if not _hindsight_available or _client is None:
        return _fallback_reflect(bank_id, query)

    try:
        response = _client.reflect(
            bank_id=bank_id,
            query=query,
            budget=budget,
            context=context,
        )
        return {"success": True, "answer": response.text, "error": None}
    except Exception as e:
        logger.error(f"reflect() failed for {bank_id}: {e}")
        return _fallback_reflect(bank_id, query)


def create_bank(customer_id: str, name: str, plan: str = "business") -> dict:
    """Create or ensure the customer's memory bank exists."""
    bank_id = _get_bank_id(customer_id)

    if not _hindsight_available or _client is None:
        # Ensure fallback store bucket exists
        if bank_id not in _fallback_store:
            _fallback_store[bank_id] = []
        return {"success": True, "bank_id": bank_id, "error": None}

    mission = (
        f"I am a customer support memory bank for {name}. "
        f"I track this customer's support history, problems, attempted solutions, "
        f"outcomes, preferences, and product environment for Nexora Workspace ({plan} plan). "
        f"I remember what worked, what failed, and what was promised."
    )

    try:
        _client.create_bank(
            bank_id=bank_id,
            name=f"Support Memory: {name}",
            mission=mission,
            disposition={
                "skepticism": 2,
                "literalism": 4,
                "empathy": 4,
            },
        )
        logger.info(f"[Hindsight] Created bank {bank_id} for {name}")
        return {"success": True, "bank_id": bank_id, "error": None}
    except Exception as e:
        if "already exists" in str(e).lower() or "conflict" in str(e).lower() or "409" in str(e):
            return {"success": True, "bank_id": bank_id, "error": None}
        logger.error(f"create_bank() failed: {e}")
        return {"success": False, "error": str(e)}


def list_memories(customer_id: str, memory_type: Optional[str] = None, limit: int = 50) -> dict:
    """List raw memories from the customer's bank."""
    bank_id = _get_bank_id(customer_id)

    if not _hindsight_available or _client is None:
        memories = _fallback_store.get(bank_id, [])
        if memory_type:
            memories = [m for m in memories if m.get("type") == memory_type]
        return {
            "success": True,
            "memories": memories[:limit],
            "count": min(len(memories), limit),
            "error": None,
        }

    try:
        kwargs: dict[str, Any] = {"bank_id": bank_id, "limit": limit}
        if memory_type:
            kwargs["type"] = memory_type

        response = _client.list_memories(**kwargs)
        memories = []
        items = response.memories if hasattr(response, "memories") else (response if isinstance(response, list) else [])
        for m in items:
            memories.append({
                "id": getattr(m, "id", None),
                "text": getattr(m, "text", str(m)),
                "type": getattr(m, "type", "unknown"),
                "created_at": str(getattr(m, "created_at", "")),
                "metadata": getattr(m, "metadata", {}),
            })
        return {"success": True, "memories": memories, "count": len(memories), "error": None}
    except Exception as e:
        logger.error(f"list_memories() failed for {bank_id}: {e}")
        # Fall back to in-process store
        memories = _fallback_store.get(bank_id, [])
        return {"success": True, "memories": memories[:limit], "count": len(memories), "error": None}


# ─────────────────────────────────────────────────────────────────────────────
# Seed historical demo memories into fallback store
# Called at startup so demo customers have memory even without Hindsight server
# ─────────────────────────────────────────────────────────────────────────────

def seed_demo_memories():
    """Pre-populate the fallback in-process store with demo customer memories."""
    from datetime import timedelta

    def ago(days):
        return datetime.now(timezone.utc) - timedelta(days=days)

    demo_memories = {
        "cust-001": [  # Sarah Mitchell
            {
                "id": "seed-sm-1",
                "text": (
                    "Sarah Mitchell reported payment failure during Business plan upgrade. "
                    "Troubleshooting step: clearing browser cache — FAILED, did NOT resolve the payment issue. "
                    "SUCCESSFUL RESOLUTION: Updating billing profile with correct billing address fixed the payment. "
                    "Customer confirmed the fix worked. Ticket TKT-SM001."
                ),
                "type": "experience",
                "context": "support_ticket:TKT-SM001",
                "metadata": {"customer_name": "Sarah Mitchell", "plan": "business"},
                "created_at": ago(24).isoformat(),
            },
            {
                "id": "seed-sm-2",
                "text": (
                    "Sarah Mitchell's Slack integration stopped sending notifications after workspace rename. "
                    "SUCCESSFUL RESOLUTION: Re-authorized Slack OAuth integration from Settings > Integrations > Slack. "
                    "Notifications resumed immediately. Customer confirmed resolved. Ticket TKT-SM002."
                ),
                "type": "experience",
                "context": "support_ticket:TKT-SM002",
                "metadata": {"customer_name": "Sarah Mitchell", "plan": "business"},
                "created_at": ago(11).isoformat(),
            },
            {
                "id": "seed-sm-3",
                "text": (
                    "Customer profile: Sarah Mitchell is the primary workspace admin at Vertex Labs. "
                    "28 members on Business plan. Uses Chrome 124 on Windows 11, Nexora v4.2.1. "
                    "Prefers email communication. Has experienced billing issues before."
                ),
                "type": "world",
                "context": "customer_profile",
                "metadata": {"customer_name": "Sarah Mitchell", "plan": "business"},
                "created_at": ago(30).isoformat(),
            },
        ],
        "cust-002": [  # Marcus Chen
            {
                "id": "seed-mc-1",
                "text": (
                    "Marcus Chen reported SAML certificate expiry causing company-wide SSO lockout (150 users). "
                    "SUCCESSFUL RESOLUTION: Renewed SAML certificate on Okta IDP and re-uploaded to "
                    "Nexora Settings > Security > SSO. Confirmed working for all users. Ticket TKT-MC001."
                ),
                "type": "experience",
                "context": "support_ticket:TKT-MC001",
                "metadata": {"customer_name": "Marcus Chen", "plan": "enterprise"},
                "created_at": ago(59).isoformat(),
            },
            {
                "id": "seed-mc-2",
                "text": (
                    "Marcus Chen's API integration was hitting rate limits (HTTP 429) causing CI/CD failures. "
                    "SUCCESSFUL RESOLUTION: Implemented exponential backoff and upgraded to Enterprise API tier. "
                    "Rate limit raised from 1000 to 10000 req/min. Ticket TKT-MC002."
                ),
                "type": "experience",
                "context": "support_ticket:TKT-MC002",
                "metadata": {"customer_name": "Marcus Chen", "plan": "enterprise"},
                "created_at": ago(29).isoformat(),
            },
            {
                "id": "seed-mc-3",
                "text": (
                    "Marcus Chen profile: DevOps lead at TechFlow Solutions. Enterprise plan, 150 members. "
                    "Uses Firefox 125 on macOS Sonoma. Manages Okta SAML SSO. Prefers Slack in mornings."
                ),
                "type": "world",
                "context": "customer_profile",
                "metadata": {"customer_name": "Marcus Chen", "plan": "enterprise"},
                "created_at": ago(65).isoformat(),
            },
        ],
        "cust-004": [  # James Okonkwo
            {
                "id": "seed-jo-1",
                "text": (
                    "James Okonkwo reported invoices not generating for 2 months. "
                    "SUCCESSFUL RESOLUTION: Billing webhook was disabled; re-enabled invoice generation in admin panel. "
                    "Ticket TKT-JO001."
                ),
                "type": "experience",
                "context": "support_ticket:TKT-JO001",
                "metadata": {"customer_name": "James Okonkwo", "plan": "business"},
                "created_at": ago(44).isoformat(),
            },
            {
                "id": "seed-jo-2",
                "text": (
                    "James Okonkwo reported double-charge on January subscription — two charges for same billing period. "
                    "Issue was ESCALATED to billing team for manual refund. Cannot be resolved by support agent alone. "
                    "Billing dispute requires billing team intervention. Ticket TKT-JO002."
                ),
                "type": "experience",
                "context": "support_ticket:TKT-JO002",
                "metadata": {"customer_name": "James Okonkwo", "plan": "business"},
                "created_at": ago(5).isoformat(),
            },
            {
                "id": "seed-jo-3",
                "text": (
                    "James Okonkwo profile: Finance team admin at FinBridge Capital. Business plan, 45 members. "
                    "Uses Edge 124 on Windows 10. Has a pattern of billing issues. Prefers phone contact."
                ),
                "type": "world",
                "context": "customer_profile",
                "metadata": {"customer_name": "James Okonkwo", "plan": "business"},
                "created_at": ago(50).isoformat(),
            },
        ],
        "cust-003": [  # Priya Sharma
            {
                "id": "seed-ps-1",
                "text": (
                    "Priya Sharma had email notifications going to spam. "
                    "Fixed by adding nexora.cloud to email allowlist/whitelist. "
                    "Also experienced notification badge count bug — fixed by clearing notification cache."
                ),
                "type": "experience",
                "context": "support_history",
                "metadata": {"customer_name": "Priya Sharma", "plan": "starter"},
                "created_at": ago(10).isoformat(),
            },
        ],
        "cust-005": [  # Elena Rodriguez
            {
                "id": "seed-er-1",
                "text": (
                    "Elena Rodriguez's desktop sync client showed 'Sync Paused' for 3 days. "
                    "Root cause: storage quota exceeded on Starter plan (50GB limit). "
                    "SUCCESSFUL RESOLUTION: Archived old projects to free storage space."
                ),
                "type": "experience",
                "context": "support_history",
                "metadata": {"customer_name": "Elena Rodriguez", "plan": "starter"},
                "created_at": ago(14).isoformat(),
            },
        ],
    }

    for customer_id, memories in demo_memories.items():
        bank_id = _get_bank_id(customer_id)
        if bank_id not in _fallback_store:
            _fallback_store[bank_id] = []
        # Only seed if bank is currently empty
        if not _fallback_store[bank_id]:
            _fallback_store[bank_id] = memories

    logger.info(f"Seeded fallback memory store for {len(demo_memories)} demo customers.")
