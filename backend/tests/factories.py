from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.tenancy import enable_rls_bypass
from app.domain import Organization, OrganizationMembership, Team, User


@asynccontextmanager
async def seeded(factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    """Session with RLS bypass for arranging test data; commits on exit."""
    async with factory() as session, session.begin():
        await enable_rls_bypass(session)
        yield session


async def create_user(session: AsyncSession, email: str, *, uid: str | None = None,
                      super_admin: bool = False) -> User:
    user = User(firebase_uid=uid or f"uid-{email}", email=email, full_name=email.split("@")[0],
                is_super_admin=super_admin)
    session.add(user)
    await session.flush()
    return user


async def create_org(session: AsyncSession, name: str, creator: User) -> Organization:
    org = Organization(name=name, created_by=creator.id)
    session.add(org)
    await session.flush()
    return org


async def add_member(session: AsyncSession, org: Organization, user: User,
                     role: str = "requester") -> OrganizationMembership:
    membership = OrganizationMembership(organization_id=org.id, user_id=user.id, role=role)
    session.add(membership)
    await session.flush()
    return membership


async def create_team(session: AsyncSession, org: Organization, name: str) -> Team:
    team = Team(organization_id=org.id, name=name)
    session.add(team)
    await session.flush()
    return team


def auth_headers(user: User, org: Organization | None = None) -> dict[str, str]:
    """Headers understood by tests.fakes.FakeTokenVerifier (token = 'uid|email')."""
    headers = {"Authorization": f"Bearer {user.firebase_uid}|{user.email}"}
    if org is not None:
        headers["X-Organization-ID"] = str(org.id)
    return headers
