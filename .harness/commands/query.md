# Command: query

目的：只回答或排查，不启动开发流程。

## 步骤

1. 分类为 `QUERY` 或 `INCIDENT`。
2. 运行类问题使用 `.harness/context/incident-query.md`。
3. 如果排查可能继续，将有用发现记录到 `state.phase_dir/00-intake.md`。
4. 如果发现真实 bug 或新需求，路由到 `dev`。

## 规则

query 模式不编辑源码。

