from fastapi import APIRouter

from app.api.deps import ActiveOrg, CurrentUser, DbSession
from app.schemas.identity import MeResponse, MyOrganization, MyOrganizationsResponse
from app.service.organizations import OrganizationService

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=MeResponse)
async def get_me(user: CurrentUser) -> MeResponse:
    return MeResponse.model_validate(user)


@router.get("/organizations", response_model=MyOrganizationsResponse)
async def my_organizations(user: CurrentUser, session: DbSession) -> MyOrganizationsResponse:
    rows = await OrganizationService(session).list_mine(user)
    return MyOrganizationsResponse(data=[MyOrganization(id=o.id, name=o.name, role=r) for o, r in rows])


@router.get("/active-organization", response_model=MyOrganization)
async def active_organization(ctx: ActiveOrg) -> MyOrganization:
    """Validates X-Organization-ID for the caller; the frontend uses it to confirm a switch."""
    return MyOrganization(id=ctx.organization_id, name=ctx.organization_name, role=ctx.role)
