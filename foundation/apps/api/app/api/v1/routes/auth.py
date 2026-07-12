from __future__ import annotations

import secrets

from fastapi import APIRouter, HTTPException, Request, status

from app.api.deps import AppSettings, CurrentOwner, DbSession
from app.core.auth import create_access_token
from app.schemas.auth import AuthenticatedOwner, LoginRequest, TokenResponse
from app.services.audit import write_audit_event
from app.services.workspace import get_or_create_default_workspace

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    settings: AppSettings,
    session: DbSession,
) -> TokenResponse:
    email_ok = secrets.compare_digest(payload.email.lower(), settings.owner_email.lower())
    password_ok = secrets.compare_digest(payload.password, settings.owner_password)
    if not email_ok or not password_ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    workspace = await get_or_create_default_workspace(session, settings)
    token = create_access_token(payload.email, workspace.slug, settings)
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=payload.email,
        action="auth.login_succeeded",
        resource_type="workspace",
        resource_id=str(workspace.id),
        request_id=getattr(request.state, "request_id", None),
    )
    await session.commit()
    return TokenResponse(access_token=token, expires_in=settings.jwt_ttl_minutes * 60)


@router.get("/me", response_model=AuthenticatedOwner)
async def me(owner: CurrentOwner) -> AuthenticatedOwner:
    return owner
