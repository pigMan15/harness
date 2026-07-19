param(
  [Parameter(Mandatory = $true)][string]$RunId
)

$ErrorActionPreference = "Stop"

$runDir = Join-Path ".harness/runs" $RunId
$snapshotPath = Join-Path $runDir "state.json"

if (-not (Test-Path -LiteralPath $snapshotPath)) {
  Write-Host "Run state snapshot not found: $snapshotPath" -ForegroundColor Red
  Write-Host "Available runs:" -ForegroundColor Yellow
  if (Test-Path -LiteralPath ".harness/runs") {
    Get-ChildItem -Directory ".harness/runs" | ForEach-Object { Write-Host " - $($_.Name)" }
  }
  exit 1
}

$state = Get-Content -Raw -LiteralPath $snapshotPath | ConvertFrom-Json
if (-not $state.phase_dir) {
  Write-Host "Run state snapshot is missing phase_dir: $snapshotPath" -ForegroundColor Red
  exit 1
}

if (-not (Test-Path -LiteralPath $state.phase_dir)) {
  New-Item -ItemType Directory -Force -Path $state.phase_dir | Out-Null
}

Copy-Item -LiteralPath $snapshotPath -Destination ".harness/state.json" -Force
Write-Host "Switched to harness run $RunId. phase_dir=$($state.phase_dir)"
