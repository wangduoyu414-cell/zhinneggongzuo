---
id: INS-M4-04
related_rfc: RFC-M4-00
owner: xuxuyang
date: 2026-03-03
project: agent-workflow-kernel
risk: mid
---

# INS-M4-04：工件命名兼容（读新优先，写新）

> 全局规则遵循 `docs/PLAYBOOK.md`，本次仅在 IO 层做命名兼容。

## 1. 本次目标
- 写入统一新名：
  - `task.md`
  - `result.json`
  - `hitl_prompt.md`
  - `hitl_response.md`
- 读取兼容旧名：
  - `codex_task.md`
  - `codex_result.json`
  - `web_gpt_prompt.md`
  - `web_gpt_response.md`
- 策略：新优先读取；读不到回退旧；写始终写新。

## 2. 允许改动范围
**允许修改**
- `core/codex_io.py`
- `tests/test_artifact_name_compat.py`
- `docs/ins/INS-M4-04-artifacts-compat.md`

**禁止修改**
- 其余所有路径

## 3. 路径优先级（result 示例）
1. `result.json`
2. `codex_result.json`
3. `artifacts/result.json`
4. `artifacts/codex_result.json`
5. `tasks/*/artifacts/result.json`
6. `tasks/*/artifacts/codex_result.json`

## 4. 验证
- `powershell -ExecutionPolicy Bypass -File scripts/fast_check.ps1`
- `python -m pytest -q`
- `python -m pytest -q tests/test_artifact_name_compat.py`
