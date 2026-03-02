from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from core.file_io import atomic_write_json

LOCK_FILENAME = "execution.lock"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _run_id_from_dir(run_dir: Path) -> str:
    return Path(run_dir).name


def lock_path(run_dir: Path) -> Path:
    return Path(run_dir) / LOCK_FILENAME


def _read_lock(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("lock file must be JSON object")
    return data


def _is_expired(lock: dict[str, Any], now: datetime) -> bool:
    acquired_raw = lock.get("acquired_at")
    ttl_raw = lock.get("ttl_sec")
    if not isinstance(acquired_raw, str) or not isinstance(ttl_raw, int):
        return True
    try:
        acquired_at = datetime.fromisoformat(acquired_raw)
    except ValueError:
        return True
    if acquired_at.tzinfo is None:
        acquired_at = acquired_at.replace(tzinfo=timezone.utc)
    return now >= (acquired_at + timedelta(seconds=ttl_raw))


def acquire(run_dir: Path, owner: str, ttl_sec: int) -> tuple[bool, dict[str, Any] | None]:
    target_dir = Path(run_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    path = lock_path(target_dir)
    now = _utc_now()
    new_lock = {
        "owner": owner,
        "acquired_at": now.isoformat(),
        "ttl_sec": int(ttl_sec),
    }
    if not path.exists():
        atomic_write_json(path, new_lock)
        return True, new_lock

    current = _read_lock(path)
    if _is_expired(current, now):
        atomic_write_json(path, new_lock)
        return True, new_lock

    return False, current


def release(run_dir: Path, owner: str) -> bool:
    path = lock_path(run_dir)
    if not path.exists():
        return True

    current = _read_lock(path)
    lock_owner = str(current.get("owner", ""))
    if lock_owner != owner:
        run_id = _run_id_from_dir(run_dir)
        raise ValueError(
            f"execution lock owner mismatch run_id={run_id} lock_owner={lock_owner} owner={owner}"
        )
    path.unlink()
    return True
