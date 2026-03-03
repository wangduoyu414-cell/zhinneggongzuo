param(
  [Parameter(Mandatory = $true)]
  [string]$RepoRoot,
  [Parameter(Mandatory = $true)]
  [string]$OutputPath
)

$ErrorActionPreference = "Stop"

function Write-Snapshot([string]$Content) {
  $parent = Split-Path -Parent $OutputPath
  if ($parent -and -not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
  }
  Set-Content -LiteralPath $OutputPath -Value $Content -Encoding UTF8
}

$timestamp = (Get-Date).ToUniversalTime().ToString("o")
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("timestamp=$timestamp")
$lines.Add("repo_root=$RepoRoot")

try {
  $null = Get-Command git -ErrorAction Stop
} catch {
  $lines.Add("git_status=unavailable")
  $lines.Add("reason=git unavailable")
  Write-Snapshot ($lines -join "`n")
  exit 0
}

try {
  $head = git -C $RepoRoot rev-parse HEAD 2>$null
  if ([string]::IsNullOrWhiteSpace($head)) {
    $head = "unknown"
  }
  $lines.Add("head_commit=$head")
} catch {
  $lines.Add("head_commit=unknown")
  $lines.Add("reason=git rev-parse failed: $($_.Exception.Message)")
}

try {
  $status = git -C $RepoRoot status --porcelain --branch 2>$null
  if ([string]::IsNullOrWhiteSpace($status)) {
    $lines.Add("working_tree=clean")
    $lines.Add("git_status_summary=(empty)")
  } else {
    $lines.Add("working_tree=dirty")
    $lines.Add("git_status_summary<<EOF")
    $lines.Add($status)
    $lines.Add("EOF")
  }
} catch {
  $lines.Add("working_tree=unknown")
  $lines.Add("reason=git status failed: $($_.Exception.Message)")
}

try {
  $diffStat = git -C $RepoRoot diff --stat 2>$null
  if ([string]::IsNullOrWhiteSpace($diffStat)) {
    $lines.Add("git_diff_stat=(empty)")
  } else {
    $lines.Add("git_diff_stat<<EOF")
    $lines.Add($diffStat)
    $lines.Add("EOF")
  }
} catch {
  $lines.Add("git_diff_stat=(error)")
  $lines.Add("reason=git diff --stat failed: $($_.Exception.Message)")
}

try {
  Write-Snapshot ($lines -join "`n")
  exit 0
} catch {
  $fallback = @(
    "timestamp=$timestamp"
    "repo_root=$RepoRoot"
    "snapshot_write=failed"
    "reason=$($_.Exception.Message)"
  ) -join "`n"
  Write-Snapshot $fallback
  exit 0
}
