---
id: INS-M4-02a
related_rfc: RFC-M4-00
owner: xuxuyang
date: 2026-03-03
project: agent-workflow-kernel
risk: high
---

# INS-M4-02a：execution lock + transitions（最小落地）

> 全局规则遵循 `docs/PLAYBOOK.md`，本次仅新增锁与迁移矩阵护栏。

## 1. 本次目标
- 新增 `core/execution_lock.py`：
  - `acquire(run_dir, owner, ttl_sec)`
  - `release(run_dir, owner)`
- 新增 `core/transitions.py`：
  - 固定允许迁移集合
  - `validate_transition(from_stage, to_stage)`
- 在 `flow/graph.py::run_serial_flow` 做最小插入：
  - 入口 `acquire`
  - 退出 `release`
  - 推进路径上做最小 transition 校验

## 2. 允许改动范围
**允许修改**
- `core/execution_lock.py`
- `core/transitions.py`
- `flow/graph.py`
- `tests/test_execution_lock.py`
- `tests/test_transitions.py`
- `docs/ins/INS-M4-02a-exec-lock-transitions.md`

**禁止修改**
- 其他任何文件/目录

## 3. 验证
- `powershell -ExecutionPolicy Bypass -File scripts/fast_check.ps1`
- `python -m pytest -q`
- `python -m pytest -q tests/test_execution_lock.py tests/test_transitions.py`
