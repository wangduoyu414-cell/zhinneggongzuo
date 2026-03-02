from __future__ import annotations

from pathlib import Path
from typing import Mapping, Protocol, TypedDict


class ExecutorResult(TypedDict):
    exit_code: int
    result_json_path: str
    commands_log_path: str
    patch_summary_path: str


class ExecutorPort(Protocol):
    def execute(
        self,
        task_dir: Path,
        task_md_path: Path,
        *,
        timeout_sec: int,
        env: Mapping[str, str] | None = None,
    ) -> ExecutorResult: ...
