"""HarnessApp — Bridle 主 TUI 仪表盘（多项目）。

左侧: 全局项目列表  右侧: 选中项目的 Workflow + Gates
不在 harness 目录也能查看所有项目状态。
"""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from .. import __version__
from ..core.i18n import _
from ..core.state import HarnessState, list_runs
from ..core.workflow import Workflow
from ..core.gates import GateEvaluator
from ..constants import THEME
from .widgets.project_list import ProjectList
from .widgets.workflow_tree import WorkflowPanel
from .widgets.gates_grid import GatesGrid
from .widgets.new_run_modal import NewRunModal, NewRunRequest


def create_state_for_new_run(project_path: Path, workflow: Workflow | None, request: NewRunRequest) -> HarnessState:
    """按用户在 TUI 中选择的 intent/risk 创建状态，避免覆盖用户意图。"""
    from ..core.state import Intent, Risk

    intent = Intent(request.intent)
    risk = Risk(request.risk)
    state = HarnessState.create_new(request.run_id, intent, risk, root=str(project_path))
    if workflow:
        state.required_nodes = workflow.route(intent.value, risk.value)
    return state


class HarnessApp(App):
    """Bridle TUI — 多项目仪表盘。"""

    TITLE = f"Bridle v{__version__}"
    SUB_TITLE = "AI Coding Harness"

    CSS = """
    Horizontal {
        height: 1fr;
    }
    ProjectList {
        width: 32;
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
    #error-msg {
        color: $error;
        padding: 1;
        display: none;
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
        self._active_project: Path | None = None
        self._state: HarnessState | None = None
        self._workflow: Workflow | None = None
        self._evaluator: GateEvaluator | None = None
        self._error: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield ProjectList(cwd=self._root, id="sidebar")
            with Vertical(id="main-content"):
                yield Static("", id="error-msg")
                yield Static("", id="knowledge-badge")
                yield WorkflowPanel(id="workflow")
                yield GatesGrid(id="gates")
        yield Footer()

    def on_mount(self) -> None:
        """挂载后自动检测当前目录并刷新。"""
        self.set_interval(3, self.refresh_all)
        if (self._root / ".harness").is_dir():
            self.load_project(self._root)
        else:
            # 不在 harness 目录，显示指引
            err = self.query_one("#error-msg", Static)
            err.styles.display = "block"
            err.styles.color = "grey"
            err.update(
                f"{_('tui.no_harness')}\n\n"
                f"{_('tui.register_hint')}\n"
                f"{_('tui.cd_hint')}"
            )
        self.refresh_all()

    # ── 数据加载 ──

    def refresh_all(self) -> None:
        """刷新项目列表和当前项目数据。"""
        sidebar = self.query_one(ProjectList)
        sidebar.reload()
        # 如果正在查看某个项目，也刷新它的数据
        if self._active_project and self._active_project.exists():
            self.load_project(self._active_project)

    def load_project(self, project_path: Path) -> None:
        """加载指定项目的 state/workflow/gates 并更新右侧面板。"""
        self._active_project = project_path
        root_str = str(project_path)

        # 隐藏之前的错误
        self.query_one("#error-msg", Static).styles.display = "none"
        self._error = None

        try:
            self._state = HarnessState.load(root_str)
            self._workflow = Workflow.load(root_str)
            self._evaluator = GateEvaluator.load(root_str)
        except FileNotFoundError as e:
            self._error = f"Not a harness project: {e}"
            self._state = None
            self._workflow = None
            self._evaluator = None
        except Exception as e:
            self._error = f"Failed to load: {e}"
            self._state = None
            self._workflow = None
            self._evaluator = None

        if self._error:
            err_widget = self.query_one("#error-msg", Static)
            err_widget.update(f"[red]{self._error}[/]")
            err_widget.styles.display = "block"
            return

        # 更新右侧面板
        try:
            if self._state and self._workflow:
                self.query_one(WorkflowPanel).update_state(self._state, self._workflow)
            if self._state and self._evaluator:
                self.query_one(GatesGrid).update_gates(self._state, self._evaluator, root_str)
            self._update_knowledge_badge()
        except Exception as e:
            err_widget = self.query_one("#error-msg", Static)
            err_widget.update(f"[red]Render error: {e}[/]")
            err_widget.styles.display = "block"

    def _update_knowledge_badge(self) -> None:
        """更新知识库待审核草稿徽标。"""
        badge = self.query_one("#knowledge-badge", Static)
        try:
            pending = self._count_pending_knowledge()
            if pending > 0:
                badge.update(f"[dim yellow]📚 {_('knowledge.badge_pending', n=pending)}[/]")
            else:
                badge.update("")
        except Exception:
            badge.update("")

    def _count_pending_knowledge(self) -> int:
        """统计所有 project 中待审核的知识草稿数。"""
        from ..constants import KNOWLEDGE_PROMOTION_ARTIFACT
        count = 0
        # 检查当前项目的 phases
        if self._active_project:
            phases = self._active_project / ".harness/phases"
            if phases.exists():
                for phase_dir in phases.iterdir():
                    if phase_dir.is_dir():
                        promo = phase_dir / KNOWLEDGE_PROMOTION_ARTIFACT
                        if promo.exists():
                            # 检查是否已被 accept（对应 knowledge/ 中有条目）
                            count += 1
        return count

    # ── Actions ──

    def action_refresh(self) -> None:
        """F5: 刷新全部。"""
        sidebar = self.query_one(ProjectList)
        sidebar.reload()
        if self._active_project:
            self.load_project(self._active_project)

    def on_project_list_selected(self, event: ProjectList.Selected) -> None:
        """ProjectList 发送 Selected 消息时加载项目。"""
        self.load_project(Path(event.path))
        self.notify(f"Loaded: {Path(event.path).name}")

    def action_new_run(self) -> None:
        """Ctrl+N: 在当前活动项目新建 Run。"""
        if not self._active_project:
            self.notify("Select a project first (Enter)", severity="warning")
            return

        project_path = self._active_project

        def _on_done(request: NewRunRequest | None) -> None:
            if request is None:
                return
            try:
                state = create_state_for_new_run(project_path, self._workflow, request)
                state.save(str(project_path))
                state.save_snapshot(str(project_path))
                self.load_project(project_path)
                self.notify(f"Created run: {request.run_id}", severity="information")
            except Exception as e:
                self.notify(f"Failed: {e}", severity="error")

        self.push_screen(NewRunModal(), _on_done)
