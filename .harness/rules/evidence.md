# 证据规则

目的：让完成状态可审计。

## 必要证据

每次完成的运行都必须包含 `state.phase_dir/15-evidence.json`。

写入证据前必须先读取 `.harness/state.json` 并解析 `phase_dir`。即使外部 Skill 默认要求把证据、设计或计划写入 `docs/superpowers`，也必须改写到当前 `phase_dir`。

最少字段：

- `run_id`
- `intent`
- `risk`
- `changed_files`
- `commands`
- `gates`
- `artifacts`
- `waivers`
- `residual_risks`

## 门禁状态值

- `PASS`：由命令、文件或直接检查证明通过。
- `FAIL`：已检查且失败。
- `WAIVED`：未执行，但有原因和负责人。
- `BLOCKED`：因环境、凭证或依赖缺失无法执行。
- `NOT_REQUIRED`：当前 workflow 不要求。

## 规则

AI 自报成功不是证据。证据必须指向命令结果、文件产物、测试输出或明确豁免。

