from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Callable

from core.file_io import atomic_write_json, atomic_write_text


def _default_runner(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)


def run_codex(
    task_dir: Path,
    codex_task_path: Path,
    *,
    runner: Callable[[list[str], Path], Any] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    task_dir = Path(task_dir)
    codex_task_path = Path(codex_task_path)
    artifacts_dir = task_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    commands_log_path = artifacts_dir / "commands.log"
    patch_summary_path = artifacts_dir / "patch_summary.md"
    codex_result_path = artifacts_dir / "codex_result.json"

    cmd = ["codex", "run", str(codex_task_path)]
    if dry_run:
        return_code = 0
        stdout = ""
        stderr = ""
    else:
        invoke = runner or _default_runner
        result = invoke(cmd, task_dir)
        return_code = int(getattr(result, "returncode", 0))
        stdout = str(getattr(result, "stdout", ""))
        stderr = str(getattr(result, "stderr", ""))

    log_text = (
        f"cwd: {task_dir}\n"
        f"command: {' '.join(cmd)}\n"
        f"return_code: {return_code}\n"
        f"--- stdout ---\n{stdout}\n"
        f"--- stderr ---\n{stderr}\n"
    )
    atomic_write_text(commands_log_path, log_text, encoding="utf-8")

    patch_summary = "# Patch Summary\n\n"
    if stdout.strip():
        patch_summary += "```\n" + stdout.strip() + "\n```\n"
    else:
        patch_summary += "_No patch summary available._\n"
    atomic_write_text(patch_summary_path, patch_summary, encoding="utf-8")

    placeholder = {
        "contract_version": "0",
        "result": "pending" if return_code == 0 else "failed",
        "artifacts": {
            "commands_log": str(commands_log_path),
            "patch_summary": str(patch_summary_path),
            "result": str(codex_result_path),
        },
        "meta": {
            "executor": "codex_cli",
            "return_code": return_code,
            "dry_run": dry_run,
        },
    }
    atomic_write_json(codex_result_path, placeholder)

    return {
        "return_code": return_code,
        "stdout": stdout,
        "stderr": stderr,
        "commands_log_path": commands_log_path,
        "patch_summary_path": patch_summary_path,
        "codex_result_path": codex_result_path,
    }
