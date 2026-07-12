from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.capture import Capture
from app.models.embedding import CaptureEmbedding
from app.services.embeddings import cosine_similarity

_TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9_-]{2,}")
_STOP_WORDS = frozenset(
    {
        "and",
        "the",
        "for",
        "with",
        "from",
        "that",
        "this",
        "into",
        "your",
        "you",
        "are",
        "was",
        "were",
        "will",
        "have",
        "has",
        "had",
    }
)


@dataclass(frozen=True, slots=True)
class RelatedCapture:
    capture: Capture
    score: float
    reasons: list[str]


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in _TOKEN_PATTERN.findall(value.lower())
        if token not in _STOP_WORDS
    }


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def capture_similarity(left: Capture, right: Capture) -> tuple[float, list[str]]:
    left_title = _tokens(left.title)
    right_title = _tokens(right.title)
    left_content = _tokens(left.content)
    right_content = _tokens(right.content)

    title_score = _jaccard(left_title, right_title)
    content_score = _jaccard(left_content, right_content)
    shared = (left_title | left_content) & (right_title | right_content)
    same_domain = bool(left.domain_hint and left.domain_hint == right.domain_hint)

    score = (title_score * 0.35) + (content_score * 0.57) + (0.08 if same_domain else 0.0)
    reasons: list[str] = []
    if shared:
        reasons.append("shared_terms")
    if same_domain:
        reasons.append("same_domain")
    return round(min(score, 1.0), 4), reasons


async def find_related_captures(
    session: AsyncSession,
    target: Capture,
    *,
    limit: int = 5,
    threshold: float = 0.18,
) -> list[RelatedCapture]:
    target_embedding_result = await session.execute(
        select(CaptureEmbedding).where(CaptureEmbedding.capture_id == target.id)
    )
    target_embedding = target_embedding_result.scalar_one_or_none()
    result = await session.execute(
        select(Capture, CaptureEmbedding)
        .outerjoin(CaptureEmbedding, CaptureEmbedding.capture_id == Capture.id)
        .where(Capture.workspace_id == target.workspace_id, Capture.id != target.id)
    )
    related: list[RelatedCapture] = []
    for candidate, candidate_embedding in result.all():
        lexical_score, reasons = capture_similarity(target, candidate)
        if target_embedding is not None and candidate_embedding is not None:
            semantic_score = max(
                0.0,
                cosine_similarity(target_embedding.vector, candidate_embedding.vector),
            )
            score = (lexical_score * 0.4) + (semantic_score * 0.6)
            if semantic_score >= 0.5:
                reasons.append("semantic_similarity")
        else:
            score = lexical_score
        score = round(min(score, 1.0), 4)
        if score >= threshold:
            related.append(RelatedCapture(capture=candidate, score=score, reasons=reasons))
    related.sort(key=lambda item: (item.score, item.capture.created_at), reverse=True)
    return related[:limit]
