"""harness list — 列出所有保存的 runs。"""

from __future__ import annotations

import json
from pathlib import Path

import typer

from ..core.state import list_runs
from ..ui.console import print_list


def list_runs_cmd(
    status_filter: str = typer.Option("", "--status", "-s", help="Filter by status (DONE, DEVELOPING, BLOCKED)"),
    intent_filter: str = typer.Option("", "--intent", "-i", help="Filter by intent (FEATURE, BUG_FIX, etc)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List all saved workflow runs."""
    root = Path.cwd()
    runs = list_runs(str(root))

    # 过滤
    if status_filter:
        runs = [r for r in runs if r["status"].upper() == status_filter.upper()]
    if intent_filter:
        runs = [r for r in runs if r["intent"].upper() == intent_filter.upper()]

    if json_output:
        print(json.dumps(runs, indent=2, ensure_ascii=False))
        return

    print_list(runs)
