param(
  [string]$PythonPath = 'python',
  [string]$Timestamp,
  [string]$OutputRoot
)

$ErrorActionPreference = 'Stop'

function Resolve-RepoRoot {
  param([string]$Path)
  Push-Location $Path
  try {
    $root = (& git rev-parse --show-toplevel 2>$null).Trim()
    if (-not $root) {
      throw "not a git worktree: $Path"
    }
    return (Resolve-Path $root).Path
  }
  finally {
    Pop-Location
  }
}

function Resolve-CollectDirs {
  param([string]$Raw)

  if ([string]::IsNullOrWhiteSpace($Raw)) {
    return @((Resolve-Path (Get-Location).Path).Path)
  }

  $result = @()
  $seen = @{}
  foreach ($part in ($Raw -split '[;,]')) {
    $dir = $part.Trim()
    if (-not $dir) { continue }

    if (-not (Test-Path $dir)) {
      throw "collect directory not found: $dir"
    }

    $resolved = (Resolve-Path $dir).Path
    if (-not $seen.ContainsKey($resolved)) {
      $seen[$resolved] = $true
      $result += $resolved
    }
  }

  if ($result.Count -eq 0) {
    throw 'COLLECT_DIRS provided but no valid directories parsed'
  }

  return $result
}

function Invoke-CollectOnly {
  param(
    [string]$Workdir,
    [string]$OutputFile
  )

  Push-Location $Workdir
  try {
    $lines = & $PythonPath -m pytest -q --collect-only 2>&1
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

function Parse-CollectedCount {
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

  throw 'unable to parse collected line from pytest output'
}

function Get-CollectedCount {
  param([string[]]$Lines)
  return (Parse-CollectedCount -Lines $Lines)
}

function Get-NodeIds {
  param([string[]]$Lines)

  # 兼容 Windows/Unix 路径与 pytest 输出格式
  $rx = '^(tests/|reports/|\.\/tests\/|\.\\tests\\|tests\\|reports\\).+::'
  return @($Lines | Where-Object { $_ -match $rx } | ForEach-Object { ([string]$_).Trim() })
}

# -------- Main --------

$repoRoot = Resolve-RepoRoot -Path (Get-Location).Path

if (-not $Timestamp) {
  $Timestamp = (Get-Date -Format 'yyyyMMdd_HHmmss') + '_' + (Get-Random -Minimum 1000 -Maximum 9999)
}

if (-not $OutputRoot) {
  $OutputRoot = Join-Path $repoRoot 'reports/preflight'
}

$reportDir = Join-Path $OutputRoot $Timestamp
New-Item -ItemType Directory -Path $reportDir -Force | Out-Null

# 记录 LATEST
$latestPath = Join-Path $OutputRoot 'LATEST.txt'
$Timestamp | Set-Content -Path $latestPath -Encoding utf8

$collectDirs = @(Resolve-CollectDirs -Raw $env:COLLECT_DIRS)
$isMulti = $collectDirs.Count -gt 1
$mode = if ($isMulti) { 'multi-dir' } else { 'single-dir' }

Write-Host "[collect_check] mode=$mode"
Write-Host "[collect_check] dirs=$($collectDirs -join ';')"
Write-Host "[collect_check] python=$PythonPath"
Write-Host "[collect_check] report=$reportDir"

$records = @()
for ($i = 0; $i -lt $collectDirs.Count; $i++) {
  $dir = $collectDirs[$i]
  $label = if ($i -eq 0) { 'main' } elseif ($i -eq 1) { 'w1' } else { "dir$($i + 1)" }

  $collectPath = Join-Path $reportDir ("{0}_collect.txt" -f $label)
  $lines = Invoke-CollectOnly -Workdir $dir -OutputFile $collectPath

  $records += [pscustomobject]@{
    Label       = $label
    Dir         = $dir
    CollectPath = $collectPath
    Count       = Get-CollectedCount -Lines $lines
    NodeIds     = Get-NodeIds -Lines $lines
  }
}

$diffPath = Join-Path $reportDir 'collected_diff.txt'
$summaryPath = Join-Path $reportDir 'summary.md'

# ---- single-dir ----
if (-not $isMulti) {
  $single = $records[0]

  @(
    'mode=single-dir'
    "dir=$($single.Dir)"
    "collect_path=$($single.CollectPath)"
    "collected=$($single.Count)"
    'status=PASS'
    'reason=single directory collect-only succeeded'
  ) | Set-Content -Path $diffPath -Encoding utf8

  @(
    '# Collect Consistency Summary'
    ''
    "- timestamp: $Timestamp"
    '- mode: single-dir'
    "- directory: $($single.Dir)"
    "- python: $PythonPath"
    "- collected: $($single.Count)"
    "- diff file: $diffPath"
  ) | Set-Content -Path $summaryPath -Encoding utf8

  Write-Host "[collect_check] PASS: single-dir collected=$($single.Count)"
  Write-Host "[collect_check] see $diffPath"
  exit 0
}

# ---- multi-dir ----
$baseline = $records[0]
$allMatch = $true

$diffLines = @(
  'mode=multi-dir'
  "baseline_label=$($baseline.Label)"
  "baseline_path=$($baseline.Dir)"
  "baseline_collected=$($baseline.Count)"
)

foreach ($record in $records) {
  $diffLines += "dir[$($record.Label)]=$($record.Dir)"
  $diffLines += "collected[$($record.Label)]=$($record.Count)"
}

foreach ($record in $records | Select-Object -Skip 1) {
  $onlyBase  = Compare-Object -ReferenceObject $baseline.NodeIds -DifferenceObject $record.NodeIds -PassThru |
               Where-Object { $_ -in $baseline.NodeIds }
  $onlyOther = Compare-Object -ReferenceObject $baseline.NodeIds -DifferenceObject $record.NodeIds -PassThru |
               Where-Object { $_ -in $record.NodeIds }

  if (($baseline.Count -ne $record.Count) -or $onlyBase.Count -gt 0 -or $onlyOther.Count -gt 0) {
    $allMatch = $false
    $diffLines += "mismatch_pair=$($baseline.Label),$($record.Label)"

    if ($baseline.Count -ne $record.Count) {
      $diffLines += "count_mismatch[$($record.Label)]=$($baseline.Count),$($record.Count)"
    }

    if ($onlyBase.Count -gt 0) {
      $diffLines += "only_in_$($baseline.Label)_vs_$($record.Label):"
      $diffLines += ($onlyBase | Select-Object -First 30)
    }
    if ($onlyOther.Count -gt 0) {
      $diffLines += "only_in_$($record.Label)_vs_$($baseline.Label):"
      $diffLines += ($onlyOther | Select-Object -First 30)
    }
  }
}

$diffLines += if ($allMatch) { 'status=PASS' } else { 'status=FAIL' }
$diffLines | Set-Content -Path $diffPath -Encoding utf8

$summary = @(
  '# Collect Consistency Summary'
  ''
  "- timestamp: $Timestamp"
  '- mode: multi-dir'
  "- python: $PythonPath"
  "- directories: $($collectDirs -join ';')"
  "- diff file: $diffPath"
)
$summary | Set-Content -Path $summaryPath -Encoding utf8

if (-not $allMatch) {
  if ($records.Count -ge 2) {
    Write-Host "[collect_check] FAIL: $($records[0].Label)=$($records[0].Count), $($records[1].Label)=$($records[1].Count)"
  }
  else {
    Write-Host '[collect_check] FAIL: collected mismatch'
  }
  Write-Host "[collect_check] see $diffPath"
  exit 1
}

if ($records.Count -ge 2) {
  Write-Host "[collect_check] PASS: $($records[0].Label)=$($records[0].Count), $($records[1].Label)=$($records[1].Count)"
}
else {
  Write-Host "[collect_check] PASS: collected=$($records[0].Count)"
}

Write-Host "[collect_check] see $diffPath"
exit 0