# 方案设计：Harness CLI + TUI 工具

## 1. 概述

为 Harness 框架构建 Python CLI + TUI 工具，替代现有 PowerShell/CMD/Shell 脚本，提供终端交互式仪表盘。

**语言**：Python 3.11+
**核心框架**：Typer（CLI）+ Rich（美化）+ Textual（TUI）
**打包**：PyInstaller → 单文件可执行
**品牌**：Bridle（缰绳）—— 给 AI 开发上缰绳
**版本**：语义化版本，CLI 版本与 Harness Schema 版本独立

## 2. 品牌与版本

### 2.1 品牌标识

**名称**：Bridle — 取自 Harness（马具/约束装置）的隐喻：给 AI 辅助开发套上缰绳，有方向、有边界。

**配色**：

| 角色 | 色值 | 终端映射 | 用途 |
|---|---|---|---|
| 主色 | `#7C3AED` | `purple` | 品牌、标题、当前节点 |
| 辅助色 | `#06B6D4` | `cyan` | 流程线、进度条、链接 |
| 成功 | `#22C55E` | `green` | PASS、完成节点 |
| 警告 | `#EAB308` | `yellow` | WAIVED、进行中 |
| 错误 | `#EF4444` | `red` | FAIL、阻断 |
| 弱化 | `#71717A` | `dim italic` | 未开始、不要求 |

**TUI 启动画面**（80 列终端）：

```
  ╔══════════════════════════════════════════════╗
  ║                                              ║
  ║    ═══╗  ╔═══  ╔═══╗  ╔══╗  ╔══╗  ╔═══╗    ║
  ║     ╔╝  ║     ║   ║  ║      ║  ║  ║         ║
  ║     ║   ╠═══  ╠═══╝  ╠══╗   ║  ║  ╚═══╗     ║
  ║     ║   ║     ║  ╲   ║  ║   ║  ║      ║     ║
  ║    ═╝   ╚═══  ║  ╲╲  ╚══╝   ╚══╝  ╚═══╝     ║
  ║                                              ║
  ║         AI Coding Harness                    ║
  ║         v0.1.0  ·  schema 1.0                ║
  ╚══════════════════════════════════════════════╝
```

**小型标识**（status 等单次命令）：

```
╭─ Bridle ────────────────────────────────────╮
│  harness v0.1.0                             │
╰─────────────────────────────────────────────╯
```

### 2.2 版本策略

**双版本线分离**：

```
CLI 工具版本（pyproject.toml）     Harness Schema 版本（state.json / workflow.yaml）
─────────────────────────────────────────────────────────────────────────────────
 遵循 semver                        不频繁变动
 0.1.0 → 0.2.0 → 1.0.0            只在结构不兼容时升级
 一个 CLI 可兼容多个 Schema          现有 schema_version: "1.0"
```

**`harness --version` 输出**：

```
bridle v0.1.0  (harness schema: 1.0)
Python 3.11  ·  Textual 0.50  ·  Rich 13.0
```

**发版节奏**：

```
0.1.0   MVP：init / new / status / validate / switch / list / gates / save
0.2.0   完善 TUI 交互 + 错误处理 + 测试覆盖
0.3.0   打包优化 + 安装文档
1.0.0   稳定 API，CLI 接口向后兼容
```

## 3. 设计原则

1. **core/ 纯逻辑层独立** — 不依赖终端或 Web，CLI、TUI、未来 Web UI 共享
2. **不加参数进 TUI** — `harness` 回车进仪表盘，加参数执行单次命令（类似 `gitk` vs `git status`）
3. **零破坏** — 不修改现有 `.harness/` 模板文件，不改变 `state.json` / `workflow.yaml` schema
4. **只做确定性事务** — CLI 负责状态管理、校验、展示；AI 仍然负责需求理解、代码实现、评审

## 4. 项目结构

