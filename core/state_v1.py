from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_STAGES = ("INIT", "WAIT_INPUT", "EXECUTING", "GATING", "DONE", "FAILED")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def map_stage(old_state: dict[str, Any]) -> str:
    raw_stage = old_state.get("stage")
    if isinstance(raw_stage, str):
        stage = raw_stage.strip()
        if stage in ALLOWED_STAGES:
            return stage
        if stage == "WAIT_GPT":
            return "WAIT_INPUT"

    raw_status = old_state.get("status")
    if isinstance(raw_status, str):
        status = raw_status.strip().upper()
        if status == "PENDING":
            return "INIT"
        if status in ("RUNNING", "WAITING_RESULT"):
            return "EXECUTING"
        if status == "DONE":
            return "DONE"
        if status == "FAILED":
            return "FAILED"

    return "INIT"


def build_state_v1(run_id: str, old_state: dict[str, Any], state_path: Path) -> dict[str, Any]:
    created_at = old_state.get("created_at")
    updated_at = old_state.get("updated_at")
    now = _utc_now()
    created_at_value = created_at if isinstance(created_at, str) and created_at else now
    updated_at_value = updated_at if isinstance(updated_at, str) and updated_at else now

    out: dict[str, Any] = {
        "schema_version": "state.v1",
        "run_id": run_id,
        "created_at": created_at_value,
        "updated_at": updated_at_value,
        "stage": map_stage(old_state),
        "evidence": {
            "state_path": str(state_path),
        },
    }

    project = old_state.get("project")
    if isinstance(project, str) and project:
        out["project"] = project

    risk = old_state.get("risk")
    if isinstance(risk, str) and risk in ("low", "mid", "high"):
        out["risk"] = risk

    raw_last_error = old_state.get("last_error")
    if raw_last_error:
        if isinstance(raw_last_error, dict):
            message = str(raw_last_error.get("message") or "unknown error")
            retryable = bool(raw_last_error.get("retryable", False))
            at_value = str(raw_last_error.get("at") or updated_at_value)
            last_error: dict[str, Any] = {
                "message": message,
                "retryable": retryable,
                "at": at_value,
            }
            code = raw_last_error.get("code")
            task_id = raw_last_error.get("task_id")
            if isinstance(code, str) and code:
                last_error["code"] = code
            if isinstance(task_id, str) and task_id:
                last_error["task_id"] = task_id
        else:
            task_id = old_state.get("task_id")
            last_error = {
                "message": str(raw_last_error),
                "retryable": False,
                "at": updated_at_value,
            }
            if isinstance(task_id, str) and task_id:
                last_error["task_id"] = task_id
        out["last_error"] = last_error

    return out
