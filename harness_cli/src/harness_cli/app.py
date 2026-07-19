"""Bridle TUI 入口：Textual App 启动。"""

from __future__ import annotations

from pathlib import Path


def launch_tui() -> None:
    """启动 Bridle TUI 仪表盘。"""
    from .ui.dashboard import HarnessApp
    app = HarnessApp()
    app.run()
