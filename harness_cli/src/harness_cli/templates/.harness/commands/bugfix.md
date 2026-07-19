# Command: bugfix

目的：修复明确的错误行为，并留下复现、修复和验证证据。

## 适用场景

- 页面、接口、任务或脚本行为错误。
- 已有异常日志、报错堆栈、复现步骤。
- 小范围修复或中等风险修复。

## 推荐 run

```powershell
.\.harness\scripts\new-run.ps1 -RunId "bugfix-topic-YYYYMMDD" -Intent BUG_FIX -Risk LOW
```

跨模块、影响核心链路或涉及数据时使用 `Risk MEDIUM` 或 `HIGH`。

## 必须读取

- `.harness/state.json`
- `.harness/workflow.yaml`
- `.harness/rules/code-search.md`
- `.harness/rules/build.md`
- `.harness/rules/evidence.md`

## 流程

1. 在 `state.phase_dir/00-intake.md` 记录现象、复现步骤、期望结果和实际结果。
2. 定位根因，避免只改表面症状。
3. 写入或选择一个能覆盖该 bug 的测试或验证方式。
4. 修改代码。
5. 运行聚焦测试、编译或等价检查。
6. 写入 `state.phase_dir/15-evidence.json`。
7. 生成 `state.phase_dir/18-acceptance-report.md`。

## 禁止

- 不要没有复现或证据就猜改。
- 不要扩大到无关重构。
- 不要把未运行的测试标记为 PASS。

## 用户短提示词

```text
按 bugfix 流程修复：
现象：……
复现步骤：……
期望结果：……
```
