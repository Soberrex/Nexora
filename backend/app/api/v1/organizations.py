import uuid

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.identity import (
    MembershipCreate,
    MembershipResponse,
    OrganizationCreate,
    OrganizationResponse,
)
from app.service.organizations import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(body: OrganizationCreate, user: CurrentUser,
                              session: DbSession) -> OrganizationResponse:
    org = await OrganizationService(session).create(user, body.name)
    return OrganizationResponse.model_validate(org)


@router.post("/{organization_id}/memberships", response_model=MembershipResponse,
             status_code=status.HTTP_201_CREATED)
async def add_membership(organization_id: uuid.UUID, body: MembershipCreate, user: CurrentUser,
                         session: DbSession) -> MembershipResponse:
    membership = await OrganizationService(session).add_member(user, organization_id, body.email, body.role)
    return MembershipResponse.model_validate(membership)
