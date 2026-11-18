import pytest
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError

from app.core.tenancy import set_org_context, set_user_context
from app.domain import OrganizationMembership, Team
from tests.factories import add_member, create_org, create_team, create_user, seeded


@pytest.fixture
async def two_orgs(session_factory):
    async with seeded(session_factory) as s:
        alice = await create_user(s, "alice@a.io")
        org_a = await create_org(s, "Org A", alice)
        org_b = await create_org(s, "Org B", alice)
        await add_member(s, org_a, alice, "org_admin")
        await add_member(s, org_b, alice, "requester")
        await create_team(s, org_a, "A-team")
        await create_team(s, org_b, "B-team")
    return alice, org_a, org_b


async def test_queries_without_where_only_see_active_org(session_factory, two_orgs) -> None:
    _, org_a, _ = two_orgs
    async with session_factory() as s, s.begin():
        await set_org_context(s, org_a.id)
        names = (await s.scalars(select(Team.name))).all()
    assert names == ["A-team"]


async def test_no_context_sees_nothing(session_factory, two_orgs) -> None:
    async with session_factory() as s, s.begin():
        assert (await s.scalars(select(Team))).all() == []
        assert (await s.scalars(select(OrganizationMembership))).all() == []


async def test_user_sees_own_memberships_across_orgs(session_factory, two_orgs) -> None:
    alice, _, _ = two_orgs
    async with session_factory() as s, s.begin():
        await set_user_context(s, alice.id)
        roles = sorted((await s.scalars(select(OrganizationMembership.role))).all())
    assert roles == ["org_admin", "requester"]


async def test_cannot_insert_into_another_org(session_factory, two_orgs) -> None:
    _, org_a, org_b = two_orgs
    with pytest.raises(DBAPIError, match="row-level security"):
        async with session_factory() as s, s.begin():
            await set_org_context(s, org_a.id)
            s.add(Team(organization_id=org_b.id, name="sneaky"))
            await s.flush()


async def test_context_does_not_leak_to_next_transaction(session_factory, two_orgs) -> None:
    _, org_a, _ = two_orgs
    async with session_factory() as s:
        async with s.begin():
            await set_org_context(s, org_a.id)
        async with s.begin():
            assert (await s.scalars(select(Team))).all() == []
