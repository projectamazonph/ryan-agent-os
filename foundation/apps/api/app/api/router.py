from fastapi import APIRouter

from app.api.v1.routes import auth, captures, health, projects, task_graphs, tasks

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
api_router.include_router(captures.router, prefix="/api/v1/captures", tags=["captures"])
api_router.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])

api_router.include_router(task_graphs.router, prefix="/api/v1/projects", tags=["task-graphs"])
api_router.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
