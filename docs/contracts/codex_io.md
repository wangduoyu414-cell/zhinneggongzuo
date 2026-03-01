# Codex IO Contract

## Paths
- Run root: `<runs_root>/<run_id>/`
- Task root: `<runs_root>/<run_id>/<task_id>/`

Run-level files:
- `codex_task.md`
- `codex_result.json`
- `run_state.json`
- `events.jsonl`

Task-level files:
- `<task_id>/run_state.json`
- `<task_id>/events.jsonl`

## Result Contract
- Schema: `docs/contracts/schemas/codex_result.v0.schema.json`
- Validator: `core.codex_result_validation.validate_codex_result(...)`

## Run State Contract (v0)
- Schema: `docs/contracts/schemas/run_state.v0.schema.json`
- Validator: `core.run_state_event_validation.validate_run_state(...)`
- `contract_version` optional; if present must be `"0"`.
- `updated_at` is ISO8601 string.
- Strict mode: `additionalProperties=false`.
- Compatibility: union shape allows current and legacy run_state fields in v0.

## Event Contract (v0)
- Per-line schema: `docs/contracts/schemas/event.v0.schema.json`
- JSONL logical container schema: `docs/contracts/schemas/events.v0.schema.json`
- Validators:
  - `core.run_state_event_validation.validate_event(...)`
  - `core.run_state_event_validation.validate_events(...)`
  - `core.run_state_event_validation.validate_events_jsonl(path)`
- Storage format: `events.jsonl`, one JSON object per line.
- Compatibility: union shape allows current (`ts/type/payload`) and legacy (`timestamp/event_type/data`) event shape in v0.

## Error Reporting
- Validation returns path-style errors, for example:
  - `payload.status: missing required field`
  - `payload.events[2].type: unknown field`
