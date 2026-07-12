from __future__ import annotations

import hashlib
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.capture import Capture
from app.schemas.capture import CaptureCreate


def capture_checksum(payload: CaptureCreate) -> str:
    canonical = "\n".join(
        [payload.type, payload.title.strip(), payload.content.strip(), payload.domain_hint or ""]
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


async def create_capture(
    session: AsyncSession, workspace_id: UUID, payload: CaptureCreate
) -> tuple[Capture, bool]:
    checksum = capture_checksum(payload)
    result = await session.execute(
        select(Capture).where(
            Capture.workspace_id == workspace_id, Capture.checksum_sha256 == checksum
        )
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing, False

    capture = Capture(
        workspace_id=workspace_id,
        type=payload.type,
        title=payload.title.strip(),
        content=payload.content.strip(),
        domain_hint=payload.domain_hint,
        sensitivity=payload.sensitivity,
        status="received",
        checksum_sha256=checksum,
    )
    session.add(capture)
    await session.flush()
    return capture, True


async def list_captures(
    session: AsyncSession, workspace_id: UUID, limit: int = 50
) -> list[Capture]:
    result = await session.execute(
        select(Capture)
        .where(Capture.workspace_id == workspace_id)
        .order_by(desc(Capture.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())
