from __future__ import annotations

import pytest

from core.run_state_event_validation import (
    validate_event,
    validate_events,
    validate_events_jsonl,
    validate_run_state,
)


def _valid_run_state() -> dict[str, object]:
    return {
        "contract_version": "0",
        "status": "RUNNING",
        "run_id": "run-1",
        "task_id": "task-1",
        "updated_at": "2026-03-01T00:00:00Z",
    }


def _valid_event_with_type() -> dict[str, object]:
    return {
        "contract_version": "0",
        "ts": "2026-03-01T00:00:00Z",
        "type": "TASK_RUNNING",
        "run_id": "run-1",
        "task_id": "task-1",
        "payload": {},
    }


def _valid_event_with_event_type() -> dict[str, object]:
    return {
        "contract_version": "0",
        "ts": "2026-03-01T00:00:01Z",
        "event_type": "TASK_DONE",
        "run_id": "run-1",
        "task_id": "task-1",
        "payload": {},
    }


def test_validate_run_state_accepts_valid_payload() -> None:
    validate_run_state(_valid_run_state())


def test_validate_run_state_rejects_unknown_field() -> None:
    payload = _valid_run_state()
    payload["unknown"] = "x"
    with pytest.raises(ValueError, match=r"payload\.unknown: unknown field"):
        validate_run_state(payload)


def test_validate_event_accepts_union_shapes() -> None:
    validate_event(_valid_event_with_type())
    validate_event(_valid_event_with_event_type())


def test_validate_event_rejects_invalid_contract_version() -> None:
    payload = _valid_event_with_type()
    payload["contract_version"] = "1"
    with pytest.raises(ValueError, match=r"expected constant value '0'"):
        validate_event(payload)


def test_validate_events_jsonl_rejects_invalid_line() -> None:
    text = (
        '{"ts":"2026-03-01T00:00:00Z","type":"A","run_id":"r","task_id":"t","payload":{}}\n'
        '{"bad":true}\n'
    )
    with pytest.raises(ValueError, match=r"events line 2"):
        validate_events_jsonl(text)


def test_validate_events_jsonl_accepts_valid_lines() -> None:
    text = (
        '{"ts":"2026-03-01T00:00:00Z","type":"A","run_id":"r","task_id":"t","payload":{}}\n'
        '{"ts":"2026-03-01T00:00:01Z","event_type":"B","run_id":"r","task_id":"t","payload":{}}\n'
    )
    validate_events_jsonl(text)


def test_validate_events_array_accepts_union_shapes() -> None:
    payload = [_valid_event_with_type(), _valid_event_with_event_type()]
    validate_events(payload)
