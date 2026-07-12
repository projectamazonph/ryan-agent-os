from __future__ import annotations

from collections.abc import Mapping

from httpx import AsyncClient

from app.api.deps import get_object_store
from app.core.config import get_settings
from app.main import app


class MemoryObjectStore:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.content_types: dict[str, str] = {}
        self.metadata: dict[str, dict[str, str]] = {}

    async def ensure_bucket(self) -> None:
        return None

    async def put_bytes(
        self,
        key: str,
        body: bytes,
        content_type: str,
        metadata: Mapping[str, str] | None = None,
    ) -> None:
        if key in self.objects:
            raise AssertionError("immutable source key was overwritten")
        self.objects[key] = body
        self.content_types[key] = content_type
        self.metadata[key] = dict(metadata or {})

    async def get_bytes(self, key: str) -> bytes:
        return self.objects[key]


async def auth_header(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ryan@example.com", "password": "test-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_file_upload_stores_immutable_source_and_is_idempotent(
    client: AsyncClient,
) -> None:
    store = MemoryObjectStore()
    app.dependency_overrides[get_object_store] = lambda: store
    headers = await auth_header(client)
    files = {"file": ("brief.md", b"# Launch plan\nBuild the capture pipeline.", "text/markdown")}
    data = {
        "title": "Launch brief",
        "domain_hint": "software",
        "sensitivity": "confidential",
    }

    first = await client.post("/api/v1/captures/files", headers=headers, files=files, data=data)
    second = await client.post("/api/v1/captures/files", headers=headers, files=files, data=data)

    assert first.status_code == 201
    assert second.status_code == 201
    first_body = first.json()
    second_body = second.json()
    assert first_body["capture"]["type"] == "file"
    assert first_body["capture"]["status"] == "received"
    assert first_body["source"]["original_filename"] == "brief.md"
    assert first_body["source"]["content_type"] == "text/markdown"
    assert first_body["source"]["size_bytes"] == len(files["file"][1])
    assert len(first_body["source"]["checksum_sha256"]) == 64
    assert first_body["capture"]["id"] == second_body["capture"]["id"]
    assert first_body["source"]["id"] == second_body["source"]["id"]
    assert len(store.objects) == 1
    stored_key = first_body["source"]["storage_key"]
    assert store.objects[stored_key] == files["file"][1]


async def test_file_upload_rejects_unsupported_type(client: AsyncClient) -> None:
    store = MemoryObjectStore()
    app.dependency_overrides[get_object_store] = lambda: store
    headers = await auth_header(client)

    response = await client.post(
        "/api/v1/captures/files",
        headers=headers,
        files={"file": ("malware.exe", b"not really", "application/x-msdownload")},
        data={"title": "Bad file", "sensitivity": "restricted"},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported file type"
    assert store.objects == {}


async def test_file_upload_rejects_oversized_body(client: AsyncClient, monkeypatch) -> None:
    store = MemoryObjectStore()
    app.dependency_overrides[get_object_store] = lambda: store
    headers = await auth_header(client)
    monkeypatch.setenv("RAOS_MAX_UPLOAD_BYTES", "8")
    get_settings.cache_clear()

    response = await client.post(
        "/api/v1/captures/files",
        headers=headers,
        files={"file": ("large.txt", b"123456789", "text/plain")},
        data={"title": "Too large", "sensitivity": "internal"},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "File exceeds upload limit"
    assert store.objects == {}
    get_settings.cache_clear()
