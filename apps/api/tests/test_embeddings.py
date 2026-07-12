from __future__ import annotations

import math
from uuid import UUID

from app.models.capture import Capture
from app.models.embedding import CaptureEmbedding
from app.services.embeddings import (
    HashEmbeddingGateway,
    cosine_similarity,
    upsert_capture_embedding,
)


async def test_hash_embedding_is_deterministic_and_normalized() -> None:
    gateway = HashEmbeddingGateway(dimensions=96)

    first = await gateway.embed("Build an agent execution queue for project tasks")
    second = await gateway.embed("Build an agent execution queue for project tasks")

    assert first == second
    assert len(first) == 96
    assert math.isclose(sum(value * value for value in first), 1.0, rel_tol=1e-6)
    assert gateway.model_name == "hash-v1-96"


async def test_upsert_capture_embedding_replaces_vector_for_same_capture(db_session) -> None:
    capture = Capture(
        workspace_id=UUID("01900000-0000-7000-8000-000000000001"),
        type="note",
        title="Execution queue",
        content="Rank project tasks by impact and urgency.",
        sensitivity="internal",
        checksum_sha256="a" * 64,
    )
    db_session.add(capture)
    await db_session.flush()

    first = await upsert_capture_embedding(
        db_session,
        capture,
        vector=[1.0, 0.0, 0.0],
        model_name="test-v1",
    )
    second = await upsert_capture_embedding(
        db_session,
        capture,
        vector=[0.0, 1.0, 0.0],
        model_name="test-v2",
    )

    assert first.id == second.id
    assert second.model_name == "test-v2"
    assert second.vector == [0.0, 1.0, 0.0]
    assert await db_session.get(CaptureEmbedding, second.id) is not None


def test_cosine_similarity_handles_orthogonal_and_equal_vectors() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0
