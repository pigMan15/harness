# 知识沉淀草稿

## 来源

- RunId: improve-quality-001
- Intent: FEATURE
- Risk: MEDIUM
- Phase dir: .harness/phases/improve-quality-001
- 原始 PRD / context-pack: 00-context-pack.md

## 候选知识

| 类型 | 标题 | 相对 PRD 的新增点 | 证据 | 建议位置 |
| --- | --- | --- | --- | --- |
| pitfall | 测试夹具必须和新增校验的不变量保持一致 | 增加 active state 与 workflow route 漂移校验后，原有 fixture 复制真实模板但写入最小 state，会制造假失败；fixture 应显式写入最小 workflow/gates/schema 或从 workflow 生成 required_nodes。 | 首次聚焦测试失败后修复 `tests/conftest.py`，最终 `79 passed`。 | `.harness/knowledge/engineering/fixture-route-drift.md` |
| pattern | TUI 交互结果用小 payload/helper 隔离以便测试 | 原始计划只指出 hard-code 问题；实现中确认将 `NewRunRequest` 和 `create_state_for_new_run()` 拆出，可不启动完整 Textual app 验证 intent/risk 保真。 | `tests/test_tui_new_run.py` 通过。 | `.harness/knowledge/engineering/tui-payload-helper.md` |
| rule | active state 的 required_nodes 应由 workflow route 校验 | 审计发现当前 state 与 workflow 路由可能漂移；本次将其固化为 validator 规则，防止 DONE 状态漏节点。 | `test_required_nodes_must_match_workflow_route` 和 harness validate 通过。 | `.harness/knowledge/engineering/state-route-validation.md` |

## 不建议沉淀的内容

- 本次 pip 安装输出：属于一次性环境准备日志，不是长期规则。
- 具体 pytest 耗时：只对当前机器有意义。
- 全量文档 mojibake 情况：仍是待办风险，但本 run 未完整修复，暂不沉淀为稳定结论。

## 待用户确认

- 是否接受上述 3 条候选知识进入长期知识库。
- 是否后续单独创建 run 处理全仓中文文档/模板 mojibake 修复。
