# Command: dev

目的：使用本 harness 运行开发流程。

## 步骤

1. 使用 `.harness/agents/intent-classifier.md` 分类 intent 和 risk。
2. 更新 `.harness/state.json`。
3. 让 dispatcher 判断下一节点。
4. 执行被选中的角色。
5. 写入 `state.phase_dir` 下的阶段产物。
6. 重复直到 verifier 门禁通过，并写出验收报告。

## 必须读取

- `.harness/state.json`
- `.harness/workflow.yaml`
- `.harness/agents/dispatcher.md`

