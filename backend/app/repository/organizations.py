import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import Organization


class OrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active(self, organization_id: uuid.UUID) -> Organization | None:
        org = await self._session.get(Organization, organization_id)
        return org if org is not None and org.is_active else None

    def add(self, org: Organization) -> None:
        self._session.add(org)
