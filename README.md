# AI Coding Harness + Bridle CLI

用文件化工程流程替代临时 prompt，让 AI 辅助开发变得**可约束、可恢复、可审计、可评测**。

配套 **[Bridle](./harness_cli/)** 命令行工具提供终端看板和项目管理。

---

## 快速开始

```bash
# 安装 Bridle CLI
cd harness_cli && pip install -e .

# 接入项目
cd /path/to/your-project
bridle init

# 开始一个任务
bridle new feat-001 --intent FEATURE --risk MEDIUM

# 查看状态
bridle status

# 交互式看板
bridle
```

## Bridle 命令速查

| 命令 | 功能 |
|---|---|
| `bridle` | 启动 TUI 看板（多项目管理、键盘导航） |
| `bridle init` | 初始化 .harness/ 结构，AGS.md/CLAUDE.md 追加不覆盖 |
| `bridle new <id> -i FEATURE -r MEDIUM` | 创建新 run，自动路由必需节点 |
| `bridle status [--json]` | 查看进度、节点列表、门禁摘要 |
| `bridle validate` | 结构完整性校验（6 项检查） |
| `bridle gates [--json]` | 8 道门禁面板 |
| `bridle list` | 所有历史 runs |
| `bridle save` | 保存状态快照 |
| `bridle switch <id>` | 切换执行中的 run |
| `bridle register` | 注册项目到全局列表 |
| `bridle projects` | 查看所有已注册项目状态 |
| `bridle --lang zh` | 切换中文界面 |

## 设计原则

1. **常驻指令尽量小** — 只加载当前角色和必要规则
2. **流程状态放在对话之外** — `state.json` 是持久化事实源
3. **角色文件拆分职责** — 11 个独立角色，各司其职
4. **每阶段产出可审计文件** — 写入 `phase_dir`
5. **完成前用门禁检查** — G1-G8，失败回退

## 目录结构

```text
.harness/
  state.json              当前持久化流程状态
  state.schema.json       状态文件结构
  workflow.yaml           21 节点流程、意图/风险路由、G1-G8 门禁
  rules/                  按需加载的原子规则
  agents/                 dispatcher、评审、开发、验证等角色说明
  context/                阶段专用深层指南和模板
  phases/<run_id>/        每次运行生成的阶段产物
  runs/<run_id>/          每个 run 的 state.json 快照
  evals/                  门禁定义、评分、审计清单
  commands/               可复用命令剧本
  knowledge/              Obsidian / LLM Wiki 知识沉淀策略
  hooks/                  运行时策略示例
  templates/              可复用产物模板
harness_cli/              Bridle CLI + TUI 工具源码
```

## 标准流程

21 个节点，`workflow.yaml` 根据意图和风险自动路由：

```
QUERY（纯查询）→ 1 节点
BUG_FIX/LOW → 6 节点
BUG_FIX/HIGH → 14 节点
FEATURE/MEDIUM → 11 节点
FEATURE/HIGH → 20 节点（完整流程）
REFACTOR/MEDIUM → 9 节点
...
```

### 21 节点全览

| # | 节点 ID | 中文 | 角色 |
|---|---|---|---|
| 1 | INTAKE | 需求进入 | dispatcher |
| 2 | CONTEXT_PACK | 上下文包 | requirement-analyst |
| 3 | REQUIREMENT_REVIEW | 需求评审 | requirement-analyst |
| 4 | REQUIREMENT_CONFIRMATION | 需求确认 | orchestrator |
| 5 | SOLUTION_DESIGN | 方案设计 | tech-architect |
| 6 | SOLUTION_CONFIRMATION | 方案确认 | orchestrator |
| 7 | PRE_MORTEM | 失败预演 | quality-guardian |
| 8 | IMPLEMENTATION_PLAN | 实施计划 | plan-generator |
| 9 | ACCEPTANCE_CONFIRMATION | 验收确认 | orchestrator |
| 10 | CHANGE_REQUEST | 变更申请 | state-keeper |
| 11 | BRANCH_CREATION | 分支创建 | state-keeper |
| 12 | WORKTREE_CREATION | Worktree 创建 | state-keeper |
| 13 | CODING_DESIGN_CONFIRMATION | 编码设计确认 | developer |
| 14 | DEVELOPMENT | 开发 | developer |
| 15 | COMPILE | 编译 | verifier |
| 16 | UNIT_TEST | 单元测试 | verifier |
| 17 | ATDD | 集成测试 | verifier |
| 18 | EVIDENCE_CAPTURE | 证据采集 | verifier |
| 19 | PRERELEASE_DEPLOYMENT | 预发部署 | deployer |
| 20 | INTERFACE_TEST | 接口测试 | tester |
| 21 | ACCEPTANCE_REPORT | 验收报告 | orchestrator |

## 8 道质量门禁

| 门禁 | 含义 | 失败回退 |
|---|---|---|
| G1 | 需求和验收标准明确 | → REQUIREMENT_REVIEW |
| G2 | 有设计、风险、实施计划 | → SOLUTION_DESIGN |
| G3 | 编译/静态检查通过 | → DEVELOPMENT |
| G4 | 单元测试通过 | → DEVELOPMENT |
| G5 | 集成/场景验证 | → DEVELOPMENT |
| G6 | 证据文件完整 | → EVIDENCE_CAPTURE |
| G7 | 预发部署和接口检查 | → PRERELEASE_DEPLOYMENT |
| G8 | 验收报告完整 | → ACCEPTANCE_REPORT |

每道门禁最多自动重试 2 次，超过 → `BLOCKED`。

## 角色模型（11 角色）

`dispatcher` · `orchestrator` · `requirement-analyst` · `tech-architect` · `quality-guardian` · `plan-generator` · `developer` · `verifier` · `deployer` · `tester` · `state-keeper`

## 使用方式（AI 侧）

1. 从 `AGENTS.md` / `CLAUDE.md` 进入
2. 读取 `.harness/state.json` 和 `.harness/workflow.yaml`
3. Dispatcher 根据状态决定下一个节点和角色
4. 只加载当前角色文件，执行节点工作
5. 产物写入 `state.phase_dir`
6. 声称完成前执行 `gates.yaml` 门禁
7. 门禁失败 → 回退，最多 2 次，超过 → BLOCKED

**铁律**：源码改动 = 非简单任务，必须走 harness。任何绕过借口无效。

## 多 Run 管理

```bash
bridle list                  # 查看所有 runs
bridle save                  # 保存当前快照
bridle switch <run-id>       # 切换到历史 run
```

## 分布式接入

Bridle 支持在任意目录查看所有注册项目：

```bash
bridle register --path /path/to/project-a
bridle register --path /path/to/project-b
bridle projects              # 查看全部项目状态
bridle                       # TUI 看板，上下键切换项目
```

## 相关文档

- 接入指南：`.harness/PROJECT-INTEGRATION-GUIDE.md`
- 上手教程：`.harness/TUTORIAL.md`
- 命令索引：`.harness/commands/README.md`
- Bridle 源码：`harness_cli/`
