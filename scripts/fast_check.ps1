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

# collect-only 一致性预检：
# - 默认只检查当前目录，避免不同阶段工作树产生误报
# - 需要跨目录时通过 COLLECT_DIRS 显式指定（分号分隔）
if (Test-Path "$PSScriptRoot/check_collect_consistency.ps1") {
  $dirs = $env:COLLECT_DIRS
  $exclude = $env:COLLECT_EXCLUDE
  if ($dirs -and $dirs.Trim().Length -gt 0) {
    Write-Host "[fast_check] collect consistency (multi-dir) enabled via COLLECT_DIRS"
    & "$PSScriptRoot/check_collect_consistency.ps1" -Directories ($dirs -split ';') -Exclude ($exclude -split ';')
  } else {
    Write-Host "[fast_check] collect consistency (single-dir)"
    & "$PSScriptRoot/check_collect_consistency.ps1" -Directories @((Get-Location).Path)
  }
}
if ($LASTEXITCODE -ne 0) {
  Write-Host "[fast_check] failed"
  exit $LASTEXITCODE
}

Write-Host "[fast_check] done"
exit 0
