from __future__ import annotations

from pathlib import Path

import pytest

from core.codex_result_validation import validate_codex_result


def _valid_payload() -> dict[str, object]:
    return {
        "contract_version": "0",
        "result": "ok",
        "artifacts": {
            "task": "reports/runs/run-1/codex_task.md",
            "result": "reports/runs/run-1/codex_result.json",
        },
    }


def test_validate_codex_result_passes_with_valid_payload() -> None:
    validate_codex_result(_valid_payload())


def test_validate_codex_result_missing_required_field() -> None:
    payload = _valid_payload()
    payload.pop("result")
    with pytest.raises(ValueError, match=r"payload\.result: missing required field"):
        validate_codex_result(payload)


def test_validate_codex_result_rejects_unknown_field() -> None:
    payload = _valid_payload()
    payload["unexpected"] = "x"
    with pytest.raises(ValueError, match=r"payload\.unexpected: unknown field"):
        validate_codex_result(payload)


def test_validate_codex_result_rejects_type_mismatch() -> None:
    payload = _valid_payload()
    payload["artifacts"] = "not-an-object"
    with pytest.raises(ValueError, match=r"payload\.artifacts: expected object"):
        validate_codex_result(payload)


def test_validate_codex_result_rejects_invalid_contract_version() -> None:
    payload = _valid_payload()
    payload["contract_version"] = "1"
    with pytest.raises(ValueError, match=r"payload\.contract_version: expected constant value '0'"):
        validate_codex_result(payload)


def test_validate_codex_result_allows_missing_contract_version() -> None:
    payload = _valid_payload()
    payload.pop("contract_version")
    validate_codex_result(payload)


def test_schema_loader_supports_utf8_sig(tmp_path: Path) -> None:
    schema_text = (
        '\ufeff{"type":"object","additionalProperties":false,'
        '"required":["result"],"properties":{"result":{"type":"string"}}}'
    )
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(schema_text, encoding="utf-8")

    validate_codex_result({"result": "ok"}, schema_path=schema_path)

