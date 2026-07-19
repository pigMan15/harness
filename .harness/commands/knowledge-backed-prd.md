# Command: knowledge-backed-prd

目的：从 Obsidian PRD、LLM Wiki 页面或需求关键词开始，先生成本次 run 的 `00-context-pack.md`，再进入 PRD 功能开发流程。

## 适用场景

- PRD 写在 Obsidian 中。
- 需求只给了 PRD ID、标题或关键词。
- 需要结合 LLM Wiki 中的业务背景、历史问题、接口约定。
- 不希望 AI 反复扫描整个知识库。

## 推荐 run

```powershell
.\.harness\scripts\new-run.ps1 -RunId "feature-topic-YYYYMMDD" -Intent FEATURE -Risk MEDIUM
```

涉及库存、订单、权限、财务、外部系统、部署或数据一致性时使用 `Risk HIGH`。

## 输入方式

三种方式都可以：

```text
PRD 路径：D:\ObsidianVault\WMS\PRD\WMS-PRD-20260625-001-波次优化.md
PRD ID：WMS-PRD-20260625-001
关键词：波次优化
```

如果只给 ID 或关键词，应先通过 LLM Wiki 或用户指定的知识库查找候选 PRD。候选不唯一时，先让用户确认，不要猜。

## 必须读取

- `AGENTS.md`
- `.harness/state.json`
- `.harness/workflow.yaml`
- `.harness/knowledge/context-pack-template.md`
- `.harness/commands/prd-feature.md`

按需读取：

- `.harness/context/acceptance.md`
- `.harness/knowledge/obsidian-prd-template.md`
- LLM Wiki 检索结果
- 用户指定的 Obsidian 文件

## 流程

1. 解析需求入口：路径、PRD ID、标题或关键词。
2. 如果用户明确要求使用 LLM Wiki，则搜索相关 PRD、业务流程、术语、历史问题和接口约定。
3. 如果使用 Obsidian 文件路径，读取该 PRD，并只补充检索与本需求相关的知识。
4. 生成 `state.phase_dir/00-context-pack.md`。
5. context-pack 必须记录知识来源路径，不允许只写“来自知识库”。
6. 从 context-pack 进入 `prd-feature` 流程。
7. 先生成需求评审，不要直接写代码。
8. 方案设计后停止，等待用户确认。
9. 如果当前 run 是 `FEATURE / HIGH`，或实现会改变模块边界、接口契约、核心流程或架构风格，实施计划后生成 `state.phase_dir/10-coding-design.md`，等待用户确认编码设计。
10. 普通 `FEATURE / MEDIUM` 在 `state.phase_dir/11-development.md` 中简要记录编码思路，然后进入开发。

## Context Pack 必须包含

- 任务来源。
- PRD 摘要。
- 相关业务知识。
- 相关历史经验。
- 相关代码锚点。
- 业务不变量。
- 待确认问题。
- 风险判断。
- 知识来源。

## 禁止

- 不要扫描整个 Obsidian vault。
- 不要把 LLM Wiki 搜索结果直接当成事实，必须记录来源并综合判断。
- 不要把无关历史 run 放进 context-pack。
- 不要在 context-pack 未生成前直接进入开发。
- 不要在方案未确认前做大范围代码改动。
- 如果已经进入 `CODING_DESIGN_CONFIRMATION`，不要在编码设计未确认前做大范围代码改动。

## 用户短提示词

```text
按 knowledge-backed-prd 流程处理：
PRD：WMS-PRD-20260625-001
风险：MEDIUM
可使用我的 LLM Wiki 查询相关业务知识。
先生成 context-pack 和需求评审，不要写代码。
```
