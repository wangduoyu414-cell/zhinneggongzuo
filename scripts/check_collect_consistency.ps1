param(
  [string]$MainPath,
  [string]$W1Path = 'D:/智能体工作流_w1_contract',
  [string]$Timestamp
)

$ErrorActionPreference = 'Stop'

function Get-RepoRoot {
  param([string]$Path)
  Push-Location $Path
  try {
    $root = (& git rev-parse --show-toplevel).Trim()
    if (-not $root) {
      throw 'unable to resolve git toplevel'
    }
    return $root
  }
  finally {
    Pop-Location
  }
}

function Invoke-CollectOnly {
  param(
    [string]$Workdir,
    [string]$OutputFile
  )

  Push-Location $Workdir
  try {
    $lines = & python -m pytest -q --collect-only 2>&1
    $exitCode = $LASTEXITCODE
    $lines | Set-Content -Path $OutputFile -Encoding utf8
    if ($exitCode -ne 0) {
      throw "pytest collect-only failed in $Workdir"
    }
    return $lines
  }
  finally {
    Pop-Location
  }
}

function Get-CollectedCount {
  param([string[]]$Lines)

  for ($i = $Lines.Count - 1; $i -ge 0; $i--) {
    $line = [string]$Lines[$i]
    if ($line -match '(?i)^(\d+)\s+tests?\s+collected') {
      return [int]$Matches[1]
    }
    if ($line -match '(?i)collected\s+(\d+)\s+items?') {
      return [int]$Matches[1]
    }
  }

  throw 'unable to parse collected item count from pytest output'
}

if (-not $MainPath) {
  $MainPath = (Get-RepoRoot -Path $PSScriptRoot)
}

$MainPath = (Resolve-Path $MainPath).Path
if (-not (Test-Path $W1Path)) {
  throw "w1 worktree path not found: $W1Path"
}
$W1Path = (Resolve-Path $W1Path).Path

if (-not $Timestamp) {
  $Timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
}

$reportDir = Join-Path $MainPath "reports/preflight/$Timestamp"
New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
$Timestamp | Set-Content -Path (Join-Path $MainPath 'reports/preflight/LATEST.txt') -Encoding utf8

$mainCollectPath = Join-Path $reportDir 'main_collect.txt'
$w1CollectPath = Join-Path $reportDir 'w1_collect.txt'
$diffPath = Join-Path $reportDir 'collected_diff.txt'
$summaryPath = Join-Path $reportDir 'summary.md'

$mainLines = Invoke-CollectOnly -Workdir $MainPath -OutputFile $mainCollectPath
$w1Lines = Invoke-CollectOnly -Workdir $W1Path -OutputFile $w1CollectPath

$mainCount = Get-CollectedCount -Lines $mainLines
$w1Count = Get-CollectedCount -Lines $w1Lines

$mainNodeIds = $mainLines | Where-Object { $_ -match '^(tests/|reports/).+::' }
$w1NodeIds = $w1Lines | Where-Object { $_ -match '^(tests/|reports/).+::' }
$onlyMain = Compare-Object -ReferenceObject $mainNodeIds -DifferenceObject $w1NodeIds -PassThru | Where-Object { $_ -in $mainNodeIds }
$onlyW1 = Compare-Object -ReferenceObject $mainNodeIds -DifferenceObject $w1NodeIds -PassThru | Where-Object { $_ -in $w1NodeIds }

$diffLines = @(
  "main_path=$MainPath"
  "w1_path=$W1Path"
  "main_collected=$mainCount"
  "w1_collected=$w1Count"
)

if ($mainCount -ne $w1Count) {
  $diffLines += "status=FAIL"
  $diffLines += "reason=collected item count mismatch"
}
else {
  $diffLines += "status=PASS"
  $diffLines += "reason=collected item count match"
}

if ($onlyMain.Count -gt 0) {
  $diffLines += 'only_in_main_nodeids:'
  $diffLines += ($onlyMain | Select-Object -First 30)
}
if ($onlyW1.Count -gt 0) {
  $diffLines += 'only_in_w1_nodeids:'
  $diffLines += ($onlyW1 | Select-Object -First 30)
}
$diffLines | Set-Content -Path $diffPath -Encoding utf8

$summary = @(
  '# Collect Consistency Summary'
  ''
  "- timestamp: $Timestamp"
  "- main path: $MainPath"
  "- w1 path: $W1Path"
  "- main collected: $mainCount"
  "- w1 collected: $w1Count"
  "- diff file: $diffPath"
)
$summary | Set-Content -Path $summaryPath -Encoding utf8

if ($mainCount -ne $w1Count) {
  Write-Host "[collect_check] FAIL: main=$mainCount, w1=$w1Count"
  Write-Host "[collect_check] see $diffPath"
  exit 1
}

Write-Host "[collect_check] PASS: main=$mainCount, w1=$w1Count"
exit 0
