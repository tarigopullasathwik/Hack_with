"""
RecallDesk — FastAPI application entry point.
"""
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database.db import Base, engine
from app.models import Customer, Ticket, Message, KnowledgeArticle, DemoScenario  # noqa: register models
from app.api import api_router
from app import hindsight as mem

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured.")

    # Initialise Hindsight memory layer
    hindsight_ok = await mem.init_hindsight(
        llm_provider=settings.HINDSIGHT_LLM_PROVIDER,
        llm_model=settings.HINDSIGHT_LLM_MODEL,
        llm_api_key=settings.get_hindsight_llm_key(),
        embedded=settings.HINDSIGHT_EMBEDDED,
        base_url=settings.HINDSIGHT_BASE_URL,
        hindsight_api_key=settings.HINDSIGHT_API_KEY,
        llm_base_url=settings.get_hindsight_llm_base_url() or "",
        embeddings_provider=settings.HINDSIGHT_EMBEDDINGS_PROVIDER,
        reranker_provider=settings.HINDSIGHT_RERANKER_PROVIDER,
        start_timeout=settings.HINDSIGHT_START_TIMEOUT,
    )
    if hindsight_ok:
        logger.info("✓ Hindsight memory layer ready.")
    else:
        logger.warning("⚠ Hindsight server not reachable — using in-process fallback memory store.")

    # Seed demo customer memories (in fallback store if Hindsight not connected)
    from app.hindsight.manager import seed_demo_memories
    seed_demo_memories()
    logger.info("✓ Demo memory banks seeded.")

    yield  # Application is running

    # ── Shutdown ─────────────────────────────────────────────────────────────
    mem.shutdown_hindsight()
    logger.info("RecallDesk shut down cleanly.")


app = FastAPI(
    title="RecallDesk API",
    description="AI customer support agent with Hindsight persistent memory.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routes
app.include_router(api_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "hindsight": mem.get_status(),
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )
