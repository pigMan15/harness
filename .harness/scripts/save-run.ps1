$ErrorActionPreference = "Stop"

$statePath = ".harness/state.json"
if (-not (Test-Path -LiteralPath $statePath)) {
  Write-Host "State file not found: $statePath" -ForegroundColor Red
  exit 1
}

$state = Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json
if (-not $state.run_id) {
  Write-Host "state.json is missing run_id." -ForegroundColor Red
  exit 1
}

$runDir = Join-Path ".harness/runs" $state.run_id
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
Copy-Item -LiteralPath $statePath -Destination (Join-Path $runDir "state.json") -Force
Write-Host "Saved current run state snapshot: $runDir\state.json"
