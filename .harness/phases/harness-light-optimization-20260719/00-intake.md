# 任务入口

- RunId：`harness-light-optimization-20260719`
- 意图：`REFACTOR`
- 风险：`MEDIUM`
- 目标：对现有 Harness 做轻量优化，提高流程一致性、失败恢复确定性和结构校验能力。
- 用户选择：保持现有目录结构，只优化行为。

## 范围

1. 修复 `workflow.yaml` 路由与硬规则冲突。
2. 增加门禁失败后的明确回退映射和重试上限。
3. 增强现有 `validate-harness.ps1/.cmd/.sh`，不新增校验脚本。

## 不在范围内

- 不增加项目上下文模板。
- 不调整 `.harness/` 目录结构。
- 不增加 MCP、Skill 注册中心或 Token 统计。
- 不增加新的流程节点和脚本入口。
