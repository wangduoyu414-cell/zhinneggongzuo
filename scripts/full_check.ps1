$ErrorActionPreference = "Stop"

Write-Host "[full_check] Python version"
python --version
if ($LASTEXITCODE -ne 0) {
  Write-Host "[full_check] failed"
  exit $LASTEXITCODE
}

Write-Host "[full_check] pytest"
python -m pytest -q
if ($LASTEXITCODE -ne 0) {
  Write-Host "[full_check] failed"
  exit $LASTEXITCODE
}

Write-Host "[full_check] done"
exit 0
