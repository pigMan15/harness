"""ArtifactPanel — 阶段产物查看面板。

未来用于展示当前 run 的产物文件列表和 Markdown 预览。
Phase 1 MVP 中为占位组件。
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Static


class ArtifactPanel(Static):
    """阶段产物查看器（Phase 2 实现 Markdown 预览）。"""

    def compose(self) -> ComposeResult:
        yield Static("Artifacts", classes="section-title")
        yield Static("  (artifact preview coming in v0.2.0)", id="artifact-placeholder")
