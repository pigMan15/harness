"""harness status — 查看当前 run 状态。"""

from __future__ import annotations

import json
from pathlib import Path

import typer

from ..core.state import HarnessState
from ..core.workflow import Workflow
from ..ui.console import print_status, print_error

console_global = None  # 延迟导入避免 TUI 模式冲突


def status(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Show current run status: progress, nodes, and gates summary."""
    root = Path.cwd()

    try:
        state = HarnessState.load(str(root))
        workflow = Workflow.load(str(root))
    except FileNotFoundError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Failed to load state: {e}")
        raise typer.Exit(1)

    if json_output:
        # 机器可读输出
        completed, total = state.progress()
        print(json.dumps({
            "run_id": state.run_id,
            "status": state.status.value,
            "intent": state.intent.value,
            "risk": state.risk.value,
            "current_node": state.current_node,
            "next_role": state.next_role,
            "progress": {"completed": completed, "total": total, "pct": round(state.progress_pct(), 2)},
            "completed_nodes": state.completed_nodes,
            "required_nodes": state.required_nodes,
            "gates": state.gates,
            "last_updated": state.last_updated,
        }, indent=2, ensure_ascii=False))
        return

    print_status(state, workflow)
