from fastapi import APIRouter
from app.api.routes import chat, customers, memory, tickets, knowledge, demo

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(chat.router)
api_router.include_router(customers.router)
api_router.include_router(memory.router)
api_router.include_router(tickets.router)
api_router.include_router(knowledge.router)
api_router.include_router(demo.router)
