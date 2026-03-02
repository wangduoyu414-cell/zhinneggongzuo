# Contracts Overlay: agent-workflow-kernel

本文件仅列本项目关键契约与变更约束；契约正文以各文件真源为准。

## Primary Contracts
- State schema:
  - `docs/contracts/schemas/state.v1.schema.json`
- Ports contract:
  - `docs/contracts/ports/ports.v0.md`
- Result schema:
  - `docs/contracts/schemas/codex_result.v0.schema.json`

## Contract Change Rules
- 先文档后实现：先更新 RFC/ADR/INS，再改代码
- 契约变更必须同步最小契约测试
- 不允许无测试地修改 stage 枚举与必需字段

## Required Minimum Tests
- `tests/contracts/test_state_v1_schema.py`
- 与变更契约对应的新增/更新测试