```
harness/                          # 仓库根
├── .harness/                     # 现有模板（不修改）
├── harness_cli/                  # Python 包
│   ├── pyproject.toml
│   └── src/harness_cli/
│       ├── __init__.py
│       ├── main.py               # Typer 入口
│       ├── app.py                # Textual TUI App
│       ├── core/                 # 纯逻辑层（无终端依赖）
│       │   ├── __init__.py
│       │   ├── state.py          # state.json 读写 + 校验
│       │   ├── workflow.py       # workflow.yaml 解析 + 路由
│       │   ├── gates.py          # 门禁评估引擎
│       │   └── validate.py       # 结构完整性校验
│       ├── commands/             # CLI 子命令（调用 core/）
│       │   ├── __init__.py
│       │   ├── new_run.py
│       │   ├── status_cmd.py
│       │   ├── validate_cmd.py
│       │   ├── switch_run.py
│       │   ├── list_runs.py
│       │   ├── gates_cmd.py
│       │   └── save_run.py
│       └── ui/                   # 展示层
│           ├── __init__.py
│           ├── dashboard.py      # TUI 主仪表盘
│           ├── console.py        # Rich 单次输出（status/gates）
│           └── widgets/          # Textual 自定义组件
│               ├── __init__.py
│               ├── workflow_tree.py
│               ├── gates_grid.py
│               ├── runs_list.py
│               └── artifact_panel.py
└── README.md
```

## 5. `harness init` 接入流程

### 5.1 入口检测逻辑

```
harness init 执行流程：

1. 检测目标目录
   ├── 没有 .harness/ 目录 → 新项目初始化
   ├── 已有 .harness/ 目录 → 已有项目检查（默认不修改文件）
   └── 目录不存在 → 报错退出

2. 新项目初始化：
   ├── 扫描目标目录已有文件
   ├── 按规则处理 AGENTS.md / CLAUDE.md（见 4.2）
   ├── 复制 .harness/ 模板结构
   ├── 输出创建文件列表
   └── 运行 validate 确认结构完整
```

### 5.2 AGENTS.md / CLAUDE.md 合并策略

这是 `init` 最关键的兼容性逻辑。核心原则：**不覆盖用户已有内容，只追加 harness 入口块**。

```
harness init 检测到的状态              处理方式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENTS.md 不存在 + CLAUDE.md 不存在    从模板创建两个文件
AGENTS.md 已存在 + CLAUDE.md 不存在    追加到 AGENTS.md + 创建 CLAUDE.md
AGENTS.md 不存在 + CLAUDE.md 已存在    创建 AGENTS.md + 追加到 CLAUDE.md
两者都已存在                           追加到两者
两者都已存在且已包含 harness 标记块    跳过，不重复追加（幂等）
```

**追加内容**是一个带标记的固定块：

```markdown
<!-- HARNESS-ENTRY:START — do not edit this block manually -->
## AI Coding Harness

本项目使用 `.harness/` 作为 AI Coding 工程化流程。

开始非简单任务前：
1. 读取 `.harness/state.json`
2. 读取 `.harness/workflow.yaml`
3. 使用 `.harness/agents/dispatcher.md` 判断下一步
4. 阶段产物写入 `state.phase_dir`
5. 完成前按 `.harness/evals/gates.yaml` 执行门禁
6. 高风险、重构或架构/接口契约变化时，先生成 `10-coding-design.md` 并让用户确认

写入前必须先判断产物类型：源码写入目标源码仓库；流程产物只写入当前 `state.phase_dir`。
<!-- HARNESS-ENTRY:END -->
```

**幂等性保障**：`harness init` 追加前先扫描文件是否已包含 `<!-- HARNESS-ENTRY:START -->` 标记，如果已经存在则跳过，不会重复追加。

**`--force` 行为**：`harness init --force` 不跳过已有标记，而是**替换**旧的 harness 入口块为新版本（标记块之间的内容整体替换），用户自己写的内容完全不受影响。

### 5.3 `harness init` 命令接口

| 命令 | 作用 |
|---|---|
| `harness init` | 交互式，自动检测场景，新项目提示确认 |
| `harness init --force` | 跳过确认；已有标记块则更新到最新版本 |
| `harness init --dry-run` | 预览会创建/修改的文件列表，不实际写入 |
| `harness init --repair` | 已有项目：只补全缺失的模板文件，不覆盖已有文件 |
| `harness init --no-validate` | 初始化完成后跳过结构校验 |

### 5.4 交互示例

