# Context Pack

## Standards Pack (W2)
- Pack location: `standards/pack.yaml`
- Purpose: centralize change level policy, gate profiles, and output directory conventions.
- Engine entrypoints: `standards/engine.py`
  - `load_pack()`
  - `get_gates_for_change_level(change_level)`
  - `generate_codex_task_text(change_level=...)`
- Template location: `standards/templates/`
- Template renderer: Python `str.format` with missing-field friendly validation.
- Feature flag: `config.yaml` -> `enable_standards_engine: false` by default.

## Run -> Task -> Executor (W4)
- Serial scheduler entrypoint: `core/scheduler.py`
  - `validate_dag(deps_by_task)`
  - `next_runnable_task(task_states, deps_by_task)`
- Task workspace manager: `core/task_manager.py`
  - per-task layout: `<runs_root>/<run_id>/<task_id>/`
  - state file: `run_state.json`
  - event stream: `events.jsonl` (JSONL append-only)
  - artifacts dir: `artifacts/`
- Codex CLI executor: `core/codex_cli_executor.py`
  - `run_codex(task_dir, codex_task_path, ...)`
  - writes `artifacts/commands.log`, `artifacts/patch_summary.md`, `artifacts/codex_result.json`
- Flow orchestration: `flow/graph.py`
  - serial path: select task -> emit codex task -> wait for result -> ingest -> DONE/FAILED
  - uses `validate_codex_result(...)` for result contract checks.

## WebGPT HITL Bridge (W3)
- Bridge spec: `bridge/spec.md`
- Runtime module: `bridge/web_gpt_hitl.py`
- Feature flag: `config.yaml` -> `enable_web_gpt_hitl: false` by default.
- Artifact contract:
  - `reports/runs/<run_id>/tasks/<task_id>/artifacts/web_gpt_prompt.md`
  - `reports/runs/<run_id>/tasks/<task_id>/artifacts/web_gpt_response.md`
  - `reports/runs/<run_id>/tasks/<task_id>/artifacts/codex_task.md`
- Golden path:
  1) call `emit_prompt(run_id, task_id)`
  2) user manually copies prompt into WebGPT and pastes response back
  3) call `ingest_response(run_id, task_id, text)`
  4) archive response and generate placeholder `codex_task.md`
