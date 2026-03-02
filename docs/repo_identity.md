# repo_identity（仓库身份证：说明这个仓库是什么、怎么跑、怎么回滚）

## 仓库信息
- 远端（remote：Git 远程地址配置）: wangduoyu414-cell/zhinneggongzuo
- 主干（main：默认集成基线）: 以 origin/main 为准
- 锚点（tag：标签，用于可回滚定位）: m3-gate-semantic-fixed-20260302

## 关键门禁（gate：合并前必须通过的检查）
- scripts/fast_check.ps1（快速门禁脚本：快检）
- scripts/full_check.ps1（全量门禁脚本：跑测试）
- pytest（测试框架：运行单元测试）基线: 29 passed（允许 1 warning，来自 Python 3.14 与 pydantic v1 兼容提示）

## 关键产物（artifact：运行输出文件）
- reports/**（证据目录：stdout/stderr/退出码/差异）
- codex_result.json（机器结果：可机读汇总；建议不提交入仓库）

## HITL（Human-in-the-loop：人工在环）最小流程
1) emit（生成）：生成 web_gpt_prompt.md
2) wait（等待）：手动网页端执行并复制回复
3) ingest（接收解析）：把回复粘贴到 web_gpt_response.md 后运行 ingest

## 回滚（rollback：回退到安全状态）
- 回滚某次提交（revert：反向提交）: git revert <sha>
- 回滚合并提交（merge commit：合并产生的提交）同样用 git revert <sha>
