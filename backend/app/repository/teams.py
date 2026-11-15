import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import Team, TeamMembership


class TeamRepository:
    """All queries filter by organization_id explicitly; RLS is the second line of defense."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_page(self, organization_id: uuid.UUID, limit: int,
                        after: uuid.UUID | None) -> list[tuple[Team, int]]:
        count = (select(func.count(TeamMembership.id)).where(TeamMembership.team_id == Team.id)
                 .scalar_subquery())
        stmt = (select(Team, count).where(Team.organization_id == organization_id, Team.is_active.is_(True))
                .order_by(Team.id).limit(limit + 1))
        if after is not None:
            stmt = stmt.where(Team.id > after)
        return [(team, n) for team, n in (await self._session.execute(stmt)).all()]

    async def get(self, organization_id: uuid.UUID, team_id: uuid.UUID) -> Team | None:
        return await self._session.scalar(
            select(Team).where(Team.id == team_id, Team.organization_id == organization_id))

    async def name_exists(self, organization_id: uuid.UUID, name: str) -> bool:
        found = await self._session.scalar(
            select(Team.id).where(Team.organization_id == organization_id,
                                  func.lower(Team.name) == name.lower()))
        return found is not None

    async def has_member(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        found = await self._session.scalar(select(TeamMembership.id).where(
            TeamMembership.team_id == team_id, TeamMembership.user_id == user_id))
        return found is not None

    def add(self, obj: Team | TeamMembership) -> None:
        self._session.add(obj)