**新项目：**
```
╭─ Harness Init ───────────────────────────────────────────╮
│  Directory: /home/user/my-new-project                    │
│  Status: No .harness/ found                              │
│                                                          │
│  Will create:                                            │
│    .harness/     (full template: ~50 files)              │
│  Will append to:                                         │
│    AGENTS.md     (add harness entry block)               │
│  Will create:                                            │
│    CLAUDE.md     (harness entry point)                   │
│                                                          │
│  Proceed? [Y/n]                                          │
╰──────────────────────────────────────────────────────────╯
```

**已有 `.harness/` 的项目：**
```
╭─ Harness Init ───────────────────────────────────────────╮
│  Directory: /home/user/old-project                       │
│  Status: .harness/ already exists                        │
│  Active run: feature-export-001 (DEVELOPING)             │
│                                                          │
│  Run 'harness validate' to check structure health.       │
│  Use 'harness init --repair' to fix missing files.       │
╰──────────────────────────────────────────────────────────╯
```

## 6. CLI 命令接口（除 init 外）

| 命令 | 参数 | 功能 | 退出码 |
|---|---|---|---|
| `harness` | 无 | 启动 TUI 仪表盘 | 0 |
| `harness new <run-id>` | `--intent` `--risk` | 创建新 run | 0/1 |
| `harness status` | `--json` | 当前 run 状态摘要 | 0/1 |
| `harness validate` | `--strict` | 结构完整性校验 | 0/1 |
| `harness switch <run-id>` | 无 | 切换到历史 run | 0/1 |
| `harness save` | 无 | 保存状态快照 | 0/1 |
| `harness list` | `--status` `--intent` | 列出所有 runs | 0 |
| `harness gates` | `--gate <id>` `--json` | 门禁状态面板 | 0/1 |
| `harness init` | `--force` | 初始化 .harness 结构到当前目录 | 0/1 |
| `harness --version` | 无 | 输出版本号 | 0 |

### 命令行为细节

**`harness`（默认）**
- 读取 `.harness/state.json`，启动 Textual TUI
- 如果没有初始化，提示 `harness init`
- TUI 内快捷键：`q` 退出、`F5` 刷新、`Ctrl+N` 新建 run、`Tab` 切换面板

**`harness new <run-id> --intent FEATURE --risk MEDIUM`**
- 校验 intent/risk 枚举值
- 创建 `phases/<run-id>/` 和 `runs/<run-id>/` 目录
- 更新 `state.json`
- 输出新 run 摘要

**`harness validate --strict`**
- 检查必需文件存在性
- 校验 state.json schema
- 校验 workflow.yaml 引用完整性（节点、门禁、角色）
- 检查 phase_dir 路径穿越
- `--strict` 模式下警告也视为失败

**`harness gates --gate G3_COMPILE --json`**
- 展示全部 8 道门禁或指定门禁状态
- `--json` 输出机器可读格式（CI 集成）

## 7. TUI 仪表盘设计

### 7.1 布局

```
┌─ Sidebar ─────┬─ Main Content ──────────────────────────────┐
│               │                                              │
│  Runs         │  Workflow Progress                           │
│               │  ████████████░░░░░░░░░░░░░░░░ 56%            │
│  ▶ feature-   │                                              │
│    auth       │  ✅ INTAKE              00-intake.md         │
│    DEVELOPING │  ✅ SOLUTION_DESIGN     03-solution-design.md │
│               │  ✅ IMPLEMENTATION_PLAN 06-plan.md            │
│  ▪ bugfix-    │  🔧 DEVELOPMENT         11-development.md    │
│    login      │  ⬜ COMPILE                                   │
│    DONE       │  ⬜ UNIT_TEST                                │
│               │  ⬜ EVIDENCE_CAPTURE                         │
│  ▪ query-     │  ⬜ ACCEPTANCE_REPORT                        │
│    auth       │                                              │
│    DONE       │  ┌─ Gates ──────────────────────────────┐    │
│               │  │ G1_REQUIREMENTS    ✅ PASS            │    │
│  [New Run]    │  │ G2_DESIGN          ✅ PASS            │    │
│    Ctrl+N     │  │ G3_COMPILE         ⬜ NOT_RUN         │    │
│               │  │ G4_UNIT_TEST       ⬜ NOT_RUN         │    │
│               │  │ G5_ATDD            ⚠ WAIVED          │    │
│               │  │ G6_EVIDENCE        ⬜ NOT_RUN         │    │
│               │  │ G7_PRERELEASE      ⚠ WAIVED          │    │
│               │  │ G8_ACCEPTANCE      ⬜ NOT_RUN         │    │
│               │  └──────────────────────────────────────┘    │
│               │                                              │
│               │  Tab 1:Artifacts | Tab 2:Gates | Tab 3:Help  │
│               │  Footer: q=Quit F5=Refresh Ctrl+N=New Run    │
└───────────────┴──────────────────────────────────────────────┘
```

