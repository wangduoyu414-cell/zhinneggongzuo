from __future__ import annotations

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "INIT": {"WAIT_INPUT", "EXECUTING"},
    "WAIT_INPUT": {"EXECUTING"},
    "EXECUTING": {"GATING", "DONE", "FAILED"},
    "GATING": {"DONE", "FAILED"},
    "DONE": set(),
    "FAILED": set(),
}


def validate_transition(from_stage: str, to_stage: str) -> None:
    allowed = ALLOWED_TRANSITIONS.get(from_stage)
    if allowed is None or to_stage not in allowed:
        raise ValueError(f"invalid stage transition from_stage={from_stage} to_stage={to_stage}")
