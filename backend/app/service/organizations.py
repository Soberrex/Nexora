import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.tenancy import enable_rls_bypass, set_org_context
from app.domain import Organization, OrganizationMembership, User
from app.repository.memberships import MembershipRepository
from app.repository.organizations import OrganizationRepository
from app.repository.users import UserRepository
from app.service.users import normalize_email

_NOT_FOUND = AppError("Organization not found", status_code=404, code="ORGANIZATION_NOT_FOUND")


class OrganizationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._orgs = OrganizationRepository(session)
        self._memberships = MembershipRepository(session)
        self._users = UserRepository(session)

    async def list_mine(self, user: User) -> list[tuple[Organization, str]]:
        return await self._memberships.list_for_user(user.id)

    async def create(self, actor: User, name: str) -> Organization:
        if not actor.is_super_admin:
            raise AppError("Super admin required", status_code=403, code="SUPER_ADMIN_REQUIRED")
        org = Organization(name=name.strip(), created_by=actor.id)
        self._orgs.add(org)
        await self._session.flush()
        await self._session.refresh(org)
        return org

    async def add_member(self, actor: User, organization_id: uuid.UUID, email: str,
                         role: str) -> OrganizationMembership:
        if await self._orgs.get_active(organization_id) is None:
            raise _NOT_FOUND
        if actor.is_super_admin:
            await enable_rls_bypass(self._session)
        else:
            await set_org_context(self._session, organization_id)
            mine = await self._memberships.get_active(organization_id, actor.id)
            if mine is None:
                raise _NOT_FOUND
            if mine.role != "org_admin":
                raise AppError("Only organization admins can add members", status_code=403,
                               code="INSUFFICIENT_ROLE")

        target = await self._users.get_by_email(normalize_email(email))
        if target is None:
            raise AppError("User not found. They must sign in once before being added.",
                           status_code=404, code="USER_NOT_FOUND")
        if await self._memberships.get(organization_id, target.id) is not None:
            raise AppError("User is already a member", status_code=409, code="ALREADY_MEMBER")

        membership = OrganizationMembership(organization_id=organization_id, user_id=target.id, role=role)
        self._memberships.add(membership)
        await self._session.flush()
        return membership
