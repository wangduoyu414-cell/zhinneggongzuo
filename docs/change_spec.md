# Change Spec

## W1: WebGPT <-> Codex CLI Contracts + Strict Gate
- ChangeLevel: L2
- Stage: Contracts + Docs-only + Tests-only
- Scope:
  - Allowed: `standards/* docs/* tests/* scripts/* config.yaml README.md`
  - Forbidden: `.venv/ reports/ __pycache__/ .pytest_cache/`
- Gates: `fast_check` + `full_check` + `strict_check` + `python -m pytest -q`
- Deliverables:
  1) `docs/contracts/web_gpt_bridge.md`
  2) `docs/contracts/codex_cli_io.md`
  3) `standards/pack.yaml` stage and strict profile extension
  4) `scripts/strict_check.ps1` with exit-code pass-through
  5) tests for contract docs + strict gate configuration
- Contract policy:
  - version: `v0`
  - compatibility window: at least one milestone
  - strict mode rejects unknown fields

### 并行影响评估/门禁（原文保留）
本次变更做 并行影响评估：是否触及热区（hotspot：冲突高发核心模块，如订单/支付/权限/结算/库存/状态机）？是否涉及迁移（migration：数据库变更）？是否涉及契约（contract：API/事件/DB 约定）破坏？
若触及热区：要求 PR 更小，指定 owner 审查（建议启用 CODEOWNERS：代码所有者规则）。
若涉及迁移：必须采用 expand/contract（扩展/收缩：先兼容再收敛）并给出回填（backfill：数据回填）与回滚策略。
若涉及契约破坏：必须给兼容窗口（compatibility window：新旧并行期）与弃用时间点（deprecation：弃用计划）。
明确门禁：fast_check 必过；里程碑/热区/迁移变更必须 full_check 必过；未完成功能必须 feature flag（功能开关：默认关闭）。

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

## W3: Codex CLI Executor (bridge runtime)
- ChangeLevel: L2
- Scope:
  - Allowed: `bridge/* core/* docs/* tests/* config.yaml`
  - Forbidden: `.venv/ reports/ __pycache__/ .pytest_cache/`
- Gates: `fast_check` + `full_check` must pass
- Feature flags:
  - `enable_codex_cli` defaults to `false`
  - unresolved CLI failures should move flow to `WAIT_CODEX` handling
- Contract outputs:
  - `artifacts/commands.log`
  - `artifacts/codex_result.json`
  - `artifacts/patch_summary.md`
- Stub/Mock strategy:
  - dry-run must work without local codex CLI
  - run path testable with stub runner, no network dependency
- Golden Path:
  1) `dry_run` validates command/path contract
  2) `run` executes configured CLI command
  3) write minimum artifact contract
  4) ingest result and proceed or `WAIT_CODEX`

并行影响评估/门禁（必须原文保留）：
本次变更做 并行影响评估：是否触及热区（hotspot：冲突高发核心模块，如订单/支付/权限/结算/库存/状态机）？是否涉及迁移（migration：数据库变更）？是否涉及契约（contract：API/事件/DB 约定）破坏？
若触及热区：要求 PR 更小，指定 owner 审查（建议启用 CODEOWNERS：代码所有者规则）。
若涉及迁移：必须采用 expand/contract（扩展/收缩：先兼容再收敛）并给出回填（backfill：数据回填）与回滚策略。
若涉及契约破坏：必须给兼容窗口（compatibility window：新旧并行期）与弃用时间点（deprecation：弃用计划）。
明确门禁：fast_check 必过；里程碑/热区/迁移变更必须 full_check 必过；未完成功能必须 feature flag（功能开关：默认关闭）。

## W2: WebGPT HITL Bridge (Copy/Paste + File Sink)
- ChangeLevel: L2
- Scope:
  - Allowed: `bridge/* core/* docs/* tests/* config.yaml`
  - Forbidden: `.venv/ reports/ __pycache__/ .pytest_cache/`
- Gates:
  - `scripts/fast_check.ps1`
  - `scripts/full_check.ps1`
  - `python -m pytest -q`
- Contract:
  - `export_prompt(run_id, task_id, prompt_text)` writes `gpt_prompt.md` + `meta.json`
  - `ingest_response(run_id, task_id, response_text)` writes `gpt_response.md` and conditionally `codex_task.md`
  - events include `WAIT_GPT`, `PROMPT_EXPORTED`, `RESPONSE_INGESTED`, `PARSE_FAILED`
- Parse mode:
  - `strict`: requires `# Codex 指令书` section
  - `lenient`: uses full response as `codex_task.md`
- Feature flag:
  - `enable_web_gpt_hitl: false` (default off)

## W4-L3 Flow Upgrade
- Stage: CodexTask
- ChangeLevel: L3 (state-machine hotspot)
- Main path: WAIT_GPT -> WAIT_CODEX -> RUN_GATES -> DONE/FAILED
- Gates: fast_check, full_check, strict_check
- Flags default off: enable_web_gpt_hitl, enable_codex_cli, enable_parallel

