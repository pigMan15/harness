# Harness 使用教程

这套模板的用法可以理解成一句话：让 AI 不直接“凭感觉干活”，而是先读状态、选流程、产出阶段文件、跑门禁，再报告结果。

## 0. 三个入口

- `AGENTS.md`：Codex 使用的主入口。
- `CLAUDE.md`：Claude Code 使用的主入口。
- `.harness/`：真正的流程工程文件目录。

日常只需要记住：

```text
先读 AGENTS.md
再读 .harness/state.json
再读 .harness/workflow.yaml
使用 dispatcher 判断下一步
产物写入 state.phase_dir
完成前跑 gates
```

## 1. 初始化一次运行

PowerShell：

```powershell
.\.harness\scripts\new-run.ps1 -RunId "feature-demo-001" -Intent FEATURE -Risk HIGH
```

Windows 命令提示符：

```cmd
.\.harness\scripts\new-run.cmd -RunId "feature-demo-001" -Intent FEATURE -Risk HIGH
```

Linux/macOS/Git Bash：

```sh
chmod +x ./.harness/scripts/new-run.sh
./.harness/scripts/new-run.sh feature-demo-001 FEATURE HIGH
```

初始化会自动创建：

```text
.harness/phases/feature-demo-001/
.harness/runs/feature-demo-001/state.json
```

并在 `.harness/state.json` 中写入：

```json
"phase_dir": ".harness/phases/feature-demo-001"
```

## 2. Intent 和 Risk

Intent：

```text
QUERY       只查询，不改代码
BUG_FIX     修 bug
FEATURE     做新功能
REFACTOR    重构
DEPLOYMENT  发布或环境操作
INCIDENT    故障排查
```

Risk：

```text
NA      无改动，通常用于 QUERY
LOW     单文件、小范围、容易验证
MEDIUM  跨文件、用户可见、涉及接口或流程
HIGH    数据、安全、部署、认证、迁移、支付、跨模块架构
```

## 3. 常用场景命令

`.harness/commands/` 下提供了场景说明。你可以直接引用命令名：

```text
按 knowledge-backed-prd 流程处理：PRD=WMS-PRD-20260625-001，可使用我的 LLM Wiki
按 prd-feature 流程处理：PRD 在 docs/prd/xxx.md，原型在 docs/prototype/xxx.png
按 prd-quick-feature 流程处理：PRD 在 docs/prd/xxx.pdf，只做最小自检
按 bugfix 流程修复：现象是……
按 refactor 流程处理：目标是……
按 code-review 流程评审当前改动
按 interface-test 流程验证：接口是……
按 release-check 流程处理：环境是预发，版本是……
按 incident 流程排查：现象是……
```

命令索引见：

```text
.harness/commands/README.md
```

如果 PRD 在 Obsidian 或已经被 LLM Wiki 索引，优先使用 `knowledge-backed-prd`。它会先生成 `state.phase_dir/00-context-pack.md`，再进入需求评审。

## 4. 从 PRD/原型开始做功能

初始化：

```powershell
.\.harness\scripts\new-run.ps1 -RunId "feature-wms-flow-20260616" -Intent FEATURE -Risk MEDIUM
```

对 Codex 说：

```text
按 prd-feature 流程处理：
PRD：docs/prd/xxx.md
原型：docs/prototype/xxx.png
目标：……
```

常见产物：

```text
00-context-pack.md
00-intake.md
01-requirement-review.md
03-solution-design.md
06-implementation-plan.md
11-development.md
12-compile.md
13-unit-test.md
15-evidence.json
18-acceptance-report.md
```

普通 `FEATURE / MEDIUM` 默认不强制生成 `10-coding-design.md`。如果任务升级为高风险、涉及架构/接口契约变化，或你明确要求确认编码设计，才会生成 `10-coding-design.md` 并等待确认。

这些文件都应写入 `state.phase_dir`，例如：

```text
.harness/phases/feature-wms-flow-20260616/01-requirement-review.md
```

## 5. 修 bug

初始化：

```powershell
.\.harness\scripts\new-run.ps1 -RunId "bugfix-login-20260616" -Intent BUG_FIX -Risk LOW
```

对 Codex 说：

```text
按 bugfix 流程修复：
现象：……
复现步骤：……
期望结果：……
```

LOW bug 通常走：

```text
INTAKE
DEVELOPMENT
COMPILE
UNIT_TEST
EVIDENCE_CAPTURE
ACCEPTANCE_REPORT
```

## 6. 继续一个中断的 run

如果中间做过其他 run，先切回目标 run。

PowerShell：

```powershell
.\.harness\scripts\switch-run.ps1 -RunId "feature-demo-001"
```

CMD：

```cmd
.\.harness\scripts\switch-run.cmd -RunId "feature-demo-001"
```

Linux/macOS/Git Bash：

```sh
chmod +x ./.harness/scripts/switch-run.sh
./.harness/scripts/switch-run.sh feature-demo-001
```

如果当前 run 的状态发生变化，可以保存快照：

```powershell
.\.harness\scripts\save-run.ps1
```

最短提示词：

```text
按当前 harness run 继续，从 state.json 和 state.phase_dir 恢复上下文。
```

更完整一点：

```text
恢复当前 harness run：
1. 读取 .harness/state.json
2. 读取 .harness/workflow.yaml
3. 读取 state.phase_dir 下已有阶段产物
4. 使用 dispatcher 判断下一步
5. 从下一步继续，产物仍写入 state.phase_dir
```

## 7. 门禁怎么看

门禁定义在：

```text
.harness/evals/gates.yaml
```

核心含义：

```text
G1_REQUIREMENTS  需求和验收是否清晰
G2_DESIGN        方案、风险、回滚、计划是否齐
G3_COMPILE       编译或静态检查是否通过
G4_UNIT_TEST     单测是否通过
G5_ATDD          集成或场景验证是否通过
G6_EVIDENCE      证据是否完整
G7_PRERELEASE    预发和接口检查是否完成
G8_ACCEPTANCE    验收报告是否完整
```

不能执行的门禁不要写 PASS，应写：

```text
WAIVED   有原因的豁免
BLOCKED  因环境、凭证、依赖等无法执行
FAIL     执行了但失败
```

## 8. 结构校验

PowerShell：

```powershell
.\.harness\scripts\validate-harness.ps1
```

CMD：

```cmd
.\.harness\scripts\validate-harness.cmd
```

Linux/macOS/Git Bash：

```sh
chmod +x ./.harness/scripts/validate-harness.sh
./.harness/scripts/validate-harness.sh
```

看到下面输出说明结构完整：

```text
Harness 校验通过。
```

## 9. 什么时候不用完整流程

这些情况不需要完整 21 节点：

- 只是问一个代码位置。
- 只是解释一段代码。
- 只是查看日志或配置。
- 修改 README 中一处错字。
- 临时草稿或探索性问题。

这些用 `QUERY / NA` 或 `BUG_FIX / LOW` 就够了。
