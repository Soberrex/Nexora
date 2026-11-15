"""M1 identity and tenancy: users, organizations, memberships, teams, RLS.

Revision ID: 0002_identity_tenancy
Revises: 0001_baseline
Create Date: 2026-11-16
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_identity_tenancy"
down_revision: str | None = "0001_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ORG = "NULLIF(current_setting('app.current_organization_id', true), '')::uuid"
USER = "NULLIF(current_setting('app.current_user_id', true), '')::uuid"
BYPASS = "current_setting('app.bypass_rls', true) = 'on'"


def _pk() -> sa.Column:
    return sa.Column("id", sa.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()"))


def _ts(name: str) -> sa.Column:
    return sa.Column(name, sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)


def _flag(name: str, default: str) -> sa.Column:
    return sa.Column(name, sa.Boolean, server_default=sa.text(default), nullable=False)


def upgrade() -> None:
    op.create_table(
        "users", _pk(),
        sa.Column("firebase_uid", sa.Text, nullable=False, unique=True),
        sa.Column("email", sa.Text, nullable=False, unique=True),
        sa.Column("full_name", sa.Text, nullable=False),
        _flag("is_super_admin", "false"), _flag("is_active", "true"),
        _ts("created_at"), _ts("updated_at"),
    )
    op.create_table(
        "organizations", _pk(),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("created_by", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        _flag("is_active", "true"), _ts("created_at"), _ts("updated_at"),
    )
    op.create_table(
        "organization_memberships", _pk(),
        sa.Column("organization_id", sa.Uuid, sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("user_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.Text, nullable=False),
        _flag("is_active", "true"), _ts("joined_at"),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_org_membership"),
        sa.CheckConstraint("role IN ('org_admin', 'admin', 'technician', 'requester')",
                           name="ck_org_membership_role"),
    )
    op.create_index("ix_organization_memberships_user_id", "organization_memberships", ["user_id"])
    op.create_table(
        "teams", _pk(),
        sa.Column("organization_id", sa.Uuid, sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        _flag("is_active", "true"), _ts("created_at"), _ts("updated_at"),
        sa.UniqueConstraint("organization_id", "name", name="uq_team_name"),
    )
    op.create_table(
        "team_memberships", _pk(),
        sa.Column("organization_id", sa.Uuid, sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("team_id", sa.Uuid, sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("user_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        _ts("created_at"),
        sa.UniqueConstraint("team_id", "user_id", name="uq_team_membership"),
    )

    for table in ("organization_memberships", "teams", "team_memberships"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

    op.execute(f"""
        CREATE POLICY tenant_isolation ON organization_memberships
        USING (organization_id = {ORG} OR user_id = {USER} OR {BYPASS})
        WITH CHECK (organization_id = {ORG} OR {BYPASS})
    """)
    for table in ("teams", "team_memberships"):
        op.execute(f"""
            CREATE POLICY tenant_isolation ON {table}
            USING (organization_id = {ORG} OR {BYPASS})
            WITH CHECK (organization_id = {ORG} OR {BYPASS})
        """)


def downgrade() -> None:
    for table in ("team_memberships", "teams", "organization_memberships", "organizations", "users"):
        op.drop_table(table)
