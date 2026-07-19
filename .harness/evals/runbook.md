# 门禁运行手册

## 验证前

1. 读取 `.harness/state.json`。
2. 从 `.harness/workflow.yaml` 读取必需门禁。
3. 读取 `.harness/evals/gates.yaml`。

## 验证中

1. 运行最窄但有意义的编译/静态检查。
2. 运行聚焦测试。
3. 中高风险任务运行更广范围测试。
4. 创建或更新 `state.phase_dir/15-evidence.json`。
5. 更新 state 中的门禁状态。

## 门禁失败时

1. 记录失败命令和关键输出。
2. 将门禁状态设为 `FAIL`。
3. 将 `state.retry_counts[gate]` 加 1；字段缺失时先按空对象初始化。
4. 从 `workflow.failure_recovery.gate_to_node` 读取回退节点。
5. 同一门禁失败次数不超过 `max_auto_retries_per_gate` 时，更新当前节点并继续处理。
6. 超过上限时，将 `status` 设为 `BLOCKED`，并在 `blocked_by` 中记录门禁和失败原因。
7. 不要声称完成。

## 失败回退表

| 门禁 | 回退节点 |
| --- | --- |
| `G1_REQUIREMENTS` | `REQUIREMENT_REVIEW` |
| `G2_DESIGN` | `SOLUTION_DESIGN` |
| `G3_COMPILE` | `DEVELOPMENT` |
| `G4_UNIT_TEST` | `DEVELOPMENT` |
| `G5_ATDD` | `DEVELOPMENT` |
| `G6_EVIDENCE` | `EVIDENCE_CAPTURE` |
| `G7_PRERELEASE` | `PRERELEASE_DEPLOYMENT` |
| `G8_ACCEPTANCE` | `ACCEPTANCE_REPORT` |

默认每个门禁最多自动重试 2 次。workflow 中的配置是唯一事实来源，本表用于人工阅读。

