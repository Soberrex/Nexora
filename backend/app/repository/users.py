from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_firebase_uid(self, uid: str) -> User | None:
        return await self._session.scalar(select(User).where(User.firebase_uid == uid))

    async def get_by_email(self, email: str) -> User | None:
        return await self._session.scalar(select(User).where(User.email == email))

    def add(self, user: User) -> None:
        self._session.add(user)
