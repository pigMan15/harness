# 实施计划：Bridle CLI + TUI 工具

## 模块依赖关系

```
Phase 0: 项目脚手架
  │
  ▼
Phase 1: core/ 纯逻辑层（零依赖）
  ├── state.py      ──── 状态读写
  ├── workflow.py   ──── 流程路由
  ├── gates.py      ──── 门禁评估
  └── validate.py   ──── 结构校验 ── 依赖 state + workflow + gates
  │
  ├──────────┬──────────┐
  ▼          ▼          ▼
Phase 2: CLI 命令层     Phase 4: 测试
  │                      │
  ▼                      │
Phase 3: TUI 界面层      │
  │                      │
  ▼                      ▼
Phase 5: 打包发布 ───────┘
```

## Phase 0: 项目脚手架

**目标**：目录结构、依赖声明、常量定义

| 文件 | 内容 |
|---|---|
| `harness_cli/pyproject.toml` | 项目名 bridle-cli，依赖 typer/rich/textual/pyyaml/jsonschema |
| `harness_cli/src/harness_cli/__init__.py` | `__version__ = "0.1.0"` |
| `harness_cli/src/harness_cli/constants.py` | 配色主题、SUPPORTED_SCHEMA_VERSIONS、路径常量 |
| `harness_cli/src/harness_cli/core/__init__.py` | 空 |
| `harness_cli/src/harness_cli/commands/__init__.py` | 空 |
| `harness_cli/src/harness_cli/ui/__init__.py` | 空 |
| `harness_cli/src/harness_cli/ui/widgets/__init__.py` | 空 |
| `harness_cli/src/harness_cli/templates/` | 内置 `.harness/` 模板副本 + AGENTS.md |

**入口标准**：无
**产物**：`harness_cli/` 目录树 + `pyproject.toml` + `pip install -e .` 可执行 `bridle --version`

---

## Phase 1: core/ 纯逻辑层

**目标**：State/Workflow/Gates/Validate 四个模块，零终端依赖，可独立单元测试

### 1.1 `core/state.py` — 状态管理

| 项 | 内容 |
|---|---|
| 依赖 | constants.py, state.schema.json |
| 类 | `HarnessState`（dataclass），`RunStatus/Intent/Risk`（Enum） |
| 方法 | `load(root)`, `save(root)`, `save_snapshot(root)`, `progress()`, `is_gate_pass(gate_id)` |
| 函数 | `list_runs(root) → list[dict]`, `switch_run(run_id, root) → HarnessState` |
| 校验 | 加载时用 jsonschema 校验 `state.schema.json`，字段缺失抛明确异常 |
| 测试 | 合法 JSON → 加载成功；缺失字段 → 抛异常；list_runs 扫描 runs/ 目录；switch_run 恢复快照 |

### 1.2 `core/workflow.py` — 流程引擎

| 项 | 内容 |
|---|---|
| 依赖 | constants.py |
| 类 | `Node`（dataclass），`Workflow` |
| 方法 | `load(root)`, `route(intent, risk) → list[str]`, `next_node(required, completed) → str\|None`, `role_for(node_id)`, `artifact_for(node_id)` |
| 逻辑 | 解析 workflow.yaml 的 nodes/routes/hard_rules/failure_recovery/gate_meanings |
| 测试 | 合法 YAML → 正确路由；BUG_FIX/LOW → 6 节点；FEATURE/HIGH → 20 节点；未知 intent → 空列表 |

### 1.3 `core/gates.py` — 门禁评估

| 项 | 内容 |
|---|---|
| 依赖 | core/state.py |
| 类 | `GateResult`（dataclass），`GateEvaluator` |
| 方法 | `load(root)`, `evaluate(gate_id, state) → GateResult`, `evaluate_all(state) → list[GateResult]`, `summary(results) → dict` |
| 逻辑 | 检查产物文件存在性 → PASS/NOT_RUN；读 evidence.json 中的豁免 → WAIVED |
| 测试 | 产物存在 → PASS；产物缺失 → NOT_RUN；豁免记录 → WAIVED；summary 计数正确 |

### 1.4 `core/validate.py` — 结构校验

