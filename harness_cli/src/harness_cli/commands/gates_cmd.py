"""harness gates — 显示门禁状态面板。"""

from __future__ import annotations

import json
from pathlib import Path

import typer

from ..core.state import HarnessState
from ..core.gates import GateEvaluator
from ..ui.console import print_gates, print_error


def gates(
    gate_id: str = typer.Option("", "--gate", "-g", help="Show a specific gate only"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Show gate status for all 8 quality gates."""
    root = Path.cwd()

    try:
        state = HarnessState.load(str(root))
        evaluator = GateEvaluator.load(str(root))
    except FileNotFoundError as e:
        print_error(str(e))
        raise typer.Exit(1)

    if gate_id:
        result = evaluator.evaluate(gate_id, state, str(root))
        results = [result]
    else:
        results = evaluator.evaluate_all(state, str(root))

    if json_output:
        print(json.dumps([
            {"gate_id": r.gate_id, "status": r.status, "description": r.description, "reason": r.reason}
            for r in results
        ], indent=2, ensure_ascii=False))
        return

    print_gates(results)

    # 汇总行
    summary = evaluator.summary(results)
    parts = []
    if summary["pass"]:
        parts.append(f"[green]{summary['pass']} PASS[/]")
    if summary["fail"]:
        parts.append(f"[red]{summary['fail']} FAIL[/]")
    if summary["waived"]:
        parts.append(f"[yellow]{summary['waived']} WAIVED[/]")
    if summary["not_run"]:
        parts.append(f"[dim]{summary['not_run']} NOT_RUN[/]")
    if summary["blocked"]:
        parts.append(f"[red]{summary['blocked']} BLOCKED[/]")
    if summary["not_required"]:
        parts.append(f"[dim]{summary['not_required']} NOT_REQUIRED[/]")

    from rich.console import Console
    Console().print("  " + "  ".join(parts))
