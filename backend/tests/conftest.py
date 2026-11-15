import os
import subprocess
import sys
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings
from app.core.db_url import build_async_db_config
from app.database import get_db_session
from app.main import app

BACKEND_DIR = Path(__file__).resolve().parents[1]
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL") or settings.TEST_DATABASE_URL

# Tables emptied before each DB test, children first.
TRUNCATE_TABLES: list[str] = [
    "team_memberships",
    "teams",
    "organization_memberships",
    "organizations",
    "users",
]


@pytest.fixture(scope="session")
def migrated_db() -> str:
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL is not set")
    env = {**os.environ, "DATABASE_URL": TEST_DATABASE_URL, "MIGRATION_DATABASE_URL": ""}
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=BACKEND_DIR, env=env, check=True)
    return TEST_DATABASE_URL


@pytest_asyncio.fixture
async def db_engine(migrated_db: str) -> AsyncIterator[AsyncEngine]:
    cfg = build_async_db_config(migrated_db)
    engine = create_async_engine(cfg.url, connect_args=cfg.connect_args, poolclass=NullPool)
    if TRUNCATE_TABLES:
        async with engine.begin() as conn:
            await conn.exec_driver_sql(f"TRUNCATE {', '.join(TRUNCATE_TABLES)} RESTART IDENTITY CASCADE")
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(db_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(db_engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture
async def client(session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncClient]:
    async def _session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session, session.begin():
            yield session

    app.dependency_overrides[get_db_session] = _session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def bare_client() -> AsyncIterator[AsyncClient]:
    """Client without a database (for tests that override get_db_session themselves)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()
