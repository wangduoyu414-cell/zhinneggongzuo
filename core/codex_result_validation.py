from __future__ import annotations

from pathlib import Path
from typing import Any

from core.file_io import read_json

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "docs" / "contracts" / "schemas" / "codex_result.v0.schema.json"


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, float)
    if expected == "null":
        return value is None
    return True


def _validate_node(schema: dict[str, Any], value: Any, path: str, errors: list[str]) -> None:
    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not _matches_type(value, expected_type):
        errors.append(f"{path}: expected {expected_type}, got {type(value).__name__}")
        return

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected constant value {schema['const']!r}")

    if expected_type == "object" and isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}.{key}: missing required field")

        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if key in properties:
                prop_schema = properties[key]
                if isinstance(prop_schema, dict):
                    _validate_node(prop_schema, item, child_path, errors)
                continue

            if additional is False:
                errors.append(f"{child_path}: unknown field")
            elif isinstance(additional, dict):
                _validate_node(additional, item, child_path, errors)

    if expected_type == "array" and isinstance(value, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate_node(item_schema, item, f"{path}[{index}]", errors)


def load_codex_result_schema(schema_path: Path = SCHEMA_PATH) -> dict[str, Any]:
    data = read_json(schema_path, encoding="utf-8-sig")
    if not isinstance(data, dict):
        raise ValueError("codex_result schema must be a JSON object")
    return data


def validate_codex_result(payload: dict[str, Any], schema_path: Path = SCHEMA_PATH) -> None:
    schema = load_codex_result_schema(schema_path)
    errors: list[str] = []
    _validate_node(schema, payload, "payload", errors)
    if errors:
        raise ValueError("codex_result validation failed: " + "; ".join(errors))

