import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.domain import Team, TeamMembership
from app.repository.memberships import MembershipRepository
from app.repository.teams import TeamRepository


class TeamService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._teams = TeamRepository(session)
        self._memberships = MembershipRepository(session)

    async def list_page(self, organization_id: uuid.UUID, limit: int,
                        after: str | None) -> tuple[list[tuple[Team, int]], str | None]:
        try:
            after_id = uuid.UUID(after) if after else None
        except ValueError:
            raise AppError("Invalid cursor", status_code=400, code="INVALID_CURSOR") from None
        rows = await self._teams.list_page(organization_id, limit, after_id)
        next_cursor = str(rows[limit - 1][0].id) if len(rows) > limit else None
        return rows[:limit], next_cursor

    async def create(self, organization_id: uuid.UUID, name: str) -> Team:
        name = name.strip()
        if await self._teams.name_exists(organization_id, name):
            raise AppError("A team with this name already exists", status_code=409, code="TEAM_NAME_TAKEN")
        team = Team(organization_id=organization_id, name=name)
        self._teams.add(team)
        await self._session.flush()
        return team

    async def add_member(self, organization_id: uuid.UUID, team_id: uuid.UUID,
                         user_id: uuid.UUID) -> TeamMembership:
        if await self._teams.get(organization_id, team_id) is None:
            raise AppError("Team not found", status_code=404, code="TEAM_NOT_FOUND")
        if await self._memberships.get_active(organization_id, user_id) is None:
            raise AppError("User is not a member of this organization", status_code=400,
                           code="USER_NOT_IN_ORGANIZATION")
        if await self._teams.has_member(team_id, user_id):
            raise AppError("User is already in this team", status_code=409, code="ALREADY_TEAM_MEMBER")
        member = TeamMembership(organization_id=organization_id, team_id=team_id, user_id=user_id)
        self._teams.add(member)
        await self._session.flush()
        return member
