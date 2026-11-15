"""Operational commands.

Usage (from nexora_main/backend):
    .venv/Scripts/python -m app.cli make-super-admin someone@example.com
The user must have signed in once so their record exists.
"""

import argparse
import asyncio
import sys

from app.database import async_session_factory, engine
from app.service.users import UserService


async def _make_super_admin(email: str) -> int:
    async with async_session_factory() as session, session.begin():
        ok = await UserService(session).promote_to_super_admin(email)
    await engine.dispose()
    if not ok:
        print(f"No user with email {email}. Sign in once first.", file=sys.stderr)
        return 1
    print(f"{email} is now a super admin.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    sub = parser.add_subparsers(dest="command", required=True)
    promote = sub.add_parser("make-super-admin", help="Grant platform super admin to an existing user")
    promote.add_argument("email")
    args = parser.parse_args(argv)
    return asyncio.run(_make_super_admin(args.email))


if __name__ == "__main__":
    raise SystemExit(main())
