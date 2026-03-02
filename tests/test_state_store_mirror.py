from __future__ import annotations

from pathlib import Path

from core.file_io import read_json
from core.run_state import save_state


def test_save_state_mirrors_to_state_v1_with_required_fields(tmp_path: Path) -> None:
    run_id = "mirror-run-1"
    runs_root = tmp_path / "reports" / "runs"

    save_state(
        run_id,
        {
            "task_id": "t1",
            "status": "RUNNING",
            "last_error": "temporary issue",
        },
        runs_root=runs_root,
    )

    state_v1_path = runs_root / run_id / "state.v1.json"
    assert state_v1_path.exists(), f"missing mirror file: {state_v1_path}"

    data = read_json(state_v1_path, encoding="utf-8")
    required = {"schema_version", "run_id", "created_at", "updated_at", "stage"}
    assert required.issubset(data.keys())
    assert data["schema_version"] == "state.v1"
    assert data["run_id"] == run_id
    assert data["stage"] in {"INIT", "WAIT_INPUT", "EXECUTING", "GATING", "DONE", "FAILED"}
