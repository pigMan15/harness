param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"

function Fail-Harness([string]$Message) {
  Write-Host "Harness validation failed: $Message" -ForegroundColor Red
  exit 1
}

function Get-WorkflowNodes([string[]]$Lines) {
  $nodes = @{}
  $currentNode = $null

  foreach ($line in $Lines) {
    if ($line -match '^\s+- id:\s*([A-Z][A-Z0-9_]*)\s*$') {
      $currentNode = $Matches[1]
      $nodes[$currentNode] = @{
        role = $null
        artifact = $null
        gates = @()
      }
      continue
    }

    if ($line -match '^routes:\s*$') {
      $currentNode = $null
      continue
    }

    if (-not $currentNode) {
      continue
    }

    if ($line -match '^\s+role:\s*([a-z][a-z0-9-]*)\s*$') {
      $nodes[$currentNode]['role'] = $Matches[1]
    } elseif ($line -match '^\s+artifact:\s*"([^"]+)"\s*$') {
      $nodes[$currentNode]['artifact'] = $Matches[1]
    } elseif ($line -match '^\s+gates:\s*\[(.*)\]\s*$') {
      $nodes[$currentNode]['gates'] = @(
        [regex]::Matches($Matches[1], 'G[0-9]+_[A-Z0-9_]+') |
          ForEach-Object { $_.Value }
      )
    }
  }

  return $nodes
}

function Get-DefinedGateIds([string[]]$Lines) {
  return @(
    $Lines | ForEach-Object {
      if ($_ -match '^\s{2}(G[0-9]+_[A-Z0-9_]+):\s*$') {
        $Matches[1]
      }
    }
  )
}

function Get-WorkflowReferences([string[]]$Lines) {
  $routeNodes = @()
  $hardRuleNodes = @()
  $recovery = @()
  $section = $null
  $inGateMap = $false

  foreach ($line in $Lines) {
    if ($line -match '^routes:\s*$') {
      $section = 'routes'
      continue
    }
    if ($line -match '^hard_rules:\s*$') {
      $section = 'hard_rules'
      continue
    }
    if ($line -match '^failure_recovery:\s*$') {
      $section = 'failure_recovery'
      continue
    }
    if ($line -match '^gate_meanings:\s*$') {
      $section = 'gate_meanings'
      $inGateMap = $false
      continue
    }

    if ($section -eq 'routes' -and $line -match '\[(.*)\]') {
      $routeNodes += @(
        [regex]::Matches($Matches[1], '"([A-Z][A-Z0-9_]*)"') |
          ForEach-Object { $_.Groups[1].Value }
      )
    } elseif ($section -eq 'hard_rules' -and $line -match '^\s+-\s+([A-Z][A-Z0-9_]*)\s*$') {
      $hardRuleNodes += $Matches[1]
    } elseif ($section -eq 'failure_recovery') {
      if ($line -match '^\s{2}gate_to_node:\s*$') {
        $inGateMap = $true
      } elseif ($inGateMap -and $line -match '^\s{4}(G[0-9]+_[A-Z0-9_]+):\s+([A-Z][A-Z0-9_]*)\s*$') {
        $recovery += [pscustomobject]@{
          Gate = $Matches[1]
          Node = $Matches[2]
        }
      }
    }
  }

  return [pscustomobject]@{
    RouteNodes = @($routeNodes | Sort-Object -Unique)
    HardRuleNodes = @($hardRuleNodes | Sort-Object -Unique)
    Recovery = $recovery
  }
}

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$required = @(
  "AGENTS.md",
  ".harness/README.md",
  ".harness/state.json",
  ".harness/state.schema.json",
  ".harness/workflow.yaml",
  ".harness/evals/gates.yaml",
  ".harness/runs/.gitkeep",
  ".harness/agents/dispatcher.md",
  ".harness/agents/developer.md",
  ".harness/agents/verifier.md",
  ".harness/rules/artifact-location.md",
  ".harness/rules/build.md",
  ".harness/rules/safety.md",
  ".harness/rules/evidence.md",
  ".harness/phases/.gitkeep"
)

$missing = @(
  $required | Where-Object {
    -not (Test-Path -LiteralPath (Join-Path $rootPath $_))
  }
)

if ($missing.Count -gt 0) {
  Fail-Harness "missing files: $($missing -join ', ')"
}

$statePath = Join-Path $rootPath ".harness/state.json"
try {
  $state = Get-Content -Raw -LiteralPath $statePath -Encoding UTF8 | ConvertFrom-Json
} catch {
  Fail-Harness "state.json is not valid JSON: $($_.Exception.Message)"
}

