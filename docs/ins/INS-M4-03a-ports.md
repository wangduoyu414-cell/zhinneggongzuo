---
id: INS-M4-03a
related_rfc: RFC-M4-00
owner: xuxuyang
date: 2026-03-03
project: agent-workflow-kernel
risk: low
---

# INS-M4-03a：落地 Ports 目录与最小接口

> 全局规则（红线/门禁/并行/可替换性/可观测）遵循 `docs/PLAYBOOK.md`，此处不重复。

## 1. 本次目标
- 新增 `ports/` 目录与 3 个最小接口：`ExecutorPort` / `HitlPort` / `GatePort`
- 接口契约与 `docs/contracts/ports/ports.v0.md` 一致
- 与现有实现共存，不做实现替换

## 2. 本次允许改动范围
**允许修改**
- ports/__init__.py
- ports/executor_port.py
- ports/hitl_port.py
- ports/gate_port.py
- docs/ins/INS-M4-03a-ports.md

**禁止修改**
- 除上述文件外的任何路径

## 3. 实现要点
- 选型：`typing.Protocol`
- 原因：
  - 非侵入定义接口，不要求现有实现继承
  - 适合“先定义端口、后逐步接入 adapter”
  - 保持最小签名，避免框架化抽象

## 4. 验证
- `powershell -ExecutionPolicy Bypass -File scripts/fast_check.ps1`
- `python -m pytest -q`
- 预期：
  - fast_check 与 pytest 通过
  - 现有行为不变，仅新增协议定义
