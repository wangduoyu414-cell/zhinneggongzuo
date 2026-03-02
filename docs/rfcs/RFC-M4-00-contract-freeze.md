---
id: RFC-M4-00
status: approved
owner: xuxuyang
date: 2026-03-03
project: agent-workflow-kernel
risk: mid
---

# RFC-M4-00：M4.0 契约冻结（state.v1 + Ports v0）

## 1. 一句话摘要
先冻结 state.v1（字段/枚举/错误语义）与 Ports v0（Executor/Hitl/Gate），并加最小契约测试，避免后续实现返工。

## 2. 背景与问题（3条以内）
- 现状：状态语义与执行器命名存在强绑定与双轨风险。
- 痛点：先实现再对齐会导致反复修改接口/状态字段。
- 为什么现在做：后续 state_store/resume/adapters 全部依赖该契约。

## 3. 目标 / 非目标（各最多3条）
**Goals**
- [ ] G1：冻结 state.v1 schema 与 stage 枚举
- [ ] G2：冻结 Ports v0 最小接口集合
- [ ] G3：新增最小契约测试防漂移

**Non-Goals**
- [ ] NG1：不实现 state.v1 写入切换（仅契约落盘）
- [ ] NG2：不做 run 内真并发
- [ ] NG3：不做无关重构/全局格式化

## 4. 关键口径与边界（返工高发区，必须写）
- 规则/口径：state.v1 为未来唯一真源；events 仅证据不为真源；stage 枚举冻结。
- 兼容性：本切片不改变现有运行链路与目录职责。
- Assumptions：
  - A1：允许新增 docs/contracts 与 tests/contracts
  - A2：pytest 可用（否则以文件落盘与 diff 审阅为准）

## 5. 契约变化（没有就写“无”）
- API/接口：新增 Ports v0 文档契约
- 数据结构/表/事件口径：新增 state.v1 schema
- 错误语义：冻结 last_error.retryable 语义（可自动重试与否）

## 6. 验收标准（可测试，最少2条）
- [ ] AC1：schema 为合法 JSON 且 stage 枚举被冻结（测试通过）
- [ ] AC2：Ports v0 文档落盘且可追溯（路径固定）

## 7. 任务拆分（可并行、可独立合并）
- T1（owner: xuxuyang）：落地 schema + ports + contract test
- T2（owner: xuxuyang）：落地 RFC/ADR/INS 文档实例
