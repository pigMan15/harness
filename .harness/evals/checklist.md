# Harness 审计清单

在信任一次运行前使用。

## 结构

- [ ] 存在 `AGENTS.md` 或 `CLAUDE.md`。
- [ ] 存在 `.harness/state.json`。
- [ ] 存在 `.harness/workflow.yaml`。
- [ ] `.harness/agents/` 下存在必需角色文件。
- [ ] `.harness/rules/` 下存在必需规则。
- [ ] `.harness/evals/gates.yaml` 下存在门禁定义。

## 流程

- [ ] 已分类 intent 和 risk。
- [ ] required_nodes 与 `workflow.yaml` 中路径一致。
- [ ] completed_nodes 均有对应产物。
- [ ] 失败门禁会路由回正确阶段。
- [ ] 豁免包含原因和负责人。

## 完成

- [ ] 证据文件存在。
- [ ] 最终报告存在。
- [ ] 验证命令已记录。
- [ ] 剩余风险已披露。

