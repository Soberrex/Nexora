from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.auth import InvalidTokenError, TokenVerifier, get_token_verifier
from app.core.errors import AppError
from app.core.tenancy import set_user_context
from app.database import get_db_session
from app.domain import User
from app.service.users import UserService

_bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    session: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    verifier: Annotated[TokenVerifier, Depends(get_token_verifier)],
) -> User:
    if credentials is None:
        raise AppError("Not authenticated", status_code=401, code="NOT_AUTHENTICATED")
    try:
        token = await verifier.verify(credentials.credentials)
    except InvalidTokenError:
        raise AppError("Invalid or expired token", status_code=401, code="INVALID_TOKEN") from None
    if settings.AUTH_REQUIRE_VERIFIED_EMAIL and not token.email_verified:
        raise AppError("Email address is not verified", status_code=403, code="EMAIL_NOT_VERIFIED")

    user = await UserService(session).get_or_provision(token)
    if not user.is_active:
        raise AppError("User account is disabled", status_code=403, code="USER_INACTIVE")
    await set_user_context(session, user.id)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
