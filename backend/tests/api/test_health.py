from collections.abc import AsyncIterator

from httpx import AsyncClient
from sqlalchemy.exc import OperationalError

from app.database import get_db_session
from app.main import app


async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


async def test_unknown_route_uses_standard_error_shape(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found", "code": None}


async def test_openapi_docs_available(client: AsyncClient) -> None:
    assert (await client.get("/docs")).status_code == 200
    assert (await client.get("/openapi.json")).status_code == 200


class _OkSession:
    async def execute(self, *_: object) -> None:
        return None


class _FailingSession:
    async def execute(self, *_: object) -> None:
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))


async def test_db_health_ok(client: AsyncClient) -> None:
    async def _override() -> AsyncIterator[_OkSession]:
        yield _OkSession()

    app.dependency_overrides[get_db_session] = _override
    response = await client.get("/api/v1/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


async def test_db_health_unavailable_returns_503_without_leaking_error(client: AsyncClient) -> None:
    async def _override() -> AsyncIterator[_FailingSession]:
        yield _FailingSession()

    app.dependency_overrides[get_db_session] = _override
    response = await client.get("/api/v1/health/db")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "disconnected"}
    assert "connection refused" not in response.text


class _DriverErrorSession:
    async def execute(self, *_: object) -> None:
        raise RuntimeError("password authentication failed for user nexora")


async def test_db_health_maps_raw_driver_errors_to_503(client: AsyncClient) -> None:
    async def _override() -> AsyncIterator[_DriverErrorSession]:
        yield _DriverErrorSession()

    app.dependency_overrides[get_db_session] = _override
    response = await client.get("/api/v1/health/db")
    assert response.status_code == 503
    assert "password" not in response.text
