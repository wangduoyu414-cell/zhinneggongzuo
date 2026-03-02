from __future__ import annotations

import pytest

from core.transitions import validate_transition


@pytest.mark.parametrize(
    ("from_stage", "to_stage"),
    [
        ("INIT", "WAIT_INPUT"),
        ("INIT", "EXECUTING"),
        ("WAIT_INPUT", "EXECUTING"),
        ("EXECUTING", "GATING"),
        ("EXECUTING", "DONE"),
        ("EXECUTING", "FAILED"),
        ("GATING", "DONE"),
        ("GATING", "FAILED"),
    ],
)
def test_allowed_transitions(from_stage: str, to_stage: str) -> None:
    validate_transition(from_stage, to_stage)


@pytest.mark.parametrize(
    ("from_stage", "to_stage"),
    [
        ("WAIT_INPUT", "DONE"),
        ("DONE", "EXECUTING"),
        ("FAILED", "INIT"),
        ("UNKNOWN", "DONE"),
        ("GATING", "EXECUTING"),
    ],
)
def test_invalid_transitions_raise(from_stage: str, to_stage: str) -> None:
    with pytest.raises(ValueError, match=f"from_stage={from_stage} to_stage={to_stage}"):
        validate_transition(from_stage, to_stage)
