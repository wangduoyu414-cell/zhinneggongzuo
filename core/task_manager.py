from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.file_io import atomic_write_json

RUN_STATE_FILENAME = "run_state.json"
EVENTS_FILENAME = "events.jsonl"
ARTIFACTS_DIRNAME = "artifacts"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskManager:
    def __init__(self, run_id: str, task_id: str, runs_root: Path = Path("reports") / "runs") -> None:
        self.run_id = run_id
        self.task_id = task_id
        self.runs_root = Path(runs_root)
        self.task_dir = self.runs_root / run_id / task_id
        self.artifacts_dir = self.task_dir / ARTIFACTS_DIRNAME
        self.run_state_path = self.task_dir / RUN_STATE_FILENAME
        self.events_path = self.task_dir / EVENTS_FILENAME

    def ensure_layout(self, max_retries: int = 3) -> None:
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        if not self.run_state_path.exists():
            state = {
                "run_id": self.run_id,
                "task_id": self.task_id,
                "status": "PENDING",
                "attempts": 0,
                "max_retries": max_retries,
                "consecutive_failures": 0,
                "stop_the_line": False,
                "last_error": None,
                "updated_at": _utc_now(),
            }
            self.save_state(state)
        if not self.events_path.exists():
            self.events_path.parent.mkdir(parents=True, exist_ok=True)
            self.events_path.touch()

    def load_state(self) -> dict[str, Any]:
        if not self.run_state_path.exists():
            self.ensure_layout()
        with self.run_state_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("run_state.json must be a JSON object")
        return data

    def save_state(self, state: dict[str, Any]) -> None:
        state["updated_at"] = _utc_now()
        atomic_write_json(self.run_state_path, state)

    def append_event(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "ts": _utc_now(),
            "run_id": self.run_id,
            "task_id": self.task_id,
            "type": event_type,
            "payload": payload or {},
        }
        with self.events_path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    def begin_attempt(self) -> dict[str, Any]:
        state = self.load_state()
        state["attempts"] = int(state.get("attempts", 0)) + 1
        state["status"] = "RUNNING"
        self.save_state(state)
        self.append_event("TASK_RUNNING", {"attempt": state["attempts"]})
        return state

    def complete_success(self) -> dict[str, Any]:
        state = self.load_state()
        state["status"] = "DONE"
        state["consecutive_failures"] = 0
        state["stop_the_line"] = False
        state["last_error"] = None
        self.save_state(state)
        self.append_event("TASK_DONE", {})
        return state

    def complete_failure(self, error: str) -> dict[str, Any]:
        state = self.load_state()
        failures = int(state.get("consecutive_failures", 0)) + 1
        max_retries = int(state.get("max_retries", 3))
        state["status"] = "FAILED"
        state["consecutive_failures"] = failures
        state["last_error"] = error
        state["stop_the_line"] = failures >= max_retries
        self.save_state(state)
        self.append_event(
            "TASK_FAILED",
            {
                "error": error,
                "consecutive_failures": failures,
                "max_retries": max_retries,
                "stop_the_line": state["stop_the_line"],
            },
        )
        return state
