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

Write-Host "[fast_check] done"
exit 0

