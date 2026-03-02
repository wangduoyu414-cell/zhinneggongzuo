---
id: INS-M4-02b
related_rfc: RFC-M4-00
owner: xuxuyang
date: 2026-03-03
project: agent-workflow-kernel
risk: high
---

# INS-M4-02b：resume_run（WAIT_INPUT / EXECUTING / GATING）

> 全局规则遵循 `docs/PLAYBOOK.md`，本次仅新增恢复推进能力与测试护栏。

## 1. 本次目标
- 新增 `core/resume_run.py`，覆盖三段恢复：
  - `WAIT_INPUT`
  - `EXECUTING`
  - `GATING`
- 幂等规则：
  - `EXECUTING` 已有 result 证据则跳过执行
  - `GATING` 已有 `gate.log` 且 PASS 则跳过门禁
- 新增恢复矩阵测试 `tests/test_resume_matrix.py`

## 2. 允许改动范围
**允许修改**
- `core/resume_run.py`
- `flow/graph.py`
- `core/run_state.py`（可选，最小补充）
- `tests/test_resume_matrix.py`
- `docs/ins/INS-M4-02b-resume-run.md`

**禁止修改**
- 其他任何文件/目录
- `docs/contracts/schemas/state.v1.schema.json`
- `scripts/*.ps1`

## 3. 实现要点
- 锁：复用 `core/execution_lock.py`
- stage 归一：复用 `core/state_v1.map_stage`
- gate 证据：`runs_root/run_id/gate.log`
- result 读取优先：
  - `result.json`
  - `codex_result.json`
  - `artifacts/result.json`
  - `artifacts/codex_result.json`
  - `tasks/t1/artifacts/result.json`
  - `tasks/t1/artifacts/codex_result.json`

## 4. 验证
- `powershell -ExecutionPolicy Bypass -File scripts/fast_check.ps1`
- `python -m pytest -q`
- `python -m pytest -q tests/test_resume_matrix.py`
