"""RunsSidebar — 左侧 Run 列表组件。"""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static, ListView, ListItem, Label

from ...constants import THEME


class RunsSidebar(Static):
    """左侧 Run 列表。显示所有保存的 runs，高亮当前激活的 run。"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._runs: list[dict[str, Any]] = []
        self._active_run_id: str = ""

    def compose(self) -> ComposeResult:
        yield Static("Runs", classes="section-title")
        yield ListView(id="run-list")

    def update_runs(self, runs: list[dict[str, Any]], active_run_id: str) -> None:
        """更新 run 列表。

        Args:
            runs: list_runs() 返回的摘要列表
            active_run_id: 当前激活的 run ID
        """
        self._runs = runs
        self._active_run_id = active_run_id

        list_view = self.query_one("#run-list", ListView)
        list_view.clear()

        if not runs:
            list_view.append(ListItem(Label("  No runs yet")))
            return

        for r in runs:
            is_active = r["run_id"] == active_run_id
            prefix = "▶" if is_active else " "

            status = r["status"]
            if status == "DONE":
                icon = "✅"
            elif status in ("DEVELOPING", "VERIFYING", "DESIGNING"):
                icon = "🔧"
            elif status in ("BLOCKED", "CORRUPTED"):
                icon = "❌"
            else:
                icon = "⬜"

            total = r["required"]
            completed = r["completed"]
            pct = f" {completed}/{total}" if total else ""

            label = Label(f" {prefix} {icon} {r['run_id']}{pct}")
            if is_active:
                label.styles.color = THEME["primary"]
            list_view.append(ListItem(label))
