from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from pydantic import BaseModel

from app.core.config import Settings


class TokenPayload(BaseModel):
    sub: str
    email: str
    workspace_slug: str
    exp: int
    iat: int


def create_access_token(email: str, workspace_slug: str, settings: Settings) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": email,
        "email": email,
        "workspace_slug": workspace_slug,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_ttl_minutes)).timestamp()),
    }
    encoded = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return encoded.decode("utf-8") if isinstance(encoded, bytes) else encoded


def decode_access_token(token: str, settings: Settings) -> TokenPayload:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    return TokenPayload.model_validate(payload)
