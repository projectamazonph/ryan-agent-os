from __future__ import annotations

from typing import Any

DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "amazon_ppc": ("amazon", "ppc", "acos", "tacos", "campaign", "keyword", "asin"),
    "software": ("github", "repository", "code", "api", "app", "frontend", "backend"),
    "training": ("course", "lesson", "student", "curriculum", "training", "module"),
    "operations": ("sop", "workflow", "clickup", "process", "playbook", "operations"),
    "personal_ai": ("agent", "llm", "hermes", "memory", "orchestrator", "ai system"),
}


def classify_capture(title: str, content: str, domain_hint: str | None) -> dict[str, Any]:
    haystack = f"{title} {content}".lower()
    scores = {
        domain: sum(1 for keyword in keywords if keyword in haystack)
        for domain, keywords in DOMAIN_KEYWORDS.items()
    }
    selected = domain_hint or max(scores, key=lambda domain: scores[domain])
    top_score = scores.get(selected, 0)
    confidence = 0.95 if domain_hint else min(0.55 + (top_score * 0.08), 0.91)
    intent = (
        "build"
        if any(word in haystack for word in ("build", "create", "implement"))
        else "organize"
    )
    return {
        "domain": selected,
        "intent": intent,
        "confidence": round(confidence, 2),
        "evidence": [
            keyword for keyword in DOMAIN_KEYWORDS.get(selected, ()) if keyword in haystack
        ][:5],
        "engine": "rules-v1",
        "needs_review": confidence < 0.65 or not any(scores.values()),
    }


def summarize_capture(content: str, max_chars: int = 280) -> str:
    compact = " ".join(content.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."
