# Claude Code Harness 入口

本文件是 `AGENTS.md` 的 Claude Code 版本。真正的流程事实来源是 `.harness/`。

## 硬性约束（不可绕过）

1. **所有任务都必须经过 harness**。涉及源码变更、构建、测试、部署、排查的任务全部走 harness。唯一例外：纯信息查询不产生文件变更。

2. **禁止自行判定任务类型**。`intent` 和 `risk` 从 `state.json` 读取，AI 不得覆盖。即使你判定"更像 bug fix"，也不得修改。

3. **禁止跳过节点**。Dispatcher 决定的节点必须执行，不得因为"简单"或"已知答案"而跳过。

4. **禁止无记录操作**。所有状态变更、门禁结果、阶段产物必须写入 `phase_dir`。

5. **禁止越权标记门禁**。只有 verifier 可以标记 G3-G8。

## 每次对话的标准流程

1. 读取 `.harness/state.json` 和 `.harness/workflow.yaml`
2. 由 `.harness/agents/dispatcher.md` 决定下一个节点和角色
3. 只加载当前角色文件和必要规则
4. 执行当前节点工作，产物写入 `state.phase_dir`
5. 更新 `state.json`，保存快照到 `runs/<run_id>/`
6. 声称完成前，执行 `.harness/evals/gates.yaml` 中适用门禁

## 常见绕过借口（全部无效）

- "这只是个小改动" → 源码改动 = 非简单任务
- "跳过评审吧" → Dispatcher 决定，不是 AI 决定
- "用户说快点" → 快 ≠ 跳门禁
- "之前做过类似的" → 每个 run 独立

## 状态纪律

- 产物写入 `state.phase_dir`，禁止写入 `docs/superpowers`
- 每次更新 `state.json` 后保存快照到 `runs/<run_id>/`
- 门禁重试上限 2 次，超过 → `BLOCKED`
