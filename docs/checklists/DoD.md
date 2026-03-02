# DoD（Definition of Done）—— 合并前必须满足

- [ ] 代码实现完成，且变更范围符合 INS
- [ ] 通过 PR 快速门禁：fmt/lint + test-fast
- [ ] risk=mid：至少新增/更新 unit 或 contract
- [ ] risk=high：unit + contract + 至少1条集成回归；包含回滚/降级说明
- [ ] 关键链路日志/错误处理满足 Playbook 的最低可观测要求
- [ ] RFC/ADR/INS 已更新到可追溯状态（draft→approved/done 等）
