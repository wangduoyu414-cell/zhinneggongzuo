from __future__ import annotations

import os
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
    (tmp_path / ".git").mkdir(parents=True, exist_ok=True)
    adapter = PowerShellGateAdapter(repo_root=tmp_path)
    run_dir = tmp_path / "runs" / "run-3"
    out = adapter.run(mode="fast", cwd=run_dir)
    assert out["status"] == "FAILED"
    assert out["exit_code"] == 127
    log = (run_dir / "gate.log").read_text(encoding="utf-8")
    assert "missing script" in log


def test_repo_snapshot_created(tmp_path: Path) -> None:
    tmp_scripts = tmp_path / "scripts"
    tmp_scripts.mkdir(parents=True, exist_ok=True)
    (tmp_path / ".git").mkdir(parents=True, exist_ok=True)
    (tmp_scripts / "fast_check.ps1").write_text("Write-Host '[fast_check] ok'; exit 0\n", encoding="utf-8")
    (tmp_scripts / "repo_snapshot.ps1").write_text(
        "param([string]$RepoRoot,[string]$OutputPath)\n"
        "Set-Content -LiteralPath $OutputPath -Encoding UTF8 -Value \"head_commit=fake`ngit_status=unavailable\"\n"
        "exit 0\n",
        encoding="utf-8",
    )

    adapter = PowerShellGateAdapter(repo_root=tmp_path)
    run_dir = tmp_path / "runs" / "run-4"
    out = adapter.run(mode="fast", cwd=run_dir)
    assert out["status"] == "PASSED"
    snapshot_text = (run_dir / "repo_snapshot.txt").read_text(encoding="utf-8")
    assert "head_commit=" in snapshot_text


def test_gate_path_independent_of_cwd(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    other_cwd = tmp_path / "outside"
    scripts_dir = repo_root / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    other_cwd.mkdir(parents=True, exist_ok=True)
    (repo_root / ".git").mkdir(parents=True, exist_ok=True)
    (scripts_dir / "fast_check.ps1").write_text("Write-Host '[fast_check] ok'; exit 0\n", encoding="utf-8")
    (scripts_dir / "repo_snapshot.ps1").write_text(
        "param([string]$RepoRoot,[string]$OutputPath)\n"
        "Set-Content -LiteralPath $OutputPath -Encoding UTF8 -Value \"head_commit=fake\"\n"
        "exit 0\n",
        encoding="utf-8",
    )

    old_cwd = Path.cwd()
    try:
        os.chdir(other_cwd)
        adapter = PowerShellGateAdapter(repo_root=repo_root)
        run_dir = tmp_path / "runs" / "run-5"
        out = adapter.run(mode="fast", cwd=run_dir)
        assert out["status"] == "PASSED"
        assert out["exit_code"] == 0
        assert "status=PASSED" in (run_dir / "gate.log").read_text(encoding="utf-8")
    finally:
        os.chdir(old_cwd)
