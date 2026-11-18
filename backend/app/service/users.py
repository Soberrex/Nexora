from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import VerifiedToken
from app.core.errors import AppError
from app.domain import User
from app.repository.users import UserRepository


def normalize_email(email: str) -> str:
    return email.strip().lower()


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = UserRepository(session)

    async def get_or_provision(self, token: VerifiedToken) -> User:
        user = await self._users.get_by_firebase_uid(token.uid)
        if user is not None:
            return user

        email = normalize_email(token.email)
        if await self._users.get_by_email(email) is not None:
            raise AppError(
                "This email is linked to a different sign-in account",
                status_code=409,
                code="EMAIL_CONFLICT",
            )

        user = User(firebase_uid=token.uid, email=email, full_name=token.name or email.split("@")[0])
        try:
            async with self._session.begin_nested():
                self._users.add(user)
                await self._session.flush()
        except IntegrityError:
            # A concurrent first request created the same user; use that row.
            existing = await self._users.get_by_firebase_uid(token.uid)
            if existing is None:
                raise
            return existing
        return user

    async def promote_to_super_admin(self, email: str) -> bool:
        user = await self._users.get_by_email(normalize_email(email))
        if user is None:
            return False
        user.is_super_admin = True
        await self._session.flush()
        return True
