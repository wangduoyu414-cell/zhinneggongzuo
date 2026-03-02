---
id: ADR-M4-00
status: accepted
date: 2026-03-03
owner: xuxuyang
related_rfc: RFC-M4-00
---

# ADR-M4-00：先冻结 state.v1 与 Ports v0（再进入实现切片）

## 背景（<=3条）
- M4 的 state_store/resume/adapters 依赖统一字段与阶段枚举。
- 并行开发需要先确定接口/数据结构/错误语义。
- 先落地护栏测试，比口头约束更可靠。

## 决策（1句话）
先落地 state.v1 schema 与 Ports v0 文档，并用最小契约测试锁住关键枚举与必需字段。

## 原因（<=3条）
- 契约先行减少返工与漂移。
- 状态/端口漂移会直接破坏恢复与证据一致性。
- 最小测试护栏成本低但收益高。

## 影响/代价（<=3条）
- 增加 docs/contracts 与 tests/contracts，但不改变运行行为。
- 若契约需调整，必须更新 RFC/ADR 并同步更新契约测试。
