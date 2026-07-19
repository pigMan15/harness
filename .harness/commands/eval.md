# Command: eval

目的：评估一次 harness 运行是否遵守流程和门禁。

## 步骤

1. 读取 `.harness/evals/checklist.md`。
2. 读取 `.harness/evals/gates.yaml`。
3. 根据 `.harness/workflow.yaml` 检查必需产物。
4. 使用 `.harness/evals/scoring.md` 评分。
5. 将发现记录到 `state.phase_dir/eval-YYYYMMDD.md`。

## 规则

评估者只观察，不得替被评估运行补齐缺失的实现产物。

