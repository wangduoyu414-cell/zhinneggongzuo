# ADR 0004: Split Contracts for Result, Run State, and Events

## Status
Accepted

## Context
The workflow persists three different artifact types with different lifecycle and ownership:
- `codex_result.json`: executor result exchange
- `run_state.json`: mutable scheduler/runtime state
- `events.jsonl`: append-only event stream

A single mixed schema couples unrelated changes and increases regression risk.

## Decision
Use independent v0 contracts and validators:
- `codex_result.v0.schema.json` -> `validate_codex_result(...)`
- `run_state.v0.schema.json` -> `validate_run_state(...)`
- `event.v0.schema.json` + `events.v0.schema.json` -> event and jsonl-level validation

## Compatibility Window
- `contract_version` is optional in v0.
- If present, it must be `"0"`.
- Keep a union shape window for legacy fields to avoid immediate breakage.

## Consequences
- Clearer boundaries for IO contracts.
- Easier strict_check scope for contract-only regression.
- Slightly higher schema/test maintenance overhead.

## 并行影响评估/门禁（原文保留）
本次变更做 并行影响评估：是否触及热区（hotspot：冲突高发核心模块，如订单/支付/权限/结算/库存/状态机）？是否涉及迁移（migration：数据库变更）？是否涉及契约（contract：API/事件/DB 约定）破坏？
若触及热区：要求 PR 更小，指定 owner 审查（建议启用 CODEOWNERS：代码所有者规则）。
若涉及迁移：必须采用 expand/contract（扩展/收缩：先兼容再收敛）并给出回填（backfill：数据回填）与回滚策略。
若涉及契约破坏：必须给兼容窗口（compatibility window：新旧并行期）与弃用时间点（deprecation：弃用计划）。
明确门禁：fast_check 必过；里程碑/热区/迁移变更必须 full_check 必过；未完成功能必须 feature flag（功能开关：默认关闭）。
