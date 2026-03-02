from __future__ import annotations

from pathlib import Path
from typing import Any

from core.file_io import atomic_write_json, read_json

STATE_V1_FILENAME = "state.v1.json"


def write_state_v1(run_id: str, state_v1: dict[str, Any], runs_root: Path) -> Path:
    path = Path(runs_root) / run_id / STATE_V1_FILENAME
    if path.exists():
        previous = read_json(path, encoding="utf-8")
        if previous == state_v1:
            return path
    atomic_write_json(path, state_v1)
    return path