| 项 | 内容 |
|---|---|
| 依赖 | core/state.py, core/workflow.py, core/gates.py |
| 类 | `ValidationIssue`, `ValidationReport`, `Validator` |
| 方法 | `validate() → ValidationReport` |
| 子校验 | `_check_required_files()`, `_check_state_schema()`, `_check_workflow_integrity()`, `_check_phase_dir_safety()`, `_check_artifact_existence()`, `_check_gate_references()` |
| 测试 | 完整目录 → passed=True；缺少必需文件 → passed=False + 错误明细；phase_dir 路径穿越 → 阻断 |

---

## Phase 2: CLI 命令层

**目标**：Typer 命令，调用 core/，用 Rich 美化输出，退出码正确

### 2.1 `main.py` — 入口

```python
app = typer.Typer(name="bridle", help="AI Coding Harness CLI")

@app.callback()
def callback(ctx, version=False):
    if version:
        print_version()  # bridle v0.1.0 (harness schema: 1.0)
        check_update_async()  # 异步检查新版
        return
    if no_args:
        launch_tui()  # 不加参数 → 进 TUI
```

### 2.2 各命令文件

| 文件 | 命令 | 核心调用 | 输出 |
|---|---|---|---|
| `commands/init_cmd.py` | `harness init` | `Validator` + 模板复制 + AGENTS.md 合并 | Rich 面板 |
| `commands/new_run.py` | `harness new <id>` | `HarnessState` 新实例 + `Workflow.route()` | 摘要表格 |
| `commands/status_cmd.py` | `harness status [--json]` | `HarnessState.load()` | 进度条 + 节点列表 / JSON |
| `commands/validate_cmd.py` | `harness validate [--strict]` | `Validator.validate()` | 错误/警告列表 |
| `commands/switch_run.py` | `harness switch <id>` | `switch_run()` | 确认消息 |
| `commands/list_runs.py` | `harness list [--status] [--intent]` | `list_runs()` | 表格 |
| `commands/gates_cmd.py` | `harness gates [--gate <id>] [--json]` | `GateEvaluator.evaluate_all()` | 网格面板 / JSON |
| `commands/save_run.py` | `harness save` | `HarnessState.save_snapshot()` | 确认消息 |

### 2.3 统一错误处理

```python
# 所有命令共享的错误装饰器
def handle_errors(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except FileNotFoundError as e:
            console.print(f"[red]Error:[/] {e}")
            raise typer.Exit(1)
        except jsonschema.ValidationError as e:
            console.print(f"[red]Schema validation failed:[/] {e.message}")
            raise typer.Exit(1)
```

**测试**：每个命令的 `--json` 输出合法 JSON；`--help` 输出完整；退出码正确（成功 0 / 失败 1）。

---

## Phase 3: TUI 界面层

**目标**：Textual 交互式仪表盘，组件化，60fps 刷新

### 3.1 `ui/console.py` — Rich 单次输出

| 函数 | 用途 |
|---|---|
| `print_status(state, workflow)` | `harness status` 的 Rich 输出 |
| `print_gates(results)` | `harness gates` 的 Rich 输出 |
| `print_list(runs)` | `harness list` 的 Rich 表格 |
| `print_banner()` | 启动画面 ASCII art |

### 3.2 `app.py` — TUI App

| 项 | 内容 |
|---|---|
| 类 | `HarnessApp(App)` |
| 快捷键 | `q` 退出，`F5` 刷新，`Ctrl+N` 新建 run，`Tab`/`Shift+Tab` 切换面板 |
| 数据流 | `on_mount` → `refresh_data()` → `query_one(WorkflowPanel).update(state, workflow)` |

### 3.3 TUI Widgets

| 文件 | 组件 | 功能 |
|---|---|---|
| `widgets/runs_list.py` | `RunsSidebar` | 左侧 Run 列表，`▶` 标记当前，颜色标记状态 |
| `widgets/workflow_tree.py` | `WorkflowPanel` | 节点列表 + 进度条，当前节点高亮 |
| `widgets/gates_grid.py` | `GatesGrid` | 4×2 门禁网格，颜色标记状态 |
| `widgets/artifact_panel.py` | `ArtifactPanel` | Tab 切换：产物列表 / Markdown 预览 |
| `widgets/new_run_modal.py` | `NewRunModal` | Ctrl+N 弹出对话框，输入 Run ID / Intent / Risk |

