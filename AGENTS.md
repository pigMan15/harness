# 项目 Harness 入口

本仓库使用 `.harness/` 作为 AI Coding 工程化流程的唯一事实来源。

## 硬性约束（不可绕过）

1. **所有任务都必须经过 harness**。只要涉及以下任何一项，就是"非简单任务"，必须走 harness：
   - 新增、修改或删除任何源码文件
   - 运行构建、测试或部署命令
   - 分析或排查生产问题
   - 任何用户明确要求按流程处理的任务
   - **唯一例外**：纯信息查询（"这个函数做什么"、"解释这段代码"），不产生任何文件变更

2. **禁止自行判定任务类型**。`intent` 和 `risk` 由用户在 `bridle new` 时指定，或从 `state.json` 读取。AI 不得覆盖——即使你觉得"这更像 bug fix"，也必须尊重已记录的类型。

3. **禁止跳过节点**。Dispatcher 决定的下一个节点必须执行。不得因为"这个节点很简单"或"我已经知道答案"而跳过。

4. **禁止无记录操作**。任何对 `state.json` 的修改、任何门禁结果、任何阶段产物，都必须写入 `phase_dir`。对话里的口头确认不构成记录。

5. **禁止越权标记门禁**。只有 verifier 角色可以标记 G3-G8 门禁。Developer 不得把 `COMPILE` 标记为 `PASS`。

## 每次对话的标准流程

1. 读取 `.harness/state.json` 和 `.harness/workflow.yaml`
2. 由 `.harness/agents/dispatcher.md` 决定下一个节点和角色
3. 只加载当前角色文件和必要规则，不预读整套 harness
4. 执行当前节点工作，产物写入 `state.phase_dir`
5. 更新 `state.json`，保存快照到 `runs/<run_id>/`
6. 声称完成前，执行 `.harness/evals/gates.yaml` 中适用门禁
7. 门禁失败 → 回退到对应阶段，最多自动重试 2 次

## 常见绕过借口（全部无效）

- "这只是个小改动" → 任何源码改动 = 非简单任务
- "我理解需求了，跳过评审吧" → Dispatcher 决定是否跳过
- "用户说快点" → 快不等于跳过门禁
- "之前做过类似的" → 每个 run 独立，不能引用历史经验
- "那个节点只是确认，可以合并" → 节点独立，不可合并

## 状态纪律

- `.harness/state.json` = 当前激活 run，每次变更后保存快照
- 产物只写入 `state.phase_dir`，禁止写入 `docs/superpowers`
- `retry_counts` 追踪门禁重试，超过 `max_auto_retries_per_gate` → `BLOCKED`
