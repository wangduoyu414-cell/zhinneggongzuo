---
id: INS-M4-00
related_rfc: RFC-M4-00
owner: xuxuyang
date: 2026-03-03
project: agent-workflow-kernel
risk: mid
---

# INS-M4-00：M4.0 契约冻结（state.v1 + Ports v0）

> 全局规则（红线/门禁/并行/可替换性/可观测）遵循 docs/PLAYBOOK.md，此处不重复。

## 1. 本次目标（对齐 RFC 的验收）
- 目标：
  - 冻结 state.v1 schema 与 stage 枚举
  - 冻结 Ports v0 文档契约
  - 新增最小契约测试护栏
- 对齐的验收条目：AC1 / AC2

## 2. 本次允许改动范围（必须明确）
**允许修改**
- docs/rfcs/
- docs/adrs/
- docs/ins/
- docs/contracts/
- tests/contracts/

**禁止修改**
- docs/PLAYBOOK.md
- docs/templates/
- docs/projects/
- core/
- bridge/
- flow/
- standards/
- scripts/
- tests/（除 tests/contracts/ 外）

## 3. 本次契约/实现要点（用于并行不互卡）
- state.v1：必需字段与 stage 枚举冻结；last_error.retryable 语义冻结
- Ports：只定义最小接口与证据输出约定，不做框架化抽象
- Assumptions：pytest 可用；不可用则以文件落盘与 diff 审阅作为最小验证

## 4. 变更计划（先计划后实施）
请先输出：
- 文件清单（将修改哪些文件）
- 每个文件的改动要点
然后按计划实施；若发现与范围/Playbook 冲突，停止并说明替代方案。

## 5. 验证（写“本次额外项”，默认门禁不重复）
- 默认：按 Playbook 跑 PR 快速门禁（fmt/lint + test-fast）
- 本次额外验证：
  - pytest -q tests/contracts/test_state_v1_schema.py
- 预期结果（2条以内）：
  - V1：测试通过
  - V2：契约文件落盘可追溯
