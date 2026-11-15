import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str


class DbHealthResponse(BaseModel):
    status: str
    database: str


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness check; does not touch the database (safe for Render cold starts)."""
    return HealthResponse(status="ok", version=settings.APP_VERSION)


@router.get("/db", response_model=None, responses={200: {"model": DbHealthResponse},
                                                  503: {"model": DbHealthResponse}})
async def db_health_check(session: Annotated[AsyncSession, Depends(get_db_session)]) -> JSONResponse:
    """Readiness check using a lightweight query."""
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:  # boundary: any failure (driver, auth, network) means "not ready"
        logger.warning("Database health check failed: %s", type(exc).__name__)
        return JSONResponse(status_code=503, content={"status": "unavailable", "database": "disconnected"})
    return JSONResponse(status_code=200, content={"status": "ok", "database": "connected"})
