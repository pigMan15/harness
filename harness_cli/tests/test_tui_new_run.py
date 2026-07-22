"""Tests for TUI new-run behavior."""

from pathlib import Path

from harness_cli.core.workflow import Workflow
from harness_cli.ui.dashboard import create_state_for_new_run
from harness_cli.ui.widgets.new_run_modal import NewRunRequest


def test_tui_new_run_uses_selected_intent_and_risk(valid_harness: Path) -> None:
    workflow = Workflow.load(str(valid_harness))
    request = NewRunRequest(run_id="bugfix-001", intent="BUG_FIX", risk="LOW")

    state = create_state_for_new_run(valid_harness, workflow, request)

    assert state.run_id == "bugfix-001"
    assert state.intent.value == "BUG_FIX"
    assert state.risk.value == "LOW"
    assert state.required_nodes == workflow.route("BUG_FIX", "LOW")
