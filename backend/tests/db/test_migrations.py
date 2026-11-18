import os
import subprocess
import sys

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from tests.conftest import BACKEND_DIR

RLS_TABLES = {"organization_memberships", "teams", "team_memberships"}


async def test_rls_enabled_and_forced(db_engine) -> None:
    async with db_engine.connect() as conn:
        rows = (await conn.execute(text(
            "SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class "
            "WHERE relname = ANY(:names)"), {"names": list(RLS_TABLES)})).all()
    assert {r.relname for r in rows} == RLS_TABLES
    assert all(r.relrowsecurity and r.relforcerowsecurity for r in rows)


async def test_role_check_constraint(db_engine) -> None:
    async with db_engine.begin() as conn:
        await conn.execute(text("SELECT set_config('app.bypass_rls', 'on', true)"))
        uid = await conn.scalar(text(
            "INSERT INTO users (firebase_uid, email, full_name) VALUES ('u1','a@x.io','A') RETURNING id"))
        org = await conn.scalar(text(
            "INSERT INTO organizations (name, created_by) VALUES ('Org', :u) RETURNING id"), {"u": uid})
        with pytest.raises(IntegrityError):
            async with conn.begin_nested():
                await conn.execute(text(
                    "INSERT INTO organization_memberships (organization_id, user_id, role) "
                    "VALUES (:o, :u, 'owner')"), {"o": org, "u": uid})


def test_migration_downgrade_and_upgrade(migrated_db: str) -> None:
    env = {**os.environ, "DATABASE_URL": migrated_db, "MIGRATION_DATABASE_URL": ""}
    for args in (["downgrade", "base"], ["upgrade", "head"]):
        subprocess.run([sys.executable, "-m", "alembic", *args], cwd=BACKEND_DIR, env=env, check=True)