### 7.2 组件树

```
HarnessApp (Textual App)
├── RunsSidebar          # 左侧 Run 列表，选中高亮
│   └── RunItem          # 每个 run：名称 + 状态图标 + 当前节点
├── WorkflowPanel        # 主区域：workflow 进度
│   ├── ProgressBar      # 百分比 + 节点计数
│   └── NodeList         # 节点列表，滚动
│       └── NodeItem     # 每个节点：状态图标 + 节点名 + 产物文件
├── GatesGrid            # 门禁网格 (4×2)
│   └── GateItem         # 每个门禁：ID + 状态 + 颜色
├── ArtifactPanel        # Tab 切换：产物文件列表 / 预览
└── Footer               # 快捷键提示
```

### 7.3 颜色和图标语义

| 状态 | 图标 | 颜色 |
|---|---|---|
| 完成 | ✅ | green |
| 进行中 | 🔧 | yellow/bright |
| 未开始 | ⬜ | dim |
| 阻断 | ❌ | red |
| 豁免 | ⚠ | yellow |
| 不要求 | — | dim |

## 8. core/ API 设计

### state.py — 状态管理

```python
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class RunStatus(Enum):
    IDLE = "IDLE"
    ROUTING = "ROUTING"
    DESIGNING = "DESIGNING"
    DEVELOPING = "DEVELOPING"
    VERIFYING = "VERIFYING"
    BLOCKED = "BLOCKED"
    DONE = "DONE"

class Intent(Enum):
    QUERY = "QUERY"
    BUG_FIX = "BUG_FIX"
    FEATURE = "FEATURE"
    REFACTOR = "REFACTOR"
    DEPLOYMENT = "DEPLOYMENT"
    INCIDENT = "INCIDENT"

class Risk(Enum):
    NA = "NA"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass
class HarnessState:
    """harness state.json 的完整内存模型"""
    schema_version: str
    run_id: str
    status: RunStatus
    intent: Intent
    risk: Risk
    current_node: str
    next_role: str
    phase_dir: str
    required_nodes: list[str] = field(default_factory=list)
    completed_nodes: list[str] = field(default_factory=list)
    blocked_by: list[str] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)
    gates: dict[str, str] = field(default_factory=dict)
    retry_counts: dict[str, int] = field(default_factory=dict)
    last_updated: str | None = None
    notes: str = ""

    @classmethod
    def load(cls, root: str = ".") -> "HarnessState":
        """从 .harness/state.json 加载并校验"""
        ...

    def save(self, root: str = ".") -> None:
        """写回 .harness/state.json"""
        ...

    def save_snapshot(self, root: str = ".") -> None:
        """保存到 .harness/runs/<run_id>/state.json"""
        ...

    def progress(self) -> tuple[int, int]:
        """返回 (已完成节点数, 总必需节点数)"""
        ...

    def is_gate_pass(self, gate_id: str) -> bool:
        """单个门禁是否通过"""
        ...


def list_runs(root: str = ".") -> list[dict]:
    """扫描 .harness/runs/ 返回所有 run 摘要列表"""
    ...


def switch_run(run_id: str, root: str = ".") -> HarnessState:
    """从 .harness/runs/<run_id>/state.json 恢复，写回 state.json"""
    ...
```

### workflow.py — 流程引擎

