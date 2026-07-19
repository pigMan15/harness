# Command: promote-learning

目的：从已完成或部分完成的 run 中提炼长期有价值的“增量工程知识”，生成可写入 Obsidian / LLM Wiki 的沉淀草稿。

它不是总结 PRD，也不是搬运 phase。它只提炼相对原始 PRD / context-pack 新增的内容。

## 适用场景

- 一个需求开发完成后。
- 一次 bug 修复暴露了可复用经验。
- 编译、测试、部署出现了重复问题。
- evidence/report 中出现了下次可复用的结论。

## 必须读取

- `.harness/state.json`
- `.harness/knowledge/promotion-policy.md`
- `state.phase_dir/00-context-pack.md`，如果存在
- `state.phase_dir/15-evidence.json`
- `state.phase_dir/18-acceptance-report.md`，如果存在

按需读取：

- `state.phase_dir/01-requirement-review.md`
- `state.phase_dir/03-solution-design.md`
- `state.phase_dir/11-development.md`
- `state.phase_dir/12-compile.md`
- `state.phase_dir/13-unit-test.md`
- 相关代码 diff

## 流程

1. 读取 context-pack，明确原始 PRD / 知识输入已经包含什么。
2. 读取 evidence 和 acceptance report。
3. 对比“原始输入”和“实际开发结果”，只寻找增量工程知识。
4. 判断每条候选知识是否可复用、是否有证据。
5. 生成 `state.phase_dir/19-knowledge-promotion.md`。
6. 输出建议写入位置，例如 Obsidian 的业务流程、历史问题、接口约定、架构决策。
7. 等用户确认后，再写入长期知识库；默认不直接写回 Obsidian 或 LLM Wiki。

## 输出格式

```markdown
# 知识沉淀草稿

## 来源

- RunId:
- Intent:
- Risk:
- Phase dir:
- 原始 PRD / context-pack:

## 候选知识

| 类型 | 标题 | 相对 PRD 的新增点 | 证据 | 建议位置 |
| --- | --- | --- | --- | --- |
| case | | | | |

## 不建议沉淀的内容

列出不沉淀的内容和原因，尤其是 PRD 已经明确写过的内容。

## 待用户确认

- 
```

## 禁止

- 不要重复总结 PRD 已有内容。
- 不要把未验证猜测写成知识。
- 不要自动写入长期知识库。
- 不要沉淀 token、cookie、密钥、用户隐私。
- 不要把一次性命令输出当成长期规则。

## 用户短提示词

```text
按 promote-learning 流程总结当前 run，只提炼相对 PRD 新增的工程知识，生成知识库沉淀草稿，不要直接写回 Obsidian。
```
