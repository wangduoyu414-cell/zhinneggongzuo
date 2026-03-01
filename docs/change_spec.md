# Change Spec

## W2: Standards Engine
- ChangeLevel: L2
- Scope:
  - Allowed: `standards/* docs/* tests/* config.yaml`
  - Forbidden: `core/* flow/* ui_app.py`
- Gates: `fast_check` + `full_check` must pass
- Stub/Mock strategy:
  - `enable_standards_engine` defaults to `false`
  - no impact to existing flow by default
- Golden Path:
  1) call standards engine function directly
  2) output resolved gates list
  3) output generated codex task text
  4) tests pass

## W3: WebGPT HITL Bridge
- ChangeLevel: L2
- Scope:
  - Allowed: `bridge/* docs/* tests/* config.yaml`
  - Forbidden: browser automation click control; any anti-detection/risk-control bypass content
- Gates: `fast_check` + `full_check` must pass
- Stub/Mock strategy:
  - pure file roundtrip only (no network dependency)
  - `enable_web_gpt_hitl` defaults to `false`
- Golden Path:
  1) `emit_prompt(run_id, task_id)` creates `web_gpt_prompt.md`
  2) ingest simulated response text
  3) output `web_gpt_response.md` and placeholder `codex_task.md`
  4) tests pass

## W4: Codex CLI Executor + Task Scheduler
- ChangeLevel: L2
- Scope:
  - Allowed: `core/* flow/* tests/* config.yaml docs/*`
  - Forbidden: do not change `scripts/*` behavior (except exit-code fixes), do not touch `.venv/` and `reports/`
- Gates: `fast_check` + `full_check` must pass
- Feature flag:
  - `enable_true_concurrency` defaults to `false`
- Stub/Mock strategy:
  - codex CLI execution is testable via `runner` stub/mock
  - no hard dependency on local `codex` install for tests
- Golden Path:
  1) create run + task workspace
  2) emit `codex_task.md`
  3) produce a valid `artifacts/codex_result.json`
  4) ingest and validate result contract
  5) transition to `DONE`

## L1 (2026-03-01): Gate Usage Update for Clean Baseline
- Scope: `scripts/**`, `docs/**` only.
- This gate update is structural only and does not change runtime business logic.
- Why:
  - avoid false failures caused by dirty/polluted directories;
  - prefer clean `main_sync` worktree for acceptance.
- Usage:
  - default fast check compares collect results for current directory only;
  - use `COLLECT_DIRS` to expand cross-directory checks (semicolon-separated paths);
  - use `COLLECT_EXCLUDE` to skip selected paths/names.
- Example:
  - `$env:COLLECT_DIRS='D:/智能体工作流_main_sync;D:/智能体工作流_w1_contract;D:/智能体工作流_w2_bridge;D:/智能体工作流_w3_codexcli;D:/智能体工作流_w4_flow'`
  - `powershell -ExecutionPolicy Bypass -File .\scripts\fast_check.ps1`
- Evidence path: `reports/preflight/<yyyyMMdd_HHmmss_rand>/`.
