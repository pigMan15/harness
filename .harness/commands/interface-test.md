# Command: interface-test

目的：对接口、联调场景或验收路径做可记录的验证。

## 适用场景

- 后端接口联调。
- 预发环境冒烟。
- 外部系统回传、推送、回调验证。
- 功能完成后的验收测试。

## 推荐 run

```powershell
.\.harness\scripts\new-run.ps1 -RunId "interface-test-topic-YYYYMMDD" -Intent FEATURE -Risk MEDIUM
```

只验证不改代码时可使用 `QUERY / NA`。

## 必须读取

- `.harness/agents/tester.md`
- `.harness/context/acceptance.md`
- `.harness/rules/evidence.md`
- `.harness/evals/gates.yaml`

## 流程

1. 明确测试目标、环境、接口地址、请求方法和鉴权方式。
2. 将场景写入 `state.phase_dir/17-interface-test.md`。
3. 执行请求或等价测试。
4. 记录请求摘要、响应状态、关键字段和结论。
5. 更新 `state.phase_dir/15-evidence.json`。

## 禁止

- 不要把真实 token、cookie、密钥写入产物。
- 不要只写“接口正常”，必须记录可复查证据。
- 不要在生产环境做破坏性测试。

## 用户短提示词

```text
按 interface-test 流程验证：
接口：……
环境：……
验收标准：……
```
