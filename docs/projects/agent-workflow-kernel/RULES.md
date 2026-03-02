# Project Rules Overlay: agent-workflow-kernel

本文件仅定义项目差异参数；全局规则以 `docs/PLAYBOOK.md` 为准。

## Scope
- 项目：`agent-workflow-kernel`
- 目标：离线优先、可恢复、证据可追溯

## Risk Policy (Project Override)
- `low`：文档与非核心脚本，要求最小本地门禁通过
- `mid`：契约或行为扩展，要求契约测试与回归验证
- `high`：状态机/恢复链路/证据链改动，要求恢复矩阵回归与回滚预案

## Guardrails
- 先锁契约再实现：`RFC -> ADR -> INS -> code`
- 默认禁止 run 内真并发
- 任何恢复逻辑必须记录 `stage` 与原因到证据链

## Local Gates
- 优先：`scripts/fast_check.ps1`
- 回归：`python -m pytest -q`
- 契约定点：按 INS 指定的最小集合执行
