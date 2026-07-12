from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.execution_pack import ExecutionPackVersion
from app.models.project import Project
from app.models.task import Task, TaskDependency, TaskGraph
from app.schemas.execution_pack import ExecutionPackContent
from app.schemas.task_graph import TaskDraft, TaskResponse


class TaskGraphCycleError(ValueError):
    def __init__(self, cycle: list[str]) -> None:
        self.cycle = cycle
        super().__init__(f"Task dependency cycle detected: {' -> '.join(cycle)}")


class TaskGraphPlanner(Protocol):
    async def plan(self, project: Project, content: ExecutionPackContent) -> list[TaskDraft]: ...


def calculate_rank_score(*, impact: int, urgency: int, confidence: int, effort: int) -> int:
    score = impact * 0.35 + urgency * 0.25 + confidence * 0.20 + (100 - effort) * 0.20
    return max(0, min(100, round(score)))


def validate_task_dag(tasks: Sequence[TaskDraft]) -> None:
    by_key: dict[str, TaskDraft] = {}
    for task in tasks:
        if task.key in by_key:
            raise ValueError(f"Duplicate task key: {task.key}")
        by_key[task.key] = task
    for task in tasks:
        unknown = [dependency for dependency in task.dependencies if dependency not in by_key]
        if unknown:
            raise ValueError(
                f"Task {task.key} references unknown dependencies: {', '.join(unknown)}"
            )

    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(key: str) -> None:
        state[key] = 1
        stack.append(key)
        for dependency in by_key[key].dependencies:
            if state.get(dependency, 0) == 0:
                visit(dependency)
            elif state.get(dependency) == 1:
                start = stack.index(dependency)
                raise TaskGraphCycleError([*stack[start:], dependency])
        stack.pop()
        state[key] = 2

    for task in tasks:
        if state.get(task.key, 0) == 0:
            visit(task.key)


class RulesTaskGraphPlanner:
    """Create a deterministic, sequential DAG from an approved execution pack."""

    async def plan(self, project: Project, content: ExecutionPackContent) -> list[TaskDraft]:
        tasks: list[TaskDraft] = []
        previous_key: str | None = None
        total_steps = sum(len(workstream.steps) for workstream in content.workstreams)
        position = 0
        for workstream_index, workstream in enumerate(content.workstreams, start=1):
            for step_index, step in enumerate(workstream.steps, start=1):
                position += 1
                key = f"ws-{workstream_index}-step-{step_index}"
                impact = min(100, max(40, project.priority + 5 - workstream_index * 2))
                urgency = max(35, 90 - position * 5)
                confidence = max(55, 90 - workstream_index * 3)
                effort = min(90, 25 + step_index * 8 + workstream_index * 3)
                tasks.append(
                    TaskDraft(
                        key=key,
                        title=step,
                        description=f"{workstream.goal} Work item: {step}",
                        verification=(
                            f"Evidence confirms '{step}' is complete and the relevant tests, "
                            "checks, or review criteria pass."
                        ),
                        impact=impact,
                        urgency=urgency,
                        confidence=confidence,
                        effort=effort,
                        dependencies=[previous_key] if previous_key else [],
                    )
                )
                previous_key = key
        if not tasks:
            raise ValueError("The approved execution pack has no workstream steps")
        if total_steps != len(tasks):
            raise AssertionError("Task planner lost workstream steps")
        validate_task_dag(tasks)
        return tasks


@dataclass(frozen=True)
class LoadedTaskGraph:
    graph: TaskGraph
    version: ExecutionPackVersion
    project: Project
    tasks: list[Task]
    dependencies: dict[UUID, list[Task]]


def unresolved_dependency_keys(dependencies: Sequence[Task]) -> list[str]:
    return [
        dependency.key
        for dependency in dependencies
        if dependency.status not in {"done", "skipped"}
    ]


def _is_ready(task: Task, dependencies: list[Task]) -> tuple[bool, list[str]]:
    blocked_by = unresolved_dependency_keys(dependencies)
    is_ready = task.status in {"planned", "in_progress"} and not blocked_by
    return is_ready, blocked_by


def task_response(
    task: Task,
    *,
    project_title: str,
    dependencies: list[Task],
) -> TaskResponse:
    is_ready, blocked_by = _is_ready(task, dependencies)
    return TaskResponse(
        id=task.id,
        task_graph_id=task.task_graph_id,
        project_id=task.project_id,
        project_title=project_title,
        key=task.key,
        title=task.title,
        description=task.description,
        verification=task.verification,
        status=task.status,
        impact=task.impact,
        urgency=task.urgency,
        confidence=task.confidence,
        effort=task.effort,
        rank_score=task.rank_score,
        position=task.position,
        dependency_keys=[dependency.key for dependency in dependencies],
        blocked_by=blocked_by,
        is_ready=is_ready,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
    )


