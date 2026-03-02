---
id: INS-M4-01
related_rfc: RFC-M4-00
owner: xuxuyang
date: 2026-03-03
project: agent-workflow-kernel
risk: high
---

# INS-M4-01：state_store 镜像写入 state.v1（不切换真源）

> 全局规则（红线/门禁/并行/可替换性/可观测）遵循 docs/PLAYBOOK.md，此处不重复。

## 1. 本次目标（对齐 RFC 的验收）
- 目标：
  - 在不改变旧真源的前提下，将 state.v1 镜像写入 reports/runs/<run_id>/state.v1.json
  - 新增最小测试护栏，锁住必需字段与 stage 枚举合法性
- 对齐的验收条目：AC1（schema 被测试锁定）+ 镜像写入测试新增

## 2. 本次允许改动范围（必须明确）
**允许修改**
- core/state_v1.py
- core/state_store.py
- core/run_state.py（仅 save_state 内追加镜像写入调用）
- tests/test_state_store_mirror.py
- docs/ins/INS-M4-01-state-store-mirror.md

**禁止修改**
- 其他任何文件/目录
- docs/contracts/schemas/state.v1.schema.json（如需变更必须 stop-the-line 并走 ADR）

## 3. 本次契约/实现要点（用于并行不互卡）
- 输出路径固定：reports/runs/<run_id>/state.v1.json
- 原子写 JSON；镜像写入失败不阻断旧真源写入，但必须可观测
- stage 映射：无法判断时写 INIT（保持确定性）

## 4. 变更计划（先计划后实施）
请先输出：
- 文件清单（将修改哪些文件）
- 每个文件的改动要点
然后按计划实施；若发现与范围/Playbook 冲突，停止并说明替代方案。

## 5. 验证（写“本次额外项”，默认门禁不重复）
- 默认：按 Playbook 跑 PR 快速门禁（fmt/lint + test-fast）
- 本次额外验证：
  - python -m pytest -q tests/test_state_store_mirror.py
- 预期结果（2条以内）：
  - V1：pytest 全通过
  - V2：镜像写入测试通过
