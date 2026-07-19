#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF'
用法:
  ./.harness/scripts/new-run.sh RUN_ID INTENT RISK

示例:
  ./.harness/scripts/new-run.sh feature-export-20260616 FEATURE MEDIUM

INTENT:
  QUERY BUG_FIX FEATURE REFACTOR DEPLOYMENT INCIDENT

RISK:
  NA LOW MEDIUM HIGH
EOF
}

if [ "$#" -ne 3 ]; then
  usage
  exit 1
fi

RUN_ID="$1"
INTENT="$2"
RISK="$3"

case "$INTENT" in
  QUERY|BUG_FIX|FEATURE|REFACTOR|DEPLOYMENT|INCIDENT) ;;
  *)
    printf '无效 Intent: %s\n' "$INTENT"
    usage
    exit 1
    ;;
esac

case "$RISK" in
  NA|LOW|MEDIUM|HIGH) ;;
  *)
    printf '无效 Risk: %s\n' "$RISK"
    usage
    exit 1
    ;;
esac

STATE_PATH=".harness/state.json"
if [ ! -f "$STATE_PATH" ]; then
  printf '找不到 %s，请在项目根目录运行。\n' "$STATE_PATH"
  exit 1
fi

PHASE_DIR=".harness/phases/$RUN_ID"
RUN_DIR=".harness/runs/$RUN_ID"
mkdir -p "$PHASE_DIR"
mkdir -p "$RUN_DIR"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  printf '%s\n' 'new-run.sh 需要 python3 或 python 来安全更新 JSON。'
  exit 1
fi

"$PYTHON_BIN" - "$STATE_PATH" "$RUN_ID" "$INTENT" "$RISK" "$PHASE_DIR" <<'PY'
import json
import sys
from datetime import datetime

state_path, run_id, intent, risk, phase_dir = sys.argv[1:6]

with open(state_path, "r", encoding="utf-8") as f:
    state = json.load(f)

state["run_id"] = run_id
state["status"] = "ROUTING"
state["intent"] = intent
state["risk"] = risk
state["current_node"] = "INTAKE"
state["next_role"] = "dispatcher"
state["phase_dir"] = phase_dir
state["required_nodes"] = []
state["completed_nodes"] = []
state["blocked_by"] = []
state["artifacts"] = {}
state["gates"] = {
    "G1_REQUIREMENTS": "NOT_RUN",
    "G2_DESIGN": "NOT_RUN",
    "G3_COMPILE": "NOT_RUN",
    "G4_UNIT_TEST": "NOT_RUN",
    "G5_ATDD": "NOT_RUN",
    "G6_EVIDENCE": "NOT_RUN",
    "G7_PRERELEASE": "NOT_RUN",
    "G8_ACCEPTANCE": "NOT_RUN",
}
state["last_updated"] = datetime.now().replace(microsecond=0).isoformat()
state["notes"] = "运行已初始化。Dispatcher 必须从 workflow.yaml 选择路径。"

with open(state_path, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
    f.write("\n")

with open(f".harness/runs/{run_id}/state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY

printf '已初始化 harness 运行 %s (%s/%s)，阶段目录：%s，状态快照：%s/state.json.\n' "$RUN_ID" "$INTENT" "$RISK" "$PHASE_DIR" "$RUN_DIR"
