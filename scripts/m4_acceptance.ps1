param(
  [string]$RunId = "",
  [string]$RunsRoot = "reports/runs"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RunId)) {
  $RunId = "m4-ac3-" + (Get-Date -Format "yyyyMMdd-HHmmss")
}

$runDir = Join-Path $RunsRoot $RunId
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$gateLogPath = Join-Path $runDir "gate.log"
$repoSnapshotPath = Join-Path $runDir "repo_snapshot.txt"

function Write-Gate([string]$Line) {
  $Line | Tee-Object -FilePath $gateLogPath -Append | Out-Host
}

if (Test-Path $gateLogPath) {
  Remove-Item $gateLogPath -Force
}

Write-Gate ("[m4_acceptance] run_id={0}" -f $RunId)
Write-Gate ("[m4_acceptance] run_dir={0}" -f (Resolve-Path $runDir))
Write-Gate ("[m4_acceptance] start_utc={0}" -f ([DateTime]::UtcNow.ToString("o")))

Write-Gate "[m4_acceptance] fast_check"
& powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "fast_check.ps1") 2>&1 | Tee-Object -FilePath $gateLogPath -Append | Out-Host
$fastExit = $LASTEXITCODE
Write-Gate ("[m4_acceptance] fast_check_exit={0}" -f $fastExit)
if ($fastExit -ne 0) {
  Write-Gate "[m4_acceptance] status=FAILED"
  throw "fast_check failed with exit code $fastExit"
}

Write-Gate "[m4_acceptance] pytest"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$prevRepoRoot = $env:REPO_ROOT
$env:REPO_ROOT = $repoRoot
Write-Gate ("[m4_acceptance] REPO_ROOT={0}" -f $repoRoot)
python -m pytest -q 2>&1 | Tee-Object -FilePath $gateLogPath -Append | Out-Host
$env:REPO_ROOT = $prevRepoRoot
$pytestExit = $LASTEXITCODE
Write-Gate ("[m4_acceptance] pytest_exit={0}" -f $pytestExit)
if ($pytestExit -ne 0) {
  Write-Gate "[m4_acceptance] status=FAILED"
  throw "pytest failed with exit code $pytestExit"
}

$snapshotLines = @()
$snapshotLines += ("timestamp_utc={0}" -f ([DateTime]::UtcNow.ToString("o")))
$snapshotLines += ("run_id={0}" -f $RunId)
$snapshotLines += ("cwd={0}" -f (Get-Location))

$gitExists = Get-Command git -ErrorAction SilentlyContinue
if ($gitExists) {
  $head = (git rev-parse HEAD 2>$null)
  if ($LASTEXITCODE -eq 0) {
    $snapshotLines += ("git_head={0}" -f $head.Trim())
  } else {
    $snapshotLines += "git_head=<unavailable>"
  }
  $snapshotLines += "git_status_short_begin"
  $snapshotLines += (git status --short)
  $snapshotLines += "git_status_short_end"
} else {
  $snapshotLines += "git=<missing>"
}

$snapshotLines | Set-Content -Path $repoSnapshotPath -Encoding utf8

Write-Gate "[m4_acceptance] status=PASSED"
Write-Gate ("[m4_acceptance] gate_log={0}" -f (Resolve-Path $gateLogPath))
Write-Gate ("[m4_acceptance] repo_snapshot={0}" -f (Resolve-Path $repoSnapshotPath))

Write-Host ("M4 acceptance completed. run_id={0}" -f $RunId)
