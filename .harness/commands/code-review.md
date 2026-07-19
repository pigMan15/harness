# Command: code-review

目的：以评审视角检查变更风险、缺陷、遗漏测试和回归可能。

## 适用场景

- 开发完成后自查。
- 提交前评审。
- 评审某个分支或 diff。
- 检查 AI 生成代码是否可靠。

## 推荐 run

可使用 `QUERY / NA`，因为默认只读不改代码：

```powershell
.\.harness\scripts\new-run.ps1 -RunId "review-topic-YYYYMMDD" -Intent QUERY -Risk NA
```

## 必须读取

- `.harness/rules/code-search.md`
- `.harness/evals/gates.yaml`
- 相关 diff 或变更文件

## 流程

1. 读取 diff 和相关上下文。
2. 优先找 bug、回归风险、安全风险、漏测。
3. 输出按严重程度排序的问题。
4. 每个问题必须包含文件、位置、原因和建议。
5. 将评审结果写入 `state.phase_dir/code-review.md`。

## 禁止

- 不要把风格建议放在严重问题前面。
- 不要在没有证据时断言 bug。
- 默认不直接改代码，除非用户要求进入修复流程。

## 用户短提示词

```text
按 code-review 流程评审当前改动。
重点看 bug、回归风险和测试缺口。
```
