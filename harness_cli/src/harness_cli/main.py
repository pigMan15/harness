"""Bridle CLI 入口。

用法:
    bridle                  → 启动 TUI 仪表盘（无参数时）
    bridle <command>        → 执行单次 CLI 命令
    bridle --version        → 显示版本信息
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from . import __version__
from .ui.console import print_banner, print_version

app = typer.Typer(
    name="bridle",
    help="AI Coding Harness CLI — structured workflow for AI-assisted development",
    no_args_is_help=False,
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Show version and exit"),
) -> None:
    """无子命令时启动 TUI，--version 显示版本。"""
    if version:
        print_version(__version__)
        return

    # 无子命令 → 进入 TUI
    if ctx.invoked_subcommand is None:
        from .app import launch_tui
        launch_tui()


# ── 注册子命令 ──

from .commands.init_cmd import init
app.command(name="init")(init)

from .commands.new_run import new
app.command(name="new")(new)

from .commands.status_cmd import status
app.command(name="status")(status)

from .commands.validate_cmd import validate
app.command(name="validate")(validate)

from .commands.switch_run import switch
app.command(name="switch")(switch)

from .commands.list_runs import list_runs_cmd
app.command(name="list")(list_runs_cmd)

from .commands.gates_cmd import gates
app.command(name="gates")(gates)

from .commands.save_run import save
app.command(name="save")(save)


def main() -> None:
    """入口函数（PyInstaller 打包用）。"""
    app()


if __name__ == "__main__":
    main()
