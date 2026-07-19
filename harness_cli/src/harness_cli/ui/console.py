"""Rich 美化输出：CLI 命令的单次渲染（非 TUI 模式）。"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from rich.table import Table
from rich.text import Text

from ..constants import THEME, BANNER
from ..core.state import HarnessState
from ..core.workflow import Workflow
from ..core.gates import GateResult

console = Console()


# ---- 版号 & 启动画面 ----


def print_banner(version: str) -> None:
    """打印 ASCII 启动画面 + 版本信息。"""
    console.print(BANNER.strip("\n"), style=THEME["primary"])
    console.print(f"         bridle v{version}    schema 1.0", style="dim")
    console.print()


def print_version(version: str, schema_version: str = "1.0") -> None:
    """打印简洁版本信息。"""
    console.print(f"bridle v{version}  (harness schema: {schema_version})", style=THEME["primary"])
    console.print("Python 3.11+  -  Textual 0.50+  -  Rich 13.0+", style="dim")


# ---- 状态输出 ----


def print_status(state: HarnessState, workflow: Workflow) -> None:
    """harness status 的 Rich 渲染。"""
    completed, total = state.progress()
    pct = state.progress_pct()

    # 标题面板
    title = Text.assemble(
        ("Run: ", "dim"),
        (state.run_id, "bold"),
        ("    Intent: ", "dim"),
        (state.intent.value, THEME["secondary"]),
        ("    Risk: ", "dim"),
        (state.risk.value, state.risk.value == "HIGH" and THEME["error"] or THEME["warning"]),
    )
    console.print(Panel(title, title="Bridle Status", border_style=THEME["primary"]))

    # 进度条
    progress = Progress(
        TextColumn("  "),
        BarColumn(bar_width=40, style="dim", complete_style=THEME["primary"]),
        TaskProgressColumn(),
        TextColumn(f"  {completed}/{total} nodes"),
    )
    task = progress.add_task("", total=total, completed=completed)
    console.print(progress)
    console.print()

    # 节点列表
    completed_set = set(state.completed_nodes)
    current_idx = -1
    try:
        current_idx = state.required_nodes.index(state.current_node)
    except ValueError:
        pass

    for i, node_id in enumerate(state.required_nodes):
        if node_id in completed_set:
            icon, style = "+", THEME["success"]
        elif i == current_idx:
            icon, style = ">", THEME["warning"]
        else:
            icon, style = ".", "dim"

        artifact = workflow.artifact_for(node_id) or ""
        role = workflow.role_for(node_id)

        line = Text.assemble(
            "  ", (icon, style), " ",
            (f"{node_id:<28}", ""),
            (f"{artifact:<24}", "dim"),
            (f"<- {role}", "dim italic"),
        )
        if i == current_idx:
            line.stylize("bold")
        console.print(line)

    console.print()

    # 门禁摘要行
    gate_parts: list[Text] = []
    for gid, gstatus in state.gates.items():
        if gstatus == "PASS":
            gs = THEME["success"]; gi = "+"
        elif gstatus == "WAIVED":
            gs = THEME["warning"]; gi = "~"
        elif gstatus == "NOT_REQUIRED":
            gs = "dim"; gi = "-"
        elif gstatus in ("FAIL", "BLOCKED"):
            gs = THEME["error"]; gi = "X"
        else:
            gs = "dim"; gi = "."
        gate_parts.append(Text.assemble((f"{gid} ", ""), (gi, gs)))
    # join with spaces
    result = Text("  ")
    for j, part in enumerate(gate_parts):
        result.append(part)
        if j < len(gate_parts) - 1:
            result.append("  ")
    console.print(result)


# ---- 门禁输出 ----


def print_gates(results: list[GateResult]) -> None:
    """harness gates 的 Rich 渲染。"""
    table = Table(title="Gates", border_style=THEME["primary"])
    table.add_column("Gate", style="bold")
    table.add_column("Status")
    table.add_column("Description")
    table.add_column("Reason", style="dim")

    for r in results:
        if r.status == "PASS":
            status_style = THEME["success"]
            icon = "+ PASS"
        elif r.status in ("WAIVED", "NOT_REQUIRED"):
            status_style = THEME["warning"]
            icon = f"~ {r.status}"
        elif r.status in ("FAIL", "BLOCKED"):
            status_style = THEME["error"]
            icon = f"X {r.status}"
        else:
            status_style = "dim"
            icon = ". NOT_RUN"

        table.add_row(r.gate_id, f"[{status_style}]{icon}[/]", r.description, r.reason)

    console.print(table)


# ---- Run 列表输出 ----


def print_list(runs: list[dict[str, Any]]) -> None:
    """harness list 的 Rich 渲染。"""
    if not runs:
        console.print("[dim]No runs found.[/]")
        return

    table = Table(title="Runs", border_style=THEME["primary"])
    table.add_column("Run ID", style="bold")
    table.add_column("Status")
    table.add_column("Intent")
    table.add_column("Risk")
    table.add_column("Progress")
    table.add_column("Updated", style="dim")

    for r in runs:
        status = r["status"]
        if status == "DONE":
            icon = "[green]DONE[/]"
        elif status in ("DEVELOPING", "VERIFYING"):
            icon = f"[yellow]{status}[/]"
        elif status in ("BLOCKED", "CORRUPTED"):
            icon = f"[red]{status}[/]"
        else:
            icon = f"[dim]{status}[/]"

        total = r["required"]
        completed = r["completed"]
        pct = f"{completed}/{total}" if total else "-"

        risk = r["risk"]
        risk_style = THEME["error"] if risk == "HIGH" else THEME["warning"] if risk == "MEDIUM" else "dim"

        table.add_row(
            r["run_id"], icon, r["intent"],
            f"[{risk_style}]{risk}[/]", pct,
            r.get("last_updated", "")[:16] if r.get("last_updated") else "-",
        )

    console.print(table)


# ---- 校验输出 ----


def print_validation(report: Any) -> None:
    """harness validate 的 Rich 渲染。"""
    if report.passed:
        console.print(Panel("Harness validation passed.", border_style=THEME["success"], style=THEME["success"]))
        return

    if report.errors:
        console.print(f"\n[red]Errors ({len(report.errors)}):[/]")
        for issue in report.errors:
            loc = f" [{issue.file}]" if issue.file else ""
            console.print(f"  [red]x[/] {issue.message}{loc}")
            if issue.detail:
                console.print(f"    [dim]{issue.detail}[/]")

    if report.warnings:
        console.print(f"\n[yellow]Warnings ({len(report.warnings)}):[/]")
        for issue in report.warnings:
            loc = f" [{issue.file}]" if issue.file else ""
            console.print(f"  [yellow]![/] {issue.message}{loc}")

    console.print()


# ---- 简单确认输出 ----


def print_success(message: str) -> None:
    """打印单行成功消息。"""
    console.print(f"[{THEME['success']}]+[/] {message}")


def print_error(message: str) -> None:
    """打印单行错误消息。"""
    console.print(f"[{THEME['error']}]X[/] {message}")


def print_info(message: str) -> None:
    """打印单行信息。"""
    console.print(f"[{THEME['secondary']}]i[/] {message}")
