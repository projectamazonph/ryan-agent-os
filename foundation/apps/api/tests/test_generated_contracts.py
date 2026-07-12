from __future__ import annotations

from pathlib import Path

from app.contracts import render_contracts


def test_generated_contracts_match_repository_files() -> None:
    repository_root = Path(__file__).resolve().parents[3]

    for relative_path, expected_content in render_contracts().items():
        contract_path = repository_root / relative_path
        assert contract_path.exists(), f"Missing generated contract: {relative_path}"
        assert contract_path.read_text(encoding="utf-8") == expected_content
