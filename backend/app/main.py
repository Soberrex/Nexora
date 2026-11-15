import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as api_v1_router
from app.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.database import engine

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Nexora API starting (env=%s)", settings.ENVIRONMENT)
    yield
    await engine.dispose()
    logger.info("Nexora API stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Nexora API",
        version=settings.APP_VERSION,
        description="Multi-tenant enterprise service operations platform",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(api_v1_router)
    return app


app = create_app()
