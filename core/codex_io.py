from __future__ import annotations

from pathlib import Path
from typing import Any

from core.events_log import append_event
from core.file_io import atomic_write_json, atomic_write_text, read_json, read_text

RUNS_ROOT = Path("reports") / "runs"
CODEX_TASK_FILENAME = "task.md"
CODEX_RESULT_FILENAME = "result.json"
HITL_PROMPT_FILENAME = "hitl_prompt.md"
HITL_RESPONSE_FILENAME = "hitl_response.md"

LEGACY_CODEX_TASK_FILENAME = "codex_task.md"
LEGACY_CODEX_RESULT_FILENAME = "codex_result.json"
LEGACY_HITL_PROMPT_FILENAME = "web_gpt_prompt.md"
LEGACY_HITL_RESPONSE_FILENAME = "web_gpt_response.md"


def get_run_dir(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return runs_root / run_id


def get_codex_task_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_run_dir(run_id, runs_root) / CODEX_TASK_FILENAME


def get_codex_result_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_run_dir(run_id, runs_root) / CODEX_RESULT_FILENAME


def get_hitl_prompt_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_run_dir(run_id, runs_root) / HITL_PROMPT_FILENAME


def get_hitl_response_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return get_run_dir(run_id, runs_root) / HITL_RESPONSE_FILENAME


def _ordered_existing_path(run_dir: Path, candidates: list[str], kind: str) -> Path:
    for rel in candidates:
        p = run_dir / rel
        if p.exists() and p.is_file():
            return p
    for rel in candidates:
        if "*" in rel:
            for matched in sorted(run_dir.glob(rel)):
                if matched.is_file():
                    return matched
    chain = " -> ".join(str(run_dir / c) for c in candidates)
    raise FileNotFoundError(f"{kind} artifact not found; lookup chain: {chain}")


def resolve_result_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    run_dir = get_run_dir(run_id, runs_root)
    candidates = [
        CODEX_RESULT_FILENAME,
        LEGACY_CODEX_RESULT_FILENAME,
        f"artifacts/{CODEX_RESULT_FILENAME}",
        f"artifacts/{LEGACY_CODEX_RESULT_FILENAME}",
        f"tasks/*/artifacts/{CODEX_RESULT_FILENAME}",
        f"tasks/*/artifacts/{LEGACY_CODEX_RESULT_FILENAME}",
    ]
    return _ordered_existing_path(run_dir, candidates, kind="result")


def resolve_task_md_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    run_dir = get_run_dir(run_id, runs_root)
    candidates = [
        CODEX_TASK_FILENAME,
        LEGACY_CODEX_TASK_FILENAME,
        f"artifacts/{CODEX_TASK_FILENAME}",
        f"artifacts/{LEGACY_CODEX_TASK_FILENAME}",
        f"tasks/*/artifacts/{CODEX_TASK_FILENAME}",
        f"tasks/*/artifacts/{LEGACY_CODEX_TASK_FILENAME}",
    ]
    return _ordered_existing_path(run_dir, candidates, kind="task")


def resolve_hitl_prompt_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    run_dir = get_run_dir(run_id, runs_root)
    candidates = [
        HITL_PROMPT_FILENAME,
        LEGACY_HITL_PROMPT_FILENAME,
        f"artifacts/{HITL_PROMPT_FILENAME}",
        f"artifacts/{LEGACY_HITL_PROMPT_FILENAME}",
        f"tasks/*/artifacts/{HITL_PROMPT_FILENAME}",
        f"tasks/*/artifacts/{LEGACY_HITL_PROMPT_FILENAME}",
    ]
    return _ordered_existing_path(run_dir, candidates, kind="hitl_prompt")


def resolve_hitl_response_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    run_dir = get_run_dir(run_id, runs_root)
    candidates = [
        HITL_RESPONSE_FILENAME,
        LEGACY_HITL_RESPONSE_FILENAME,
        f"artifacts/{HITL_RESPONSE_FILENAME}",
        f"artifacts/{LEGACY_HITL_RESPONSE_FILENAME}",
        f"tasks/*/artifacts/{HITL_RESPONSE_FILENAME}",
        f"tasks/*/artifacts/{LEGACY_HITL_RESPONSE_FILENAME}",
    ]
    return _ordered_existing_path(run_dir, candidates, kind="hitl_response")


def write_codex_task(run_id: str, content: str, runs_root: Path = RUNS_ROOT) -> Path:
    path = get_codex_task_path(run_id, runs_root)
    atomic_write_text(path, content, encoding="utf-8")
    return path


def read_codex_task(run_id: str, runs_root: Path = RUNS_ROOT) -> str:
    return read_text(resolve_task_md_path(run_id, runs_root), encoding="utf-8")


def write_codex_result(run_id: str, payload: dict[str, Any], runs_root: Path = RUNS_ROOT) -> Path:
    path = get_codex_result_path(run_id, runs_root)
    if path.exists():
        previous = read_json(path, encoding="utf-8")
        if previous == payload:
            append_event(
                run_id,
                {
                    "type": "codex_result_skipped_idempotent",
                    "path": str(path),
                },
            )
            return path

    atomic_write_json(path, payload)
    append_event(
        run_id,
        {
            "type": "codex_result_written",
            "path": str(path),
        },
    )
    return path


def read_codex_result(run_id: str, runs_root: Path = RUNS_ROOT) -> dict[str, Any]:
    data = read_json(resolve_result_path(run_id, runs_root), encoding="utf-8")
    if not isinstance(data, dict):
        raise ValueError("codex_result must be a JSON object")
    return data


def write_hitl_prompt(run_id: str, content: str, runs_root: Path = RUNS_ROOT) -> Path:
    path = get_hitl_prompt_path(run_id, runs_root)
    atomic_write_text(path, content, encoding="utf-8")
    return path


def read_hitl_prompt(run_id: str, runs_root: Path = RUNS_ROOT) -> str:
    return read_text(resolve_hitl_prompt_path(run_id, runs_root), encoding="utf-8")


def write_hitl_response(run_id: str, content: str, runs_root: Path = RUNS_ROOT) -> Path:
    path = get_hitl_response_path(run_id, runs_root)
    atomic_write_text(path, content, encoding="utf-8")
    return path


def read_hitl_response(run_id: str, runs_root: Path = RUNS_ROOT) -> str:
    return read_text(resolve_hitl_response_path(run_id, runs_root), encoding="utf-8")

