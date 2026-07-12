from __future__ import annotations

from uuid import UUID

from app.models.capture import Capture
from app.services.embeddings import upsert_capture_embedding
from app.services.related import find_related_captures


async def test_hybrid_related_search_uses_semantic_score_without_shared_terms(db_session) -> None:
    workspace_id = UUID("01900000-0000-7000-8000-000000000001")
    target = Capture(
        workspace_id=workspace_id,
        type="note",
        title="Prioritize implementation work",
        content="Order initiatives using expected value and effort.",
        sensitivity="internal",
        checksum_sha256="1" * 64,
    )
    semantic_match = Capture(
        workspace_id=workspace_id,
        type="note",
        title="Queue scoring framework",
        content="Rank backlog items by payoff divided by complexity.",
        sensitivity="internal",
        checksum_sha256="2" * 64,
    )
    unrelated = Capture(
        workspace_id=workspace_id,
        type="note",
        title="Massage appointment",
        content="Book a weekend massage in Iloilo.",
        sensitivity="internal",
        checksum_sha256="3" * 64,
    )
    db_session.add_all([target, semantic_match, unrelated])
    await db_session.flush()
    await upsert_capture_embedding(
        db_session, target, vector=[0.95, 0.05, 0.0], model_name="test"
    )
    await upsert_capture_embedding(
        db_session, semantic_match, vector=[0.92, 0.08, 0.0], model_name="test"
    )
    await upsert_capture_embedding(
        db_session, unrelated, vector=[0.0, 0.0, 1.0], model_name="test"
    )

    related = await find_related_captures(db_session, target, threshold=0.4)

    assert [item.capture.id for item in related] == [semantic_match.id]
    assert related[0].score > 0.55
    assert "semantic_similarity" in related[0].reasons
