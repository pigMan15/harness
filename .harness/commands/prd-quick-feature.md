# Command: prd-quick-feature

目的：从 PRD/原型开始实现功能，但使用轻量流程，避免完整测试链路带来的 token 和时间消耗。

## 适用场景

- PRD 已经比较明确。
- 需要前后端一起改，但不需要预发部署和接口联调。
- 用户希望快速实现功能，再做最小自检。
- 当前任务不是库存、订单、权限、财务、外部系统等高风险核心链路。

## 推荐 run

```powershell
.\.harness\scripts\new-run.ps1 -RunId "feature-topic-YYYYMMDD" -Intent FEATURE -Risk MEDIUM
```

## 必须读取

- `AGENTS.md`
- `.harness/state.json`
- `.harness/workflow.yaml`
- `.harness/rules/context-budget.md`
- `.harness/context/acceptance.md`
- 用户指定的 PRD / 原型 / 参考界面
- 相关前端和后端代码入口

## 流程

1. 读取 PRD 和用户指定的前后端路径。
2. 生成轻量 `state.phase_dir/00-context-pack.md`，只记录本次实现必需信息。
3. 生成简要需求评审 `state.phase_dir/01-requirement-review.md`。
4. 生成简要方案 `state.phase_dir/03-solution-design.md`，不用写长篇架构文档。
5. 生成实施计划 `state.phase_dir/06-implementation-plan.md`。
6. 直接执行开发，并在 `state.phase_dir/11-development.md` 中简要记录编码思路、复用点和风险。
7. 如发现需要改变模块边界、接口契约、核心流程或架构风格，暂停并补充 `state.phase_dir/10-coding-design.md`，等待用户确认后再继续。
8. 做最小自检，记录到 `state.phase_dir/15-evidence.json`。
9. 生成简短验收说明 `state.phase_dir/18-acceptance-report.md`。

## 轻量编码思路记录

默认不强制生成 `10-coding-design.md`。在 `11-development.md` 中简要记录：

- 推荐实现方案。
- 是否沿用现有页面/接口风格。
- 前端组件拆分和状态管理方式。
- 后端接口、Service、DTO、权限、状态校验边界。
- 是否使用设计模式，以及为什么。
- 复用现有代码的位置。
- 中文注释策略。
- 风险点和需要用户确认的问题。

只有当任务升级为高风险、需要改变架构边界，或用户明确要求“先确认编码设计”时，才生成 `10-coding-design.md` 并停等确认。

## 最小自检范围

优先选择低成本验证：

- 前端类型检查、lint、构建或局部页面自检。
- 后端编译或相关类/接口的局部检查。
- 关键接口或按钮流程的人工自检说明。

允许不执行：

- ATDD。
- 预发部署。
- 完整接口联调。
- 全量回归测试。
- 与本需求无关的大范围测试。

如果检查无法执行，必须在 evidence 中标记为 `BLOCKED` 或 `WAIVED`，不要写 `PASS`。

## 升级条件

如果发现任务涉及以下内容，应暂停并询问是否升级为 `FEATURE / HIGH`：

- 库存数量或库存状态变化。
- 订单状态流转。
- 权限、认证、审计。
- 财务、结算。
- 外部系统回调或回传。
- 数据迁移。
- 生产部署。
- 高影响核心链路。

## 禁止

- 不要跑完整 21 节点流程。
- 不要执行 ATDD、预发部署、接口联调，除非用户明确要求。
- 不要为了补齐测试而进行大范围无关改造。
- 不要读取整套 `.harness/` 或无关历史 run。
- 如果已经进入 `CODING_DESIGN_CONFIRMATION`，用户未确认 `10-coding-design.md` 前，不要进行大范围代码修改。

## 用户短提示词

```text
按 prd-quick-feature 流程处理：
PRD：C:\path\to\prd.pdf
前端代码：D:\projects\frontend
后端代码：D:\projects\backend
需求：……
参考界面：……
只做最小自检，不走 ATDD、部署、接口联调；如发现需要调整架构或接口契约，再暂停让我确认编码设计。
```
