import pytest

from tests.factories import add_member, auth_headers, create_org, create_team, create_user, seeded


@pytest.fixture
async def world(session_factory):
    async with seeded(session_factory) as s:
        admin = await create_user(s, "admin@a.io")
        req = await create_user(s, "req@a.io")
        b_user = await create_user(s, "user@b.io")
        org_a = await create_org(s, "Org A", admin)
        org_b = await create_org(s, "Org B", admin)
        await add_member(s, org_a, admin, "admin")
        await add_member(s, org_a, req, "requester")
        await add_member(s, org_b, b_user, "org_admin")
        b_team = await create_team(s, org_b, "B-ops")
    return {"admin": admin, "req": req, "b_user": b_user, "org_a": org_a, "org_b": org_b, "b_team": b_team}


async def test_admin_creates_and_lists_teams(client, world) -> None:
    h = auth_headers(world["admin"], world["org_a"])
    created = await client.post("/api/v1/teams", json={"name": "Service Desk"}, headers=h)
    assert created.status_code == 201
    listed = await client.get("/api/v1/teams", headers=h)
    assert listed.json() == {
        "data": [{"id": created.json()["id"], "name": "Service Desk", "member_count": 0}],
        "next_cursor": None,
    }


async def test_duplicate_team_name_is_409(client, world) -> None:
    h = auth_headers(world["admin"], world["org_a"])
    await client.post("/api/v1/teams", json={"name": "Ops"}, headers=h)
    again = await client.post("/api/v1/teams", json={"name": "Ops"}, headers=h)
    assert (again.status_code, again.json()["code"]) == (409, "TEAM_NAME_TAKEN")


async def test_same_team_name_allowed_in_other_org(client, world) -> None:
    h = auth_headers(world["b_user"], world["org_b"])
    assert (await client.post("/api/v1/teams", json={"name": "Service Desk"}, headers=h)).status_code == 201


async def test_requester_cannot_create_team(client, world) -> None:
    response = await client.post("/api/v1/teams", json={"name": "X"},
                                 headers=auth_headers(world["req"], world["org_a"]))
    assert (response.status_code, response.json()["code"]) == (403, "INSUFFICIENT_ROLE")


async def test_list_never_shows_other_org_teams(client, world) -> None:
    listed = await client.get("/api/v1/teams", headers=auth_headers(world["req"], world["org_a"]))
    assert listed.json()["data"] == []


async def test_add_member_to_team(client, world) -> None:
    h = auth_headers(world["admin"], world["org_a"])
    team_id = (await client.post("/api/v1/teams", json={"name": "Desk"}, headers=h)).json()["id"]
    added = await client.post(f"/api/v1/teams/{team_id}/members", json={"user_id": str(world["req"].id)},
                              headers=h)
    assert added.status_code == 201
    again = await client.post(f"/api/v1/teams/{team_id}/members", json={"user_id": str(world["req"].id)},
                              headers=h)
    assert (again.status_code, again.json()["code"]) == (409, "ALREADY_TEAM_MEMBER")
    listed = await client.get("/api/v1/teams", headers=h)
    assert listed.json()["data"][0]["member_count"] == 1


async def test_cannot_add_non_member_or_touch_other_org_team(client, world) -> None:
    h = auth_headers(world["admin"], world["org_a"])
    team_id = (await client.post("/api/v1/teams", json={"name": "Desk"}, headers=h)).json()["id"]
    outsider = await client.post(f"/api/v1/teams/{team_id}/members",
                                 json={"user_id": str(world["b_user"].id)}, headers=h)
    foreign = await client.post(f"/api/v1/teams/{world['b_team'].id}/members",
                                json={"user_id": str(world["req"].id)}, headers=h)
    assert (outsider.status_code, outsider.json()["code"]) == (400, "USER_NOT_IN_ORGANIZATION")
    assert (foreign.status_code, foreign.json()["code"]) == (404, "TEAM_NOT_FOUND")


async def test_pagination(client, world) -> None:
    h = auth_headers(world["admin"], world["org_a"])
    for name in ("t1", "t2", "t3"):
        await client.post("/api/v1/teams", json={"name": name}, headers=h)
    page1 = (await client.get("/api/v1/teams?limit=2", headers=h)).json()
    page2 = (await client.get(f"/api/v1/teams?limit=2&after={page1['next_cursor']}", headers=h)).json()
    assert len(page1["data"]) == 2 and page2["next_cursor"] is None
    assert {t["name"] for t in page1["data"] + page2["data"]} == {"t1", "t2", "t3"}


async def test_blank_team_name_is_422(client, world) -> None:
    h = auth_headers(world["admin"], world["org_a"])
    response = await client.post("/api/v1/teams", json={"name": "  "}, headers=h)
    assert response.status_code == 422
