"""Per-transaction tenant context read by the PostgreSQL RLS policies (migration 0002).

set_config(..., is_local => true) lasts only until the end of the current transaction,
so a pooled connection never carries one request's tenant into the next.
"""

import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_SET = text("SELECT set_config(:name, :value, true)")


async def set_user_context(session: AsyncSession, user_id: uuid.UUID) -> None:
    await session.execute(_SET, {"name": "app.current_user_id", "value": str(user_id)})


async def set_org_context(session: AsyncSession, organization_id: uuid.UUID) -> None:
    await session.execute(_SET, {"name": "app.current_organization_id", "value": str(organization_id)})


async def enable_rls_bypass(session: AsyncSession) -> None:
    """Only for super-admin operations; callers must have checked is_super_admin."""
    await session.execute(_SET, {"name": "app.bypass_rls", "value": "on"})