```python
@dataclass
class Node:
    id: str
    role: str
    artifact: str | None
    gates: list[str]

@dataclass
class Workflow:
    nodes: dict[str, Node]
    routes: dict[str, dict[str, list[str]]]
    hard_rules: dict[str, list[str]]
    failure_recovery: dict
    gate_meanings: dict[str, str]

    @classmethod
    def load(cls, root: str = ".") -> "Workflow":
        """从 .harness/workflow.yaml 加载"""
        ...

    def route(self, intent: str, risk: str) -> list[str]:
        """根据意图和风险返回必需节点列表"""
        ...

    def next_node(self, required: list[str], completed: set[str]) -> str | None:
        """返回第一个未完成的必需节点"""
        ...

    def role_for(self, node_id: str) -> str:
        """返回节点的角色"""
        ...

    def artifact_for(self, node_id: str) -> str | None:
        """返回节点的产物文件名"""
        ...
```

### gates.py — 门禁评估

```python
@dataclass
class GateResult:
    gate_id: str
    status: str          # PASS | FAIL | WAIVED | NOT_RUN | NOT_REQUIRED | BLOCKED
    description: str
    required_artifacts: list[str]
    reason: str = ""

@dataclass
class GateEvaluator:
    """门禁评估器，基于 gates.yaml 规则"""
    definition_path: str

    @classmethod
    def load(cls, root: str = ".") -> "GateEvaluator":
        """从 .harness/evals/gates.yaml 加载"""
        ...

    def evaluate(self, gate_id: str, state: HarnessState) -> GateResult:
        """评估单个门禁"""
        ...

    def evaluate_all(self, state: HarnessState) -> list[GateResult]:
        """评估全部 8 道门禁"""
        ...

    def summary(self, results: list[GateResult]) -> dict:
        """返回 {pass: N, fail: N, waived: N, not_run: N, blocked: N}"""
        ...
```

### validate.py — 结构校验

```python
@dataclass
class ValidationIssue:
    level: str           # "error" | "warning"
    message: str
    file: str | None
    detail: str | None

@dataclass  
class ValidationReport:
    passed: bool
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]

class Validator:
    """整合所有校验逻辑的结构校验器"""
    
    def __init__(self, root: str = ".", strict: bool = False):
        ...
    
    def validate(self) -> ValidationReport:
        """运行全部校验"""
        ...
    
    # 子校验方法：
    def _check_required_files(self) -> list[ValidationIssue]: ...
    def _check_state_schema(self) -> list[ValidationIssue]: ...
    def _check_workflow_integrity(self) -> list[ValidationIssue]: ...
    def _check_phase_dir_safety(self) -> list[ValidationIssue]: ...
    def _check_artifact_existence(self) -> list[ValidationIssue]: ...
    def _check_gate_references(self) -> list[ValidationIssue]: ...
```

## 9. TUI 组件详细设计

### 9.1 dashboard.py — 主 App

```python
class HarnessApp(App):
    """Textual TUI 主应用"""
    CSS_PATH = "harness.tcss"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("f5", "refresh", "Refresh"),
        Binding("ctrl+n", "new_run", "New Run"),
        Binding("tab", "focus_next", "Next Panel"),
        Binding("shift+tab", "focus_previous", "Prev Panel"),
    ]
    
    def compose(self) -> ComposeResult:
        yield RunsSidebar(id="sidebar")
        yield WorkflowPanel(id="workflow")
        yield GatesGrid(id="gates")
        yield Footer()
    
    def on_mount(self) -> None:
        self.refresh_data()
    
    def action_refresh(self) -> None:
        self.refresh_data()
    
    def refresh_data(self) -> None:
        state = HarnessState.load()
        workflow = Workflow.load()
        # 更新各组件数据...
```

### 9.2 数据流

```
                   ┌──────────────────┐
                   │  .harness/ 文件系统 │
                   │  state.json       │
                   │  workflow.yaml    │
                   │  gates.yaml       │
                   │  phases/<id>/     │
                   └────────┬─────────┘
                            │
                    ┌───────▼───────┐
                    │   core/ 层     │  ← 纯逻辑，无 IO 之外副作用
                    │ state.load()   │
                    │ workflow.load()│
                    │ gates.eval()   │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
        ┌─────▼──────┐ ┌───▼────┐ ┌──────▼──────┐
        │ TUI 组件   │ │ CLI    │ │ 未来 Web     │
        │ (Textual)  │ │ (Rich) │ │ (FastAPI)    │
        └────────────┘ └────────┘ └─────────────┘
```

## 10. 与现有脚本的关系

