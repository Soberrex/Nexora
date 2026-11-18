from app.service.users import UserService
from tests.factories import create_user, seeded


async def test_promote_to_super_admin(session_factory) -> None:
    async with seeded(session_factory) as s:
        await create_user(s, "boss@x.io")
    async with session_factory() as s, s.begin():
        assert await UserService(s).promote_to_super_admin("BOSS@x.io") is True
        assert await UserService(s).promote_to_super_admin("missing@x.io") is False
