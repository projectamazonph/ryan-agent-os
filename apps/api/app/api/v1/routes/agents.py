from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import AppSettings, CurrentOwner, DbSession
from app.schemas.agent import AgentDefinitionListResponse
from app.services.agent_registry import list_agent_versions, list_current_agent_definitions
from app.services.agent_runs import definition_response
from app.services.workspace import get_or_create_default_workspace

router = APIRouter()


@router.get("", response_model=AgentDefinitionListResponse)
async def list_agents_route(
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> AgentDefinitionListResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    definitions = await list_current_agent_definitions(session, workspace.id)
    await session.commit()
    return AgentDefinitionListResponse(items=[definition_response(item) for item in definitions])


@router.get("/{agent_key}/versions", response_model=AgentDefinitionListResponse)
async def list_agent_versions_route(
    agent_key: str,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> AgentDefinitionListResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    definitions = await list_agent_versions(session, workspace.id, agent_key)
    if not definitions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    await session.commit()
    return AgentDefinitionListResponse(items=[definition_response(item) for item in definitions])