| 现有脚本 | 替代方式 |
|---|---|
| `new-run.ps1/.cmd/.sh` | `harness new <id>` |
| `save-run.ps1/.cmd/.sh` | `harness save` |
| `switch-run.ps1/.cmd/.sh` | `harness switch <id>` |
| `validate-harness.ps1/.cmd/.sh` | `harness validate` |
| 无 | `harness status` — 新增 |
| 无 | `harness list` — 新增 |
| 无 | `harness gates` — 新增 |
| 无 | `harness` TUI — 新增 |

现有脚本保留不删除，确保向后兼容。README 中推荐 CLI 工具，但仍保留脚本路径说明。

## 11. 依赖清单

```toml
# pyproject.toml
[project]
name = "harness-cli"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.9",
    "rich>=13.0",
    "textual>=0.50",
    "pyyaml>=6.0",
    "jsonschema>=4.20",
]

[project.scripts]
harness = "harness_cli.main:app"

[project.optional-dependencies]
dev = [
    "pyinstaller>=6.0",
    "pytest>=8.0",
    "pytest-textual-snapshot>=1.0",
]
```

## 12. 分发与安装

### 12.1 三种安装方式

| 方式 | 命令 | 适用场景 |
|---|---|---|
| PyPI | `pip install bridle-cli` | 开发者，有 Python 环境 |
| 单二进制 | 下载 `bridle.exe` / `bridle` | 无 Python 环境，快速试用 |
| 开发模式 | `pip install -e .` | 贡献者，本地开发 |

### 12.2 单文件打包

PyInstaller 打包为单个可执行文件，内嵌：
- Python 运行时
- 全部依赖（typer, rich, textual, pyyaml, jsonschema）
- `.harness/` 模板（用于 `init` 命令）

```bash
pyinstaller --onefile --name bridle src/harness_cli/main.py
```

## 13. 版本管理与发布

### 13.1 双版本线

```
CLI 版本（bridle）               Harness Schema 版本
─────────────────────────────────────────────────────
 pyproject.toml 中定义             state.json: "schema_version"
 遵循 semver                       workflow.yaml: "schema_version"
 随功能/修复/bug 升级              只在结构不兼容时升级
 例如: 0.1.0 → 0.2.0 → 1.0.0    例如: "1.0" → "2.0"
```

**兼容性矩阵**：一个 CLI 版本声明自己支持的 Schema 版本范围。

```python
# main.py
SUPPORTED_SCHEMA_VERSIONS = ["1.0"]  # 后续扩展 ["1.0", "2.0"]
```

如果 CLI 读取到不兼容的 Schema 版本：
```
╭─ Error ───────────────────────────────────────────────╮
│  Schema version 2.0 is not supported by bridle v0.1.0 │
│  Supported: 1.0                                       │
│  Upgrade bridle: pip install --upgrade bridle-cli     │
╰──────────────────────────────────────────────────────╯
```

### 13.2 发布流程

每次发布走固定流程，确保一致性：

```
1. 版本号升级
   ├── pyproject.toml: version = "0.1.0" → "0.2.0"
   └── main.py: __version__ = "0.2.0"

2. 更新 CHANGELOG.md
   ├── Added / Changed / Fixed / Deprecated
   └── 记录迁移注意事项（如有）

3. 质量门禁
   ├── pytest 全部通过
   ├── validate 自检通过（harness validate 校验自身模板）
   └── 手动冒烟测试（init / new / status / validate 四命令验证）

4. Git 打标签
   └── git tag v0.2.0 -m "bridle v0.2.0"

5. 构建与发布
   ├── PyPI: python -m build && twine upload dist/*
   └── GitHub Release: 附带 bridle.exe / bridle 二进制

6. 更新通知
   └── CLI 启动时检查 PyPI，有新版显示提示
```

### 13.3 CHANGELOG.md 规范

