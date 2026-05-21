from fastapi import APIRouter

from src.app.health import router as health_router
from src.app.v1 import v1_router

api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)

# Root-level routes (no /api prefix) — health checks, etc.
root_router = APIRouter()
root_router.include_router(health_router)

__all__ = ["api_router", "root_router"]
