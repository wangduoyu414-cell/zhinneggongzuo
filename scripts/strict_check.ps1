$ErrorActionPreference = "Stop"

Write-Host "[strict_check] Python version"
python --version
if ($LASTEXITCODE -ne 0) {
  Write-Host "[strict_check] failed"
  exit $LASTEXITCODE
}

Write-Host "[strict_check] pytest contract validation tests"
python -m pytest -q `
  tests/test_codex_result_validation.py `
  tests/test_codex_io.py `
  tests/test_run_state_event_validation.py
if ($LASTEXITCODE -ne 0) {
  Write-Host "[strict_check] failed"
  exit $LASTEXITCODE
}

Write-Host "[strict_check] done"
exit 0
