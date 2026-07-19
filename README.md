# AI Coding Harness + Bridle CLI<br><small>AI 编码 Harness + Bridle CLI</small>

**EN** — Replace ad-hoc prompts with a file-based engineering workflow. AI-assisted development becomes **constrained, recoverable, auditable, and measurable**.

**ZH** — 用文件化工程流程替代临时 prompt，让 AI 辅助开发变得**可约束、可恢复、可审计、可评测**。

The companion **[Bridle](./harness_cli/)** CLI provides a terminal dashboard and project management.<br>
配套 **[Bridle](./harness_cli/)** 命令行工具提供终端看板和项目管理。

---

## Quick Start / 快速开始

```bash
# Install Bridle CLI / 安装 Bridle CLI
cd harness_cli && pip install -e .

# Initialize a project / 接入项目
cd /path/to/your-project
bridle init

# Start a task / 开始一个任务
bridle new feat-001 --intent FEATURE --risk MEDIUM

# Check status / 查看状态
bridle status

# Interactive TUI dashboard / 交互式看板
bridle
```

## Bridle Commands / 命令速查

| Command / 命令 | Description / 功能 |
|---|---|
| `bridle` | Launch TUI dashboard (multi-project, keyboard nav) / 启动 TUI 看板（多项目管理、键盘导航） |
| `bridle init` | Initialize `.harness/` structure, append to AGENTS.md/CLAUDE.md / 初始化 .harness/ 结构，追加不覆盖 |
| `bridle new <id> -i FEATURE -r MEDIUM` | Create a new run with auto-routed required nodes / 创建新 run，自动路由必需节点 |
| `bridle status [--json]` | View progress, node list, gate summary / 查看进度、节点列表、门禁摘要 |
| `bridle validate` | Structural integrity check (6 checks) / 结构完整性校验（6 项检查） |
| `bridle gates [--json]` | 8-gate quality panel / 8 道门禁面板 |
| `bridle list` | List all historical runs / 所有历史 runs |
| `bridle save` | Save state snapshot / 保存状态快照 |
| `bridle switch <id>` | Switch active run / 切换执行中的 run |
| `bridle register` | Register project to global list / 注册项目到全局列表 |
| `bridle projects` | View all registered project statuses / 查看所有已注册项目状态 |
| `bridle --lang zh` | Switch to Chinese UI / 切换中文界面 |

## Design Principles / 设计原则

| # | EN | ZH |
|---|---|---|
| 1 | **Minimal always-on instructions** — load only the current role and needed rules | **常驻指令尽量小** — 只加载当前角色和必要规则 |
| 2 | **State lives outside the conversation** — `state.json` is the persistent source of truth | **流程状态放在对话之外** — `state.json` 是持久化事实源 |
| 3 | **Role files split responsibilities** — 11 independent roles, each with a clear job | **角色文件拆分职责** — 11 个独立角色，各司其职 |
| 4 | **Every phase produces auditable artifacts** — written to `phase_dir` | **每阶段产出可审计文件** — 写入 `phase_dir` |
| 5 | **Gates check before claiming done** — G1–G8, retry on failure | **完成前用门禁检查** — G1-G8，失败回退 |

## Directory Structure / 目录结构

```text
.harness/
  state.json              Current persistent workflow state / 当前持久化流程状态
  state.schema.json       State file schema / 状态文件结构
  workflow.yaml           21-node flow, intent/risk routing, G1–G8 gates / 21 节点流程、意图/风险路由、G1-G8 门禁
  rules/                  Atomic rules loaded on demand / 按需加载的原子规则
  agents/                 Dispatcher, reviewer, developer, verifier, etc. / 各角色说明
  context/                Phase-specific deep guides and templates / 阶段专用深层指南和模板
  phases/<run_id>/        Phase artifacts generated per run / 每次运行生成的阶段产物
  runs/<run_id>/          Snapshot of state.json per run / 每个 run 的 state.json 快照
  evals/                  Gate definitions, scoring, audit checklists / 门禁定义、评分、审计清单
  commands/               Reusable command playbooks / 可复用命令剧本
  knowledge/              Obsidian / LLM Wiki knowledge retention / 知识沉淀策略
  hooks/                  Runtime policy examples / 运行时策略示例
  templates/              Reusable artifact templates / 可复用产物模板
harness_cli/              Bridle CLI + TUI tool source / Bridle CLI + TUI 工具源码
```

