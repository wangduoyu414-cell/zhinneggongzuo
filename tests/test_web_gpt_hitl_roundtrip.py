from __future__ import annotations

from pathlib import Path

from bridge.web_gpt_hitl import (
    CODEX_TASK_FILENAME,
    PROMPT_FILENAME,
    RESPONSE_FILENAME,
    emit_prompt,
    get_artifacts_dir,
    ingest_response,
)
from core.file_io import read_text


def test_emit_prompt_creates_prompt_artifact(tmp_path: Path) -> None:
    run_id = "run-w3"
    task_id = "task-001"
    runs_root = tmp_path / "reports" / "runs"

    path = emit_prompt(run_id, task_id, runs_root=runs_root)
    artifacts_dir = get_artifacts_dir(run_id, task_id, runs_root=runs_root)

    assert path == artifacts_dir / PROMPT_FILENAME
    content = read_text(path)
    assert run_id in content
    assert task_id in content
    assert "does not perform browser automation" in content


def test_ingest_response_roundtrip_and_minimal_parse(tmp_path: Path) -> None:
    run_id = "run-w3"
    task_id = "task-002"
    runs_root = tmp_path / "reports" / "runs"
    response = (
        "Summary line\n\n"
        "```markdown\n"
        "# Next Step\n"
        "- do A\n"
        "```\n\n"
        "tail"
    )

    result = ingest_response(run_id, task_id, response, runs_root=runs_root)
    artifacts_dir = get_artifacts_dir(run_id, task_id, runs_root=runs_root)

    response_path = artifacts_dir / RESPONSE_FILENAME
    codex_task_path = artifacts_dir / CODEX_TASK_FILENAME

    assert result["response_path"] == str(response_path)
    assert result["codex_task_path"] == str(codex_task_path)
    assert result["response_char_count"] == len(response)
    assert result["fenced_code_block_count"] == 1
    assert result["warnings"] == []

    assert read_text(response_path) == response
    codex_task = read_text(codex_task_path)
    assert "# Codex Task (Generated from WebGPT HITL)" in codex_task
    assert "# Next Step" in codex_task


def test_ingest_empty_response_records_warning(tmp_path: Path) -> None:
    run_id = "run-w3"
    task_id = "task-empty"
    runs_root = tmp_path / "reports" / "runs"

    result = ingest_response(run_id, task_id, "   ", runs_root=runs_root)
    assert result["warnings"] == ["response text is empty"]
