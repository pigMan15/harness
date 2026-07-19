#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF'
用法:
  ./.harness/scripts/switch-run.sh RUN_ID

示例:
  ./.harness/scripts/switch-run.sh feature-export-20260616
EOF
}

if [ "$#" -ne 1 ]; then
  usage
  exit 1
fi

RUN_ID="$1"
SNAPSHOT_PATH=".harness/runs/$RUN_ID/state.json"

if [ ! -f "$SNAPSHOT_PATH" ]; then
  printf '找不到 run 状态快照：%s\n' "$SNAPSHOT_PATH"
  printf '%s\n' '可用 run：'
  if [ -d ".harness/runs" ]; then
    find .harness/runs -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sed 's/^/ - /'
  fi
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  printf '%s\n' 'switch-run.sh 需要 python3 或 python 来读取 JSON。'
  exit 1
fi

PHASE_DIR="$("$PYTHON_BIN" - "$SNAPSHOT_PATH" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    state = json.load(f)

phase_dir = state.get("phase_dir")
if not phase_dir:
    raise SystemExit("run 状态快照缺少 phase_dir。")

print(phase_dir)
PY
)"

mkdir -p "$PHASE_DIR"
cp "$SNAPSHOT_PATH" ".harness/state.json"
printf '已切换到 harness run %s，阶段目录：%s.\n' "$RUN_ID" "$PHASE_DIR"
