from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.file_io import read_json, read_text

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "docs" / "contracts" / "schemas"
RUN_STATE_SCHEMA_PATH = SCHEMAS_DIR / "run_state.v0.schema.json"
EVENT_SCHEMA_PATH = SCHEMAS_DIR / "event.v0.schema.json"
EVENTS_SCHEMA_PATH = SCHEMAS_DIR / "events.v0.schema.json"

_ISO_8601_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")


def _matches_type(value: Any, expected: str | list[str]) -> bool:
    if isinstance(expected, list):
        return any(_matches_type(value, item) for item in expected)
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
    any_of = schema.get("anyOf")
    if isinstance(any_of, list):
        branch_messages: list[str] = []
        for idx, branch in enumerate(any_of):
            if not isinstance(branch, dict):
                continue
            branch_errors: list[str] = []
            _validate_node(branch, value, path, branch_errors)
            if not branch_errors:
                return
            branch_messages.append(f"anyOf[{idx}] -> " + "; ".join(branch_errors))
        errors.append(f"{path}: does not match anyOf branches")
        errors.extend(f"{path}: {msg}" for msg in branch_messages)
        return

    expected_type = schema.get("type")
    if isinstance(expected_type, (str, list)) and not _matches_type(value, expected_type):
        errors.append(f"{path}: expected {expected_type}, got {type(value).__name__}")
        return

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected constant value {schema['const']!r}")

    if isinstance(value, str) and schema.get("format") == "date-time":
        if _ISO_8601_RE.match(value) is None:
            errors.append(f"{path}: expected ISO8601 date-time string")

    if isinstance(value, dict):
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

    if isinstance(value, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate_node(item_schema, item, f"{path}[{index}]", errors)


def _load_schema(schema_path: Path) -> dict[str, Any]:
    data = read_json(schema_path, encoding="utf-8-sig")
    if not isinstance(data, dict):
        raise ValueError(f"schema must be a JSON object: {schema_path}")
    return data


def _validate_payload(payload: dict[str, Any], schema_path: Path, label: str) -> None:
    schema = _load_schema(schema_path)
    errors: list[str] = []
    _validate_node(schema, payload, "payload", errors)
    if errors:
        raise ValueError(f"{label} validation failed: " + "; ".join(errors))


def validate_run_state(payload: dict[str, Any], schema_path: Path = RUN_STATE_SCHEMA_PATH) -> None:
    _validate_payload(payload, schema_path, "run_state")


def validate_event(payload: dict[str, Any], schema_path: Path = EVENT_SCHEMA_PATH) -> None:
    _validate_payload(payload, schema_path, "event")


def load_events_descriptor(schema_path: Path = EVENTS_SCHEMA_PATH) -> dict[str, Any]:
    descriptor = _load_schema(schema_path)
    # compatibility: array logical view or descriptor object
    if descriptor.get("type") == "array":
        return descriptor
    line_schema_const = descriptor.get("properties", {}).get("line_schema", {}).get("const")
    if line_schema_const != "event.v0.schema.json":
        raise ValueError("events descriptor must point to event.v0.schema.json")
    return descriptor


def validate_events(payload: list[dict[str, Any]], schema_path: Path = EVENTS_SCHEMA_PATH) -> None:
    schema = load_events_descriptor(schema_path)
    if schema.get("type") == "array":
        errors: list[str] = []
        _validate_node(schema, payload, "payload", errors)
        if errors:
            raise ValueError("events validation failed: " + "; ".join(errors))
        return

    if not isinstance(payload, list):
        raise ValueError("events validation failed: payload must be an array")
    for idx, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"events validation failed: payload[{idx}] must be an object")
        try:
            validate_event(item)
        except ValueError as exc:
            raise ValueError(f"events validation failed: payload[{idx}] -> {exc}") from exc


def validate_events_jsonl(
    payload: str | Path,
    *,
    line_schema_path: Path = EVENT_SCHEMA_PATH,
    descriptor_path: Path = EVENTS_SCHEMA_PATH,
) -> None:
    load_events_descriptor(descriptor_path)
    text = read_text(payload, encoding="utf-8") if isinstance(payload, Path) else payload

    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"events line {line_no}: invalid json: {exc.msg}") from exc
        if not isinstance(parsed, dict):
            raise ValueError(f"events line {line_no}: expected object")
        try:
            validate_event(parsed, schema_path=line_schema_path)
        except ValueError as exc:
            raise ValueError(f"events line {line_no}: {exc}") from exc
