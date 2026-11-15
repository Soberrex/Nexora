from app.core.auth import InvalidTokenError, VerifiedToken


class FakeTokenVerifier:
    """Token format: 'uid|email' or 'uid|email|unverified'."""

    async def verify(self, token: str) -> VerifiedToken:
        parts = token.split("|")
        if len(parts) < 2 or not parts[0] or "@" not in parts[1]:
            raise InvalidTokenError("malformed fake token")
        verified = not (len(parts) > 2 and parts[2] == "unverified")
        return VerifiedToken(uid=parts[0], email=parts[1], email_verified=verified, name=None)
