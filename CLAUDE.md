# Claude Code Harness 入口

本文件是 `AGENTS.md` 的 Claude Code 版本。真正的流程事实来源是 `.harness/`。

## 必须遵守

1. 开始非简单任务前，先阅读 `.harness/README.md`。
2. 流程类工作开始前，读取 `.harness/state.json` 和 `.harness/workflow.yaml`。
3. 使用 `.harness/agents/dispatcher.md` 选择下一角色和阶段。
4. 阶段产物写入 `.harness/state.json` 中 `phase_dir` 指向的目录，例如 `.harness/phases/<run_id>/`。
5. 只读取当前阶段必要文件：当前命令、`state.json`、`workflow.yaml`、dispatcher、当前角色、必要规则/上下文和相关阶段产物；不要一次性加载整套 harness。
6. 声称完成前，执行或记录 `.harness/evals/gates.yaml` 中所有适用门禁。
7. 门禁失败默认阻断，除非用户明确接受有记录的豁免。
8. 每次更新 `.harness/state.json` 后，保存到 `.harness/runs/<run_id>/state.json`。
9. 编码阶段新增或修改核心逻辑时，必须按 `.harness/rules/code-comment.md` 添加必要中文注释。
10. 进入 `CODING_DESIGN_CONFIRMATION` 时，必须先生成 `state.phase_dir/10-coding-design.md`，等待用户确认编码思想、架构风格和模块边界后再大范围改代码。
11. 所有需求、设计、实施计划、开发记录和验证证据必须写入当前 `.harness/state.json` 的 `phase_dir`；任何 Skill 指定的默认文档目录均不得覆盖该规则，跨仓库任务也不例外。
12. 明确禁止使用 `docs/superpowers` 作为 harness 流程产物目录。写设计、计划、证据前必须先读取 `.harness/state.json` 并解析 `phase_dir`。

## 最小常驻 Prompt

不要把整套 harness 复制到当前对话。上下文里只保留当前阶段、当前角色说明、必要规则和当前 run 的相关产物。

写入前必须先判断产物类型：源码写入目标源码仓库；流程产物只写入当前 `state.phase_dir`。
