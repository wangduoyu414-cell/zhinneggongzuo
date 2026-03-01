$ErrorActionPreference = "Stop"

Write-Host "[fast_check] Python version"
python --version
if ($LASTEXITCODE -ne 0) {
  Write-Host "[fast_check] failed"
  exit $LASTEXITCODE
}

Write-Host "[fast_check] compileall"
python -m compileall .
if ($LASTEXITCODE -ne 0) {
  Write-Host "[fast_check] failed"
  exit $LASTEXITCODE
}

Write-Host "[fast_check] done"
exit 0
