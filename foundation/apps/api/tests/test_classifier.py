from app.services.classifier import classify_capture, summarize_capture


def test_classifies_amazon_ppc() -> None:
    result = classify_capture(
        "Campaign audit", "Review Amazon PPC campaigns, keywords, ACoS, and ASIN structure.", None
    )
    assert result["domain"] == "amazon_ppc"
    assert result["confidence"] > 0.5


def test_summary_is_bounded() -> None:
    summary = summarize_capture("word " * 200, max_chars=80)
    assert len(summary) <= 80
    assert summary.endswith("...")
