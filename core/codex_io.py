from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.file_io import atomic_write_json, atomic_write_text, read_json, read_text

RUNS_ROOT = Path("reports") / "runs"
CODEX_TASK_FILENAME = "codex_task.md"
CODEX_RESULT_FILENAME = "codex_result.json"
RUN_STATE_FILENAME = "run_state.json"
EVENTS_FILENAME = "events.jsonl"


def get_run_dir(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return runs_root / run_id


def get_task_dir(run_id: str, task_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_run_dir(run_id, runs_root) / task_id


def get_codex_task_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_run_dir(run_id, runs_root) / CODEX_TASK_FILENAME


def get_codex_result_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_run_dir(run_id, runs_root) / CODEX_RESULT_FILENAME


def get_run_state_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_run_dir(run_id, runs_root) / RUN_STATE_FILENAME


def get_events_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_run_dir(run_id, runs_root) / EVENTS_FILENAME


def get_task_run_state_path(run_id: str, task_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_task_dir(run_id, task_id, runs_root) / RUN_STATE_FILENAME


def get_task_events_path(run_id: str, task_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_task_dir(run_id, task_id, runs_root) / EVENTS_FILENAME


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


def write_run_state(run_id: str, payload: dict[str, Any], runs_root: Path = RUNS_ROOT) -> Path:
    path = get_run_state_path(run_id, runs_root)
    atomic_write_json(path, payload)
    return path


def read_run_state(run_id: str, runs_root: Path = RUNS_ROOT) -> dict[str, Any]:
    data = read_json(get_run_state_path(run_id, runs_root), encoding="utf-8")
    if not isinstance(data, dict):
        raise ValueError("run_state must be a JSON object")
    return data


def write_task_run_state(
    run_id: str,
    task_id: str,
    payload: dict[str, Any],
    runs_root: Path = RUNS_ROOT,
) -> Path:
    path = get_task_run_state_path(run_id, task_id, runs_root)
    atomic_write_json(path, payload)
    return path


def read_task_run_state(run_id: str, task_id: str, runs_root: Path = RUNS_ROOT) -> dict[str, Any]:
    data = read_json(get_task_run_state_path(run_id, task_id, runs_root), encoding="utf-8")
    if not isinstance(data, dict):
        raise ValueError("run_state must be a JSON object")
    return data


def append_event(run_id: str, event: dict[str, Any], runs_root: Path = RUNS_ROOT) -> Path:
    path = get_events_path(run_id, runs_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def read_events(run_id: str, runs_root: Path = RUNS_ROOT) -> list[dict[str, Any]]:
    path = get_events_path(run_id, runs_root)
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line_no, line in enumerate(read_text(path, encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parsed = json.loads(line)
        if not isinstance(parsed, dict):
            raise ValueError(f"events line {line_no} must be a JSON object")
        events.append(parsed)
    return events


def append_task_event(run_id: str, task_id: str, event: dict[str, Any], runs_root: Path = RUNS_ROOT) -> Path:
    path = get_task_events_path(run_id, task_id, runs_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def read_task_events(run_id: str, task_id: str, runs_root: Path = RUNS_ROOT) -> list[dict[str, Any]]:
    path = get_task_events_path(run_id, task_id, runs_root)
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line_no, line in enumerate(read_text(path, encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parsed = json.loads(line)
        if not isinstance(parsed, dict):
            raise ValueError(f"events line {line_no} must be a JSON object")
        events.append(parsed)
    return events
