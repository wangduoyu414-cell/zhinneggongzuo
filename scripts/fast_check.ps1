$ErrorActionPreference = "Stop"

Write-Host "[fast_check] Python version"
python --version
if ($LASTEXITCODE -ne 0) {
  Write-Host "[fast_check] failed"
  exit $LASTEXITCODE
}

Write-Host "[fast_check] compileall"
python -X utf8 -m compileall -q .
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

$repoRoot = (& git rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0 -or -not $repoRoot) {
  Write-Host "[fast_check] failed"
  exit 1
}
$collectDirs = @($repoRoot)
if ($env:COLLECT_DIRS) {
  $collectDirs = @($env:COLLECT_DIRS -split ';' | Where-Object { $_ -and $_.Trim().Length -gt 0 })
}
$collectExclude = @()
if ($env:COLLECT_EXCLUDE) {
  $collectExclude = @($env:COLLECT_EXCLUDE -split ';' | Where-Object { $_ -and $_.Trim().Length -gt 0 })
}
$pythonCmd = if ($env:PYTHON) { $env:PYTHON } else { "python" }
Write-Host "[fast_check] verify collected item consistency (default: current directory only)"
& "$PSScriptRoot/check_collect_consistency.ps1" -Directories $collectDirs -Exclude $collectExclude -PythonPath $pythonCmd
if ($LASTEXITCODE -ne 0) {
  Write-Host "[fast_check] failed"
  exit $LASTEXITCODE
}

Write-Host "[fast_check] done"
exit 0