### 3.4 CSS 主题

```css
/* harness.tcss */
Screen {
    background: $surface;
}
RunsSidebar {
    width: 30;
    border: solid $primary;
}
WorkflowPanel {
    border: solid $secondary;
}
GatesGrid {
    height: 10;
    border: solid $surface-lighten-1;
}
```

**测试**：Textual snapshot 测试（`pytest-textual-snapshot`），CSS 无语法错误，组件树正确挂载。

---

## Phase 4: 测试

### 4.1 测试策略

```
层级        框架              覆盖目标
─────────────────────────────────────────
单元测试    pytest             core/ 全部公开方法，100% 分支覆盖
集成测试    pytest             命令端到端（创建真实临时 .harness/）
TUI 测试    pytest + snapshot  Textual 组件渲染快照，交互流
```

### 4.2 测试目录结构

```
harness_cli/tests/
├── conftest.py                      # fixture: 临时 .harness/ 目录
├── test_state.py
├── test_workflow.py
├── test_gates.py
├── test_validate.py
├── test_init.py
├── test_new_run.py
├── test_status.py
├── test_switch_run.py
├── test_list_runs.py
├── test_gates_cmd.py
├── test_save_run.py
├── test_tui_snapshot.py
└── fixtures/
    ├── valid_harness/               # 完整合法的 .harness/ 测试夹具
    ├── missing_files/               # 缺失必需文件的 .harness/
    └── invalid_state/               # 非法 state.json
```

### 4.3 关键测试场景

| 场景 | 预期结果 |
|---|---|
| `harness init` 到空目录 | 创建完整 .harness/ + AGENTS.md + CLAUDE.md |
| `harness init` 到已有 AGENTS.md 的目录 | 追加标记块，不覆盖原有内容 |
| `harness init` 二次执行 | 幂等，不重复追加 |
| `harness new feat-001 --intent FEATURE --risk MEDIUM` | 创建目录，state.json 正确，路由 10 节点 |
| `harness validate` 完整目录 | PASS，exit 0 |
| `harness validate` 缺失文件 | FAIL，exit 1，列出缺失项 |
| `harness status --json` | 合法 JSON，字段完整 |
| `harness gates --json` | 合法 JSON，8 道门禁状态 |
| `harness switch non-existent` | exit 1，明确错误信息 |
| TUI 启动 | 组件树完整挂载，Run 列表正确，节点进度正确 |
| F5 刷新 | 数据实时更新 |
| Ctrl+N 新建 Run | 弹窗，输入校验，创建成功后刷新列表 |

---

## Phase 5: 打包发布

### 5.1 PyInstaller 配置

```bash
pyinstaller \
  --onefile \
  --name bridle \
  --add-data "src/harness_cli/templates:templates" \
  --hidden-import textual \
  --hidden-import rich \
  --hidden-import yaml \
  --hidden-import jsonschema \
  src/harness_cli/main.py
```

### 5.2 CI/CD（GitHub Actions）

```yaml
# .github/workflows/release.yml
on:
  push:
    tags: ["v*"]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
      python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[dev]"
      - run: pytest

  build:
    needs: test
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    steps:
      - run: pyinstaller --onefile ...
      - uses: softprops/action-gh-release@v1
        with:
          files: dist/*
```

### 5.3 PyPI 发布

```bash
python -m build
twine upload dist/*
```

---

## 交付顺序

```
Day 1-2:   Phase 0 (scaffold) + Phase 1 (core/ 四个模块)
Day 3-4:   Phase 2 (CLI 8 个命令)
Day 5-6:   Phase 3 (TUI + widgets)
Day 7:     Phase 4 (测试补齐)
Day 8:     Phase 5 (打包 + CI)
Day 9:     文档 + CHANGELOG + 冒烟
Day 10:    v0.1.0 发布
```

每个 Phase 结束后：`harness validate` 自检 + `pytest` 单元测试全部通过，再进入下一 Phase。
