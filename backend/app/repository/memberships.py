import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import Organization, OrganizationMembership


class MembershipRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, organization_id: uuid.UUID, user_id: uuid.UUID) -> OrganizationMembership | None:
        return await self._session.scalar(select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user_id))

    async def get_active(
        self, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> OrganizationMembership | None:
        membership = await self.get(organization_id, user_id)
        return membership if membership is not None and membership.is_active else None

    async def list_for_user(self, user_id: uuid.UUID) -> list[tuple[Organization, str]]:
        rows = await self._session.execute(
            select(Organization, OrganizationMembership.role)
            .join(OrganizationMembership, OrganizationMembership.organization_id == Organization.id)
            .where(OrganizationMembership.user_id == user_id,
                   OrganizationMembership.is_active.is_(True),
                   Organization.is_active.is_(True))
            .order_by(Organization.name))
        return [(org, role) for org, role in rows.all()]

    def add(self, membership: OrganizationMembership) -> None:
        self._session.add(membership)
