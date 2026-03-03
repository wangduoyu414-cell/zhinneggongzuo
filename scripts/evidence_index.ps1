param(
  [string]$RunId = "",
  [string]$RunsRoot = "reports/runs"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $RunsRoot)) {
  throw "runs_root does not exist: $RunsRoot"
}

if ([string]::IsNullOrWhiteSpace($RunId)) {
  $latest = Get-ChildItem -Path $RunsRoot -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if (-not $latest) {
    throw "no run directories found under $RunsRoot"
  }
  $RunId = $latest.Name
}

$runDir = Join-Path $RunsRoot $RunId
if (-not (Test-Path $runDir)) {
  throw "run_dir does not exist: $runDir"
}

Write-Host ("run_id={0}" -f $RunId)
Write-Host ("run_dir={0}" -f (Resolve-Path $runDir))

$checks = @(
  @{ Name = "state.v1.json"; Path = Join-Path $runDir "state.v1.json" },
  @{ Name = "events.jsonl"; Path = Join-Path $runDir "events.jsonl" },
  @{ Name = "result.json"; Path = Join-Path $runDir "result.json" },
  @{ Name = "gate.log"; Path = Join-Path $runDir "gate.log" },
  @{ Name = "commands.log"; Path = Join-Path $runDir "commands.log" },
  @{ Name = "patch_summary.md"; Path = Join-Path $runDir "patch_summary.md" },
  @{ Name = "artifacts/commands.log"; Path = Join-Path $runDir "artifacts/commands.log" },
  @{ Name = "artifacts/patch_summary.md"; Path = Join-Path $runDir "artifacts/patch_summary.md" },
  @{ Name = "repo_snapshot.txt"; Path = Join-Path $runDir "repo_snapshot.txt" }
)

foreach ($item in $checks) {
  $exists = Test-Path $item.Path
  $tag = if ($exists) { "OK" } else { "MISSING" }
  Write-Host ("[{0}] {1} => {2}" -f $tag, $item.Name, $item.Path)
}
