from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.file_io import atomic_write_json, read_json

RUNS_ROOT = Path("reports") / "runs"
STATE_FILENAME = "run_state.json"


def state_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return runs_root / run_id / STATE_FILENAME


def load_state(run_id: str, runs_root: Path = RUNS_ROOT) -> dict[str, Any] | None:
    path = state_path(run_id, runs_root=runs_root)
    if not path.exists():
        return None
    data = read_json(path, encoding="utf-8")
    if not isinstance(data, dict):
        raise ValueError("run_state must be a JSON object")
    return data


def save_state(run_id: str, state_dict: dict[str, Any], runs_root: Path = RUNS_ROOT) -> Path:
    path = state_path(run_id, runs_root=runs_root)
    state = dict(state_dict)
    state["run_id"] = run_id
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    atomic_write_json(path, state)
    return path
