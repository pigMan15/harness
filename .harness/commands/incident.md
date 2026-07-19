# Command: incident

目的：对故障或异常现象进行只读排查，必要时转入 bugfix。

## 适用场景

- 线上或预发异常。
- 日志告警。
- 用户反馈无法复现。
- 需要判断是否真实 bug。

## 推荐 run

```powershell
.\.harness\scripts\new-run.ps1 -RunId "incident-topic-YYYYMMDD" -Intent INCIDENT -Risk MEDIUM
```

生产核心链路或数据风险使用 `HIGH`。

## 必须读取

- `.harness/context/incident-query.md`
- `.harness/rules/evidence.md`
- `.harness/rules/safety.md`

## 流程

1. 在 `state.phase_dir/00-intake.md` 记录现象、时间窗口、影响范围和已知线索。
2. 只读排查日志、配置、代码和数据流。
3. 记录证据，不做破坏性操作。
4. 判断是否为 bug、配置问题、数据问题、环境问题或误报。
5. 如果需要改代码，停止并建议转入 `bugfix` 流程。

## 禁止

- 不要在 incident 流程中直接改代码。
- 不要执行数据修复、删除、迁移等动作。
- 不要泄露敏感日志、token 或用户隐私。

## 用户短提示词

```text
按 incident 流程排查：
现象：……
时间窗口：……
影响范围：……
```
