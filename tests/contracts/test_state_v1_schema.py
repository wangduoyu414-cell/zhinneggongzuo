import json
from pathlib import Path


def test_state_v1_schema_is_valid_json_and_has_stage_enum():
    schema_path = Path("docs/contracts/schemas/state.v1.schema.json")
    assert schema_path.exists(), f"missing schema file: {schema_path}"

    data = json.loads(schema_path.read_text(encoding="utf-8"))

    assert data.get("type") == "object"
    required = set(data.get("required", []))
    for k in ["schema_version", "run_id", "created_at", "updated_at", "stage"]:
        assert k in required, f"required field missing: {k}"

    stage = data.get("properties", {}).get("stage", {})
    enum = stage.get("enum", [])
    assert enum == ["INIT", "WAIT_INPUT", "EXECUTING", "GATING", "DONE", "FAILED"]