## Standard Workflow / 标准流程

**EN** — 21 nodes in total. `workflow.yaml` auto-routes based on intent and risk.

**ZH** — 21 个节点，`workflow.yaml` 根据意图和风险自动路由：

```
QUERY          → 1 node
BUG_FIX/LOW    → 6 nodes
BUG_FIX/HIGH   → 14 nodes
FEATURE/MEDIUM → 11 nodes
FEATURE/HIGH   → 20 nodes (full pipeline / 完整流程)
REFACTOR/MEDIUM → 9 nodes
...
```

### All 21 Nodes / 21 节点全览

| # | Node ID | EN | ZH | Role / 角色 |
|---|---|---|---|---|
| 1 | INTAKE | Intake | 需求进入 | dispatcher |
| 2 | CONTEXT_PACK | Context Pack | 上下文包 | requirement-analyst |
| 3 | REQUIREMENT_REVIEW | Requirement Review | 需求评审 | requirement-analyst |
| 4 | REQUIREMENT_CONFIRMATION | Requirement Confirmation | 需求确认 | orchestrator |
| 5 | SOLUTION_DESIGN | Solution Design | 方案设计 | tech-architect |
| 6 | SOLUTION_CONFIRMATION | Solution Confirmation | 方案确认 | orchestrator |
| 7 | PRE_MORTEM | Pre-Mortem | 失败预演 | quality-guardian |
| 8 | IMPLEMENTATION_PLAN | Implementation Plan | 实施计划 | plan-generator |
| 9 | ACCEPTANCE_CONFIRMATION | Acceptance Confirmation | 验收确认 | orchestrator |
| 10 | CHANGE_REQUEST | Change Request | 变更申请 | state-keeper |
| 11 | BRANCH_CREATION | Branch Creation | 分支创建 | state-keeper |
| 12 | WORKTREE_CREATION | Worktree Creation | Worktree 创建 | state-keeper |
| 13 | CODING_DESIGN_CONFIRMATION | Coding Design Confirmation | 编码设计确认 | developer |
| 14 | DEVELOPMENT | Development | 开发 | developer |
| 15 | COMPILE | Compile | 编译 | verifier |
| 16 | UNIT_TEST | Unit Test | 单元测试 | verifier |
| 17 | ATDD | ATDD / Integration Test | 集成测试 | verifier |
| 18 | EVIDENCE_CAPTURE | Evidence Capture | 证据采集 | verifier |
| 19 | PRERELEASE_DEPLOYMENT | Prerelease Deployment | 预发部署 | deployer |
| 20 | INTERFACE_TEST | Interface Test | 接口测试 | tester |
| 21 | ACCEPTANCE_REPORT | Acceptance Report | 验收报告 | orchestrator |

## 8 Quality Gates / 8 道质量门禁

| Gate / 门禁 | Meaning / 含义 | On Failure / 失败回退 |
|---|---|---|
| G1 | Requirements and acceptance criteria are clear / 需求和验收标准明确 | → REQUIREMENT_REVIEW |
| G2 | Design, risks, and implementation plan exist / 有设计、风险、实施计划 | → SOLUTION_DESIGN |
| G3 | Compile / static check passes / 编译/静态检查通过 | → DEVELOPMENT |
| G4 | Unit tests pass / 单元测试通过 | → DEVELOPMENT |
| G5 | Integration / scenario validation / 集成/场景验证 | → DEVELOPMENT |
| G6 | Evidence file is complete / 证据文件完整 | → EVIDENCE_CAPTURE |
| G7 | Prerelease deployment and interface check / 预发部署和接口检查 | → PRERELEASE_DEPLOYMENT |
| G8 | Acceptance report is complete / 验收报告完整 | → ACCEPTANCE_REPORT |

**EN** — Each gate auto-retries up to 2 times. Exceeding → `BLOCKED`.

**ZH** — 每道门禁最多自动重试 2 次，超过 → `BLOCKED`。

## Role Model / 角色模型 (11 roles / 角色)

`dispatcher` · `orchestrator` · `requirement-analyst` · `tech-architect` · `quality-guardian` · `plan-generator` · `developer` · `verifier` · `deployer` · `tester` · `state-keeper`

## AI-Side Usage / 使用方式（AI 侧）

