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

Write-Host "[fast_check] done"
exit 0
