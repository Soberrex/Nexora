"""Normalize PostgreSQL URLs (including Neon's) for SQLAlchemy + asyncpg.

Neon hands out ``postgresql://...?sslmode=require&channel_binding=require``. asyncpg does not
understand ``sslmode``/``channel_binding`` as URL parameters, so they are translated into
``connect_args``. Neon's pooled endpoint (host contains ``-pooler``) runs PgBouncer in transaction
mode, which breaks prepared-statement caching, so caching is disabled there.
"""

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.engine import URL, make_url

_SSL_MODES_REQUIRING_TLS = {"require", "verify-ca", "verify-full"}
_DROPPED_PARAMS = {"sslmode", "channel_binding", "ssl"}


@dataclass(frozen=True)
class AsyncDbConfig:
    url: URL
    connect_args: dict[str, Any] = field(default_factory=dict)

    @property
    def is_pooled(self) -> bool:
        return "-pooler" in (self.url.host or "")


def build_async_db_config(raw_url: str) -> AsyncDbConfig:
    url = make_url(raw_url.strip())

    if url.drivername in {"postgres", "postgresql", "postgresql+psycopg2", "postgresql+psycopg"}:
        url = url.set(drivername="postgresql+asyncpg")
    if url.drivername != "postgresql+asyncpg":
        raise ValueError(f"Unsupported database driver: {url.drivername}")

    query = dict(url.query)
    sslmode = str(query.get("sslmode") or query.get("ssl") or "").lower()
    url = url.set(query={k: v for k, v in query.items() if k not in _DROPPED_PARAMS})

    connect_args: dict[str, Any] = {}
    if sslmode in _SSL_MODES_REQUIRING_TLS or sslmode == "true":
        connect_args["ssl"] = "require"

    if "-pooler" in (url.host or ""):
        connect_args["statement_cache_size"] = 0
        url = url.update_query_dict({"prepared_statement_cache_size": "0"})

    return AsyncDbConfig(url=url, connect_args=connect_args)
