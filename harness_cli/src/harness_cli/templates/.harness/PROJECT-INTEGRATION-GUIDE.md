# 已有工程项目集成指南

这份指南用于把当前 harness 模板接入到一个已经存在的工程项目中。目标是：不改业务代码，只增加一套 AI Coding 流程约束，让后续需求开发、修复、验证都有状态、有产物、有门禁。

## 1. 推荐目录结构

```text
your-project/
  AGENTS.md
  CLAUDE.md
  .harness/
    README.md
    TUTORIAL.md
    PROJECT-INTEGRATION-GUIDE.md
    state.json
    workflow.yaml
    agents/
    commands/
    context/
    evals/
    hooks/
    knowledge/
    phases/
    runs/
    rules/
    scripts/
    templates/
  src/
  package.json 或 pom.xml 或 pyproject.toml 等
```

`AGENTS.md` 和 `CLAUDE.md` 放在项目根目录，不放进 `.harness/`。它们是 AI 工具自动发现的入口；`.harness/` 是真正的流程工程目录。

## 2. 复制到已有工程

假设模板目录是：

```powershell
C:\Users\pig\Documents\调研1
```

已有工程目录是：

```powershell
D:\your-project
```

复制：

```powershell
cd C:\Users\pig\Documents\调研1
Copy-Item -Recurse .harness D:\your-project\.harness
Copy-Item AGENTS.md D:\your-project\AGENTS.md
Copy-Item CLAUDE.md D:\your-project\CLAUDE.md
```

如果已有工程已经有 `AGENTS.md` 或 `CLAUDE.md`，不要直接覆盖。至少合并下面这段：

```markdown
本项目使用 `.harness/` 作为 AI Coding 工程化流程。

开始非简单任务前：
1. 读取 `.harness/state.json`
2. 读取 `.harness/workflow.yaml`
3. 使用 `.harness/agents/dispatcher.md` 判断下一步
4. 阶段产物写入 `state.phase_dir`
5. 完成前按 `.harness/evals/gates.yaml` 执行门禁
6. 高风险、重构或架构/接口契约变化时，先生成 `10-coding-design.md` 并让用户确认；普通中风险细节实现不需要反复确认
```

## 3. 结构校验

PowerShell：

```powershell
cd D:\your-project
.\.harness\scripts\validate-harness.ps1
```

CMD：

```cmd
cd /d D:\your-project
.\.harness\scripts\validate-harness.cmd
```

Linux/macOS/Git Bash：

```sh
cd /path/to/your-project
chmod +x ./.harness/scripts/validate-harness.sh
./.harness/scripts/validate-harness.sh
```

看到下面输出说明结构完整：

```text
Harness 校验通过。
```

## 4. 适配构建和测试命令

编辑：

```text
.harness/rules/build.md
```

把通用说明改成项目真实命令。

Node：

```powershell
npm install
npm run build
npm test
```

pnpm：

```powershell
pnpm install
pnpm build
pnpm test
```

Java Maven：

```powershell
mvn test
mvn package
```

Python：

```powershell
pip install -r requirements.txt
pytest
```

如果项目没有测试命令，也要写清楚替代验证方式，并在 `evidence.json` 中把相关门禁标记为 `WAIVED` 或 `BLOCKED`，不要写 `PASS`。

## 5. 适配部署流程

如果项目没有部署流程，可以先不启用预发节点。日常使用时选择 `LOW` 或 `MEDIUM` 风险路径，避免走到 `PRERELEASE_DEPLOYMENT`。

如果项目有部署流程，编辑：

```text
.harness/rules/deployment.md
```

写入真实信息：

```markdown
- 预发环境：
- 部署命令：
- 版本确认方式：
- 回滚命令：
- 冒烟测试方式：
```

生产部署不要交给 AI 自动执行。生产动作应保留人工确认。

## 6. 每个需求如何开始

会产生代码改动或需要验收的任务，建议每个独立需求初始化一次 run。

普通功能：

```powershell
.\.harness\scripts\new-run.ps1 -RunId "feature-export-20260616" -Intent FEATURE -Risk MEDIUM
```

低风险 bug：

