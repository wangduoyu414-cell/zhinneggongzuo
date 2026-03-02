----
id: CTX
version: 1.0
owner: Team
---

# 团队上下文包（仓库版）

## 我们在做什么
- PHP 餐饮服务系统：前厅/后台/仓储/ERP + 硬件融合 + 数据采集分析
- Python 电脑配置清单生成：对话采集需求 + 价格更新 + 性能预估打分 + 渲染图
- Python 自动化流程工具：为以上两系统提效，已接近完成（用于生成/校验 RFC/INS/检查门禁）

## 我们的工程内核（REK）
- 产物驱动：PLAYBOOK / RFC / ADR / INS / DoR / DoD
- 边界优先：契约先行 + 模块独立
- 风险驱动质量：快速门禁 + 风险分级
- 可替换性：Port/Adapter/Contract Test
- 可观测：出问题能定位

## 默认约束（引用 Playbook）
全局红线、测试门禁、并行规则、可替换性要求，均以 `docs/PLAYBOOK.md` 为准。
