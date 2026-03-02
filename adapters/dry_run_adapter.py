from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from core.file_io import atomic_write_json, atomic_write_text
from ports.executor_port import ExecutorPort, ExecutorResult


class DryRunAdapter(ExecutorPort):
    def execute(
        self,
        task_dir: Path,
        task_md_path: Path,
        *,
        timeout_sec: int,
        env: Mapping[str, str] | None = None,
    ) -> ExecutorResult:
        task_dir = Path(task_dir)
        run_dir = task_dir.parent
        run_dir.mkdir(parents=True, exist_ok=True)

        result_path = run_dir / "result.json"
        commands_path = run_dir / "commands.log"
        patch_summary_path = run_dir / "patch_summary.md"

        atomic_write_text(
            commands_path,
            (
                "adapter=dry_run\n"
                f"task_md_path={Path(task_md_path)}\n"
                f"timeout_sec={int(timeout_sec)}\n"
                f"env_keys={','.join(sorted((env or {}).keys()))}\n"
                "exit_code=0\n"
            ),
            encoding="utf-8",
        )
        atomic_write_text(
            patch_summary_path,
            "# Patch Summary\n\n_Dry run adapter: no external command executed._\n",
            encoding="utf-8",
        )

        payload = {
            "success": True,
            "exit_code": 0,
            "summary": "dry run completed",
            "artifacts": {
                "result_json_path": str(result_path),
                "commands_log_path": str(commands_path),
                "patch_summary_path": str(patch_summary_path),
            },
        }
        # Guard against accidental non-serializable values.
        json.dumps(payload, ensure_ascii=False)
        atomic_write_json(result_path, payload)

        return {
            "exit_code": 0,
            "result_json_path": str(result_path),
            "commands_log_path": str(commands_path),
            "patch_summary_path": str(patch_summary_path),
        }
