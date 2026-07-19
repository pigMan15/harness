# 完整 AI Coding Harness 模板

这套 harness 用文件化工程流程替代临时 prompt，让 AI 辅助开发变得可约束、可恢复、可审计、可评测。

它基于五个原则：

1. 常驻指令尽量小。
2. 流程状态放在对话之外。
3. 用角色文件拆分职责。
4. 每个阶段都产出可审计文件。
5. 完成前用确定性门禁检查。

所有流程产物都归属当前 `.harness/state.json` 的 `phase_dir`。外部 Skill、插件或跨仓库任务的默认文档路径不得覆盖该规则，尤其禁止把 harness 流程产物写入 `docs/superpowers`。

## 目录说明

```text
.harness/
  state.json              当前持久化流程状态
  state.schema.json       状态文件结构
  workflow.yaml           21 节点流程、意图/风险路由、G1-G8 门禁
  rules/                  按需加载的原子规则
  agents/                 dispatcher、评审、开发、验证等角色说明
  context/                阶段专用深层指南和模板
  phases/                 每次运行生成的阶段产物，按 run_id 分目录
  runs/                   每个 run 的 state.json 快照，按 run_id 分目录
  evals/                  门禁定义、评分、审计清单
  commands/               可复用命令剧本
  knowledge/              Obsidian / LLM Wiki 接入规则和知识沉淀策略
  hooks/                  运行时策略示例
  templates/              可复用产物模板
```

## 标准流程

完整流程最多包含 21 个节点：

1. 需求进入
2. 上下文包
3. 需求评审
4. 需求确认
5. 方案设计
6. 方案确认
7. 失败预演
8. 实施计划
9. 验收标准确认
10. 变更申请
11. 分支创建
12. Worktree 创建
13. 编码设计确认
14. 开发
15. 编译
16. 单元测试
17. ATDD 或集成测试
18. 证据采集
19. 预发部署
20. 接口测试
21. 验收报告

不是所有任务都要走满 21 个节点。`workflow.yaml` 会根据意图和风险选择最小必要路径。

## 角色模型

- `dispatcher`：读取状态和 workflow，决定下一角色。
- `orchestrator`：合成多角色评审，并在需要时请求用户确认。
- `requirement-analyst`：检查业务意图和验收缺口。
- `tech-architect`：检查设计、集成边界和可维护性。
- `quality-guardian`：检查风险、测试范围、回滚和门禁。
- `plan-generator`：编写实施计划。
- `developer`：实现代码。
- `verifier`：运行门禁并记录证据。
- `deployer`：处理预发部署。
- `tester`：执行接口或验收测试。
- `state-keeper`：负责状态更新。

## 使用方式

1. 从 `AGENTS.md` 或 `CLAUDE.md` 进入。
2. 读取 `state.json`。
3. 让 dispatcher 判断下一阶段。
4. 只加载当前角色文件。
5. 在 `state.json` 的 `phase_dir` 指向目录下生成或更新一个阶段产物。
6. 执行 workflow 要求的门禁。
7. 重复直到验收报告完成。

写设计、计划、证据前必须先读取 `.harness/state.json`，确定 `run_id` 和 `phase_dir`。如果本次还会修改其他源码仓库，源码写目标仓库，流程产物仍写发起任务的 harness `phase_dir`。

## 多 Run 切换

`.harness/state.json` 只表示当前激活 run。每个 run 的状态快照保存在：

```text
.harness/runs/<run_id>/state.json
```

创建新 run 会自动写入快照。流程中状态变化后，可保存当前快照：

```powershell
.\.harness\scripts\save-run.ps1
```

恢复旧 run：

```powershell
.\.harness\scripts\switch-run.ps1 -RunId "run-id"
```

完整上手示例见 `.harness/TUTORIAL.md`。

已有工程接入指南见 `.harness/PROJECT-INTEGRATION-GUIDE.md`。

常用场景命令索引见 `.harness/commands/README.md`。

## 默认拒绝原则

当状态、证据或门禁结果不清楚时，默认“不算完成”。记录不确定性，并路由回合适阶段。
