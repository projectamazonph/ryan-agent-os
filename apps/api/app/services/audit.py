from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditEvent


async def write_audit_event(
    session: AsyncSession,
    *,
    workspace_id: UUID | None,
    actor_type: str,
    actor_id: str | None,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    request_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    event = AuditEvent(
        workspace_id=workspace_id,
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        request_id=request_id,
        metadata_json=metadata or {},
    )
    session.add(event)
    await session.flush()
    return event
