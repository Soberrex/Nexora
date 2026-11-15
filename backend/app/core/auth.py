"""Firebase ID token verification behind a small interface (tests use a fake)."""

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol

from starlette.concurrency import run_in_threadpool

from app.config import settings


@dataclass(frozen=True)
class VerifiedToken:
    uid: str
    email: str
    email_verified: bool
    name: str | None


class InvalidTokenError(Exception):
    """The token is missing claims, malformed, expired or revoked."""


class TokenVerifier(Protocol):
    async def verify(self, token: str) -> VerifiedToken: ...


class FirebaseTokenVerifier:
    def __init__(self, *, project_id: str, emulator_host: str, environment: str) -> None:
        if emulator_host:
            if environment == "production":
                raise RuntimeError("FIREBASE_AUTH_EMULATOR_HOST must never be set in production")
            # firebase-admin reads this variable to trust emulator-issued (unsigned) tokens.
            os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = emulator_host
        if not project_id:
            raise RuntimeError("FIREBASE_PROJECT_ID is required for token verification")

        import firebase_admin

        name = f"nexora-{project_id}"
        try:
            self._app = firebase_admin.get_app(name)
        except ValueError:
            self._app = firebase_admin.initialize_app(options={"projectId": project_id}, name=name)

    async def verify(self, token: str) -> VerifiedToken:
        from firebase_admin import auth

        try:
            claims = await run_in_threadpool(auth.verify_id_token, token, self._app)
        except (
            ValueError,
            auth.InvalidIdTokenError,
            auth.ExpiredIdTokenError,
            auth.RevokedIdTokenError,
            auth.CertificateFetchError,
        ) as exc:
            raise InvalidTokenError(type(exc).__name__) from exc

        email = claims.get("email")
        if not isinstance(email, str) or "@" not in email:
            raise InvalidTokenError("token has no email claim")
        return VerifiedToken(
            uid=str(claims["uid"]),
            email=email,
            email_verified=bool(claims.get("email_verified", False)),
            name=claims.get("name"),
        )


@lru_cache
def get_token_verifier() -> TokenVerifier:
    return FirebaseTokenVerifier(
        project_id=settings.FIREBASE_PROJECT_ID,
        emulator_host=settings.FIREBASE_AUTH_EMULATOR_HOST,
        environment=settings.ENVIRONMENT,
    )
