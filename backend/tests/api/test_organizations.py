import uuid

import pytest

from tests.factories import add_member, auth_headers, create_org, create_user, seeded


@pytest.fixture
async def world(session_factory):
    async with seeded(session_factory) as s:
        root = await create_user(s, "root@nexora.io", super_admin=True)
        admin_a = await create_user(s, "admin@a.io")
        tech_a = await create_user(s, "tech@a.io")
        outsider = await create_user(s, "out@b.io")
        org_a = await create_org(s, "Org A", root)
        org_b = await create_org(s, "Org B", root)
        await add_member(s, org_a, admin_a, "org_admin")
        await add_member(s, org_a, tech_a, "technician")
        await add_member(s, org_b, outsider, "org_admin")
    return {"root": root, "admin_a": admin_a, "tech_a": tech_a, "outsider": outsider,
            "org_a": org_a, "org_b": org_b}


async def test_my_organizations_lists_only_mine_with_role(client, world) -> None:
    response = await client.get("/api/v1/me/organizations", headers=auth_headers(world["tech_a"]))
    assert response.status_code == 200
    assert response.json() == {"data": [
        {"id": str(world["org_a"].id), "name": "Org A", "role": "technician"}]}


async def test_super_admin_creates_organization(client, world) -> None:
    response = await client.post("/api/v1/organizations", json={"name": "Org C"},
                                 headers=auth_headers(world["root"]))
    assert response.status_code == 201
    assert response.json()["name"] == "Org C"


async def test_non_super_admin_cannot_create_organization(client, world) -> None:
    response = await client.post("/api/v1/organizations", json={"name": "X"},
                                 headers=auth_headers(world["admin_a"]))
    assert response.status_code == 403
    assert response.json()["code"] == "SUPER_ADMIN_REQUIRED"


async def test_org_admin_adds_member(client, world, session_factory) -> None:
    async with seeded(session_factory) as s:
        await create_user(s, "new@a.io")
    response = await client.post(f"/api/v1/organizations/{world['org_a'].id}/memberships",
                                 json={"email": "NEW@a.io", "role": "requester"},
                                 headers=auth_headers(world["admin_a"]))
    assert response.status_code == 201
    assert response.json()["role"] == "requester"
    assert response.json()["organization_id"] == str(world["org_a"].id)


async def test_super_admin_adds_member_to_any_org(client, world) -> None:
    response = await client.post(f"/api/v1/organizations/{world['org_b'].id}/memberships",
                                 json={"email": "tech@a.io", "role": "technician"},
                                 headers=auth_headers(world["root"]))
    assert response.status_code == 201


async def test_technician_cannot_add_member(client, world) -> None:
    response = await client.post(f"/api/v1/organizations/{world['org_a'].id}/memberships",
                                 json={"email": "out@b.io", "role": "requester"},
                                 headers=auth_headers(world["tech_a"]))
    assert response.status_code == 403
    assert response.json()["code"] == "INSUFFICIENT_ROLE"


async def test_admin_of_other_org_gets_404(client, world) -> None:
    response = await client.post(f"/api/v1/organizations/{world['org_a'].id}/memberships",
                                 json={"email": "tech@a.io", "role": "requester"},
                                 headers=auth_headers(world["outsider"]))
    assert response.status_code == 404
    assert response.json()["code"] == "ORGANIZATION_NOT_FOUND"


async def test_unknown_user_and_duplicate_member(client, world) -> None:
    url = f"/api/v1/organizations/{world['org_a'].id}/memberships"
    headers = auth_headers(world["admin_a"])
    missing = await client.post(url, json={"email": "nobody@a.io", "role": "requester"}, headers=headers)
    duplicate = await client.post(url, json={"email": "tech@a.io", "role": "requester"}, headers=headers)
    assert (missing.status_code, missing.json()["code"]) == (404, "USER_NOT_FOUND")
    assert (duplicate.status_code, duplicate.json()["code"]) == (409, "ALREADY_MEMBER")


async def test_org_header_rules(client, world) -> None:
    # /api/v1/teams (Task 7) is tenant-scoped; until then use the probe endpoint below.
    url = "/api/v1/me/active-organization"
    user = world["tech_a"]
    missing = await client.get(url, headers=auth_headers(user))
    bad = await client.get(url, headers={**auth_headers(user), "X-Organization-ID": "nope"})
    other = await client.get(url, headers=auth_headers(user, world["org_b"]))
    unknown = await client.get(url, headers={**auth_headers(user), "X-Organization-ID": str(uuid.uuid4())})
    ok = await client.get(url, headers=auth_headers(user, world["org_a"]))
    assert (missing.status_code, missing.json()["code"]) == (400, "ORGANIZATION_REQUIRED")
    assert (bad.status_code, bad.json()["code"]) == (400, "INVALID_ORGANIZATION_ID")
    assert (other.status_code, other.json()["code"]) == (403, "NOT_A_MEMBER")
    assert (unknown.status_code, unknown.json()["code"]) == (403, "NOT_A_MEMBER")
    assert ok.json() == {"id": str(world["org_a"].id), "name": "Org A", "role": "technician"}


async def test_blank_organization_name_is_422(client, world) -> None:
    response = await client.post("/api/v1/organizations", json={"name": "   "},
                                 headers=auth_headers(world["root"]))
    assert response.status_code == 422
