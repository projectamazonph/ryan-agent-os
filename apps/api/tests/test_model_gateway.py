from app.schemas.classification import ClassificationResult
from app.services.model_gateway import RulesModelGateway


async def test_rules_gateway_returns_typed_classification() -> None:
    gateway = RulesModelGateway()
    result = await gateway.classify(
        "Campaign audit",
        "Review Amazon PPC campaigns, keywords, ACoS, and ASIN structure.",
        None,
    )

    assert isinstance(result, ClassificationResult)
    assert result.domain == "amazon_ppc"
    assert result.intent == "organize"
    assert result.confidence > 0.5
    assert result.evidence
    assert result.engine == "rules-v1"


async def test_rules_gateway_flags_low_evidence_for_review() -> None:
    gateway = RulesModelGateway()
    result = await gateway.classify("Untitled", "miscellaneous thought", None)
    assert result.needs_review is True
