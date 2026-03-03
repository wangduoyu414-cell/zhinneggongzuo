# M4 Acceptance (AC1~AC3)

This document fixes a reproducible acceptance flow for M4 in local offline mode.

## 1) Scope

- AC1: `resume_run` can continue from interrupted stage and end in `DONE` or `FAILED`.
- AC2: switching executor adapter selection does not break `result` contract validation.
- AC3: offline one-command gate can run `fast_check + pytest` and emit `gate.log + repo_snapshot`.

## 2) Run Identity And Evidence Root

- `runs_root` default: `reports/runs` (from `core/run_state.py: RUNS_ROOT = Path("reports") / "runs"`).
- `run_id` recommended format: `m4-<ac>-<yyyyMMdd-HHmmss>`.
- Example (PowerShell):

```powershell
$runId = "m4-ac1-" + (Get-Date -Format "yyyyMMdd-HHmmss")
$runsRoot = "reports/runs"
$runDir = Join-Path $runsRoot $runId
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
```

## 3) Evidence Path Contract

For each acceptance run, inspect `reports/runs/<run_id>/`:

- `state.v1.json`
- `events.jsonl`
- `result.json`
- `gate.log`
- optional: `commands.log`, `patch_summary.md`, HITL artifacts

## 4) AC1 Reproduction (`resume_run`)

### AC1-A: interrupted `EXECUTING -> GATING -> DONE`

```powershell
$runId = "m4-ac1-done-" + (Get-Date -Format "yyyyMMdd-HHmmss")
python -c "from core.run_state import save_state; save_state('$runId', {'stage':'EXECUTING','status':'RUNNING','task_id':'t1'})"
python -c "import json, pathlib; p=pathlib.Path('reports/runs/$runId/result.json'); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps({'result':'ok','artifacts':{}}), encoding='utf-8')"
Set-Content -Encoding utf8 "reports/runs/$runId/gate.log" "status=PASSED"
python -c "from core.resume_run import resume_run; print(resume_run('$runId')); print(resume_run('$runId'))"
python -c "from core.run_state import load_state; print(load_state('$runId')['stage'])"
```

Expected final stage: `DONE`.

### AC1-B: interrupted `GATING -> FAILED`

```powershell
$runId = "m4-ac1-failed-" + (Get-Date -Format "yyyyMMdd-HHmmss")
python -c "from core.run_state import save_state; save_state('$runId', {'stage':'GATING','status':'RUNNING'})"
Set-Content -Encoding utf8 "reports/runs/$runId/gate.log" "status=FAILED"
python -c "from core.resume_run import resume_run; print(resume_run('$runId'))"
python -c "from core.run_state import load_state; s=load_state('$runId'); print(s['stage']); print(bool(s.get('last_error')))"
```

Expected final stage: `FAILED`, and `last_error` is present.

## 5) AC2 Reproduction (adapter switch + result contract)

```powershell
$env:EXECUTOR_ADAPTER = "dry_run"
python -c "from core.config import load_adapter_selection_from_env; print(load_adapter_selection_from_env())"
python -m pytest -q tests/test_adapters_smoke.py tests/test_codex_result_validation.py
Remove-Item Env:EXECUTOR_ADAPTER
```

Expected:

- adapter selection prints `executor_adapter='dry_run'`
- tests pass, proving generated/validated result payload still satisfies contract checks

## 6) AC3 Reproduction (offline one-command gate)

Use one-command script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\m4_acceptance.ps1
```

Expected:

- command exits with code `0`
- script prints generated `run_id`
- `reports/runs/<run_id>/gate.log` exists
- `reports/runs/<run_id>/repo_snapshot.txt` exists

## 7) Baseline Gates (mandatory)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\fast_check.ps1
python -m pytest -q
```

## 8) Evidence Index Helper

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\evidence_index.ps1 -RunId <run_id>
```

The helper prints key file paths and existence status for quick audit.