遵循 [Keep a Changelog](https://keepachangelog.com/)：

```markdown
# Changelog

## [0.2.0] - 2026-08-01

### Added
- `harness watch` 命令：文件变化自动刷新 TUI
- `harness gates --check` CI 集成模式

### Changed
- `harness status` 输出增加门禁摘要行

### Fixed
- Windows 路径反斜杠导致 phase_dir 校验失败

## [0.1.0] - 2026-07-19

### Added
- 首个 MVP 版本
- 9 个 CLI 命令 + TUI 仪表盘
```

### 13.4 发布节奏

```
版本号规则：
  MAJOR.minor.patch

  MAJOR (1.0.0)    CLI 接口 breaking change（命令改名、参数变化）
  MINOR (0.2.0)    新命令、新功能，向后兼容
  PATCH (0.1.1)    Bug 修复，无新功能

节奏（非严格）：
  0.x 阶段   → 快速迭代，break 可接受
  1.0 以后   → 严格向后兼容，break 需 MAJOR 升级
```

## 14. 模板更新与项目升级

### 14.1 问题

CLI 升级后，用户已有项目中的 `.harness/` 模板是旧版本。新版本可能：

- 新增了 agent 或 rule 文件
- 修改了 workflow.yaml 的路由
- 增加了新的门禁定义
- 调整了 state.json schema

如何让已有项目跟上模板更新，同时不破坏正在进行中的 run？

### 14.2 更新策略：`harness init --repair`

```
harness init --repair 做的事：

1. 对比 CLI 内置模板 与 项目 .harness/ 目录
2. 列出差异（新增文件、缺失文件）
3. 不覆盖任何已存在的文件
4. 只补全缺失的模板文件
5. 对 AGENTS.md / CLAUDE.md 检查标记块版本，提示是否需更新
6. 输出变更摘要
```

```
╭─ Harness Repair ───────────────────────────────────────╮
│  CLI:     v0.2.0  (schema: 1.0)                       │
│  Project: v0.1.0  (schema: 1.0)                       │
│                                                        │
│  New files to add:                                     │
│    .harness/rules/code-search.md                       │
│    .harness/agents/tester.md                           │
│                                                        │
│  Modified templates (will NOT overwrite):              │
│    .harness/workflow.yaml        (manual merge needed) │
│                                                        │
│  Proceed with adding new files? [Y/n]                  │
╰──────────────────────────────────────────────────────────╯
```

### 14.3 核心原则

```
文件类型                  repair 行为
─────────────────────────────────────────────────
纯模板文件（agents/rules/context/commands）     补全缺失，不覆盖已有
配置文件（workflow.yaml/gates.yaml）            仅提示有新版，需人工合并
状态文件（state.json/phases/）                 永不触碰
用户修改过且有标记块的文件（AGENTS.md等）        检查标记块版本，提示更新
```

### 14.4 Schema 迁移

当 Schema 版本升级（如 `1.0` → `2.0`），`state.json` 结构不兼容时：

```python
# 内置迁移脚本
MIGRATIONS = {
    "1.0": {
        "2.0": migrate_v1_to_v2,  # 转换函数
    }
}
```

CLI 遇到旧 Schema 版本时自动运行迁移，输出变更：
```
Schema migration: 1.0 → 2.0
  - Added field: retry_counts
  - Renamed: current_stage → current_node
Migration successful. Original backed up to state.json.bak
```

## 15. CLI 自更新

### 15.1 启动检查

CLI 启动时（非阻塞）异步检查 PyPI 是否有新版本：

```python
# 版本检查缓存 24 小时，避免每次启动都网络请求
CACHE_FILE = "~/.bridle/version-check.json"

def check_update() -> str | None:
    """返回最新版本号，或 None"""
    # 1. 读缓存，24h 内跳过
    # 2. 请求 PyPI JSON API: https://pypi.org/pypi/bridle-cli/json
    # 3. 对比当前版本
```

更新提醒出现在 TUI footer 或 `harness --version` 输出中：

```
bridle v0.1.0  (schema: 1.0)   ← update available: v0.2.0
Run: pip install --upgrade bridle-cli
```

### 15.2 不自动更新

- 不做 `harness self-update`（自动下载覆盖自己）
- 原因：权限复杂、跨平台坑多、安全风险
- 替代方案：提示命令，用户自己执行 `pip install --upgrade`

## 16. 边界说明

- **不做**：需求分析、代码生成、评审——这些是 AI（Claude Code）的职责
- **不做**：多用户服务端、数据库——纯本地文件系统操作
- **不做**：修改 workflow.yaml 或 state.json schema
- **不做**：自动更新自己的二进制（安全边界）
- **只做**：状态管理、流程导航、校验、可视化展示、模板分发
