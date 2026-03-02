from __future__ import annotations

from pathlib import Path

from adapters.dry_run_adapter import DryRunAdapter
from adapters.manual_hitl_adapter import ManualHitlAdapter
from adapters.powershell_gate_adapter import PowerShellGateAdapter
from core.file_io import read_json


def test_dry_run_adapter_writes_minimal_result_json(tmp_path: Path) -> None:
    task_dir = tmp_path / "run-1" / "task-1"
    task_dir.mkdir(parents=True, exist_ok=True)
    task_md_path = task_dir / "task.md"
    task_md_path.write_text("do something", encoding="utf-8")

    adapter = DryRunAdapter()
    out = adapter.execute(task_dir, task_md_path, timeout_sec=30)
    payload = read_json(out["result_json_path"], encoding="utf-8")
    assert out["result_json_path"] == str(tmp_path / "run-1" / "result.json")
    assert payload["success"] is True
    assert payload["exit_code"] == 0
    assert "summary" in payload


def test_manual_hitl_adapter_emit_receive_and_idempotent_ingest(tmp_path: Path) -> None:
    prompt_path = tmp_path / "run-2" / "hitl_prompt.md"
    adapter = ManualHitlAdapter()

    emitted = adapter.emit_prompt(prompt_path)
    assert emitted.exists()
    first = adapter.ingest_response(prompt_path, "response from web")
    second = adapter.ingest_response(prompt_path, "response from web")
    received = adapter.receive_response(prompt_path)

    assert first["ingested"] is True
    assert second["ingested"] is False
    assert received["received"] is True


def test_gate_adapter_missing_script_is_observable_failure(tmp_path: Path) -> None:
    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        adapter = PowerShellGateAdapter()
        run_dir = tmp_path / "runs" / "run-3"
        out = adapter.run(mode="fast", cwd=run_dir)
        assert out["status"] == "FAILED"
        assert out["exit_code"] == 127
        log = (run_dir / "gate.log").read_text(encoding="utf-8")
        assert "missing script" in log
    finally:
        import os

        os.chdir(old_cwd)


def test_gate_adapter_runs_script_and_writes_gate_log(tmp_path: Path) -> None:
    scripts_dir = Path("scripts")
    tmp_scripts = tmp_path / "scripts"
    tmp_scripts.mkdir(parents=True, exist_ok=True)
    (tmp_scripts / "fast_check.ps1").write_text("Write-Host '[fast_check] ok'; exit 0\n", encoding="utf-8")

    # Execute from temporary repo root so adapter resolves scripts/fast_check.ps1 locally.
    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        adapter = PowerShellGateAdapter()
        run_dir = tmp_path / "runs" / "run-4"
        out = adapter.run(mode="fast", cwd=run_dir)
        assert out["status"] == "PASSED"
        assert out["exit_code"] == 0
        assert "status=PASSED" in (run_dir / "gate.log").read_text(encoding="utf-8")
    finally:
        import os

        os.chdir(old_cwd)
