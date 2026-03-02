from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Mapping

from core.file_io import atomic_write_text
from ports.gate_port import GateMode, GatePort, GateResult


class PowerShellGateAdapter(GatePort):
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

        script_name = "fast_check.ps1" if mode == "fast" else "full_check.ps1"
        script_path = Path("scripts") / script_name
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
