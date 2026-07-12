from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import select

from app.api.deps import get_job_queue, get_object_store
from app.main import app
from app.models.capture import Capture
from app.models.relation import CaptureRelation
from app.models.source import SourceObject


class MemoryObjectStore:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    async def ensure_bucket(self) -> None:
        return None

    async def put_bytes(
        self,
        key: str,
        body: bytes,
        content_type: str,
        metadata: Mapping[str, str] | None = None,
    ) -> None:
        del content_type, metadata
        self.objects[key] = body

    async def get_bytes(self, key: str) -> bytes:
        return self.objects[key]


class MemoryQueue:
    def __init__(self) -> None:
        self.jobs: list[tuple[str, dict[str, str]]] = []

    async def enqueue(self, job_type: str, payload: dict[str, str]) -> None:
        self.jobs.append((job_type, payload))


async def auth_header(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ryan@example.com", "password": "test-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_failed_source_can_be_retried_and_is_enqueued(
    client: AsyncClient, db_session
) -> None:
    store = MemoryObjectStore()
    queue = MemoryQueue()
    app.dependency_overrides[get_object_store] = lambda: store
    app.dependency_overrides[get_job_queue] = lambda: queue
    headers = await auth_header(client)
    upload = await client.post(
        "/api/v1/captures/files",
        headers=headers,
        files={"file": ("brief.md", b"Build the retry loop.", "text/markdown")},
    )
    capture_id = upload.json()["capture"]["id"]
    source_id = upload.json()["source"]["id"]

    source = await db_session.get(SourceObject, UUID(source_id))
    capture = await db_session.get(Capture, UUID(capture_id))
    assert source is not None and capture is not None
    source.extraction_status = "failed"
    source.extraction_error = "temporary parser failure"
    capture.status = "failed"
    await db_session.commit()

    response = await client.post(f"/api/v1/captures/{capture_id}/retry", headers=headers)

    assert response.status_code == 202
    assert response.json()["source"]["extraction_status"] == "pending"
    assert response.json()["source"]["extraction_error"] is None
    assert queue.jobs == [("source.extract", {"source_id": source_id})]


async def test_reference_and_merge_relations_are_idempotent(
    client: AsyncClient, db_session
) -> None:
    headers = await auth_header(client)
    created = []
    for title in ("Primary plan", "Follow-up plan", "Duplicate plan"):
        response = await client.post(
            "/api/v1/captures",
            headers=headers,
            json={"type": "note", "title": title, "content": f"Content for {title}."},
        )
        created.append(response.json())

    reference = await client.post(
        f"/api/v1/captures/{created[0]['id']}/relations",
        headers=headers,
        json={"target_capture_id": created[1]["id"], "action": "reference"},
    )
    duplicate_reference = await client.post(
        f"/api/v1/captures/{created[0]['id']}/relations",
        headers=headers,
        json={"target_capture_id": created[1]["id"], "action": "reference"},
    )
    merged = await client.post(
        f"/api/v1/captures/{created[2]['id']}/relations",
        headers=headers,
        json={"target_capture_id": created[0]["id"], "action": "merge"},
    )

    assert reference.status_code == 201
    assert duplicate_reference.status_code == 200
    assert reference.json()["id"] == duplicate_reference.json()["id"]
    assert merged.status_code == 201

    relations = (await db_session.execute(select(CaptureRelation))).scalars().all()
    merged_capture = await db_session.get(Capture, UUID(created[2]["id"]))

    assert len(relations) == 2
    assert merged_capture is not None
    assert merged_capture.review_status == "merged"
