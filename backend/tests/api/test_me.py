from sqlalchemy import func, select

from app.config import settings
from app.domain import User
from tests.factories import create_user, seeded


async def test_missing_token_is_401(client) -> None:
    response = await client.get("/api/v1/me")
    assert response.status_code == 401
    assert response.json()["code"] == "NOT_AUTHENTICATED"


async def test_invalid_token_is_401(client) -> None:
    response = await client.get("/api/v1/me", headers={"Authorization": "Bearer garbage"})
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_TOKEN"


async def test_first_call_provisions_user_once(client, session_factory) -> None:
    headers = {"Authorization": "Bearer fb-1|Alice@Example.com"}
    first = await client.get("/api/v1/me", headers=headers)
    second = await client.get("/api/v1/me", headers=headers)
    assert first.status_code == second.status_code == 200
    body = first.json()
    assert body["email"] == "alice@example.com"
    assert body["full_name"] == "alice"
    assert body["is_super_admin"] is False
    assert second.json()["id"] == body["id"]
    async with session_factory() as s:
        assert await s.scalar(select(func.count()).select_from(User)) == 1


async def test_email_linked_to_other_firebase_account_is_409(client, session_factory) -> None:
    async with seeded(session_factory) as s:
        await create_user(s, "bob@example.com", uid="fb-original")
    response = await client.get("/api/v1/me", headers={"Authorization": "Bearer fb-other|bob@example.com"})
    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_CONFLICT"


async def test_unverified_email_rejected_when_required(client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "AUTH_REQUIRE_VERIFIED_EMAIL", True)
    response = await client.get("/api/v1/me", headers={"Authorization": "Bearer fb-2|c@x.io|unverified"})
    assert response.status_code == 403
    assert response.json()["code"] == "EMAIL_NOT_VERIFIED"


async def test_unverified_email_allowed_when_not_required(client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "AUTH_REQUIRE_VERIFIED_EMAIL", False)
    response = await client.get("/api/v1/me", headers={"Authorization": "Bearer fb-3|d@x.io|unverified"})
    assert response.status_code == 200


async def test_inactive_user_is_403(client, session_factory) -> None:
    async with seeded(session_factory) as s:
        user = await create_user(s, "gone@x.io", uid="fb-gone")
        user.is_active = False
    response = await client.get("/api/v1/me", headers={"Authorization": "Bearer fb-gone|gone@x.io"})
    assert response.status_code == 403
    assert response.json()["code"] == "USER_INACTIVE"
