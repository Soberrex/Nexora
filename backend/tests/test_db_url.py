import pytest

from app.core.db_url import build_async_db_config

NEON_DIRECT = "postgresql://u:p@ep-cool-name-123.eu-central-1.aws.neon.tech/nexora?sslmode=require&channel_binding=require"
NEON_POOLED = "postgresql://u:p@ep-cool-name-123-pooler.eu-central-1.aws.neon.tech/nexora?sslmode=require"


def test_neon_direct_url_is_converted_for_asyncpg() -> None:
    cfg = build_async_db_config(NEON_DIRECT)
    assert cfg.url.drivername == "postgresql+asyncpg"
    assert dict(cfg.url.query) == {}
    assert cfg.connect_args == {"ssl": "require"}
    assert not cfg.is_pooled


def test_neon_pooled_url_disables_statement_caching() -> None:
    cfg = build_async_db_config(NEON_POOLED)
    assert cfg.is_pooled
    assert cfg.connect_args == {"ssl": "require", "statement_cache_size": 0}
    assert cfg.url.query["prepared_statement_cache_size"] == "0"


def test_local_url_is_left_alone() -> None:
    cfg = build_async_db_config("postgresql+asyncpg://nexora:nexora@localhost:5432/nexora")
    assert cfg.url.render_as_string(hide_password=False) == "postgresql+asyncpg://nexora:nexora@localhost:5432/nexora"
    assert cfg.connect_args == {}


def test_postgres_scheme_alias_is_accepted() -> None:
    assert build_async_db_config("postgres://u:p@host/db").url.drivername == "postgresql+asyncpg"


def test_unsupported_driver_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported database driver"):
        build_async_db_config("mysql://u:p@host/db")
