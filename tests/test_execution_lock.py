from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from core.execution_lock import acquire, lock_path, release


def test_acquire_and_release_success(tmp_path: Path) -> None:
    run_dir = tmp_path / "reports" / "runs" / "run-1"
    ok, info = acquire(run_dir, owner="owner-a", ttl_sec=60)
    assert ok is True
    assert info is not None
    assert info["owner"] == "owner-a"
    assert lock_path(run_dir).exists()

    released = release(run_dir, owner="owner-a")
    assert released is True
    assert not lock_path(run_dir).exists()


def test_acquire_fails_when_lock_not_expired(tmp_path: Path) -> None:
    run_dir = tmp_path / "reports" / "runs" / "run-2"
    ok1, _ = acquire(run_dir, owner="owner-a", ttl_sec=60)
    ok2, info2 = acquire(run_dir, owner="owner-b", ttl_sec=60)
    assert ok1 is True
    assert ok2 is False
    assert info2 is not None
    assert info2["owner"] == "owner-a"


def test_acquire_can_preempt_expired_lock(tmp_path: Path) -> None:
    run_dir = tmp_path / "reports" / "runs" / "run-3"
    path = lock_path(run_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    stale = {
        "owner": "stale-owner",
        "acquired_at": (datetime.now(timezone.utc) - timedelta(seconds=120)).isoformat(),
        "ttl_sec": 1,
    }
    path.write_text(json.dumps(stale), encoding="utf-8")

    ok, info = acquire(run_dir, owner="owner-new", ttl_sec=60)
    assert ok is True
    assert info is not None
    assert info["owner"] == "owner-new"


def test_release_rejects_owner_mismatch(tmp_path: Path) -> None:
    run_dir = tmp_path / "reports" / "runs" / "run-4"
    ok, _ = acquire(run_dir, owner="owner-a", ttl_sec=60)
    assert ok is True

    with pytest.raises(ValueError, match="run_id=run-4"):
        release(run_dir, owner="owner-b")
