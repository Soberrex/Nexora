import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.auth import InvalidTokenError, TokenVerifier, get_token_verifier
from app.core.errors import AppError
from app.core.tenancy import set_org_context, set_user_context
from app.database import get_db_session
from app.domain import User
from app.repository.memberships import MembershipRepository
from app.repository.organizations import OrganizationRepository
from app.service.users import UserService

_bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    session: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    verifier: Annotated[TokenVerifier, Depends(get_token_verifier)],
) -> User:
    if credentials is None:
        raise AppError("Not authenticated", status_code=401, code="NOT_AUTHENTICATED")
    try:
        token = await verifier.verify(credentials.credentials)
    except InvalidTokenError:
        raise AppError("Invalid or expired token", status_code=401, code="INVALID_TOKEN") from None
    if settings.AUTH_REQUIRE_VERIFIED_EMAIL and not token.email_verified:
        raise AppError("Email address is not verified", status_code=403, code="EMAIL_NOT_VERIFIED")

    user = await UserService(session).get_or_provision(token)
    if not user.is_active:
        raise AppError("User account is disabled", status_code=403, code="USER_INACTIVE")
    await set_user_context(session, user.id)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


@dataclass(frozen=True)
class OrgContext:
    user: User
    organization_id: uuid.UUID
    organization_name: str
    role: str


async def get_org_context(
    session: DbSession,
    user: CurrentUser,
    x_organization_id: Annotated[str | None, Header(alias="X-Organization-ID")] = None,
) -> OrgContext:
    if not x_organization_id:
        raise AppError("X-Organization-ID header is required", status_code=400, code="ORGANIZATION_REQUIRED")
    try:
        organization_id = uuid.UUID(x_organization_id)
    except ValueError:
        raise AppError("X-Organization-ID is not a valid id", status_code=400,
                       code="INVALID_ORGANIZATION_ID") from None

    org = await OrganizationRepository(session).get_active(organization_id)
    membership = await MembershipRepository(session).get_active(organization_id, user.id) if org else None
    if org is None or membership is None:
        raise AppError("You are not a member of this organization", status_code=403, code="NOT_A_MEMBER")

    await set_org_context(session, organization_id)
    return OrgContext(user=user, organization_id=organization_id, organization_name=org.name,
                      role=membership.role)


ActiveOrg = Annotated[OrgContext, Depends(get_org_context)]


def require_roles(*roles: str):  # returns a FastAPI dependency
    async def _check(ctx: ActiveOrg) -> OrgContext:
        if ctx.role not in roles:
            raise AppError("Your role does not allow this action", status_code=403, code="INSUFFICIENT_ROLE")
        return ctx

    return _check
