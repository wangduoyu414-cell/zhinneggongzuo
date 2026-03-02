from __future__ import annotations

from pathlib import Path

import pytest

from core.codex_io import (
    CODEX_RESULT_FILENAME,
    CODEX_TASK_FILENAME,
    LEGACY_CODEX_RESULT_FILENAME,
    LEGACY_CODEX_TASK_FILENAME,
    LEGACY_HITL_PROMPT_FILENAME,
    LEGACY_HITL_RESPONSE_FILENAME,
    read_codex_result,
    read_codex_task,
    read_hitl_prompt,
    read_hitl_response,
    write_codex_result,
    write_codex_task,
    write_hitl_prompt,
    write_hitl_response,
)
from core.file_io import read_json


def test_read_new_preferred_over_legacy(tmp_path: Path) -> None:
    runs_root = tmp_path / "reports" / "runs"
    run_id = "run-new-first"
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / LEGACY_CODEX_TASK_FILENAME).write_text("legacy-task", encoding="utf-8")
    (run_dir / CODEX_TASK_FILENAME).write_text("new-task", encoding="utf-8")
    (run_dir / LEGACY_CODEX_RESULT_FILENAME).write_text('{"result":"legacy","artifacts":{}}', encoding="utf-8")
    (run_dir / CODEX_RESULT_FILENAME).write_text('{"result":"new","artifacts":{}}', encoding="utf-8")

    assert read_codex_task(run_id, runs_root=runs_root) == "new-task"
    assert read_codex_result(run_id, runs_root=runs_root)["result"] == "new"


def test_read_falls_back_to_legacy_when_new_missing(tmp_path: Path) -> None:
    runs_root = tmp_path / "reports" / "runs"
    run_id = "run-fallback"
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / LEGACY_CODEX_TASK_FILENAME).write_text("legacy-only-task", encoding="utf-8")
    (run_dir / LEGACY_CODEX_RESULT_FILENAME).write_text('{"result":"ok","artifacts":{}}', encoding="utf-8")
    (run_dir / LEGACY_HITL_PROMPT_FILENAME).write_text("legacy prompt", encoding="utf-8")
    (run_dir / LEGACY_HITL_RESPONSE_FILENAME).write_text("legacy response", encoding="utf-8")

    assert read_codex_task(run_id, runs_root=runs_root) == "legacy-only-task"
    assert read_codex_result(run_id, runs_root=runs_root)["result"] == "ok"
    assert read_hitl_prompt(run_id, runs_root=runs_root) == "legacy prompt"
    assert read_hitl_response(run_id, runs_root=runs_root) == "legacy response"


def test_write_always_writes_new_names(tmp_path: Path) -> None:
    runs_root = tmp_path / "reports" / "runs"
    run_id = "run-write-new"
    run_dir = runs_root / run_id

    write_codex_task(run_id, "new task", runs_root=runs_root)
    write_codex_result(run_id, {"result": "ok", "artifacts": {}}, runs_root=runs_root)
    write_hitl_prompt(run_id, "new prompt", runs_root=runs_root)
    write_hitl_response(run_id, "new response", runs_root=runs_root)

    assert (run_dir / CODEX_TASK_FILENAME).exists()
    assert (run_dir / CODEX_RESULT_FILENAME).exists()
    assert (run_dir / "hitl_prompt.md").exists()
    assert (run_dir / "hitl_response.md").exists()

    assert not (run_dir / LEGACY_CODEX_TASK_FILENAME).exists()
    assert not (run_dir / LEGACY_CODEX_RESULT_FILENAME).exists()
    assert not (run_dir / LEGACY_HITL_PROMPT_FILENAME).exists()
    assert not (run_dir / LEGACY_HITL_RESPONSE_FILENAME).exists()

    data = read_json(run_dir / CODEX_RESULT_FILENAME, encoding="utf-8")
    assert data["result"] == "ok"


def test_read_raises_clear_error_when_missing_everywhere(tmp_path: Path) -> None:
    runs_root = tmp_path / "reports" / "runs"
    run_id = "run-missing"
    (runs_root / run_id).mkdir(parents=True, exist_ok=True)

    with pytest.raises(FileNotFoundError, match="lookup chain"):
        read_codex_result(run_id, runs_root=runs_root)
