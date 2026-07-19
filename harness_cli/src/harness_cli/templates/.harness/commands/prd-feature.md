# Command: prd-feature

目的：从 PRD、原型、截图、流程图或产品说明开始，按完整功能开发流程推进。

## 适用场景

- 从 PRD 实现新功能。
- 根据原型图补齐前后端逻辑。
- 根据业务流程图设计接口和数据流。
- 需要先确认需求和方案，不能直接写代码。
- 高风险或架构边界变化时，需要额外确认编码设计。

## 推荐 run

```powershell
.\.harness\scripts\new-run.ps1 -RunId "feature-topic-YYYYMMDD" -Intent FEATURE -Risk HIGH
```

小功能可使用 `Risk MEDIUM`。涉及库存、订单、财务、权限、数据迁移、部署、外部接口时使用 `HIGH`。

## 必须读取

- `AGENTS.md`
- `.harness/state.json`
- `.harness/workflow.yaml`
- `.harness/agents/dispatcher.md`
- `.harness/agents/requirement-analyst.md`
- `.harness/context/acceptance.md`
- `.harness/rules/coding-design.md`

## 流程

1. 在 `state.phase_dir/00-intake.md` 记录输入材料路径、目标和约束。
2. 读取 PRD/原型，先做需求评审，写入 `state.phase_dir/01-requirement-review.md`。
3. 明确验收标准，不能只写“完成 PRD”。
4. 如果需求不清晰，停止并向用户提问。
5. 需求确认后，进入方案设计，写入 `state.phase_dir/03-solution-design.md`。
6. 方案设计后停止，等待用户确认。
7. 用户确认后，写实施计划 `state.phase_dir/06-implementation-plan.md`。
8. 如果当前 run 是 `FEATURE / HIGH`，或实现会改变模块边界、接口契约、核心流程或架构风格，开发前生成 `state.phase_dir/10-coding-design.md` 并等待用户确认。
9. 普通 `FEATURE / MEDIUM` 在 `state.phase_dir/11-development.md` 中简要记录编码思路即可，不因细节实现停等确认。
10. 进入开发、编译、测试、证据和验收报告。

## 禁止

- 不要一开始就写代码。
- 不要跳过需求评审和方案设计。
- 不要在高风险或架构边界变化时跳过编码设计确认。
- 不要把原型中的视觉细节直接等同于后端业务规则。
- 不要在用户未确认方案或编码设计时做大范围改动。

## 用户短提示词

```text
按 prd-feature 流程处理：
PRD：docs/prd/xxx.md
原型：docs/prototype/xxx.png
目标：……
```
