from __future__ import annotations

import os
from pathlib import Path

from ports.gate_port import GateMode


def resolve_repo_root(*, start_dir: Path | None = None, explicit_repo_root: Path | None = None) -> Path:
    if explicit_repo_root is not None:
        root = Path(explicit_repo_root).resolve()
        return root

    env_root = os.getenv("REPO_ROOT")
    if env_root:
        return Path(env_root).resolve()

    cursor = (start_dir or Path(__file__).resolve().parent).resolve()
    for candidate in (cursor, *cursor.parents):
        if (candidate / ".git").exists():
            return candidate

    raise RuntimeError(
        "Unable to resolve repo_root. Set REPO_ROOT or pass explicit repo_root to gate adapter."
    )


def gate_script_path(*, repo_root: Path, mode: GateMode) -> Path:
    script_name = "fast_check.ps1" if mode == "fast" else "full_check.ps1"
    return Path(repo_root) / "scripts" / script_name


def snapshot_script_path(*, repo_root: Path) -> Path:
    return Path(repo_root) / "scripts" / "repo_snapshot.ps1"
