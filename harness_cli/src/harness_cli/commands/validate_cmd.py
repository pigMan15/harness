"""harness validate — 校验 .harness/ 结构完整性。"""

from __future__ import annotations

import json
from pathlib import Path

import typer

from ..core.validate import Validator
from ..ui.console import print_validation, print_success


def validate(
    strict: bool = typer.Option(False, "--strict", "-s", help="Treat warnings as errors"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as machine-readable JSON"),
) -> None:
    """Validate .harness/ structure integrity."""
    root = Path.cwd()
    v = Validator(str(root), strict=strict)
    report = v.validate()

    if json_output:
        print(json.dumps({
            "passed": report.passed,
            "errors": [{"level": e.level, "message": e.message, "file": e.file} for e in report.errors],
            "warnings": [{"level": w.level, "message": w.message, "file": w.file} for w in report.warnings],
        }, indent=2, ensure_ascii=False))
        return

    print_validation(report)
    if report.passed:
        raise typer.Exit(0)
    else:
        raise typer.Exit(1)
