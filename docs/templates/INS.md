---
id: INS-XXX
related_rfc: RFC-XXX
owner: <name>
date: YYYY-MM-DD
project: <project>
risk: low|mid|high
---

# INS-XXX：<标题>

> 全局规则（红线/门禁/并行/可替换性/可观测）遵循 `docs/PLAYBOOK.md`，此处不重复。

## 1. 本次目标（对齐 RFC 的验收）
- 目标：
- 对齐的验收条目：AC1 / AC2 / ...

## 2. 本次允许改动范围（必须明确）
**允许修改**
- <path1>
- <path2>

**禁止修改**
- <pathX>
- <pathY>

## 3. 本次契约/实现要点（用于并行不互卡）
- 接口/数据结构要点（如有）：
- 关键流程步骤（1-2-3）：
- Assumptions（如有）：

## 4. 变更计划（先计划后实施）
请先输出：
- 文件清单（将修改哪些文件）
- 每个文件的改动要点
然后按计划实施；若发现与范围/Playbook 冲突，停止并说明替代方案。

## 5. 验证（写“本次额外项”，默认门禁不重复）
- 默认：按 Playbook 跑 PR 快速门禁（fmt/lint + test-fast）
- 本次额外验证（仅当需要）：
  - <integration/e2e/联调命令或步骤>
- 预期结果（2条以内）：
  - V1
  - V2
