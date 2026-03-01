param(
  [string[]]$Directories,
  [string[]]$Exclude = @(),
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

if (-not $Directories -or $Directories.Count -eq 0) {
  $cwd = (Get-Location).Path
  $Directories = @(
    $cwd,
    'D:/智能体工作流_w1_contract',
    'D:/智能体工作流_w2_bridge',
    'D:/智能体工作流_w3_codexcli',
    'D:/智能体工作流_w4_flow'
  )
}

$excludeResolved = @{}
foreach ($e in $Exclude) {
  if (-not $e) { continue }
  if (Test-Path $e) {
    $excludeResolved[(Resolve-Path $e).Path.ToLowerInvariant()] = $true
  }
  else {
    $excludeResolved[$e.ToLowerInvariant()] = $true
  }
}

$resolvedDirs = @()
foreach ($d in $Directories) {
  if (-not (Test-Path $d)) {
    throw "directory not found: $d"
  }
  $full = (Resolve-Path $d).Path
  if ($excludeResolved.ContainsKey($full.ToLowerInvariant())) {
    continue
  }
  if ($excludeResolved.ContainsKey((Split-Path $full -Leaf).ToLowerInvariant())) {
    continue
  }
  $resolvedDirs += $full
}

if ($resolvedDirs.Count -eq 0) {
  throw 'no directories left after applying exclude filter'
}

$root = Resolve-RepoRoot -Path $resolvedDirs[0]
if (-not $OutputRoot) {
  $OutputRoot = Join-Path $root 'reports/preflight'
}

if (-not $Timestamp) {
  $Timestamp = (Get-Date -Format 'yyyyMMdd_HHmmss') + '_' + (Get-Random -Minimum 1000 -Maximum 9999)
}

$reportDir = Join-Path $OutputRoot $Timestamp
New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
$Timestamp | Set-Content -Path (Join-Path $root 'reports/preflight/LATEST.txt') -Encoding utf8

$results = @()

foreach ($dir in $resolvedDirs) {
  $name = Split-Path $dir -Leaf
  $dirReport = Join-Path $reportDir $name
  New-Item -ItemType Directory -Path $dirReport -Force | Out-Null

  Push-Location $dir
  try {
    $head = (& git rev-parse --short HEAD 2>&1)
    if ($LASTEXITCODE -ne 0) {
      throw "failed to read HEAD in $dir"
    }
    $headText = ([string]$head[0]).Trim()
    $headText | Set-Content -Path (Join-Path $dirReport 'head.txt') -Encoding utf8

    $statusLines = @(& git status --porcelain 2>&1)
    $statusLines | Set-Content -Path (Join-Path $dirReport 'git_status.txt') -Encoding utf8
    $isDirty = ($statusLines | Where-Object { $_ -and $_.Trim().Length -gt 0 }).Count -gt 0
    $hasConflict = ($statusLines | Where-Object { $_ -match '^(UU|AA|DD|AU|UA|DU|UD)\s' }).Count -gt 0

    $collectLines = @(& $PythonPath -m pytest -q --collect-only 2>&1)
    $collectExit = $LASTEXITCODE
    $collectLines | Set-Content -Path (Join-Path $dirReport 'collect.txt') -Encoding utf8

    if ($collectExit -ne 0) {
      $hint = "pytest collect-only failed in $dir. Ensure dependencies are installed and use a valid interpreter, e.g. -PythonPath D:/智能体工作流/.venv/Scripts/python.exe"
      $hint | Set-Content -Path (Join-Path $dirReport 'error.txt') -Encoding utf8
      throw $hint
    }

    $collectCount = Parse-CollectedCount -Lines $collectLines
    $collectLine = ($collectLines | Where-Object { $_ -match '(?i)(tests? collected|collected\s+\d+\s+items?)' } | Select-Object -Last 1)
    if (-not $collectLine) {
      $collectLine = "collect_count=$collectCount"
    }

    "collect_line=$collectLine" | Set-Content -Path (Join-Path $dirReport 'collect_line.txt') -Encoding utf8
    "collect_count=$collectCount" | Set-Content -Path (Join-Path $dirReport 'collect_count.txt') -Encoding utf8

    $nodeIds = @($collectLines | Where-Object { $_ -match '::' -and $_ -match '^(tests/|reports/|\./tests/|\.\\tests\\)' } | ForEach-Object { ([string]$_).Trim() })
    $nodeIds | Set-Content -Path (Join-Path $dirReport 'collected_items.txt') -Encoding utf8

    $results += [pscustomobject]@{
      Name = $name
      Path = $dir
      Head = $headText
      IsDirty = $isDirty
      HasConflict = $hasConflict
      CollectCount = $collectCount
      CollectLine = [string]$collectLine
      Items = $nodeIds
    }
  }
  finally {
    Pop-Location
  }
}

$collectedDiffPath = Join-Path $reportDir 'collected_diff.txt'
$summaryPath = Join-Path $reportDir 'summary.md'

$counts = @($results | Select-Object -ExpandProperty CollectCount)
$uniqueCounts = @($counts | Sort-Object -Unique)
$countConsistent = ($uniqueCounts.Count -eq 1)
$dirtyDirs = @($results | Where-Object { $_.IsDirty } | Select-Object -ExpandProperty Name)
$conflictDirs = @($results | Where-Object { $_.HasConflict } | Select-Object -ExpandProperty Name)

$fileSetConsistent = $true
$fileSetNote = 'skipped'
if ($results.Count -gt 1) {
  $baseSet = @($results[0].Items | Sort-Object -Unique)
  $fileSetNote = 'compared'
  foreach ($r in $results | Select-Object -Skip 1) {
    $compare = Compare-Object -ReferenceObject $baseSet -DifferenceObject (@($r.Items | Sort-Object -Unique))
    if ($compare) {
      $fileSetConsistent = $false
      break
    }
  }
}

$diff = @()
$diff += "timestamp=$Timestamp"
$diff += "status_count_consistent=$countConsistent"
$diff += "status_fileset_consistent=$fileSetConsistent"
$diff += "status_dirty_dirs=$($dirtyDirs.Count)"
$diff += "status_conflict_dirs=$($conflictDirs.Count)"
$diff += "counts=$($uniqueCounts -join ',')"
foreach ($r in $results) {
  $diff += "--- $($r.Name)"
  $diff += "path=$($r.Path)"
  $diff += "head=$($r.Head)"
  $diff += "dirty=$($r.IsDirty)"
  $diff += "conflict=$($r.HasConflict)"
  $diff += "collect_count=$($r.CollectCount)"
  $diff += "collect_line=$($r.CollectLine)"
}
$diff | Set-Content -Path $collectedDiffPath -Encoding utf8

$summary = @(
  '# Collect Consistency Preflight',
  '',
  "- timestamp: $Timestamp",
  "- report_dir: $reportDir",
  "- python: $PythonPath",
  "- directories: $($resolvedDirs.Count)",
  "- collected counts: $($uniqueCounts -join ', ')",
  "- count consistent: $countConsistent",
  "- file set check: $fileSetNote / consistent=$fileSetConsistent",
  "- conflict directories: $($conflictDirs -join ', ')",
  "- dirty directories: $($dirtyDirs -join ', ')"
)
$summary | Set-Content -Path $summaryPath -Encoding utf8

if ($conflictDirs.Count -gt 0) {
  Write-Host "[collect_check] FAIL: conflicted worktree detected: $($conflictDirs -join ', ')"
  Write-Host "[collect_check] see $collectedDiffPath"
  exit 1
}
if ($resolvedDirs.Count -gt 1 -and $dirtyDirs.Count -gt 0) {
  Write-Host "[collect_check] FAIL: dirty worktree detected: $($dirtyDirs -join ', ')"
  Write-Host "[collect_check] see $collectedDiffPath"
  exit 1
}
if (-not $countConsistent) {
  Write-Host "[collect_check] FAIL: collected item count mismatch ($($uniqueCounts -join ', '))"
  Write-Host "[collect_check] see $collectedDiffPath"
  exit 1
}
if (-not $fileSetConsistent) {
  Write-Host "[collect_check] FAIL: collected item file set mismatch"
  Write-Host "[collect_check] see $collectedDiffPath"
  exit 1
}

Write-Host "[collect_check] PASS: collected count and file set are consistent"
Write-Host "[collect_check] report: $reportDir"
exit 0
