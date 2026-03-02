# Ports v0（最小接口契约）

> Port（端口接口）隔离内核与具体实现；Adapter（适配器实现）可替换且必须有契约测试兜底。

## 1) ExecutorPort（执行端口）
### 职责
- 执行任务动作（跑命令/应用 patch）
- 输出 result.json（机器可读结果）
- 输出证据：commands.log / patch_summary.md

### 最小输入
- task_dir（任务目录）
- task_md_path（任务说明 task.md）
- timeout_sec（超时秒数，可配置）
- env（环境变量，可选）

### 最小输出
- exit_code（退出码）
- result_json_path
- commands_log_path
- patch_summary_path

## 2) HitlPort（人工端口）
### 职责
- 生成 hitl_prompt.md
- 接收 hitl_response.md
- ingest 幂等：同一 prompt 指纹重复 ingest 不应破坏状态/证据

### 最小输入/输出
- 输入：hitl_prompt.md 路径
- 输出：hitl_response.md 路径 + 是否已收到

## 3) GatePort（门禁端口）
### 职责
- 运行本地门禁 fast/full
- 输出 gate.log
- 返回通过/失败与退出码

### 最小输入
- mode：fast | full
- cwd：仓库根目录
- env：环境变量（可选）

### 最小输出
- status：PASSED | FAILED
- exit_code
- gate_log_path
