from __future__ import annotations

import pytest

from app.services.agent_runs import AgentRunStateError, validate_run_transition


def test_agent_run_state_machine_rejects_skipping_review() -> None:
    with pytest.raises(AgentRunStateError, match="Invalid agent run transition"):
        validate_run_transition("queued", "succeeded")


def test_agent_run_state_machine_allows_documented_lifecycle() -> None:
    transitions = [
        ("created", "queued"),
        ("queued", "preparing_context"),
        ("preparing_context", "running"),
        ("running", "needs_review"),
        ("needs_review", "succeeded"),
    ]
    for current, target in transitions:
        validate_run_transition(current, target)
