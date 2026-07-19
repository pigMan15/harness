"""WorkflowPanel — Workflow 进度面板。"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static, ProgressBar

from ...core.state import HarnessState
from ...core.workflow import Workflow
from ...constants import THEME


class WorkflowPanel(Static):
    """Workflow 进度面板：进度条 + 节点列表。"""

    def compose(self) -> ComposeResult:
        yield Static("Workflow Progress", classes="section-title")
        yield ProgressBar(id="wf-progress", show_eta=False)
        yield Static("", id="wf-nodes")

    def update_state(self, state: HarnessState, workflow: Workflow) -> None:
        """根据当前状态更新进度条和节点列表。

        Args:
            state: 当前 HarnessState
            workflow: 已加载的 Workflow
        """
        # 进度条
        completed, total = state.progress()
        bar = self.query_one("#wf-progress", ProgressBar)
        bar.update(total=total, progress=completed)

        # 节点列表
        nodes_text = self.query_one("#wf-nodes", Static)
        completed_set = set(state.completed_nodes)

        try:
            current_idx = state.required_nodes.index(state.current_node)
        except ValueError:
            current_idx = -1

        lines: list[str] = []
        for i, node_id in enumerate(state.required_nodes):
            if node_id in completed_set:
                icon = "✅"
            elif i == current_idx:
                icon = "🔧"
            else:
                icon = "⬜"

            artifact = workflow.artifact_for(node_id) or ""
            role = workflow.role_for(node_id)
            line = f"  {icon} {node_id:<24}  {artifact:<20}  ({role})"
            lines.append(line)

        nodes_text.update("\n".join(lines))
