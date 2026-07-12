from __future__ import annotations

import hashlib
import re
from pathlib import PurePath
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.uuid7 import uuid7
from app.models.capture import Capture
from app.models.source import SourceObject
from app.services.object_storage import ObjectStore

ALLOWED_CONTENT_TYPES = frozenset(
    {
        "text/plain",
        "text/markdown",
        "text/csv",
        "text/html",
        "application/json",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
)


class UnsupportedSourceTypeError(ValueError):
    pass


class UploadTooLargeError(ValueError):
    pass


def normalize_filename(filename: str | None) -> str:
    candidate = PurePath(filename or "upload.bin").name
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", candidate).strip("-.")
    return (normalized or "upload.bin")[:300]


async def read_upload(upload: UploadFile, max_bytes: int) -> bytes:
    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise UnsupportedSourceTypeError(upload.content_type or "unknown")

    parts: list[bytes] = []
    size = 0
    while chunk := await upload.read(1024 * 1024):
        size += len(chunk)
        if size > max_bytes:
            raise UploadTooLargeError(str(size))
        parts.append(chunk)
    return b"".join(parts)


async def create_file_capture(
    session: AsyncSession,
    store: ObjectStore,
    workspace_id: UUID,
    *,
    body: bytes,
    filename: str,
    content_type: str,
    title: str | None,
    domain_hint: str | None,
    sensitivity: str,
) -> tuple[Capture, SourceObject, bool]:
    checksum = hashlib.sha256(body).hexdigest()
    result = await session.execute(
        select(SourceObject).where(
            SourceObject.workspace_id == workspace_id,
            SourceObject.checksum_sha256 == checksum,
        )
    )
    existing_source = result.scalar_one_or_none()
    if existing_source is not None:
        capture_result = await session.execute(
            select(Capture).where(Capture.id == existing_source.capture_id)
        )
        return capture_result.scalar_one(), existing_source, False

    safe_filename = normalize_filename(filename)
    source_id = uuid7()
    storage_key = (
        f"workspaces/{workspace_id}/sources/{source_id}/{checksum[:16]}-{safe_filename}"
    )
    capture = Capture(
        workspace_id=workspace_id,
        type="file",
        title=(title or safe_filename).strip(),
        content="",
        domain_hint=domain_hint,
        sensitivity=sensitivity,
        status="received",
        checksum_sha256=checksum,
    )
    session.add(capture)
    await session.flush()

    await store.ensure_bucket()
    await store.put_bytes(
        storage_key,
        body,
        content_type,
        metadata={
            "workspace-id": str(workspace_id),
            "capture-id": str(capture.id),
            "checksum-sha256": checksum,
            "original-filename": safe_filename,
        },
    )

    source = SourceObject(
        id=source_id,
        workspace_id=workspace_id,
        capture_id=capture.id,
        storage_key=storage_key,
        original_filename=safe_filename,
        content_type=content_type,
        size_bytes=len(body),
        checksum_sha256=checksum,
        extraction_status="pending",
        metadata_json={"immutable": True},
    )
    session.add(source)
    await session.flush()
    return capture, source, True
