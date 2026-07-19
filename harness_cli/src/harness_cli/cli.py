"""Bridle standalone entry point — PyInstaller friendly (no relative imports)."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from harness_cli import __version__
from harness_cli.core.i18n import set_lang
from harness_cli.ui.console import print_version
from harness_cli.commands.init_cmd import init
from harness_cli.commands.new_run import new
from harness_cli.commands.status_cmd import status
from harness_cli.commands.validate_cmd import validate
from harness_cli.commands.switch_run import switch
from harness_cli.commands.list_runs import list_runs_cmd
from harness_cli.commands.gates_cmd import gates
from harness_cli.commands.save_run import save
from harness_cli.commands.projects_cmd import register, unregister, projects
from harness_cli.commands.knowledge_cmd import knowledge_app

app = typer.Typer(
    name="bridle",
    help="AI Coding Harness CLI",
    no_args_is_help=False,
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Show version and exit"),
    lang: str = typer.Option("", "--lang", "-L", help="Language: en, zh"),
) -> None:
    if lang:
        set_lang(lang)
    if version:
        print_version(__version__)
        return
    if ctx.invoked_subcommand is None:
        from harness_cli.app import launch_tui
        launch_tui()


app.command(name="init")(init)
app.command(name="new")(new)
app.command(name="status")(status)
app.command(name="validate")(validate)
app.command(name="switch")(switch)
app.command(name="list")(list_runs_cmd)
app.command(name="gates")(gates)
app.command(name="save")(save)
app.command(name="register")(register)
app.command(name="unregister")(unregister)
app.command(name="projects")(projects)
app.add_typer(knowledge_app, name="knowledge")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
