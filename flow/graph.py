from __future__ import annotations

from pathlib import Path
from typing import Any

from core.codex_cli_executor import run_codex
from core.codex_result_validation import validate_codex_result
from core.file_io import atomic_write_text, read_json
from core.scheduler import next_runnable_task
from core.task_manager import TaskManager


def run_serial_flow(
    run_id: str,
    tasks: dict[str, dict[str, Any]],
    *,
    runs_root: Path = Path("reports") / "runs",
    enable_true_concurrency: bool = False,
) -> dict[str, str]:
    if enable_true_concurrency:
        raise ValueError("enable_true_concurrency is not supported in W4")

    task_states: dict[str, str] = {task_id: "PENDING" for task_id in tasks}
    deps_by_task = {task_id: list(task.get("deps", [])) for task_id, task in tasks.items()}

    while True:
        task_id = next_runnable_task(task_states, deps_by_task)
        if task_id is None:
            break

        task = tasks[task_id]
        manager = TaskManager(run_id=run_id, task_id=task_id, runs_root=runs_root)
        manager.ensure_layout(max_retries=int(task.get("max_retries", 3)))
        manager.begin_attempt()
        manager.append_event("TASK_SELECTED", {"deps": deps_by_task.get(task_id, [])})

        codex_task_path = manager.task_dir / "codex_task.md"
        atomic_write_text(codex_task_path, str(task.get("codex_task", "")), encoding="utf-8")
        manager.append_event("CODEX_TASK_EMITTED", {"path": str(codex_task_path)})

        run_codex(manager.task_dir, codex_task_path, dry_run=bool(task.get("dry_run", False)))
        manager.append_event("WAITING_RESULT", {"path": str(manager.artifacts_dir / "codex_result.json")})

        result_path = manager.artifacts_dir / "codex_result.json"
        if not result_path.exists():
            task_states[task_id] = "WAITING_RESULT"
            continue

        try:
            payload = read_json(result_path, encoding="utf-8")
            if not isinstance(payload, dict):
                raise ValueError("codex_result must be a JSON object")
            validate_codex_result(payload)
            manager.append_event("RESULT_INGESTED", {"result": payload.get("result")})
            manager.complete_success()
            task_states[task_id] = "DONE"
        except Exception as exc:
            manager.complete_failure(str(exc))
            task_states[task_id] = "FAILED"

    return task_states
