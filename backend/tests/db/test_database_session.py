from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker


async def test_request_session_is_transactional(session_factory: async_sessionmaker) -> None:
    async with session_factory() as session, session.begin():
        await session.execute(text("SELECT set_config('app.probe', 'x', true)"))
        value = await session.scalar(text("SELECT current_setting('app.probe', true)"))
    assert value == "x"


async def test_db_health_against_real_database(client) -> None:
    response = await client.get("/api/v1/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}
