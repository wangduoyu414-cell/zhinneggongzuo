from __future__ import annotations

from pathlib import Path

from core.codex_io import (
    CODEX_RESULT_FILENAME,
    CODEX_TASK_FILENAME,
    EVENTS_FILENAME,
    RUNS_ROOT,
    RUN_STATE_FILENAME,
    append_event,
    append_task_event,
    get_codex_result_path,
    get_codex_task_path,
    get_events_path,
    get_run_dir,
    get_run_state_path,
    get_task_dir,
    get_task_events_path,
    get_task_run_state_path,
    read_codex_result,
    read_codex_task,
    read_events,
    read_run_state,
    read_task_events,
    read_task_run_state,
    write_codex_result,
    write_codex_task,
    write_run_state,
    write_task_run_state,
)


def test_path_contract_defaults() -> None:
    run_id = "run-001"
    task_id = "task-001"

    assert RUNS_ROOT == Path("reports") / "runs"
    assert get_run_dir(run_id) == Path("reports") / "runs" / run_id
    assert get_task_dir(run_id, task_id) == Path("reports") / "runs" / run_id / task_id

    assert get_codex_task_path(run_id) == Path("reports") / "runs" / run_id / CODEX_TASK_FILENAME
    assert get_codex_result_path(run_id) == Path("reports") / "runs" / run_id / CODEX_RESULT_FILENAME
    assert get_run_state_path(run_id) == Path("reports") / "runs" / run_id / RUN_STATE_FILENAME
    assert get_events_path(run_id) == Path("reports") / "runs" / run_id / EVENTS_FILENAME

    assert get_task_run_state_path(run_id, task_id) == Path("reports") / "runs" / run_id / task_id / RUN_STATE_FILENAME
    assert get_task_events_path(run_id, task_id) == Path("reports") / "runs" / run_id / task_id / EVENTS_FILENAME


def test_write_and_read_codex_artifacts(tmp_path: Path) -> None:
    run_id = "run-xyz"
    runs_root = tmp_path / "reports" / "runs"
    task_text = "# task\nhello\n"
    result_payload = {"result": "ok", "artifacts": {"log": "reports/runs/run-xyz/log.txt"}}

    task_path = write_codex_task(run_id, task_text, runs_root=runs_root)
    result_path = write_codex_result(run_id, result_payload, runs_root=runs_root)

    assert task_path == runs_root / run_id / CODEX_TASK_FILENAME
    assert result_path == runs_root / run_id / CODEX_RESULT_FILENAME
    assert read_codex_task(run_id, runs_root=runs_root) == task_text
    assert read_codex_result(run_id, runs_root=runs_root) == result_payload


def test_run_and_task_state_events_helpers(tmp_path: Path) -> None:
    run_id = "run-evt"
    task_id = "task-1"
    runs_root = tmp_path / "reports" / "runs"

    run_state = {
        "contract_version": "0",
        "status": "RUNNING",
        "run_id": run_id,
        "task_id": task_id,
        "updated_at": "2026-03-01T00:00:00Z",
    }
    task_state = {
        "contract_version": "0",
        "status": "DONE",
        "run_id": run_id,
        "task_id": task_id,
        "updated_at": "2026-03-01T00:00:01Z",
    }
    run_event = {"ts": "2026-03-01T00:00:00Z", "type": "RUN_START", "payload": {}}
    task_event = {"ts": "2026-03-01T00:00:01Z", "type": "TASK_DONE", "payload": {}}

    run_state_path = write_run_state(run_id, run_state, runs_root=runs_root)
    task_state_path = write_task_run_state(run_id, task_id, task_state, runs_root=runs_root)
    run_events_path = append_event(run_id, run_event, runs_root=runs_root)
    task_events_path = append_task_event(run_id, task_id, task_event, runs_root=runs_root)

    assert run_state_path == runs_root / run_id / RUN_STATE_FILENAME
    assert task_state_path == runs_root / run_id / task_id / RUN_STATE_FILENAME
    assert run_events_path == runs_root / run_id / EVENTS_FILENAME
    assert task_events_path == runs_root / run_id / task_id / EVENTS_FILENAME

    assert read_run_state(run_id, runs_root=runs_root) == run_state
    assert read_task_run_state(run_id, task_id, runs_root=runs_root) == task_state
    assert read_events(run_id, runs_root=runs_root) == [run_event]
    assert read_task_events(run_id, task_id, runs_root=runs_root) == [task_event]
