from __future__ import annotations

import json
from pathlib import Path

from core.task_manager import ARTIFACTS_DIRNAME, EVENTS_FILENAME, RUN_STATE_FILENAME, TaskManager


def test_task_manager_creates_layout_and_writes_state_and_events(tmp_path: Path) -> None:
    manager = TaskManager(run_id="run-1", task_id="task-1", runs_root=tmp_path / "runs")
    manager.ensure_layout(max_retries=3)

    assert (manager.task_dir / ARTIFACTS_DIRNAME).exists()
    assert (manager.task_dir / RUN_STATE_FILENAME).exists()
    assert (manager.task_dir / EVENTS_FILENAME).exists()

    manager.append_event("TEST_EVENT", {"k": "v"})
    lines = (manager.task_dir / EVENTS_FILENAME).read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["type"] == "TEST_EVENT"
    assert event["payload"] == {"k": "v"}


def test_task_manager_stop_the_line_after_max_retries(tmp_path: Path) -> None:
    manager = TaskManager(run_id="run-2", task_id="task-2", runs_root=tmp_path / "runs")
    manager.ensure_layout(max_retries=3)

    manager.complete_failure("boom-1")
    manager.complete_failure("boom-2")
    state = manager.complete_failure("boom-3")

    assert state["status"] == "FAILED"
    assert state["consecutive_failures"] == 3
    assert state["stop_the_line"] is True
