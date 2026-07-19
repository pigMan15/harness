#!/usr/bin/env sh
set -eu

ROOT="${1:-.}"

required='
AGENTS.md
.harness/README.md
.harness/state.json
.harness/state.schema.json
.harness/workflow.yaml
.harness/evals/gates.yaml
.harness/runs/.gitkeep
.harness/agents/dispatcher.md
.harness/agents/developer.md
.harness/agents/verifier.md
.harness/rules/artifact-location.md
.harness/rules/build.md
.harness/rules/safety.md
.harness/rules/evidence.md
.harness/phases/.gitkeep
'

missing=0
for item in $required; do
  if [ ! -e "$ROOT/$item" ]; then
    if [ "$missing" -eq 0 ]; then
      printf '%s\n' 'Harness validation failed: missing files:'
    fi
    printf ' - %s\n' "$item"
    missing=1
  fi
done

if [ "$missing" -ne 0 ]; then
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  python3 - "$ROOT" <<'PY'
from pathlib import Path
import json
import re
import sys


def fail(message):
    raise SystemExit(f"Harness validation failed: {message}")


root = Path(sys.argv[1]).resolve()
state_path = root / ".harness/state.json"
workflow_path = root / ".harness/workflow.yaml"
gates_path = root / ".harness/evals/gates.yaml"

try:
    state = json.loads(state_path.read_text(encoding="utf-8-sig"))
except (OSError, json.JSONDecodeError) as exc:
    fail(f"state.json is not valid JSON: {exc}")

required_state_fields = {
    "schema_version",
    "run_id",
    "status",
    "intent",
    "risk",
    "current_node",
    "next_role",
    "phase_dir",
    "required_nodes",
    "completed_nodes",
    "blocked_by",
    "artifacts",
    "gates",
}
missing_fields = sorted(required_state_fields - set(state))
if missing_fields:
    fail(f"state.json is missing fields: {', '.join(missing_fields)}")

phase_dir = str(state["phase_dir"]).replace("\\", "/")
if not re.fullmatch(r"\.harness/phases/[^/]+", phase_dir):
    fail(f"phase_dir must match .harness/phases/<run_id>: {state['phase_dir']}")

phase_root = (root / ".harness/phases").resolve()
phase_path = (root / phase_dir).resolve()
if not phase_path.is_dir():
    fail(f"phase_dir does not exist: {state['phase_dir']}")

# 同时校验规范化格式与真实路径，防止 phase_dir 穿越到 phases 之外。
if phase_root not in phase_path.parents:
    fail(f"phase_dir is outside .harness/phases: {state['phase_dir']}")

workflow_lines = workflow_path.read_text(encoding="utf-8-sig").splitlines()
gate_lines = gates_path.read_text(encoding="utf-8-sig").splitlines()

nodes = {}
current_node = None
for line in workflow_lines:
    match = re.match(r"^\s+- id:\s*([A-Z][A-Z0-9_]*)\s*$", line)
    if match:
        current_node = match.group(1)
        nodes[current_node] = {"role": None, "artifact": None, "gates": []}
        continue
    if re.match(r"^routes:\s*$", line):
        current_node = None
        continue
    if current_node is None:
        continue
    match = re.match(r"^\s+role:\s*([a-z][a-z0-9-]*)\s*$", line)
    if match:
        nodes[current_node]["role"] = match.group(1)
        continue
    match = re.match(r'^\s+artifact:\s*"([^"]+)"\s*$', line)
    if match:
        nodes[current_node]["artifact"] = match.group(1)
        continue
    match = re.match(r"^\s+gates:\s*\[(.*)\]\s*$", line)
    if match:
        nodes[current_node]["gates"] = re.findall(
            r"G[0-9]+_[A-Z0-9_]+", match.group(1)
        )

defined_gates = {
    match.group(1)
    for line in gate_lines
    if (match := re.match(r"^\s{2}(G[0-9]+_[A-Z0-9_]+):\s*$", line))
}
if not nodes:
    fail("workflow.yaml defines no nodes")
if not defined_gates:
    fail("gates.yaml defines no gates")

