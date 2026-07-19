"""NewRunModal — 新建 Run 的对话框。"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select


class NewRunModal(ModalScreen[str | None]):
    """新建 Run 弹窗。

    返回: run_id 字符串，取消时返回 None。
    """

    CSS = """
    NewRunModal {
        align: center middle;
    }
    #new-run-dialog {
        width: 50;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    #new-run-dialog Label {
        width: 12;
    }
    #new-run-dialog Input {
        width: 1fr;
    }
    #new-run-dialog Select {
        width: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="new-run-dialog"):
            yield Label("New Run", classes="section-title")
            with Grid(id="form-grid"):
                yield Label("Run ID:")
                yield Input(placeholder="feat-login-001", id="run-id")
                yield Label("Intent:")
                yield Select(
                    [("Feature", "FEATURE"), ("Bug Fix", "BUG_FIX"), ("Refactor", "REFACTOR"),
                     ("Query", "QUERY"), ("Deployment", "DEPLOYMENT"), ("Incident", "INCIDENT")],
                    value="FEATURE", id="intent",
                )
                yield Label("Risk:")
                yield Select(
                    [("Low", "LOW"), ("Medium", "MEDIUM"), ("High", "HIGH")],
                    value="MEDIUM", id="risk",
                )
            with Horizontal():
                yield Button("Create", variant="primary", id="btn-create")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-create":
            run_id = self.query_one("#run-id", Input).value.strip()
            if not run_id:
                self.notify("Run ID cannot be empty", severity="error")
                return
            self.dismiss(run_id)
        else:
            self.dismiss(None)
