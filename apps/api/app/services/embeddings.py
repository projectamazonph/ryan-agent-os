from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.capture import Capture
from app.models.embedding import EMBEDDING_DIMENSIONS, CaptureEmbedding

_TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9_-]{1,}")


class EmbeddingGateway(Protocol):
    model_name: str

    async def embed(self, text: str) -> list[float]: ...


class HashEmbeddingGateway:
    """Deterministic local embedding fallback.

    It is intentionally dependency-light and private. PostgreSQL stores the
    resulting vectors through pgvector, while SQLite tests use JSON.
    """

    def __init__(self, dimensions: int = EMBEDDING_DIMENSIONS) -> None:
        if dimensions < 8:
            raise ValueError("Embedding dimensions must be at least 8")
        self.dimensions = dimensions
        self.model_name = f"hash-v1-{dimensions}"

    async def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = _TOKEN_PATTERN.findall(text.lower())
        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=16).digest()
            index = int.from_bytes(digest[:8], "big") % self.dimensions
            sign = 1.0 if digest[8] & 1 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    score = sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)
    return round(max(-1.0, min(1.0, score)), 6)


def capture_embedding_text(capture: Capture) -> str:
    parts = [capture.title, capture.summary or "", capture.content, capture.domain_hint or ""]
    return "\n".join(part for part in parts if part).strip()


async def upsert_capture_embedding(
    session: AsyncSession,
    capture: Capture,
    *,
    vector: list[float],
    model_name: str,
) -> CaptureEmbedding:
    result = await session.execute(
        select(CaptureEmbedding).where(CaptureEmbedding.capture_id == capture.id)
    )
    embedding = result.scalar_one_or_none()
    checksum = hashlib.sha256(capture_embedding_text(capture).encode("utf-8")).hexdigest()
    if embedding is None:
        embedding = CaptureEmbedding(
            workspace_id=capture.workspace_id,
            capture_id=capture.id,
            model_name=model_name,
            dimensions=len(vector),
            vector=vector,
            content_checksum=checksum,
        )
        session.add(embedding)
    else:
        embedding.model_name = model_name
        embedding.dimensions = len(vector)
        embedding.vector = vector
        embedding.content_checksum = checksum
    await session.flush()
    return embedding


async def embed_capture(
    session: AsyncSession,
    capture: Capture,
    gateway: EmbeddingGateway,
) -> CaptureEmbedding:
    vector = await gateway.embed(capture_embedding_text(capture))
    return await upsert_capture_embedding(
        session,
        capture,
        vector=vector,
        model_name=gateway.model_name,
    )