??????/??(??????):
????? ??????:??????(hotspot:????????,???/??/??/??/??/???)???????(migration:?????)???????(contract:API/??/DB ??)???
?????:?? PR ??,?? owner ??(???? CODEOWNERS:???????)?
?????:???? expand/contract(??/??:??????)?????(backfill:????)??????
???????:???????(compatibility window:?????)??????(deprecation:????)?
????:fast_check ??;???/??/?????? full_check ??;??????? feature flag(????:????)?

## W2 (2026-03-01): Standards Engine Reinforcement
- ChangeLevel: L1
- Scope:
  - Allowed: `standards/**`, `docs/**`, `tests/test_standards_engine.py`, `config.yaml`
  - Forbidden: `core/**`, `flow/**`, `bridge/**`, `ui_app.py`
- Gate policy in `standards/pack.yaml`:
  - L0 = `fast_check`
  - L1 = `fast_check + full_check`
  - L2 = `fast_check + full_check + strict_check`
  - L3 = `fast_check + full_check + strict_check + stop_the_line` (placeholder)
- Feature flag:
  - `enable_standards_engine: false` (default off)
- Templates:
  - docs / impl / fix / release placeholders are available.

## W3: Codex CLI Executor + Evidence Artifacts + Idempotency
- Stage: CodexTask
- ChangeLevel: L2
- Scope:
  - Allowed: `core/codex_cli_executor.py`, `core/file_io.py` (helper only if needed), `tests/test_codex_cli_executor_dry_run.py`, `docs/**`
  - Forbidden: `flow/**`, `bridge/**`, `standards/**`, `ui_app.py`
- Gates:
  - `fast_check` + `full_check` must pass
- Runtime behavior:
  1) dry-run writes simulated `codex_result.json` without invoking external CLI
  2) real run executes local `codex` command and captures stdout/stderr
  3) evidence artifacts persisted: `commands.log`, `codex_result.json`, `patch_summary.md`
- Idempotency:
  - `.task.lock` blocks concurrent runs
  - existing valid `ok=true` result is reused by default unless `force=true`
- Contract:
  - output `codex_result.json` must pass W1 schema validator

## 并行影响评估/门禁（原文保留）
本次变更做 并行影响评估：是否触及热区（hotspot：冲突高发核心模块，如订单/支付/权限/结算/库存/状态机）？是否涉及迁移（migration：数据库变更）？是否涉及契约（contract：API/事件/DB 约定）破坏？
若触及热区：要求 PR 更小，指定 owner 审查（建议启用 CODEOWNERS：代码所有者规则）。
若涉及迁移：必须采用 expand/contract（扩展/收缩：先兼容再收敛）并给出回填（backfill：数据回填）与回滚策略。
若涉及契约破坏：必须给兼容窗口（compatibility window：新旧并行期）与弃用时间点（deprecation：弃用计划）。
明确门禁：fast_check 必过；里程碑/热区/迁移变更必须 full_check 必过；未完成功能必须 feature flag（功能开关：默认关闭）。

## W4 / Stage=CodexTask: HITL Flow Chain + Manual WebGPT Bridge
- ChangeLevel: L2 (flow orchestration hotspot)
- Scope:
  - Allowed: `flow/**`, `bridge/**`, `tests/test_hitl_flow.py`, `tests/test_web_gpt_hitl_roundtrip.py`, `docs/**`
  - Forbidden: `core/**` (reference existing APIs only), `standards/**`, `ui_app.py`
- Gates: `fast_check` + `full_check` must pass
- Feature flags: `enable_hitl=false` by default
- Golden path:
  1) `emit_codex_task` writes `codex_task.md` + `evidence_plan.md`
  2) `wait_hitl` blocks with `WAIT_HITL` until `artifacts/codex_result.json`
  3) `ingest_codex_result` validates schema and transitions `DONE` or `FAILED`

??????/??(????):
????? ??????:??????(hotspot:????????,???/??/??/??/??/???)???????(migration:?????)???????(contract:API/??/DB ??)???
?????:?? PR ??,?? owner ??(???? CODEOWNERS:???????)?
?????:???? expand/contract(??/??:??????)?????(backfill:????)??????
???????:???????(compatibility window:?????)??????(deprecation:????)?
????:fast_check ??;???/??/?????? full_check ??;??????? feature flag(????:????)?

## Test Suite Reconciliation (2026-03-01)
- Stage: CodexTask
- ChangeLevel: L1
- Decision: reconcile by removing local drift tests from main working tree (archived under reports), keep shared tracked suite as baseline.
- Verification:
  - main vs w1 `pytest --collect-only` test-file set is consistent.
  - `python -m pytest -q` passes on both main and w1.
- Evidence: `reports/preflight/<timestamp>/`.
