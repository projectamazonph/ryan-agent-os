from __future__ import annotations

from collections.abc import Mapping

from httpx import AsyncClient

from app.api.deps import get_object_store
from app.main import app


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


async def auth_header(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ryan@example.com", "password": "test-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_capture_review_includes_source_metadata(client: AsyncClient) -> None:
    store = MemoryObjectStore()
    app.dependency_overrides[get_object_store] = lambda: store
    headers = await auth_header(client)
    uploaded = await client.post(
        "/api/v1/captures/files",
        headers=headers,
        files={"file": ("brief.md", b"Build the extraction pipeline.", "text/markdown")},
        data={"title": "Extraction brief", "domain_hint": "software"},
    )
    capture_id = uploaded.json()["capture"]["id"]

    response = await client.get(f"/api/v1/captures/{capture_id}/review", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["capture"]["id"] == capture_id
    assert body["source"]["original_filename"] == "brief.md"
    assert body["source"]["metadata_json"]["immutable"] is True
    assert body["related"] == []


async def test_capture_review_ranks_related_context(client: AsyncClient) -> None:
    headers = await auth_header(client)
    payloads = [
        {
            "type": "note",
            "title": "Capture pipeline",
            "content": "Build file ingestion extraction jobs and capture review.",
            "domain_hint": "software",
        },
        {
            "type": "note",
            "title": "File extraction pipeline",
            "content": "Implement capture ingestion, file extraction, and review workflow.",
            "domain_hint": "software",
        },
        {
            "type": "note",
            "title": "Amazon bid review",
            "content": "Audit sponsored product bids, ACoS, and search terms.",
            "domain_hint": "amazon_ppc",
        },
    ]
    created = [
        (await client.post("/api/v1/captures", headers=headers, json=payload)).json()
        for payload in payloads
    ]

    response = await client.get(
        f"/api/v1/captures/{created[0]['id']}/review", headers=headers
    )

    assert response.status_code == 200
    related = response.json()["related"]
    assert len(related) == 1
    assert related[0]["capture"]["id"] == created[1]["id"]
    assert related[0]["score"] >= 0.3
    assert "shared_terms" in related[0]["reasons"]
