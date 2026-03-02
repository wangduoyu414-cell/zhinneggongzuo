from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUNS_ROOT = Path("reports") / "runs"
EVENTS_FILENAME = "events.jsonl"

def get_events_path(run_id: str, runs_root: Path = RUNS_ROOT) -> Path:
    return runs_root / run_id / EVENTS_FILENAME

def append_event(run_id: str, event: dict[str, Any], runs_root: Path = RUNS_ROOT) -> Path:
    path = get_events_path(run_id, runs_root)
    path.parent.mkdir(parents=True, exist_ok=True)

    record = dict(event)
    record.setdefault("ts", datetime.now(timezone.utc).isoformat())

    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()

    return path
