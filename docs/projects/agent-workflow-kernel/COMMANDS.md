# Project Commands: agent-workflow-kernel

本文件仅记录项目常用命令，不替代全局规范。

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Local Validation
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\fast_check.ps1
python -m pytest -q
```

## Contract-focused Validation
```powershell
python -m pytest -q tests/contracts/test_state_v1_schema.py
```

## Notes
- 仅本地验证，不依赖远端 CI。
- 若 `pytest` 命令不可用，统一使用 `python -m pytest`。
