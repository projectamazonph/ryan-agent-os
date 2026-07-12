from __future__ import annotations

import asyncio
import json
import logging
from typing import Any
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import select

from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.db.session import SessionFactory
from app.models.capture import Capture
from app.services.audit import write_audit_event
from app.services.embeddings import EmbeddingGateway, HashEmbeddingGateway, embed_capture
from app.services.extraction import process_source_extraction
from app.services.model_gateway import ModelGateway, build_model_gateway
from app.services.object_storage import ObjectStorage, ObjectStore
from app.services.queue import JobQueue

logger = logging.getLogger("raos.worker")


async def process_capture(
    payload: dict[str, Any], gateway: ModelGateway, embedding_gateway: EmbeddingGateway
) -> None:
    capture_id = UUID(payload["capture_id"])
    async with SessionFactory() as session:
        result = await session.execute(select(Capture).where(Capture.id == capture_id))
        capture = result.scalar_one_or_none()
        if capture is None:
            logger.warning("Capture not found: %s", capture_id)
            return
        capture.status = "processing"
        await session.commit()

        capture.summary = await gateway.summarize(capture.content)
        classification = await gateway.classify(
            capture.title, capture.content, capture.domain_hint
        )
        capture.classification = classification.model_dump(mode="json")
        capture.status = "ready"
        await embed_capture(session, capture, embedding_gateway)
        await write_audit_event(
            session,
            workspace_id=capture.workspace_id,
            actor_type="system",
            actor_id="capture-worker",
            action="capture.processed",
            resource_type="capture",
            resource_id=str(capture.id),
            metadata={
                "engine": classification.engine,
                "embedding_model": embedding_gateway.model_name,
            },
        )
        await session.commit()
        logger.info("Processed capture %s", capture_id)


async def process_source(
    payload: dict[str, Any],
    store: ObjectStore,
    gateway: ModelGateway,
    embedding_gateway: EmbeddingGateway,
) -> None:
    source_id = UUID(payload["source_id"])
    async with SessionFactory() as session:
        await process_source_extraction(
            session, source_id, store, gateway, embedding_gateway
        )
    logger.info("Extracted source %s", source_id)


async def dispatch_job(
    job: dict[str, Any],
    settings: Settings,
    store: ObjectStore,
    gateway: ModelGateway,
    embedding_gateway: EmbeddingGateway,
) -> None:
    del settings
    job_type = job.get("type")
    payload = job.get("payload", {})
    if job_type == "capture.process":
        await process_capture(payload, gateway, embedding_gateway)
    elif job_type == "source.extract":
        await process_source(payload, store, gateway, embedding_gateway)
    else:
        logger.warning("Unknown job type: %s", job_type)


async def run() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    store = ObjectStorage(settings)
    gateway = build_model_gateway(settings)
    embedding_gateway = HashEmbeddingGateway()
    logger.info(
        "Worker listening on %s with model provider %s",
        JobQueue.queue_name,
        settings.model_provider,
    )
    try:
        while True:
            item = await client.blpop(JobQueue.queue_name, timeout=5)
            if item is None:
                continue
            _, raw = item
            job = json.loads(raw)
            try:
                await dispatch_job(job, settings, store, gateway, embedding_gateway)
            except Exception:
                logger.exception("Job failed: %s", job.get("type"))
    finally:
        await client.aclose()  # type: ignore[attr-defined]


if __name__ == "__main__":
    asyncio.run(run())