async def create_or_get_task_graph(
    session: AsyncSession,
    *,
    project: Project,
    version: ExecutionPackVersion,
    content: ExecutionPackContent,
    planner: TaskGraphPlanner,
) -> tuple[TaskGraph, bool]:
    existing_result = await session.execute(
        select(TaskGraph).where(TaskGraph.execution_pack_version_id == version.id)
    )
    existing = existing_result.scalar_one_or_none()
    if existing is not None:
        return existing, False

    drafts = await planner.plan(project, content)
    validate_task_dag(drafts)
    await session.execute(
        update(TaskGraph)
        .where(TaskGraph.project_id == project.id, TaskGraph.status == "active")
        .values(status="superseded")
    )
    graph = TaskGraph(
        workspace_id=project.workspace_id,
        project_id=project.id,
        execution_pack_version_id=version.id,
        status="active",
    )
    session.add(graph)
    await session.flush()

    task_by_key: dict[str, Task] = {}
    for position, draft in enumerate(drafts, start=1):
        task = Task(
            task_graph_id=graph.id,
            workspace_id=project.workspace_id,
            project_id=project.id,
            key=draft.key,
            title=draft.title,
            description=draft.description,
            verification=draft.verification,
            status="planned",
            impact=draft.impact,
            urgency=draft.urgency,
            confidence=draft.confidence,
            effort=draft.effort,
            rank_score=calculate_rank_score(
                impact=draft.impact,
                urgency=draft.urgency,
                confidence=draft.confidence,
                effort=draft.effort,
            ),
            position=position,
        )
        session.add(task)
        task_by_key[draft.key] = task
    await session.flush()

    for draft in drafts:
        task = task_by_key[draft.key]
        for dependency_key in draft.dependencies:
            session.add(
                TaskDependency(
                    task_id=task.id,
                    depends_on_task_id=task_by_key[dependency_key].id,
                )
            )
    await session.flush()
    return graph, True


async def load_task_graph(
    session: AsyncSession,
    *,
    project_id: UUID,
    execution_pack_version_id: UUID | None = None,
) -> LoadedTaskGraph | None:
    statement = select(TaskGraph).where(TaskGraph.project_id == project_id)
    if execution_pack_version_id is not None:
        statement = statement.where(
            TaskGraph.execution_pack_version_id == execution_pack_version_id
        )
    else:
        statement = statement.where(TaskGraph.status == "active").order_by(
            TaskGraph.created_at.desc()
        )
    graph_result = await session.execute(statement.limit(1))
    graph = graph_result.scalar_one_or_none()
    if graph is None:
        return None
    version_result = await session.execute(
        select(ExecutionPackVersion).where(
            ExecutionPackVersion.id == graph.execution_pack_version_id
        )
    )
    version = version_result.scalar_one()
    project_result = await session.execute(select(Project).where(Project.id == graph.project_id))
    project = project_result.scalar_one()
    task_result = await session.execute(
        select(Task).where(Task.task_graph_id == graph.id).order_by(Task.position)
    )
    tasks = list(task_result.scalars().all())
    dependencies = await _dependencies_for_tasks(session, tasks)
    return LoadedTaskGraph(
        graph=graph,
        version=version,
        project=project,
        tasks=tasks,
        dependencies=dependencies,
    )


async def _dependencies_for_tasks(
    session: AsyncSession, tasks: Sequence[Task]
) -> dict[UUID, list[Task]]:
    mapping: dict[UUID, list[Task]] = {task.id: [] for task in tasks}
    if not tasks:
        return mapping
    task_by_id = {task.id: task for task in tasks}
    result = await session.execute(
        select(TaskDependency).where(TaskDependency.task_id.in_(task_by_id))
    )
    for relation in result.scalars().all():
        dependency = task_by_id.get(relation.depends_on_task_id)
        if dependency is not None:
            mapping[relation.task_id].append(dependency)
    for dependencies in mapping.values():
        dependencies.sort(key=lambda item: item.position)
    return mapping


async def list_implementation_queue(
    session: AsyncSession, workspace_id: UUID
) -> list[TaskResponse]:
    result = await session.execute(
        select(Task, Project)
        .join(TaskGraph, TaskGraph.id == Task.task_graph_id)
        .join(Project, Project.id == Task.project_id)
        .where(
            Task.workspace_id == workspace_id,
            TaskGraph.status == "active",
            Task.status.not_in({"done", "skipped"}),
        )
    )
    rows = list(result.all())
    tasks = [row[0] for row in rows]
    dependencies = await _dependencies_for_tasks(session, tasks)
    responses = [
        task_response(
            task,
            project_title=project.title,
            dependencies=dependencies[task.id],
        )
        for task, project in rows
    ]
    status_order = {"in_progress": 0, "planned": 1, "blocked": 2}
    return sorted(
        responses,
        key=lambda item: (
            not item.is_ready,
            status_order.get(item.status, 9),
            -item.rank_score,
            item.position,
            item.title.lower(),
        ),
    )


_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "planned": {"planned", "in_progress", "blocked", "done", "skipped"},
    "in_progress": {"in_progress", "blocked", "done", "skipped"},
    "blocked": {"blocked", "planned", "in_progress", "done", "skipped"},
    "done": {"done"},
    "skipped": {"skipped"},
}


async def update_task_status(task: Task, new_status: str) -> Task:
    if new_status not in _ALLOWED_TRANSITIONS.get(task.status, set()):
        raise ValueError(f"Invalid task transition: {task.status} -> {new_status}")
    task.status = new_status
    if new_status in {"done", "skipped"}:
        task.completed_at = task.completed_at or datetime.now(UTC)
    else:
        task.completed_at = None
    return task
