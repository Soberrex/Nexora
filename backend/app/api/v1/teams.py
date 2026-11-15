import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import ActiveOrg, DbSession, OrgContext, require_roles
from app.schemas.identity import (
    TeamCreate,
    TeamListResponse,
    TeamMemberCreate,
    TeamMemberResponse,
    TeamResponse,
)
from app.service.teams import TeamService

router = APIRouter(prefix="/teams", tags=["teams"])
TeamManager = Annotated[OrgContext, Depends(require_roles("org_admin", "admin"))]


@router.get("", response_model=TeamListResponse)
async def list_teams(ctx: ActiveOrg, session: DbSession,
                     limit: Annotated[int, Query(ge=1, le=100)] = 50,
                     after: str | None = None) -> TeamListResponse:
    rows, next_cursor = await TeamService(session).list_page(ctx.organization_id, limit, after)
    return TeamListResponse(data=[TeamResponse(id=t.id, name=t.name, member_count=n) for t, n in rows],
                            next_cursor=next_cursor)


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(body: TeamCreate, ctx: TeamManager, session: DbSession) -> TeamResponse:
    team = await TeamService(session).create(ctx.organization_id, body.name)
    return TeamResponse(id=team.id, name=team.name, member_count=0)


@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(team_id: uuid.UUID, body: TeamMemberCreate, ctx: TeamManager,
                          session: DbSession) -> TeamMemberResponse:
    member = await TeamService(session).add_member(ctx.organization_id, team_id, body.user_id)
    return TeamMemberResponse(team_id=member.team_id, user_id=member.user_id)