```powershell
.\.harness\scripts\new-run.ps1 -RunId "bugfix-login-20260616" -Intent BUG_FIX -Risk LOW
```

只查询：

```powershell
.\.harness\scripts\new-run.ps1 -RunId "query-auth-20260616" -Intent QUERY -Risk NA
```

初始化后会自动创建：

```text
.harness/phases/<run_id>/
.harness/runs/<run_id>/state.json
```

并写入 `.harness/state.json` 的 `phase_dir` 字段。

切换回旧 run：

```powershell
.\.harness\scripts\switch-run.ps1 -RunId "feature-export-20260616"
```

保存当前 run 状态快照：

```powershell
.\.harness\scripts\save-run.ps1
```

## 7. 日常短提示词

不用每次贴很长的流程说明。接入后可以这样说：

```text
按 harness 流程处理：
需求：这里写具体需求
类型：FEATURE
风险：MEDIUM
```

也可以直接引用常用命令：

```text
按 knowledge-backed-prd 流程处理：PRD=WMS-PRD-20260625-001，可使用我的 LLM Wiki
按 prd-feature 流程处理：PRD 在 docs/prd/xxx.md，原型在 docs/prototype/xxx.png
按 prd-quick-feature 流程处理：PRD 在 docs/prd/xxx.pdf，只做最小自检
按 bugfix 流程修复：现象是……
按 code-review 流程评审当前改动
```

## 8. 如何选择 Intent 和 Risk

Intent：

```text
QUERY       只查询、解释、定位，不改代码
BUG_FIX     修复错误行为
FEATURE     新增功能
REFACTOR    重构，不改变预期行为
DEPLOYMENT  发布或环境操作
INCIDENT    故障排查
```

Risk：

```text
NA      无改动，通常配 QUERY
LOW     单文件、小范围、容易验证
MEDIUM  跨文件、用户可见、涉及接口或流程
HIGH    数据、安全、部署、认证、迁移、支付、跨模块架构
```

## 9. 阶段产物管理

所有流程产物写入当前 run 目录，也就是 `state.json` 中 `phase_dir` 指向的位置：

```text
.harness/phases/<run_id>/
```

常见文件：

```text
00-intake.md
00-context-pack.md
01-requirement-review.md
03-solution-design.md
06-implementation-plan.md
11-development.md
12-compile.md
13-unit-test.md
15-evidence.json
18-acceptance-report.md
```

普通 `FEATURE / MEDIUM` 默认不强制生成 `10-coding-design.md`。如果任务升级为高风险、涉及重构、需要改变架构/接口契约，或用户明确要求确认编码设计，才生成 `10-coding-design.md` 并等待确认。

## 10. Git 建议

推荐提交模板文件：

```text
AGENTS.md
CLAUDE.md
.harness/README.md
.harness/TUTORIAL.md
.harness/PROJECT-INTEGRATION-GUIDE.md
.harness/workflow.yaml
.harness/rules/
.harness/agents/
.harness/context/
.harness/evals/
.harness/commands/
.harness/scripts/
.harness/templates/
```

是否提交 `.harness/state.json` 和 `.harness/phases/` 取决于团队习惯：

- 个人项目：可以提交，方便审计。
- 团队项目：建议只提交模板，不提交个人运行状态。
- 已交付需求：可以归档关键 phase 产物作为审计记录。

如果不想提交运行状态，可以在 `.gitignore` 中加入：

```gitignore
.harness/state.json
.harness/phases/*
.harness/runs/*
!.harness/phases/.gitkeep
!.harness/runs/.gitkeep
```

## 11. 接入完成检查清单

- [ ] `AGENTS.md` 位于项目根目录。
- [ ] `.harness/` 位于项目根目录。
- [ ] `validate-harness.ps1` 或对应平台脚本通过。
- [ ] `build.md` 已改成项目真实构建/测试命令。
- [ ] `deployment.md` 已写清楚部署策略，或确认暂不使用部署节点。
- [ ] 团队知道每个独立需求要新建 run。
- [ ] 高风险、重构或架构/接口契约变化前会确认 `10-coding-design.md`。
- [ ] 完成前会检查 `gates.yaml`。
