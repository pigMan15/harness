"""HarnessApp — Bridle 主 TUI 仪表盘。

布局:
┌─ Sidebar ───┬─ Main Content ──────────────────────────┐
│ Runs        │  Workflow Progress                       │
│             │  ████████░░░░░░ 56%                      │
│ ▶ current   │  ✅ INTAKE     ✅ DESIGN    🔧 DEVELOP   │
│ ▪ other     │  ⬜ COMPILE    ⬜ TEST     ⬜ REPORT      │
│             │                                          │
│ [New Run]   │  ┌─ Gates ──────────────────────────┐    │
│             │  │ G1✅ G2✅ G3⬜ G4⬜              │    │
│             │  │ G5⬜ G6⬜ G7⬜ G8⬜             │    │
│             │  └──────────────────────────────────┘    │
│             │                                          │
│             │  Footer: q=Quit  F5=Refresh  Ctrl+N=New  │
└─────────────┴──────────────────────────────────────────┘
"""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from .. import __version__
from ..core.state import HarnessState, list_runs
from ..core.workflow import Workflow
from ..core.gates import GateEvaluator
from ..constants import THEME
from .widgets.runs_list import RunsSidebar
from .widgets.workflow_tree import WorkflowPanel
from .widgets.gates_grid import GatesGrid
from .widgets.new_run_modal import NewRunModal


class HarnessApp(App):
    """Bridle TUI 主应用。"""

    TITLE = f"Bridle v{__version__}"
    SUB_TITLE = "AI Coding Harness"

    CSS = """
    Horizontal {
        height: 1fr;
    }
    RunsSidebar {
        width: 30;
        border: solid $surface-lighten-1;
        background: $surface-lighten-2;
    }
    #main-content {
        width: 1fr;
    }
    WorkflowPanel {
        border: solid $surface-lighten-1;
        padding: 1;
    }
    GatesGrid {
        height: 9;
        border: solid $surface-lighten-1;
        padding: 0 1;
    }
    .section-title {
        text-style: bold;
        color: $text;
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("f5", "refresh", "Refresh", show=True),
        Binding("ctrl+n", "new_run", "New Run", show=True),
        Binding("tab", "focus_next", "Next Panel", show=False),
        Binding("shift+tab", "focus_previous", "Prev Panel", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._root = Path.cwd()
        self._state: HarnessState | None = None
        self._workflow: Workflow | None = None
        self._evaluator: GateEvaluator | None = None
        self._error: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield RunsSidebar(id="sidebar")
            with Vertical(id="main-content"):
                yield WorkflowPanel(id="workflow")
                yield GatesGrid(id="gates")
        yield Footer()

    def on_mount(self) -> None:
        """挂载后加载数据并刷新所有组件。"""
        self.refresh_data()

    # ── 数据加载 ──

    def refresh_data(self) -> None:
        """从文件系统重新加载状态、workflow 和门禁。"""
        try:
            self._state = HarnessState.load(str(self._root))
            self._workflow = Workflow.load(str(self._root))
            self._evaluator = GateEvaluator.load(str(self._root))
            self._error = None
        except FileNotFoundError as e:
            self._error = f"Not a harness project: {e}\n\nRun 'bridle init' first."
            self._state = None
            self._workflow = None
            self._evaluator = None
            return
        except Exception as e:
            self._error = f"Failed to load harness: {e}"
            self._state = None
            self._workflow = None
            self._evaluator = None
            return

        # 更新各组件
        runs = list_runs(str(self._root))
        sidebar = self.query_one(RunsSidebar)
        sidebar.update_runs(runs, self._state.run_id)

        if self._state and self._workflow:
            wf_panel = self.query_one(WorkflowPanel)
            wf_panel.update_state(self._state, self._workflow)

        if self._state and self._evaluator:
            gates_grid = self.query_one(GatesGrid)
            gates_grid.update_gates(self._state, self._evaluator, str(self._root))

    # ── Actions ──

    def action_refresh(self) -> None:
        """F5: 刷新数据。"""
        self.refresh_data()

    def action_new_run(self) -> None:
        """Ctrl+N: 弹出新建 Run 对话框。"""

        def _on_done(run_id: str | None) -> None:
            if run_id is None:
                return
            # 新建 run
            try:
                from ..core.state import HarnessState, Intent, Risk
                state = HarnessState.create_new(run_id, Intent.FEATURE, Risk.MEDIUM, root=str(self._root))
                if self._workflow:
                    state.required_nodes = self._workflow.route("FEATURE", "MEDIUM")
                state.save(str(self._root))
                state.save_snapshot(str(self._root))
                self._state = state
                self.refresh_data()
                self.notify(f"Created run: {run_id}", severity="information")
            except Exception as e:
                self.notify(f"Failed to create run: {e}", severity="error")

        self.push_screen(NewRunModal(), _on_done)
