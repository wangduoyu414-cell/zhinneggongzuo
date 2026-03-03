from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.events_log import append_event
from core.execution_lock import acquire, release
from core.file_io import atomic_write_text, read_json
from core.repo_paths import gate_script_path, resolve_repo_root, snapshot_script_path
from core.run_state import RUNS_ROOT, load_state, save_state
from core.state_v1 import map_stage
from core.transitions import validate_transition
from flow.graph import resume_execute_once

RESULT_CANDIDATES = (
    "result.json",
    "codex_result.json",
    "artifacts/result.json",
    "artifacts/codex_result.json",
    "tasks/t1/artifacts/result.json",
    "tasks/t1/artifacts/codex_result.json",
)

INPUT_CANDIDATES = (
    "hitl_response.md",
    "web_gpt_response.md",
    "artifacts/hitl_response.md",
    "artifacts/web_gpt_response.md",
    "tasks/t1/artifacts/hitl_response.md",
    "tasks/t1/artifacts/web_gpt_response.md",
)

GATE_LOG_NAME = "gate.log"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _find_existing(run_dir: Path, candidates: tuple[str, ...]) -> Path | None:
    for rel in candidates:
        path = run_dir / rel
        if path.exists() and path.is_file():
            return path
    return None


def _result_exists_and_valid(run_dir: Path) -> bool:
    path = _find_existing(run_dir, RESULT_CANDIDATES)
    if path is None:
        return False
    try:
        payload = read_json(path, encoding="utf-8")
    except Exception:
        return False
    return isinstance(payload, dict)


def _input_exists(run_dir: Path) -> bool:
    path = _find_existing(run_dir, INPUT_CANDIDATES)
    return path is not None and path.stat().st_size > 0


def _gate_status_from_log(gate_log_path: Path) -> str | None:
    if not gate_log_path.exists():
        return None
    text = gate_log_path.read_text(encoding="utf-8")
    if "status=PASSED" in text or "PASSED" in text:
        return "PASSED"
    if "status=FAILED" in text or "FAILED" in text:
        return "FAILED"
    return None


def _write_repo_snapshot(run_dir: Path, repo_root: Path) -> Path:
    snapshot_path = run_dir / "repo_snapshot.txt"
    script_path = snapshot_script_path(repo_root=repo_root)
    if not script_path.exists():
        atomic_write_text(
            snapshot_path,
            (
                f"timestamp={_utc_now()}\n"
                "snapshot_status=warning\n"
                f"reason=missing script: {script_path}\n"
                "git_status=unavailable\n"
            ),
            encoding="utf-8",
        )
        return snapshot_path
    try:
        proc = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script_path),
                "-RepoRoot",
                str(repo_root),
                "-OutputPath",
                str(snapshot_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if not snapshot_path.exists():
            atomic_write_text(
                snapshot_path,
                (
                    f"timestamp={_utc_now()}\n"
                    "snapshot_status=warning\n"
                    "reason=snapshot script did not create output file\n"
                    f"exit_code={proc.returncode}\n"
                ),
                encoding="utf-8",
            )
    except Exception as exc:
        atomic_write_text(
            snapshot_path,
            (
                f"timestamp={_utc_now()}\n"
                "snapshot_status=warning\n"
                f"reason=snapshot execution failed: {exc}\n"
            ),
            encoding="utf-8",
        )
    return snapshot_path


def _run_gate(run_dir: Path, mode: str) -> tuple[bool, Path, str]:
    gate_log_path = run_dir / GATE_LOG_NAME
    try:
        repo_root = resolve_repo_root(start_dir=run_dir)
    except RuntimeError as exc:
        log = (
            f"mode={mode}\nstatus=FAILED\nexit_code=126\n"
            f"reason={exc}\n"
            "hint=Set REPO_ROOT to the repository root path\n"
        )
        atomic_write_text(gate_log_path, log, encoding="utf-8")
        return False, gate_log_path, "repo_root unresolved"

    _write_repo_snapshot(run_dir, repo_root)
    script_path = gate_script_path(repo_root=repo_root, mode=mode)
    if not script_path.exists():
        log = f"mode={mode}\nstatus=FAILED\nexit_code=127\nreason=missing script: {script_path}\n"
        atomic_write_text(gate_log_path, log, encoding="utf-8")
        return False, gate_log_path, "missing script"

    proc = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    status = "PASSED" if proc.returncode == 0 else "FAILED"
    log = (
        f"mode={mode}\nstatus={status}\nexit_code={proc.returncode}\n"
        f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}\n"
    )
    atomic_write_text(gate_log_path, log, encoding="utf-8")
    return proc.returncode == 0, gate_log_path, status


