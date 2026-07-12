from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import decode_access_token
from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.schemas.auth import AuthenticatedOwner
from app.services.object_storage import ObjectStorage, ObjectStore
from app.services.queue import JobQueue

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_object_store(settings: AppSettings) -> ObjectStore:
    return ObjectStorage(settings)


ObjectStoreDep = Annotated[ObjectStore, Depends(get_object_store)]


def get_job_queue(settings: AppSettings) -> JobQueue:
    return JobQueue(settings.redis_url)


JobQueueDep = Annotated[JobQueue, Depends(get_job_queue)]


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_owner(
    settings: AppSettings,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AuthenticatedOwner:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = credentials.credentials
    try:
        payload = decode_access_token(token, settings)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc
    if payload.email.lower() != settings.owner_email.lower():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner access required")
    return AuthenticatedOwner(email=payload.email, workspace_slug=payload.workspace_slug)


CurrentOwner = Annotated[AuthenticatedOwner, Depends(get_current_owner)]
