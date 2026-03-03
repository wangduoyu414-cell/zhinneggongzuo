from __future__ import annotations

import json
from pathlib import Path

import pytest

import core.resume_run as resume_mod
from core.execution_lock import acquire, release
from core.resume_run import resume_run
from core.run_state import load_state, save_state


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_wait_input_without_response_stays_wait_input(tmp_path: Path) -> None:
    runs_root = tmp_path / "reports" / "runs"
    run_id = "r1"
    save_state(run_id, {"stage": "WAIT_INPUT", "status": "PENDING"}, runs_root=runs_root)

    stage = resume_run(run_id, runs_root=runs_root)
    assert stage == "WAIT_INPUT"


def test_wait_input_with_response_moves_to_executing(tmp_path: Path) -> None:
    runs_root = tmp_path / "reports" / "runs"
    run_id = "r2"
    save_state(run_id, {"stage": "WAIT_INPUT", "status": "PENDING"}, runs_root=runs_root)
    run_dir = runs_root / run_id
    (run_dir / "hitl_response.md").write_text("ok", encoding="utf-8")

    stage = resume_run(run_id, runs_root=runs_root)
    assert stage == "EXECUTING"


def test_executing_with_existing_result_moves_to_gating(tmp_path: Path) -> None:
    runs_root = tmp_path / "reports" / "runs"
    run_id = "r3"
    save_state(run_id, {"stage": "EXECUTING", "status": "RUNNING", "task_id": "t1"}, runs_root=runs_root)
    _write_json(runs_root / run_id / "codex_result.json", {"result": "ok", "artifacts": {}})

    stage = resume_run(run_id, runs_root=runs_root)
    assert stage == "GATING"


def test_gating_with_pass_log_moves_to_done(tmp_path: Path) -> None:
    runs_root = tmp_path / "reports" / "runs"
    run_id = "r4"
    save_state(run_id, {"stage": "GATING", "status": "RUNNING"}, runs_root=runs_root)
    (runs_root / run_id / "gate.log").write_text("status=PASSED\n", encoding="utf-8")

    stage = resume_run(run_id, runs_root=runs_root)
    assert stage == "DONE"


def test_gating_with_fail_log_moves_to_failed_and_sets_last_error(tmp_path: Path) -> None:
    runs_root = tmp_path / "reports" / "runs"
    run_id = "r5"
    save_state(run_id, {"stage": "GATING", "status": "RUNNING"}, runs_root=runs_root)
    (runs_root / run_id / "gate.log").write_text("status=FAILED\n", encoding="utf-8")

    stage = resume_run(run_id, runs_root=runs_root)
    assert stage == "FAILED"
    state = load_state(run_id, runs_root=runs_root)
    assert state is not None
    assert isinstance(state.get("last_error"), dict)
    assert state["last_error"]["retryable"] is True


def test_lock_not_expired_blocks_progress(tmp_path: Path) -> None:
    runs_root = tmp_path / "reports" / "runs"
    run_id = "r6"
    run_dir = runs_root / run_id
    save_state(run_id, {"stage": "WAIT_INPUT", "status": "PENDING"}, runs_root=runs_root)
    ok, _ = acquire(run_dir, owner="other-owner", ttl_sec=300)
    assert ok is True
    try:
        stage = resume_run(run_id, runs_root=runs_root)
        assert stage == "WAIT_INPUT"
    finally:
        release(run_dir, owner="other-owner")


def test_regression_chain_executing_to_gating_to_done(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runs_root = tmp_path / "reports" / "runs"
    run_id = "r7"
    run_dir = runs_root / run_id
    save_state(run_id, {"stage": "EXECUTING", "status": "RUNNING", "task_id": "t1"}, runs_root=runs_root)
    _write_json(run_dir / "codex_result.json", {"result": "ok", "artifacts": {}})

    stage1 = resume_run(run_id, runs_root=runs_root)
    assert stage1 == "GATING"

    def fake_run_gate(run_dir: Path, mode: str) -> tuple[bool, Path, str]:
        log_path = run_dir / "gate.log"
        log_path.write_text("status=PASSED\n", encoding="utf-8")
        return True, log_path, "PASSED"

    monkeypatch.setattr("core.resume_run._run_gate", fake_run_gate)
    stage2 = resume_run(run_id, runs_root=runs_root)
    assert stage2 == "DONE"


def test_run_gate_path_independent_of_cwd_and_snapshot_created(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_root = tmp_path / "repo"
    scripts_dir = repo_root / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (repo_root / ".git").mkdir(parents=True, exist_ok=True)
    (scripts_dir / "fast_check.ps1").write_text("Write-Host ok; exit 0\n", encoding="utf-8")
    (scripts_dir / "repo_snapshot.ps1").write_text("Write-Host snapshot; exit 0\n", encoding="utf-8")

    run_dir = tmp_path / "reports" / "runs" / "r8"
    run_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = run_dir / "repo_snapshot.txt"
    called_files: list[str] = []

    class _Proc:
        def __init__(self, returncode: int = 0) -> None:
            self.returncode = returncode
            self.stdout = "ok"
            self.stderr = ""

    def fake_subprocess_run(args, capture_output, text, check):  # type: ignore[no-untyped-def]
        called_files.append(str(args[4]))
        if str(args[4]).endswith("repo_snapshot.ps1"):
            out_idx = args.index("-OutputPath")
            Path(args[out_idx + 1]).write_text("head_commit=fake\n", encoding="utf-8")
        return _Proc(0)

    monkeypatch.setenv("REPO_ROOT", str(repo_root))
    monkeypatch.setattr(resume_mod.subprocess, "run", fake_subprocess_run)
    ok, _, status = resume_mod._run_gate(run_dir, "fast")
    assert ok is True
    assert status == "PASSED"
    assert snapshot_path.exists()
    assert any(Path(p).name == "fast_check.ps1" for p in called_files)
