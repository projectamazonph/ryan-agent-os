from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models.identity import Workspace


async def get_or_create_default_workspace(session: AsyncSession, settings: Settings) -> Workspace:
    result = await session.execute(select(Workspace).where(Workspace.slug == "ryan-personal"))
    workspace = result.scalar_one_or_none()
    if workspace is not None:
        return workspace
    workspace = Workspace(name="Ryan Personal Workspace", slug="ryan-personal")
    session.add(workspace)
    await session.flush()
    return workspace
