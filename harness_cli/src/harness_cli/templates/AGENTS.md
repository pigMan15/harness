# 项目 Harness 入口

本仓库使用文件化 AI Coding Harness。Harness 是流程、状态、规则、门禁和交接产物的唯一事实来源。

## 操作约定

1. 开始非简单任务前，先阅读 `.harness/README.md`。
2. 凡是实现、修复、部署或排查任务，都要读取 `.harness/state.json` 和 `.harness/workflow.yaml`。
3. 由 `.harness/agents/dispatcher.md` 根据当前状态决定下一步。
4. 重要产物必须写入 `.harness/state.json` 中 `phase_dir` 指向的目录，不要只留在对话里。
5. 只读取当前阶段必要文件：当前命令、`state.json`、`workflow.yaml`、dispatcher、当前角色、必要规则/上下文和相关阶段产物；不要读取无关 agents/context/rules。
6. 声称完成前，必须执行 `.harness/evals/gates.yaml` 中适用的门禁。
7. 任一门禁失败，必须更新状态并回退到对应阶段。
8. 不得绕过 `.harness/rules/safety.md` 中的安全规则。
9. 每次更新 `.harness/state.json` 后，保存到 `.harness/runs/<run_id>/state.json`，避免切换 run 后丢失进度。
10. 编码阶段新增或修改核心逻辑时，必须按 `.harness/rules/code-comment.md` 添加必要中文注释。
11. 进入 `CODING_DESIGN_CONFIRMATION` 时，必须先生成 `state.phase_dir/10-coding-design.md`，等待用户确认编码思想、架构风格和模块边界后再大范围改代码。
12. 所有需求、设计、实施计划、开发记录和验证证据必须写入当前 `.harness/state.json` 的 `phase_dir`；任何 Skill 指定的默认文档目录均不得覆盖该规则，跨仓库任务也不例外。
13. 明确禁止使用 `docs/superpowers` 作为 harness 流程产物目录。写设计、计划、证据前必须先读取 `.harness/state.json` 并解析 `phase_dir`。

## 上下文预算

常驻上下文要尽量小。推荐加载顺序：

1. 当前入口文件。
2. `.harness/state.json`。
3. `.harness/workflow.yaml`。
4. `.harness/agents/` 中的当前角色文件。
5. 该角色引用的必要规则和上下文。

写入前必须先判断产物类型：源码写入目标源码仓库；流程产物只写入当前 `state.phase_dir`。

默认原则：只读取当前阶段必要文件。除非 dispatcher、当前角色或用户明确要求，不要预读整套 `.harness/`，也不要扫描无关历史 run。

## 状态纪律

当前流程阶段记录在 `.harness/state.json` 中。流程阶段发生变化时，要更新状态文件，并在 `phase_dir` 目录下写一条简短阶段记录，例如 `.harness/phases/<run_id>/`。

`.harness/state.json` 表示当前激活 run；每个 run 的状态快照保存在 `.harness/runs/<run_id>/state.json`。恢复旧 run 时使用 `.harness/scripts/switch-run.*`。

## 完成标准

完成意味着：

- 必需产物已存在。
- 必需门禁已通过，或有明确记录的豁免。
- 验证证据已记录。
- 最终说明讲清楚改了什么、如何验证、还有什么风险。
