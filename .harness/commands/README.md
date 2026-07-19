# Commands 使用索引

这里的文件不是可执行脚本，而是给 AI worker 读取的场景流程说明。你可以在需求里直接引用命令名，减少重复提示词。

## 常用场景

| 场景 | 命令文件 | 你可以怎么说 |
| --- | --- | --- |
| 从 PRD/原型做完整功能 | `prd-feature.md` | 按 prd-feature 流程处理，PRD 在 xxx，原型在 xxx |
| 从 PRD 快速实现功能 | `prd-quick-feature.md` | 按 prd-quick-feature 流程处理，PRD 在 xxx |
| 从知识库/PRD 开始做功能 | `knowledge-backed-prd.md` | 按 knowledge-backed-prd 流程处理，PRD=xxx |
| 从 run 提炼知识 | `promote-learning.md` | 按 promote-learning 流程总结当前 run |
| 修 bug | `bugfix.md` | 按 bugfix 流程修复：现象是 xxx |
| 重构 | `refactor.md` | 按 refactor 流程重构：目标是 xxx |
| 代码评审 | `code-review.md` | 按 code-review 流程评审这次改动 |
| 接口联调/验收 | `interface-test.md` | 按 interface-test 流程验证接口 xxx |
| 预发部署验证 | `release-check.md` | 按 release-check 流程做预发验证 |
| 事故排查 | `incident.md` | 按 incident 流程排查：现象是 xxx |
| 只读查询 | `query.md` | 按 query 模式分析，不改代码 |

## 使用规则

1. 先初始化 run，除非只是纯查询。
2. 命令文件只决定“怎么走流程”，不替代 `state.json` 和 `workflow.yaml`。
3. 阶段产物必须写入 `state.phase_dir`。
4. 完成前仍然要按 `gates.yaml` 跑适用门禁。
5. 如果用户明确要求轻量实现，优先使用 `prd-quick-feature.md`。
6. 高风险功能、重构、高风险修复，或开发中需要调整架构/接口契约时，才在开发前生成 `10-coding-design.md` 并等待确认；普通中风险功能默认不因细节实现反复确认。

## 最短提示词

```text
按 <command-name> 流程处理：
需求/问题：……
输入材料：……
```
