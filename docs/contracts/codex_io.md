# Codex IO Contract (W4)

## Task Directory Layout

Each task uses a dedicated workspace:

`<runs_root>/<run_id>/<task_id>/`

Files:
- `run_state.json`: mutable task state (`PENDING/RUNNING/DONE/FAILED`, retries, stop-the-line).
- `events.jsonl`: append-only event stream, one JSON object per line.
- `codex_task.md`: task prompt emitted for the executor.
- `artifacts/commands.log`: command invocation and captured output.
- `artifacts/patch_summary.md`: summary extracted from executor output.
- `artifacts/codex_result.json`: result payload to ingest and validate.

## Result Validation

`artifacts/codex_result.json` must satisfy schema:
- `docs/contracts/schemas/codex_result.v0.schema.json`

Validation entrypoint:
- `core.codex_result_validation.validate_codex_result(...)`

Invalid results must transition task state to `FAILED`.
