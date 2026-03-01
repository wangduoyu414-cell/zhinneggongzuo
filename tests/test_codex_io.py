from __future__ import annotations

from pathlib import Path

from core.codex_io import (
    CODEX_RESULT_FILENAME,
    CODEX_TASK_FILENAME,
    RUNS_ROOT,
    get_codex_result_path,
    get_codex_task_path,
    get_run_dir,
    read_codex_result,
    read_codex_task,
    write_codex_result,
    write_codex_task,
)


def test_path_contract_defaults() -> None:
    run_id = "run-001"
    assert RUNS_ROOT == Path("reports") / "runs"
    assert get_run_dir(run_id) == Path("reports") / "runs" / run_id
    assert get_codex_task_path(run_id) == Path("reports") / "runs" / run_id / CODEX_TASK_FILENAME
    assert get_codex_result_path(run_id) == Path("reports") / "runs" / run_id / CODEX_RESULT_FILENAME


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

