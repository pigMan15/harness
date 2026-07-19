"""harness switch — 切换到历史 run。"""

from __future__ import annotations

from pathlib import Path

import typer

from ..core.state import switch_run, HarnessState
from ..ui.console import print_success, print_error


def switch(
    run_id: str = typer.Argument(..., help="Run ID to restore from .harness/runs/<run_id>/"),
) -> None:
    """Switch to a previously saved run snapshot."""
    root = Path.cwd()

    try:
        state = switch_run(run_id, str(root))
    except FileNotFoundError as e:
        print_error(str(e))
        print_error(f"Available runs can be listed with: bridle list")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Failed to switch run: {e}")
        raise typer.Exit(1)

    print_success(f"Switched to run: {state.run_id}")
    print(f"  Status: {state.status.value}  Intent: {state.intent.value}  Risk: {state.risk.value}")
    print(f"  Phase: {state.phase_dir}")
