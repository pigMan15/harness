param(
  [Parameter(Mandatory = $true)][string]$RunId,
  [Parameter(Mandatory = $true)][ValidateSet("QUERY", "BUG_FIX", "FEATURE", "REFACTOR", "DEPLOYMENT", "INCIDENT")][string]$Intent,
  [Parameter(Mandatory = $true)][ValidateSet("NA", "LOW", "MEDIUM", "HIGH")][string]$Risk
)

$ErrorActionPreference = "Stop"

$statePath = ".harness/state.json"
$state = Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json
$phaseDir = Join-Path ".harness/phases" $RunId
$runDir = Join-Path ".harness/runs" $RunId
New-Item -ItemType Directory -Force -Path $phaseDir | Out-Null
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$state.run_id = $RunId
$state.status = "ROUTING"
$state.intent = $Intent
$state.risk = $Risk
$state.current_node = "INTAKE"
$state.next_role = "dispatcher"
$state | Add-Member -NotePropertyName phase_dir -NotePropertyValue $phaseDir.Replace('\', '/') -Force
$state.required_nodes = @()
$state.completed_nodes = @()
$state.blocked_by = @()
$state.artifacts = [pscustomobject]@{}
$state.gates = [pscustomobject]@{
  G1_REQUIREMENTS = "NOT_RUN"
  G2_DESIGN = "NOT_RUN"
  G3_COMPILE = "NOT_RUN"
  G4_UNIT_TEST = "NOT_RUN"
  G5_ATDD = "NOT_RUN"
  G6_EVIDENCE = "NOT_RUN"
  G7_PRERELEASE = "NOT_RUN"
  G8_ACCEPTANCE = "NOT_RUN"
}
$state.last_updated = (Get-Date).ToString("s")
$state.notes = "Run initialized. Dispatcher must choose route from workflow.yaml."

$state | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $statePath -Encoding UTF8
$state | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $runDir "state.json") -Encoding UTF8
Write-Host "Initialized harness run $RunId ($Intent/$Risk). phase_dir=$phaseDir snapshot=$runDir\state.json"
