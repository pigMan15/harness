# Command: release-check

目的：在预发或发布前检查部署、回滚、冒烟和证据。

## 适用场景

- 预发部署验证。
- 发布前检查。
- 发布后冒烟。
- 需要明确回滚策略的变更。

## 推荐 run

```powershell
.\.harness\scripts\new-run.ps1 -RunId "release-topic-YYYYMMDD" -Intent DEPLOYMENT -Risk HIGH
```

## 必须读取

- `.harness/rules/deployment.md`
- `.harness/rules/safety.md`
- `.harness/context/release.md`
- `.harness/evals/gates.yaml`

## 流程

1. 确认目标环境，不默认生产。
2. 记录版本、commit、配置变更和影响范围。
3. 确认回滚路径。
4. 部署前检查必需门禁是否满足。
5. 执行预发部署或记录人工部署结果。
6. 执行冒烟或接口测试。
7. 写入 `state.phase_dir/16-prerelease-deployment.md` 和 `state.phase_dir/17-interface-test.md`。

## 禁止

- 不要自主执行生产发布。
- 不要没有回滚策略就推进高风险发布。
- 不要把“命令已提交”当成“部署成功”。

## 用户短提示词

```text
按 release-check 流程处理：
环境：预发
版本：……
验证目标：……
```