$requiredStateFields = @(
  'schema_version', 'run_id', 'status', 'intent', 'risk',
  'current_node', 'next_role', 'phase_dir', 'required_nodes',
  'completed_nodes', 'blocked_by', 'artifacts', 'gates'
)

foreach ($field in $requiredStateFields) {
  if ($state.PSObject.Properties.Name -notcontains $field) {
    Fail-Harness "state.json is missing field: $field"
  }
}

$normalizedPhaseDir = ([string]$state.phase_dir) -replace '\\', '/'
if ($normalizedPhaseDir -notmatch '^\.harness/phases/[^/]+$') {
  Fail-Harness "phase_dir must match .harness/phases/<run_id>: $($state.phase_dir)"
}

$phaseDirPath = Join-Path $rootPath ([string]$state.phase_dir)
if (-not (Test-Path -LiteralPath $phaseDirPath -PathType Container)) {
  Fail-Harness "phase_dir does not exist: $($state.phase_dir)"
}

# 同时检查规范化路径和真实绝对路径，防止路径穿越到 phases 之外。
$phaseRootPath = (Resolve-Path -LiteralPath (Join-Path $rootPath '.harness/phases')).Path.TrimEnd('\', '/')
$resolvedPhaseDir = (Resolve-Path -LiteralPath $phaseDirPath).Path
$phasePrefix = $phaseRootPath + [IO.Path]::DirectorySeparatorChar
if (-not $resolvedPhaseDir.StartsWith($phasePrefix, [StringComparison]::OrdinalIgnoreCase)) {
  Fail-Harness "phase_dir is outside .harness/phases: $($state.phase_dir)"
}

$workflowLines = @(Get-Content -LiteralPath (Join-Path $rootPath '.harness/workflow.yaml') -Encoding UTF8)
$gateLines = @(Get-Content -LiteralPath (Join-Path $rootPath '.harness/evals/gates.yaml') -Encoding UTF8)
$nodes = Get-WorkflowNodes $workflowLines
$definedGateIds = @(Get-DefinedGateIds $gateLines | Sort-Object -Unique)
$references = Get-WorkflowReferences $workflowLines

if ($nodes.Count -eq 0) {
  Fail-Harness "workflow.yaml defines no nodes"
}
if ($definedGateIds.Count -eq 0) {
  Fail-Harness "gates.yaml defines no gates"
}

foreach ($nodeId in @($references.RouteNodes + $references.HardRuleNodes | Sort-Object -Unique)) {
  if (-not $nodes.ContainsKey($nodeId)) {
    Fail-Harness "workflow.yaml references unknown node: $nodeId"
  }
}

foreach ($nodeId in $nodes.Keys) {
  $node = $nodes[$nodeId]
  if (-not $node['role']) {
    Fail-Harness "node $nodeId has no role"
  }

  $rolePath = Join-Path $rootPath ".harness/agents/$($node['role']).md"
  if (-not (Test-Path -LiteralPath $rolePath -PathType Leaf)) {
    Fail-Harness "node $nodeId references missing role: $($node['role'])"
  }

  foreach ($gateId in @($node['gates'])) {
    if ($definedGateIds -notcontains $gateId) {
      Fail-Harness "node $nodeId references unknown gate: $gateId"
    }
  }
}

foreach ($item in @($references.Recovery)) {
  if ($definedGateIds -notcontains $item.Gate) {
    Fail-Harness "failure_recovery references unknown gate: $($item.Gate)"
  }
  if (-not $nodes.ContainsKey($item.Node)) {
    Fail-Harness "failure_recovery references unknown node: $($item.Node)"
  }
}

$stateNodeIds = @($state.current_node) + @($state.required_nodes) + @($state.completed_nodes)
foreach ($nodeId in @($stateNodeIds | Where-Object { $_ } | Sort-Object -Unique)) {
  if (-not $nodes.ContainsKey([string]$nodeId)) {
    Fail-Harness "state.json references unknown node: $nodeId"
  }
}

foreach ($gateId in @($state.gates.PSObject.Properties.Name)) {
  if ($definedGateIds -notcontains $gateId) {
    Fail-Harness "state.json references unknown gate: $gateId"
  }
}

foreach ($nodeId in @($state.completed_nodes)) {
  $artifact = $nodes[[string]$nodeId]['artifact']
  if ($artifact) {
    $artifactPath = Join-Path $resolvedPhaseDir $artifact
    if (-not (Test-Path -LiteralPath $artifactPath -PathType Leaf)) {
      Fail-Harness "completed node $nodeId is missing artifact: $artifact"
    }
  }
}

Write-Host "Harness validation passed." -ForegroundColor Green
exit 0
