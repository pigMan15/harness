# 任务入口

- RunId：`harness-tui-20260719`
- 意图：`FEATURE`
- 风险：`MEDIUM`
- 目标：为 Harness 框架构建 Python CLI + TUI 工具，替代现有 PowerShell/CMD/Shell 脚本，提供终端交互式仪表盘。

## 范围

1. Python CLI 工具（Typer），包含核心命令：new, status, validate, switch, list, gates
2. TUI 仪表盘（Textual + Rich），实时展示 run 状态、workflow 进度、门禁面板
3. 纯逻辑核心层（core/），可被 CLI 和未来 Web UI 共用
4. 打包为单文件可分发（PyInstaller）

## 不在范围

- Web Dashboard（Phase 2）
- VS Code 扩展（Phase 3）
- 不修改现有 .harness/ 模板结构
- 不改变 workflow.yaml 和 state.json schema

## 技术决策

- 语言：Python 3.11+
- CLI 框架：Typer
- 终端美化：Rich
- TUI 框架：Textual
- 打包：PyInstaller
- 用户已确认 TUI 方向