1. Enter from `AGENTS.md` / `CLAUDE.md` / 从入口文件进入
2. Read `.harness/state.json` and `.harness/workflow.yaml` / 读取状态和工作流
3. Dispatcher decides next node and role based on state / Dispatcher 根据状态决定下一个节点和角色
4. Load only the current role file, execute node work / 只加载当前角色文件，执行节点工作
5. Write artifacts to `state.phase_dir` / 产物写入阶段目录
6. Execute `gates.yaml` gates before claiming done / 声称完成前执行门禁
7. Gate failure → rollback, max 2 retries, exceeding → BLOCKED / 门禁失败 → 回退，最多 2 次，超过 → BLOCKED

**Iron Rule / 铁律**: Source code changes = non-trivial task, MUST go through harness. No bypass excuses are valid.<br>
**源码改动 = 非简单任务，必须走 harness。任何绕过借口无效。**

## Multi-Run Management / 多 Run 管理

```bash
bridle list                  # List all runs / 查看所有 runs
bridle save                  # Save current snapshot / 保存当前快照
bridle switch <run-id>       # Switch to historical run / 切换到历史 run
```

## Distributed Access / 分布式接入

**EN** — Bridle supports viewing all registered projects from any directory.

**ZH** — Bridle 支持在任意目录查看所有注册项目：

```bash
bridle register --path /path/to/project-a
bridle register --path /path/to/project-b
bridle projects              # View all project statuses / 查看全部项目状态
bridle                       # TUI dashboard, ↑↓ to switch projects / TUI 看板，上下键切换项目
```

## Building & Releasing / 发布 Bridle 二进制

```bash
cd harness_cli

# 1. Install build dependency / 安装构建依赖
pip install pyinstaller

# 2. Build single-file exe / 构建单文件 exe
python -m PyInstaller bridle.spec --clean --noconfirm

# 3. Output (stable name for PATH) / 产物 (稳定文件名，方便加入 PATH)
ls -lh dist/bridle.exe            # ~15MB, no Python required / 无需 Python 环境

# 4. Versioned copy for GitHub Release / GitHub Release 时复制为版本化文件名
copy dist\bridle.exe dist\bridle-v0.1.0.exe
```

### Add to System PATH / 设置到系统 PATH

```powershell
# Copy to a fixed directory (no version in path, permanently stable)
# 复制到固定目录（不用版本号，永久稳定）
mkdir C:\Users\<user>\bridle
copy dist\bridle.exe C:\Users\<user>\bridle\

# Add to user PATH (Admin PowerShell)
# 添加到用户 PATH（管理员 PowerShell）
[Environment]::SetEnvironmentVariable(
    "Path",
    $env:Path + ";C:\Users\<user>\bridle",
    [EnvironmentVariableTarget]::User
)

# Restart terminal, then available globally / 重启终端后即可全局使用
bridle --version
bridle status
bridle                    # TUI dashboard / TUI 看板
```

## Versioning / 版本管理

| Version Line / 版本线 | Location / 位置 | Description / 说明 |
|---|---|---|
| CLI Version / CLI 版本 | `pyproject.toml` → `version` | Semantic versioning / 语义化版本 (0.1.0) |
| Schema Version / Schema 版本 | `state.json` → `schema_version` | Bump on structural incompatibility / 结构不兼容时升级 (1.0) |
| Release Cadence / 发版节奏 | 0.x rapid iteration → 1.0 stable / 0.x 快速迭代 → 1.0 稳定 | MAJOR.MINOR.PATCH |

### Release Checklist / 发版 checklist

1. Update `pyproject.toml` version / 更新版本号
2. Update `bridle.spec` output name `bridle-vX.Y.Z` / 更新输出文件名
3. Run `pytest tests/` — all tests pass / 确保测试全通过
4. Run `bridle validate` — structure check passes / 确保结构校验通过
5. Update `CHANGELOG.md` / 更新变更日志
6. Build binary: `python -m PyInstaller bridle.spec --clean --noconfirm` / 构建二进制
7. Test binary: `dist/bridle-vX.Y.Z.exe status` / 测试二进制
8. Git tag + push + GitHub Release

## Related Docs / 相关文档

| Doc / 文档 | Path / 位置 |
|---|---|
| Integration Guide / 接入指南 | `.harness/PROJECT-INTEGRATION-GUIDE.md` |
| Tutorial / 上手教程 | `.harness/TUTORIAL.md` |
| Command Index / 命令索引 | `.harness/commands/README.md` |
| Bridle Source / Bridle 源码 | `harness_cli/` |
