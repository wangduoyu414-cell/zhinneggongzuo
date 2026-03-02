# release_runbook（发布回滚手册：可执行发布/回滚步骤）

## 发布前检查
1) 工作区干净：git status -sb（除 reports/** 与 codex_result.json 外无改动）
2) 门禁全绿：
   - powershell -ExecutionPolicy Bypass -File .\scripts\fast_check.ps1
   - powershell -ExecutionPolicy Bypass -File .\scripts\full_check.ps1

## 发布步骤（最小）
1) 确认 main == origin/main
2) 打 tag（标签锚点：用于回滚定位）
   - git tag -a <tag_name> -m "<message>"
   - git push origin <tag_name>

## 回滚步骤
1) 回滚合并/提交：
   - git revert <sha>
2) 重新跑门禁确认恢复：
   - fast_check / full_check

## 常见故障
- 443 网络失败：先本地提交（commit：提交记录变更），网络恢复后再 push（推送：上传到远端）
- Python 3.14 warning：允许 1 warning（兼容提示），不视为失败
