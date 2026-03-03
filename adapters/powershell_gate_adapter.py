from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from core.file_io import atomic_write_text
from core.repo_paths import gate_script_path, resolve_repo_root, snapshot_script_path
from ports.gate_port import GateMode, GatePort, GateResult


class PowerShellGateAdapter(GatePort):
    def __init__(self, repo_root: Path | None = None) -> None:
        self._repo_root = Path(repo_root) if repo_root is not None else None

    def _write_repo_snapshot(self, run_dir: Path, repo_root: Path, env: Mapping[str, str] | None) -> None:
        snapshot_path = run_dir / "repo_snapshot.txt"
        script_path = snapshot_script_path(repo_root=repo_root)
        if not script_path.exists():
            atomic_write_text(
                snapshot_path,
                (
                    "snapshot_status=warning\n"
                    f"timestamp={datetime.now(timezone.utc).isoformat()}\n"
                    f"reason=missing script: {script_path}\n"
                    "git_status=unavailable\n"
                ),
                encoding="utf-8",
            )
            return
        try:
            subprocess.run(
                [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script_path),
                    "-RepoRoot",
                    str(repo_root),
                    "-OutputPath",
                    str(snapshot_path),
                ],
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
                env=dict(env) if env is not None else None,
            )
            if not snapshot_path.exists():
                atomic_write_text(
                    snapshot_path,
                    "snapshot_status=warning\nreason=snapshot script did not create output file\n",
                    encoding="utf-8",
                )
        except Exception as exc:
            atomic_write_text(
                snapshot_path,
                f"snapshot_status=warning\nreason=snapshot execution failed: {exc}\n",
                encoding="utf-8",
            )

    def run(
        self,
        *,
        mode: GateMode,
        cwd: Path,
        env: Mapping[str, str] | None = None,
    ) -> GateResult:
        run_dir = Path(cwd)
        run_dir.mkdir(parents=True, exist_ok=True)
        gate_log_path = run_dir / "gate.log"
        try:
            repo_root = resolve_repo_root(start_dir=Path.cwd(), explicit_repo_root=self._repo_root)
        except RuntimeError as exc:
            atomic_write_text(
                gate_log_path,
                (
                    f"mode={mode}\n"
                    "status=FAILED\n"
                    "exit_code=126\n"
                    f"reason={exc}\n"
                    "hint=Set REPO_ROOT or pass explicit repo_root to PowerShellGateAdapter\n"
                ),
                encoding="utf-8",
            )
            return {"status": "FAILED", "exit_code": 126, "gate_log_path": str(gate_log_path)}

        self._write_repo_snapshot(run_dir, repo_root, env)

        script_path = gate_script_path(repo_root=repo_root, mode=mode)
        if not script_path.exists():
            atomic_write_text(
                gate_log_path,
                (
                    f"mode={mode}\n"
                    "status=FAILED\n"
                    "exit_code=127\n"
                    f"reason=missing script: {script_path}\n"
                ),
                encoding="utf-8",
            )
            return {"status": "FAILED", "exit_code": 127, "gate_log_path": str(gate_log_path)}

        proc = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            env=dict(env) if env is not None else None,
        )
        status = "PASSED" if proc.returncode == 0 else "FAILED"
        atomic_write_text(
            gate_log_path,
            (
                f"mode={mode}\n"
                f"status={status}\n"
                f"exit_code={proc.returncode}\n"
                "--- stdout ---\n"
                f"{proc.stdout}\n"
                "--- stderr ---\n"
                f"{proc.stderr}\n"
            ),
            encoding="utf-8",
        )
        return {
            "status": status,
            "exit_code": int(proc.returncode),
            "gate_log_path": str(gate_log_path),
        }
