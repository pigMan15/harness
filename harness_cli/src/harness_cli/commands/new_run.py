"""harness new — 创建新的 workflow run。"""

from __future__ import annotations

import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..core.state import HarnessState, Intent, Risk
from ..core.workflow import Workflow
from ..constants import THEME

console = Console()


def new(
    run_id: str = typer.Argument(..., help="Unique run identifier (e.g. feat-login-001)"),
    intent: str = typer.Option("FEATURE", "--intent", "-i", help="Task intent: QUERY, BUG_FIX, FEATURE, REFACTOR, DEPLOYMENT, INCIDENT"),
    risk: str = typer.Option("MEDIUM", "--risk", "-r", help="Risk level: NA, LOW, MEDIUM, HIGH"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite if run already exists"),
) -> None:
    """Create a new harness workflow run."""
    root = Path.cwd()

    # 校验枚举值
    try:
        intent_enum = Intent(intent.upper())
    except ValueError:
        valid = ", ".join(i.value for i in Intent if i != Intent.UNKNOWN)
        console.print(f"[red]Invalid intent:[/] {intent}. Must be one of: {valid}")
        raise typer.Exit(1)

    try:
        risk_enum = Risk(risk.upper())
    except ValueError:
        valid = ", ".join(r.value for r in Risk if r != Risk.UNKNOWN)
        console.print(f"[red]Invalid risk:[/] {risk}. Must be one of: {valid}")
        raise typer.Exit(1)

    # 检查是否已存在
    phase_dir = Path(root) / ".harness/phases" / run_id
    run_dir = Path(root) / ".harness/runs" / run_id

    if (phase_dir.exists() or run_dir.exists()) and not force:
        console.print(f"[red]Run already exists:[/] {run_id}. Use --force to overwrite.")
        raise typer.Exit(1)

    # 加载 workflow 获取路由
    try:
        workflow = Workflow.load(str(root))
    except FileNotFoundError:
        console.print("[red]Error:[/] .harness/workflow.yaml not found. Run 'bridle init' first.")
        raise typer.Exit(1)

    required_nodes = workflow.route(intent_enum.value, risk_enum.value)
    if not required_nodes:
        console.print(f"[yellow]Warning:[/] No route found for {intent_enum.value}/{risk_enum.value}")
        required_nodes = []

    # 创建目录
    phase_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)

    # 创建状态
    state = HarnessState.create_new(run_id, intent_enum, risk_enum, root=str(root))
    state.required_nodes = required_nodes

    # 保存
    state.save(str(root))
    state.save_snapshot(str(root))

    # 输出
    table = Table(title="New Run Created", border_style=THEME["primary"])
    table.add_column("Field", style="dim")
    table.add_column("Value", style="bold")
    table.add_row("Run ID", state.run_id)
    table.add_row("Intent", intent_enum.value)
    table.add_row("Risk", risk_enum.value)
    table.add_row("Required Nodes", f"{len(required_nodes)} ({', '.join(required_nodes[:5])}{'...' if len(required_nodes) > 5 else ''})")
    table.add_row("Phase Dir", state.phase_dir)
    table.add_row("Status", state.status.value)
    console.print(table)

    # 自动拉取共享知识库
    try:
        from ..core.knowledge import KnowledgeConfig, SyncManager
        cfg = KnowledgeConfig.load(str(root))
        if cfg.remote_url and cfg.auto_pull:
            mgr = SyncManager(str(root), cfg)
            ok, msg = mgr.pull()
            if ok:
                console.print(f"[dim]Knowledge pulled: {msg}[/]")
            else:
                console.print(f"[dim]Knowledge pull skipped: {msg}[/]")
    except Exception:
        pass  # 知识库拉取失败不应阻塞 run 创建

    console.print()
    console.print(f"[dim]Next: dispatcher will route to the first required node.[/]")
