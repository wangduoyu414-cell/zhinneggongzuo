---
id: INS-M4-03b
related_rfc: RFC-M4-00
owner: xuxuyang
date: 2026-03-03
project: agent-workflow-kernel
risk: mid
---

# INS-M4-03b：adapters 最小集合（dry_run / manual_hitl / powershell_gate）

> 全局规则遵循 `docs/PLAYBOOK.md`，本次仅新增适配器实现与最小选择入口。

## 1. 本次目标
- 新增 `DryRunAdapter`：产出最小 `result.json`
- 新增 `ManualHitlAdapter`：生成/接收 `hitl_prompt.md`、`hitl_response.md`，并提供幂等 ingest
- 新增 `PowerShellGateAdapter`：执行 `scripts/fast_check.ps1|full_check.ps1` 并写 `gate.log`
- 默认行为不变，不替换现有主链路

## 2. 允许改动范围
**允许修改**
- adapters/__init__.py
- adapters/dry_run_adapter.py
- adapters/manual_hitl_adapter.py
- adapters/powershell_gate_adapter.py
- core/config.py
- tests/test_adapters_smoke.py
- docs/ins/INS-M4-03b-adapters.md

**禁止修改**
- 其他任何文件

## 3. adapter 选择入口
- `core/config.py` 中新增 `AdapterSelection`
- 通过环境变量显式选择：
  - `EXECUTOR_ADAPTER`
  - `HITL_ADAPTER`
  - `GATE_ADAPTER`
- 默认值均为 `legacy`，因此不改变既有行为

## 4. 验证
- `powershell -ExecutionPolicy Bypass -File scripts/fast_check.ps1`
- `python -m pytest -q`
- `python -m pytest -q tests/test_adapters_smoke.py`
