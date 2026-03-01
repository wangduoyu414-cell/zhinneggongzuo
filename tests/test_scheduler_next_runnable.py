from __future__ import annotations

import pytest

from core.scheduler import next_runnable_task, validate_dag


def test_next_runnable_task_returns_first_pending_with_done_deps() -> None:
    deps_by_task = {
        "task_a": [],
        "task_b": ["task_a"],
        "task_c": ["task_b"],
    }
    states = {
        "task_a": "DONE",
        "task_b": "PENDING",
        "task_c": "PENDING",
    }
    assert next_runnable_task(states, deps_by_task) == "task_b"


def test_next_runnable_task_returns_none_when_no_task_ready() -> None:
    deps_by_task = {"task_a": [], "task_b": ["task_a"]}
    states = {"task_a": "RUNNING", "task_b": "PENDING"}
    assert next_runnable_task(states, deps_by_task) is None


def test_validate_dag_rejects_cycle() -> None:
    deps_by_task = {"task_a": ["task_c"], "task_b": ["task_a"], "task_c": ["task_b"]}
    with pytest.raises(ValueError, match="dependency cycle detected"):
        validate_dag(deps_by_task)
