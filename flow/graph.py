from __future__ import annotations

from pathlib import Path
from typing import Any

from core.codex_cli_executor import run_codex
from core.execution_lock import acquire, release
from core.codex_result_validation import validate_codex_result
from core.file_io import atomic_write_text, read_json
from core.scheduler import next_runnable_task
from core.task_manager import TaskManager
from core.transitions import validate_transition


def run_serial_flow(
    run_id: str,
    tasks: dict[str, dict[str, Any]],
    *,
    runs_root: Path = Path("reports") / "runs",
    enable_true_concurrency: bool = False,
) -> dict[str, str]:
    run_dir = Path(runs_root) / run_id
    lock_owner = "run_serial_flow"
    acquired, lock_info = acquire(run_dir, lock_owner, ttl_sec=300)
    if not acquired:
        lock_owner_info = None if lock_info is None else lock_info.get("owner")
        raise ValueError(f"execution lock busy run_id={run_id} lock_owner={lock_owner_info}")

    if enable_true_concurrency:
        raise ValueError("enable_true_concurrency is not supported in W4")

    try:
        task_states: dict[str, str] = {task_id: "PENDING" for task_id in tasks}
        deps_by_task = {task_id: list(task.get("deps", [])) for task_id, task in tasks.items()}

        while True:
            task_id = next_runnable_task(task_states, deps_by_task)
            if task_id is None:
                break

            task_stage = "INIT"
            validate_transition(task_stage, "EXECUTING")
            task_stage = "EXECUTING"

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
                validate_transition(task_stage, "WAIT_INPUT")
                task_states[task_id] = "WAITING_RESULT"
                continue

            try:
                payload = read_json(result_path, encoding="utf-8")
                if not isinstance(payload, dict):
                    raise ValueError("codex_result must be a JSON object")
                validate_codex_result(payload)
                manager.append_event("RESULT_INGESTED", {"result": payload.get("result")})
                validate_transition(task_stage, "DONE")
                manager.complete_success()
                task_states[task_id] = "DONE"
            except Exception as exc:
                validate_transition(task_stage, "FAILED")
                manager.complete_failure(str(exc))
                task_states[task_id] = "FAILED"

        return task_states
    finally:
        release(run_dir, lock_owner)


def resume_execute_once(
    run_id: str,
    task_id: str,
    *,
    runs_root: Path = Path("reports") / "runs",
) -> dict[str, Any]:
    manager = TaskManager(run_id=run_id, task_id=task_id, runs_root=runs_root)
    manager.ensure_layout()
    codex_task_path = manager.task_dir / "codex_task.md"
    if not codex_task_path.exists():
        return {"status": "MISSING_CODEX_TASK", "result_path": str(manager.artifacts_dir / "codex_result.json")}

    output = run_codex(manager.task_dir, codex_task_path, dry_run=False)
    return {
        "status": "EXECUTED",
        "return_code": int(output.get("return_code", 0)),
        "result_path": str(manager.artifacts_dir / "codex_result.json"),
    }
