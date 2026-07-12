from fastapi import APIRouter

from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health/live", response_model=HealthResponse)
async def live() -> HealthResponse:
    return HealthResponse(status="ok", service="raos-api")
