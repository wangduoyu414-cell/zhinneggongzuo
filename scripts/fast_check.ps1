$ErrorActionPreference = "Stop"

Write-Host "[fast_check] Python version"
python --version
if ($LASTEXITCODE -ne 0) {
  Write-Host "[fast_check] failed"
  exit $LASTEXITCODE
}

Write-Host "[fast_check] compileall"
python -m compileall -q .
if ($LASTEXITCODE -ne 0) {
  Write-Host "[fast_check] failed"
  exit $LASTEXITCODE
}

Write-Host "[fast_check] verify no untracked tests/test_*.py drift files"
$untrackedTests = git ls-files --others --exclude-standard tests/test_*.py
if ($LASTEXITCODE -ne 0) {
  Write-Host "[fast_check] failed"
  exit $LASTEXITCODE
}
if ($untrackedTests) {
  Write-Host "[fast_check] failed: untracked test files detected"
  $untrackedTests | ForEach-Object { Write-Host "  $_" }
  exit 1
}

 fix/collect-consistency-default-single
Write-Host "[fast_check] verify collected item count consistency"
& "$PSScriptRoot/check_collect_consistency.ps1"

$pythonCmd = if ($env:PYTHON) { $env:PYTHON } else { "python" }
# collect-only consistency preflight:
# - default checks current directory only
# - set COLLECT_DIRS to enable cross-worktree compare
if (Test-Path "$PSScriptRoot/check_collect_consistency.ps1") {
  $dirs = $env:COLLECT_DIRS
  $exclude = $env:COLLECT_EXCLUDE
  if ($dirs -and $dirs.Trim().Length -gt 0) {
    Write-Host "[fast_check] collect consistency (multi-dir) enabled via COLLECT_DIRS"
    & "$PSScriptRoot/check_collect_consistency.ps1" -Directories ($dirs -split ';') -Exclude ($exclude -split ';') -PythonPath $pythonCmd
  } else {
    Write-Host "[fast_check] collect consistency (single-dir)"
    & "$PSScriptRoot/check_collect_consistency.ps1" -Directories @((Get-Location).Path) -PythonPath $pythonCmd
  }
}
 main
if ($LASTEXITCODE -ne 0) {
  Write-Host "[fast_check] failed"
  exit $LASTEXITCODE
}

Write-Host "[fast_check] done"
exit 0