route_nodes = set()
hard_rule_nodes = set()
recovery = []
section = None
in_gate_map = False
for line in workflow_lines:
    if re.match(r"^routes:\s*$", line):
        section = "routes"
        continue
    if re.match(r"^hard_rules:\s*$", line):
        section = "hard_rules"
        continue
    if re.match(r"^failure_recovery:\s*$", line):
        section = "failure_recovery"
        continue
    if re.match(r"^gate_meanings:\s*$", line):
        section = "gate_meanings"
        in_gate_map = False
        continue

    if section == "routes":
        match = re.search(r"\[(.*)\]", line)
        if match:
            route_nodes.update(re.findall(r'"([A-Z][A-Z0-9_]*)"', match.group(1)))
    elif section == "hard_rules":
        match = re.match(r"^\s+-\s+([A-Z][A-Z0-9_]*)\s*$", line)
        if match:
            hard_rule_nodes.add(match.group(1))
    elif section == "failure_recovery":
        if re.match(r"^\s{2}gate_to_node:\s*$", line):
            in_gate_map = True
            continue
        if in_gate_map:
            match = re.match(
                r"^\s{4}(G[0-9]+_[A-Z0-9_]+):\s+([A-Z][A-Z0-9_]*)\s*$",
                line,
            )
            if match:
                recovery.append((match.group(1), match.group(2)))

for node_id in sorted(route_nodes | hard_rule_nodes):
    if node_id not in nodes:
        fail(f"workflow.yaml references unknown node: {node_id}")

for node_id, node in nodes.items():
    role = node["role"]
    if not role:
        fail(f"node {node_id} has no role")
    if not (root / f".harness/agents/{role}.md").is_file():
        fail(f"node {node_id} references missing role: {role}")
    for gate_id in node["gates"]:
        if gate_id not in defined_gates:
            fail(f"node {node_id} references unknown gate: {gate_id}")

for gate_id, node_id in recovery:
    if gate_id not in defined_gates:
        fail(f"failure_recovery references unknown gate: {gate_id}")
    if node_id not in nodes:
        fail(f"failure_recovery references unknown node: {node_id}")

state_nodes = (
    [state.get("current_node")]
    + list(state.get("required_nodes") or [])
    + list(state.get("completed_nodes") or [])
)
for node_id in sorted({str(value) for value in state_nodes if value}):
    if node_id not in nodes:
        fail(f"state.json references unknown node: {node_id}")

for gate_id in state.get("gates", {}):
    if gate_id not in defined_gates:
        fail(f"state.json references unknown gate: {gate_id}")

for node_id in state.get("completed_nodes") or []:
    artifact = nodes[str(node_id)]["artifact"]
    if artifact and not (phase_path / artifact).is_file():
        fail(f"completed node {node_id} is missing artifact: {artifact}")

print("Harness validation passed.")
PY
else
  printf '%s\n' 'Python 3 not found; running basic harness validation only.'

  phase_dir="$(sed -n 's/.*"phase_dir"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$ROOT/.harness/state.json" | head -n 1)"
  case "$phase_dir" in
    ''|*..*|.harness/phases/*/*)
      printf 'Harness validation failed: invalid phase_dir: %s\n' "$phase_dir"
      exit 1
      ;;
    .harness/phases/*) ;;
    *)
      printf 'Harness validation failed: invalid phase_dir: %s\n' "$phase_dir"
      exit 1
      ;;
  esac

  if [ ! -d "$ROOT/$phase_dir" ]; then
    printf 'Harness validation failed: phase_dir does not exist: %s\n' "$phase_dir"
    exit 1
  fi

  for gate in G1_REQUIREMENTS G2_DESIGN G3_COMPILE G4_UNIT_TEST G5_ATDD G6_EVIDENCE G7_PRERELEASE G8_ACCEPTANCE; do
    if ! grep -q "$gate" "$ROOT/.harness/workflow.yaml"; then
      printf 'Harness validation failed: workflow.yaml does not contain %s.\n' "$gate"
      exit 1
    fi
  done

  printf '%s\n' 'Harness basic validation passed.'
fi
