from __future__ import annotations

from collections.abc import Mapping

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.capture import Capture
from app.models.identity import Workspace
from app.models.source import SourceObject
from app.schemas.classification import ClassificationResult
from app.services.extraction import ExtractionFailedError, extract_text, process_source_extraction
from app.services.model_gateway import ModelGateway


class MemoryObjectStore:
    def __init__(self, objects: dict[str, bytes]) -> None:
        self.objects = objects

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


class StubGateway(ModelGateway):
    async def summarize(self, content: str) -> str:
        return f"Summary: {content[:40]}"

    async def classify(
        self, title: str, content: str, domain_hint: str | None
    ) -> ClassificationResult:
        del title, content
        return ClassificationResult(
            domain=domain_hint or "software",
            intent="build",
            confidence=0.92,
            evidence=["capture pipeline"],
            engine="stub-v1",
            needs_review=False,
        )


def test_extract_text_from_markdown() -> None:
    body = b"# Launch plan\n\nBuild the capture pipeline."
    assert extract_text(body, "text/markdown", "launch.md") == body.decode()


async def test_process_source_extraction_updates_capture_and_source(
    db_session: AsyncSession,
) -> None:
    workspace = Workspace(name="Ryan", slug="ryan", timezone="Asia/Manila")
    db_session.add(workspace)
    await db_session.flush()
    capture = Capture(
        workspace_id=workspace.id,
        type="file",
        title="Launch brief",
        content="",
        domain_hint="software",
        sensitivity="internal",
        status="received",
        checksum_sha256="a" * 64,
    )
    db_session.add(capture)
    await db_session.flush()
    source = SourceObject(
        workspace_id=workspace.id,
        capture_id=capture.id,
        storage_key="sources/launch.md",
        original_filename="launch.md",
        content_type="text/markdown",
        size_bytes=42,
        checksum_sha256="a" * 64,
        extraction_status="pending",
        metadata_json={"immutable": True},
    )
    db_session.add(source)
    await db_session.commit()

    await process_source_extraction(
        db_session,
        source.id,
        MemoryObjectStore({"sources/launch.md": b"Build the capture pipeline."}),
        StubGateway(),
    )
    await db_session.refresh(source)
    await db_session.refresh(capture)

    assert source.extraction_status == "ready"
    assert source.extracted_text == "Build the capture pipeline."
    assert source.extracted_at is not None
    assert source.extraction_error is None
    assert capture.status == "ready"
    assert capture.content == source.extracted_text
    assert capture.summary == "Summary: Build the capture pipeline."
    assert capture.classification == {
        "domain": "software",
        "intent": "build",
        "confidence": 0.92,
        "evidence": ["capture pipeline"],
        "engine": "stub-v1",
        "needs_review": False,
    }


async def test_process_source_extraction_records_failure(
    db_session: AsyncSession,
) -> None:
    workspace = Workspace(name="Ryan", slug="ryan", timezone="Asia/Manila")
    db_session.add(workspace)
    await db_session.flush()
    capture = Capture(
        workspace_id=workspace.id,
        type="file",
        title="Broken text",
        content="",
        domain_hint=None,
        sensitivity="internal",
        status="received",
        checksum_sha256="b" * 64,
    )
    db_session.add(capture)
    await db_session.flush()
    source = SourceObject(
        workspace_id=workspace.id,
        capture_id=capture.id,
        storage_key="sources/broken.txt",
        original_filename="broken.txt",
        content_type="text/plain",
        size_bytes=2,
        checksum_sha256="b" * 64,
        extraction_status="pending",
        metadata_json={"immutable": True},
    )
    db_session.add(source)
    await db_session.commit()

    with pytest.raises(ExtractionFailedError):
        await process_source_extraction(
            db_session,
            source.id,
            MemoryObjectStore({"sources/broken.txt": b"\xff\xfe"}),
            StubGateway(),
        )

    await db_session.refresh(source)
    await db_session.refresh(capture)
    assert source.extraction_status == "failed"
    assert source.extraction_error is not None
    assert capture.status == "failed"
