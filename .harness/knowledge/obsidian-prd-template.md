# Obsidian PRD Template

建议每份 PRD 使用 frontmatter，方便 LLM Wiki 检索和 disambiguation。

```markdown
---
type: prd
id: WMS-PRD-YYYYMMDD-001
title: 需求标题
module: wms-rear
domain: outbound
risk: medium
status: draft
owner: pig
related:
  - "[[业务流程]]"
  - "[[接口约定]]"
  - "[[历史问题]]"
---

# 需求标题

## 背景

## 目标

## 非目标

## 用户流程

## 业务规则

## 原型/截图

## 接口与字段

## 验收标准

## 待确认问题

## 相关链接
```

## 命名建议

```text
WMS/PRD/WMS-PRD-YYYYMMDD-001-需求标题.md
```

## 使用建议

- `id` 必须稳定，后续提示词可只写 PRD ID。
- `related` 尽量链接到业务流程、术语、接口、历史问题。
- `risk` 是初始建议，harness 仍可在需求评审后调整。
