"""harness save — 保存当前 run 状态快照。"""

from __future__ import annotations

from pathlib import Path

import typer

from ..core.state import HarnessState
from ..ui.console import print_success, print_error


def save() -> None:
    """Save current run state to .harness/runs/<run_id>/state.json."""
    root = Path.cwd()

    try:
        state = HarnessState.load(str(root))
    except FileNotFoundError as e:
        print_error(str(e))
        raise typer.Exit(1)

    snapshot_path = state.save_snapshot(str(root))
    print_success(f"Snapshot saved: {snapshot_path}")
    print(f"  Run: {state.run_id}  Status: {state.status.value}  Node: {state.current_node}")
