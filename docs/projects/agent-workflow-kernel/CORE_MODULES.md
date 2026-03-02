# Core Modules: agent-workflow-kernel

本文件定义项目核心模块边界，避免并行改动互相干扰。

## Core (High Review Bar)
- `core/run_state.py`：运行状态读写与阶段推进锚点
- `core/task_manager.py`：任务级状态、重试与事件记录
- `flow/graph.py`：串行编排主入口
- `core/codex_result_validation.py`：结果契约校验

## Integration/Bridge
- `bridge/web_gpt_hitl.py`：HITL emit/ingest/resume
- `core/codex_io.py`：工件命名兼容（读旧写新）

## Change Policy
- 触及 Core 模块默认按 `high` 风险处理
- 变更前必须有 RFC/INS，必要时补 ADR
- 合并前需提供可复现回归步骤
