from __future__ import annotations

from pathlib import Path

from core.codex_cli_executor import run_codex
from core.file_io import read_json, read_text


class _StubResult:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_codex_cli_executor_dry_run_writes_artifacts(tmp_path: Path) -> None:
    task_dir = tmp_path / "run-1" / "task-1"
    task_dir.mkdir(parents=True, exist_ok=True)
    codex_task_path = task_dir / "codex_task.md"
    codex_task_path.write_text("# task", encoding="utf-8")

    output = run_codex(task_dir, codex_task_path, dry_run=True)

    assert output["return_code"] == 0
    assert output["commands_log_path"].exists()
    assert output["patch_summary_path"].exists()
    assert output["codex_result_path"].exists()

    payload = read_json(output["codex_result_path"], encoding="utf-8")
    assert payload["result"] == "pending"
    assert payload["meta"]["dry_run"] is True


def test_codex_cli_executor_uses_stub_runner(tmp_path: Path) -> None:
    task_dir = tmp_path / "run-1" / "task-2"
    task_dir.mkdir(parents=True, exist_ok=True)
    codex_task_path = task_dir / "codex_task.md"
    codex_task_path.write_text("# task", encoding="utf-8")

    def runner(cmd: list[str], cwd: Path) -> _StubResult:
        assert cmd[0] == "codex"
        assert cwd == task_dir
        return _StubResult(returncode=0, stdout="patched file A", stderr="")

    output = run_codex(task_dir, codex_task_path, runner=runner)
    log_text = read_text(output["commands_log_path"], encoding="utf-8")
    assert "patched file A" in log_text