def _legacy_status_for(stage: str) -> str:
    if stage in ("INIT", "WAIT_INPUT"):
        return "PENDING"
    if stage in ("EXECUTING", "GATING"):
        return "RUNNING"
    return stage


def _write_stage(run_id: str, runs_root: Path, state: dict[str, Any], new_stage: str) -> None:
    merged = dict(state)
    merged["stage"] = new_stage
    merged["status"] = _legacy_status_for(new_stage)
    merged["updated_at"] = _utc_now()
    save_state(run_id, merged, runs_root=runs_root)
    append_event(
        run_id,
        {"type": "resume_stage_set", "from_stage": map_stage(state), "to_stage": new_stage},
        runs_root=runs_root,
    )


def resume_run(run_id: str, runs_root: Path = RUNS_ROOT, gate_mode: str = "fast") -> str:
    run_dir = Path(runs_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    owner = "resume_run"
    acquired, lock_info = acquire(run_dir, owner, ttl_sec=300)
    if not acquired:
        lock_owner = None if lock_info is None else lock_info.get("owner")
        append_event(
            run_id,
            {"type": "resume_lock_blocked", "run_id": run_id, "lock_owner": lock_owner},
            runs_root=runs_root,
        )
        state = load_state(run_id, runs_root=runs_root) or {}
        return map_stage(state)

    try:
        state = load_state(run_id, runs_root=runs_root) or {"run_id": run_id}
        stage = map_stage(state)
        append_event(run_id, {"type": "resume_started", "run_id": run_id, "stage": stage}, runs_root=runs_root)

        if stage == "INIT":
            validate_transition("INIT", "WAIT_INPUT")
            _write_stage(run_id, runs_root, state, "WAIT_INPUT")
            return "WAIT_INPUT"

        if stage == "WAIT_INPUT":
            if not _input_exists(run_dir):
                append_event(
                    run_id,
                    {"type": "resume_wait_input", "run_id": run_id, "reason": "missing input artifact"},
                    runs_root=runs_root,
                )
                return "WAIT_INPUT"
            validate_transition("WAIT_INPUT", "EXECUTING")
            _write_stage(run_id, runs_root, state, "EXECUTING")
            return "EXECUTING"

        if stage == "EXECUTING":
            if _result_exists_and_valid(run_dir):
                validate_transition("EXECUTING", "GATING")
                _write_stage(run_id, runs_root, state, "GATING")
                return "GATING"

            task_id = state.get("task_id")
            if not isinstance(task_id, str) or not task_id:
                err = {
                    "message": "missing task_id for EXECUTING resume",
                    "retryable": True,
                    "at": _utc_now(),
                }
                failed = dict(state)
                failed["last_error"] = err
                validate_transition("EXECUTING", "FAILED")
                _write_stage(run_id, runs_root, failed, "FAILED")
                return "FAILED"

            exec_result = resume_execute_once(run_id, task_id, runs_root=runs_root)
            append_event(
                run_id,
                {"type": "resume_execute_once", "run_id": run_id, "result": exec_result.get("status", "unknown")},
                runs_root=runs_root,
            )
            if _result_exists_and_valid(run_dir):
                validate_transition("EXECUTING", "GATING")
                _write_stage(run_id, runs_root, state, "GATING")
                return "GATING"

            err = {
                "message": "execution did not produce valid result artifact",
                "retryable": True,
                "at": _utc_now(),
            }
            failed = dict(state)
            failed["last_error"] = err
            validate_transition("EXECUTING", "FAILED")
            _write_stage(run_id, runs_root, failed, "FAILED")
            return "FAILED"

        if stage == "GATING":
            gate_log_path = run_dir / GATE_LOG_NAME
            gate_status = _gate_status_from_log(gate_log_path)
            if gate_status == "PASSED":
                validate_transition("GATING", "DONE")
                _write_stage(run_id, runs_root, state, "DONE")
                return "DONE"
            if gate_status == "FAILED":
                failed = dict(state)
                failed["last_error"] = {
                    "message": "gate evidence indicates FAILED",
                    "retryable": True,
                    "at": _utc_now(),
                }
                validate_transition("GATING", "FAILED")
                _write_stage(run_id, runs_root, failed, "FAILED")
                return "FAILED"

            ok, _, status = _run_gate(run_dir, gate_mode)
            if ok:
                validate_transition("GATING", "DONE")
                _write_stage(run_id, runs_root, state, "DONE")
                return "DONE"

            failed = dict(state)
            failed["last_error"] = {
                "message": f"gate execution failed status={status}",
                "retryable": True,
                "at": _utc_now(),
            }
            validate_transition("GATING", "FAILED")
            _write_stage(run_id, runs_root, failed, "FAILED")
            return "FAILED"

        return stage
    finally:
        release(run_dir, owner)
