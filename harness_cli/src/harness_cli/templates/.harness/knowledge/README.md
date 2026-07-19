# Knowledge Layer

这一层用于连接 Obsidian、LLM Wiki 和 harness。

核心原则：

```text
Obsidian / LLM Wiki 是长期知识源
context-pack 是本次 run 的冻结上下文
harness phases 是本次执行过程
promotion 是 run 完成后的知识反哺
```

## 推荐链路

```text
PRD / 原型 / Obsidian 笔记 / LLM Wiki 检索结果
        ↓
state.phase_dir/00-context-pack.md
        ↓
需求评审 / 方案设计 / 实施计划
        ↓
开发 / 验证 / 验收报告
        ↓
知识沉淀草稿
```

## 使用边界

- 不要让 AI 每次自由扫描整个 Obsidian vault。
- 不要把 LLM Wiki 检索结果直接当成开发结论。
- 先生成 `00-context-pack.md`，后续阶段优先读取它。
- 只把长期有价值的经验沉淀回知识库。
- 写回 Obsidian 或 LLM Wiki 前应先生成草稿并让用户确认。

## 本目录文件

- `context-pack-template.md`：本次 run 的上下文包模板。
- `obsidian-prd-template.md`：建议的 Obsidian PRD 模板。
- `promotion-policy.md`：什么值得沉淀、沉淀到哪里。
