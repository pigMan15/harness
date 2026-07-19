# Command: refactor

目的：在不改变预期行为的前提下改善结构、性能、可读性或可维护性。

## 适用场景

- 消除重复代码。
- 拆分过大的函数或类。
- 优化查询、循环或数据组装路径。
- 改善命名和边界。

## 推荐 run

```powershell
.\.harness\scripts\new-run.ps1 -RunId "refactor-topic-YYYYMMDD" -Intent REFACTOR -Risk MEDIUM
```

小范围单文件重构可使用 `LOW`；核心链路或跨模块重构使用 `HIGH`。

## 必须读取

- `.harness/rules/code-search.md`
- `.harness/rules/build.md`
- `.harness/context/tdd.md`
- `.harness/rules/evidence.md`

## 流程

1. 在 `state.phase_dir/00-intake.md` 写清楚重构目标和不变行为。
2. 在 `state.phase_dir/06-implementation-plan.md` 写小步计划。
3. 修改前确认现有测试或补充保护性测试。
4. 小步改动，避免混入功能变化。
5. 运行编译和相关测试。
6. 在 `state.phase_dir/11-development.md` 记录结构变化。
7. 在 `state.phase_dir/15-evidence.json` 记录验证结果。

## 禁止

- 不要借重构改变业务语义。
- 不要同时做无关格式化。
- 不要在验证阻塞时声称重构安全。

## 用户短提示词

```text
按 refactor 流程处理：
目标：……
不允许改变的行为：……
```
