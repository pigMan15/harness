"""GatesGrid — 门禁状态面板（4×2 网格）。"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Static

from ...core.state import HarnessState
from ...core.gates import GateEvaluator


class GatesGrid(Static):
    """门禁网格面板：4×2 布局显示 8 道门禁状态。"""

    def compose(self) -> ComposeResult:
        yield Static("Gates", classes="section-title")
        yield Static("", id="gates-content")

    def update_gates(self, state: HarnessState, evaluator: GateEvaluator, root: str) -> None:
        """更新门禁显示。

        Args:
            state: 当前 HarnessState
            evaluator: 已加载的 GateEvaluator
            root: 项目根目录路径
        """
        results = evaluator.evaluate_all(state, root)
        content = self.query_one("#gates-content", Static)

        lines: list[str] = []
        row: list[str] = []

        for i, r in enumerate(results):
            if r.status == "PASS":
                icon = "✅"
            elif r.status == "WAIVED":
                icon = "⚠️"
            elif r.status == "NOT_REQUIRED":
                icon = "—"
            elif r.status in ("FAIL", "BLOCKED"):
                icon = "❌"
            else:
                icon = "⬜"

            gid = r.gate_id.replace("G", "").replace("_", " ")
            row.append(f"  {icon} {gid}")

            if len(row) == 4 or i == len(results) - 1:
                lines.append("    ".join(row))
                row = []

        content.update("\n".join(lines))
