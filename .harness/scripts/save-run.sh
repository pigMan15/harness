#!/usr/bin/env sh
set -eu

STATE_PATH=".harness/state.json"
if [ ! -f "$STATE_PATH" ]; then
  printf '找不到 %s\n' "$STATE_PATH"
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  printf '%s\n' 'save-run.sh 需要 python3 或 python 来读取 JSON。'
  exit 1
fi

RUN_ID="$("$PYTHON_BIN" - "$STATE_PATH" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    state = json.load(f)

run_id = state.get("run_id")
if not run_id:
    raise SystemExit("state.json 缺少 run_id。")

print(run_id)
PY
)"

RUN_DIR=".harness/runs/$RUN_ID"
mkdir -p "$RUN_DIR"
cp "$STATE_PATH" "$RUN_DIR/state.json"
printf '已保存当前 run 状态快照：%s/state.json\n' "$RUN_DIR"
