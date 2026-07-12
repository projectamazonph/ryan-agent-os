from __future__ import annotations

import io
import json
from datetime import UTC, datetime
from html.parser import HTMLParser
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.capture import Capture
from app.models.source import SourceObject
from app.services.audit import write_audit_event
from app.services.embeddings import EmbeddingGateway, embed_capture
from app.services.model_gateway import ModelGateway
from app.services.object_storage import ObjectStore


class ExtractionFailedError(RuntimeError):
    pass


class SourceNotFoundError(LookupError):
    pass


class _TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())

    def text(self) -> str:
        return "\n".join(self.parts)


def _extract_pdf(body: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise ValueError("PDF extraction dependency is unavailable") from exc
    reader = PdfReader(io.BytesIO(body))
    return "\n\n".join(filter(None, (page.extract_text() for page in reader.pages))).strip()


def _extract_docx(body: bytes) -> str:
    try:
        from docx import Document
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise ValueError("DOCX extraction dependency is unavailable") from exc
    document = Document(io.BytesIO(body))
    return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text).strip()


def extract_text(body: bytes, content_type: str, filename: str) -> str:
    del filename
    if content_type.startswith("text/"):
        text = body.decode("utf-8-sig")
        if content_type == "text/html":
            parser = _TextHTMLParser()
            parser.feed(text)
            text = parser.text()
    elif content_type == "application/json":
        payload = json.loads(body.decode("utf-8-sig"))
        text = json.dumps(payload, ensure_ascii=False, indent=2)
    elif content_type == "application/pdf":
        text = _extract_pdf(body)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = _extract_docx(body)
    else:
        raise ValueError(f"No extractor for content type: {content_type}")

    normalized = "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n"))
    normalized = normalized.strip()
    if not normalized:
        raise ValueError("No extractable text found")
    return normalized


async def process_source_extraction(
    session: AsyncSession,
    source_id: UUID,
    store: ObjectStore,
    gateway: ModelGateway,
    embedding_gateway: EmbeddingGateway | None = None,
) -> SourceObject:
    result = await session.execute(select(SourceObject).where(SourceObject.id == source_id))
    source = result.scalar_one_or_none()
    if source is None:
        raise SourceNotFoundError(str(source_id))

    capture_result = await session.execute(select(Capture).where(Capture.id == source.capture_id))
    capture = capture_result.scalar_one()
    source.extraction_status = "processing"
    source.extraction_attempts += 1
    source.last_attempt_at = datetime.now(UTC)
    source.extraction_error = None
    capture.status = "processing"
    await session.commit()

    try:
        body = await store.get_bytes(source.storage_key)
        text = extract_text(body, source.content_type, source.original_filename)
        summary = await gateway.summarize(text)
        classification = await gateway.classify(capture.title, text, capture.domain_hint)

        source.extracted_text = text
        source.extracted_at = datetime.now(UTC)
        source.extraction_status = "ready"
        source.extraction_error = None
        capture.content = text
        capture.summary = summary
        capture.classification = classification.model_dump(mode="json")
        capture.status = "ready"
        if embedding_gateway is not None:
            await embed_capture(session, capture, embedding_gateway)
        await write_audit_event(
            session,
            workspace_id=source.workspace_id,
            actor_type="system",
            actor_id="extraction-worker",
            action="source.extracted",
            resource_type="source_object",
            resource_id=str(source.id),
            metadata={
                "capture_id": str(capture.id),
                "content_type": source.content_type,
                "characters": len(text),
                "classification_engine": classification.engine,
            },
        )
        await session.commit()
        return source
    except Exception as exc:
        source.extraction_status = "failed"
        source.extraction_error = str(exc)[:2000]
        capture.status = "failed"
        await write_audit_event(
            session,
            workspace_id=source.workspace_id,
            actor_type="system",
            actor_id="extraction-worker",
            action="source.extraction_failed",
            resource_type="source_object",
            resource_id=str(source.id),
            metadata={"capture_id": str(capture.id), "error": str(exc)[:500]},
        )
        await session.commit()
        raise ExtractionFailedError(str(exc)) from exc
