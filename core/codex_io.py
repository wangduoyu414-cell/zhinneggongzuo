from __future__ import annotations

from pathlib import Path
from typing import Any

from core.file_io import atomic_write_json, atomic_write_text, read_json, read_text

RUNS_ROOT = Path("reports") / "runs"
CODEX_TASK_FILENAME = "codex_task.md"
CODEX_RESULT_FILENAME = "codex_result.json"


def get_run_dir(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return runs_root / run_id


def get_codex_task_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_run_dir(run_id, runs_root) / CODEX_TASK_FILENAME


def get_codex_result_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_run_dir(run_id, runs_root) / CODEX_RESULT_FILENAME


def write_codex_task(run_id: str, content: str, runs_root: Path = RUNS_ROOT) -> Path:
    path = get_codex_task_path(run_id, runs_root)
    atomic_write_text(path, content, encoding="utf-8")
    return path


def read_codex_task(run_id: str, runs_root: Path = RUNS_ROOT) -> str:
    return read_text(get_codex_task_path(run_id, runs_root), encoding="utf-8")


def write_codex_result(run_id: str, payload: dict[str, Any], runs_root: Path = RUNS_ROOT) -> Path:
    path = get_codex_result_path(run_id, runs_root)
    atomic_write_json(path, payload)
    return path


def read_codex_result(run_id: str, runs_root: Path = RUNS_ROOT) -> dict[str, Any]:
    data = read_json(get_codex_result_path(run_id, runs_root), encoding="utf-8")
    if not isinstance(data, dict):
        raise ValueError("codex_result must be a JSON object")
    return data

