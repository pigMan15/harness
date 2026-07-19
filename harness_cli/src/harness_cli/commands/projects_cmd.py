"""harness projects / register / unregister — 全局项目管理。"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..constants import THEME
from ..core.state import HarnessState

console = Console()

# 全局注册表文件
REGISTRY_DIR = Path.home() / ".bridle"
REGISTRY_PATH = REGISTRY_DIR / "projects.json"


def _load_registry() -> dict:
    """加载全局项目注册表。"""
    if not REGISTRY_PATH.exists():
        return {"projects": []}
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, KeyError):
        return {"projects": []}


def _save_registry(data: dict) -> None:
    """保存注册表。"""
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _register_project(root_path: str, silent: bool = False) -> bool:
    """内部注册逻辑：注册成功返回 True。不抛 typer.Exit，可被 init 等命令安全调用。"""
    root = Path(root_path).resolve()
    if not (root / ".harness").is_dir():
        if not silent:
            console.print(f"[red]Error:[/] No .harness/ found in {root}")
        return False

    registry = _load_registry()
    existing = [p for p in registry["projects"] if Path(p["path"]).resolve() == root]
    if existing:
        return False  # 已注册

    registry["projects"].append({
        "name": root.name,
        "path": str(root),
        "added_at": datetime.now(timezone.utc).isoformat(),
    })
    _save_registry(registry)

    if not silent:
        console.print(f"[green]+[/] Registered: {root.name} ({root})")
    return True


def register(
    path: str = typer.Option(".", "--path", "-p", help="Project directory path"),
) -> None:
    """Register a harness project for global tracking."""
    if not _register_project(path):
        raise typer.Exit(1)


def unregister(
    path: str = typer.Argument(..., help="Project path or name to unregister"),
) -> None:
    """Remove a project from global tracking."""
    registry = _load_registry()
    before = len(registry["projects"])

    registry["projects"] = [
        p for p in registry["projects"]
        if p["name"] != path and p["path"] != path and str(Path(p["path"]).resolve()) != str(Path(path).resolve())
    ]

    if len(registry["projects"]) == before:
        console.print(f"[yellow]Not found:[/] {path}")
        raise typer.Exit(1)

    _save_registry(registry)
    console.print(f"[green]-[/] Unregistered: {path}")


def projects(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List all registered harness projects and their active run status."""
    registry = _load_registry()

    if not registry["projects"]:
        console.print("[dim]No registered projects.[/]")
        console.print(f"Run 'bridle register --path <dir>' to add one.")
        return

    # 收集每个项目的信息
    rows = []
    for p in registry["projects"]:
        proj_path = Path(p["path"])
        if not proj_path.exists():
            status = "MISSING"
            run = "-"
            nodes = "-"
        elif not (proj_path / ".harness").is_dir():
            status = "NO_HARNESS"
            run = "-"
            nodes = "-"
        else:
            try:
                state = HarnessState.load(str(proj_path))
                status = state.status.value
                run = state.run_id
                completed, total = state.progress()
                nodes = f"{completed}/{total}"
            except Exception:
                status = "ERROR"
                run = "-"
                nodes = "-"

        rows.append({
            "name": p["name"],
            "path": p["path"],
            "status": status,
            "run": run,
            "nodes": nodes,
        })

    if json_output:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return

    table = Table(title="Harness Projects", border_style=THEME["primary"])
    table.add_column("Project", style="bold")
    table.add_column("Status")
    table.add_column("Active Run")
    table.add_column("Progress")
    table.add_column("Path", style="dim")

    for r in rows:
        if r["status"] == "DONE":
            icon = "[green]DONE[/]"
        elif r["status"] in ("DEVELOPING", "IN_PROGRESS", "VERIFYING"):
            icon = f"[yellow]{r['status']}[/]"
        elif r["status"] in ("BLOCKED", "ERROR"):
            icon = f"[red]{r['status']}[/]"
        elif r["status"] == "IDLE":
            icon = "[dim]IDLE[/]"
        else:
            icon = f"[dim]{r['status']}[/]"

        table.add_row(r["name"], icon, r["run"], r["nodes"], r["path"])

    console.print(table)
