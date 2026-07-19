"""ProjectList — 全局项目列表侧边栏（带键盘光标导航）。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from textual.app import ComposeResult
from textual.widgets import Static
from textual import events
from textual.message import Message

from ...constants import THEME
from ...commands.projects_cmd import _load_registry
from ...core.state import HarnessState


class ProjectList(Static, can_focus=True):
    """左侧项目列表。键盘上下键选择项目，Enter 加载。"""

    class Selected(Message):
        """项目被选中时发送的消息。"""
        def __init__(self, path: str) -> None:
            super().__init__()
            self.path = path

    def __init__(self, cwd: Path | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._cwd = cwd or Path.cwd()
        self._projects: list[dict[str, Any]] = []
        self._selected_idx = 0

    def compose(self) -> ComposeResult:
        yield Static("Projects", classes="section-title")
        yield Static("Loading...", id="project-items")
        yield Static("[grey]Up/Down=Move  Enter=Select  Ctrl+N=New[/]", id="project-hint")

    def on_mount(self) -> None:
        self.reload()

    def on_key(self, event: events.Key) -> None:
        """键盘导航。"""
        if not self._projects:
            return
        if event.key == "down":
            self._selected_idx = (self._selected_idx + 1) % len(self._projects)
            self._draw()
            event.prevent_default()
        elif event.key == "up":
            self._selected_idx = (self._selected_idx - 1) % len(self._projects)
            self._draw()
            event.prevent_default()
        elif event.key == "enter":
            path = self.get_selected_path()
            if path:
                self.post_message(self.Selected(path))

    def reload(self) -> None:
        """重新加载全局项目列表。"""
        registry = _load_registry()
        self._projects = []

        # 当前目录项目（即使未注册也显示）
        cwd_harness = self._cwd / ".harness"
        if cwd_harness.is_dir():
            already = any(
                Path(p["path"]).resolve() == self._cwd.resolve()
                for p in registry["projects"]
            )
            if not already:
                try:
                    state = HarnessState.load(str(self._cwd))
                    self._projects.append({
                        "name": self._cwd.name,
                        "path": str(self._cwd),
                        "status": state.status.value,
                        "run": state.run_id,
                        "nodes": f"{state.progress()[0]}/{state.progress()[1]}",
                        "is_current": True,
                    })
                except Exception:
                    pass

        for p in registry["projects"]:
            proj_path = Path(p["path"])
            exists = proj_path.exists() and (proj_path / ".harness").is_dir()
            info = {
                "name": p["name"],
                "path": p["path"],
                "status": "LOST",
                "run": "-",
                "nodes": "-",
                "is_current": Path(p["path"]).resolve() == self._cwd.resolve(),
            }
            if exists:
                try:
                    state = HarnessState.load(str(proj_path))
                    info["status"] = state.status.value
                    info["run"] = state.run_id
                    c, t = state.progress()
                    info["nodes"] = f"{c}/{t}"
                except Exception:
                    info["status"] = "ERROR"
            self._projects.append(info)

        # 修正选中索引
        if self._selected_idx >= len(self._projects):
            self._selected_idx = max(0, len(self._projects) - 1)

        self._draw()

    def _draw(self) -> None:
        """渲染项目列表文本。"""
        items_widget = self.query_one("#project-items", Static)

        if not self._projects:
            items_widget.update("\n  No registered projects\n")
            return

        lines: list[str] = [""]
        for i, p in enumerate(self._projects):
            s = p["status"]
            if s == "DONE":
                icon, color = "DONE   ", "green"
            elif s in ("DEVELOPING", "IN_PROGRESS", "VERIFYING", "DESIGNING"):
                icon, color = f"{s[:7]:<7}", "yellow"
            elif s in ("BLOCKED", "ERROR"):
                icon, color = f"{s[:7]:<7}", "red"
            elif s == "IDLE":
                icon, color = "IDLE   ", "grey"
            elif s == "LOST":
                icon, color = "LOST   ", "red"
            else:
                icon, color = f"{s[:7]:<7}", "grey"

            # 光标和当前目录标记
            if i == self._selected_idx:
                cursor = "[bold yellow]>[/]"
            else:
                cursor = " "
            is_cur = "[cyan]*[/]" if p["is_current"] else " "

            lines.append(f"{cursor}{is_cur} [{color}]{icon}[/] {p['name']:<20} {p['nodes']}")

        items_widget.update("\n".join(lines))

    def get_selected_path(self) -> str | None:
        """返回当前光标所在项目的路径。"""
        if 0 <= self._selected_idx < len(self._projects):
            return self._projects[self._selected_idx]["path"]
        return None
