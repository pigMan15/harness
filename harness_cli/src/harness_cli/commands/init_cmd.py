"""harness init — 初始化 .harness/ 结构到项目目录。"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..constants import (
    HARNESS_DIR, HARNESS_ENTRY_MARKER_START, HARNESS_ENTRY_MARKER_END,
    HARNESS_ENTRY_BLOCK, AGENTS_FILE, CLAUDE_FILE, THEME,
)
from ..core.validate import Validator
from ..ui.console import print_validation, print_success, print_error, print_info

console = Console()

# 内置模板目录（相对于 CLI 安装位置）
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def _get_templates_dir() -> Path:
    """返回内置模板目录。开发时在 package 内，PyInstaller 打包后通过 sys._MEIPASS。"""
    import sys
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", "."))
        return base / "templates"
    return _TEMPLATES_DIR


def _has_harness_entry(file_path: Path) -> bool:
    """检查文件是否已包含 harness 入口标记块。"""
    if not file_path.exists():
        return False
    content = file_path.read_text(encoding="utf-8")
    return HARNESS_ENTRY_MARKER_START in content


def _append_harness_entry(file_path: Path) -> bool:
    """向文件追加 harness 入口块。已存在则跳过。返回是否实际写入。"""
    if _has_harness_entry(file_path):
        return False
    content = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
    if content and not content.endswith("\n"):
        content += "\n"
    content += "\n" + HARNESS_ENTRY_BLOCK
    file_path.write_text(content, encoding="utf-8")
    return True


def _replace_harness_entry(file_path: Path) -> bool:
    """替换已有的 harness 入口块为新版本。无旧块时追加。返回是否实际写入。"""
    if not file_path.exists():
        file_path.write_text(HARNESS_ENTRY_BLOCK + "\n", encoding="utf-8")
        return True

    content = file_path.read_text(encoding="utf-8")
    if HARNESS_ENTRY_MARKER_START not in content:
        # 无旧块，追加
        return _append_harness_entry(file_path)

    # 替换标记块之间的内容
    start = content.find(HARNESS_ENTRY_MARKER_START)
    end = content.find(HARNESS_ENTRY_MARKER_END)
    if end != -1:
        end += len(HARNESS_ENTRY_MARKER_END)
        # 找到块结束后的换行
        while end < len(content) and content[end] in ("\r", "\n"):
            end += 1
        new_content = content[:start] + HARNESS_ENTRY_BLOCK + "\n" + content[end:]
    else:
        # 有 START 无 END，替换从 START 到文件尾
        new_content = content[:start] + HARNESS_ENTRY_BLOCK + "\n"

    file_path.write_text(new_content, encoding="utf-8")
    return True


def _copy_templates(target: Path, dry_run: bool = False) -> list[str]:
    """复制内置模板到目标目录。返回创建的文件列表。"""
    templates_dir = _get_templates_dir()
    created: list[str] = []

    if not templates_dir.exists():
        console.print(f"[yellow]Warning:[/] Templates directory not found: {templates_dir}")
        return created

    for item in templates_dir.rglob("*"):
        if item.is_dir():
            continue
        rel = item.relative_to(templates_dir)
        dest = target / rel
        if dest.exists():
            continue  # 不覆盖已有文件
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)
        created.append(str(rel))

    return created


def init(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation; update harness entry blocks"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without writing"),
    repair: bool = typer.Option(False, "--repair", help="Only fill missing template files, don't touch existing"),
    no_validate: bool = typer.Option(False, "--no-validate", help="Skip final validation"),
) -> None:
    """Initialize .harness/ structure in the current directory.

    Auto-detects: new project (no .harness/) or existing project (has .harness/).
    AGENTS.md / CLAUDE.md are appended to, never overwritten.
    """
    root = Path.cwd()
    has_harness = (root / HARNESS_DIR).is_dir()

    # ── 场景：已有 .harness/ ──
    if has_harness:
        if repair:
            # repair 模式：只补全缺失文件
            created = _copy_templates(root, dry_run=dry_run)
            if dry_run:
                console.print("[bold]Would add missing files:[/]")
                for f in created:
                    console.print(f"  + {f}")
                return
            if created:
                console.print(f"[green]Added {len(created)} missing template file(s):[/]")
                for f in created:
                    console.print(f"  + {f}")
            else:
                console.print("[dim]All template files present. Nothing to repair.[/]")
        else:
            # 已有 .harness/，只做健康检查
            console.print(Panel(
                Text.assemble(
                    (".harness/ already exists\n", "dim"),
                    ("Run 'bridle validate' to check structure health.\n", ""),
                    ("Use 'bridle init --repair' to fill missing files.", ""),
                ),
                title="Harness Status",
                border_style=THEME["secondary"],
            ))

        if not no_validate and not dry_run:
            v = Validator(str(root))
            report = v.validate()
            print_validation(report)
        return

    # ── 场景：新项目 ──
    # 列出将要做什么
    actions: list[str] = []
    agents_exists = (root / AGENTS_FILE).exists()
    claude_exists = (root / CLAUDE_FILE).exists()

    if agents_exists:
        if force or not _has_harness_entry(root / AGENTS_FILE):
            actions.append(f"Append harness entry to {AGENTS_FILE}")
    else:
        actions.append(f"Create {AGENTS_FILE}")

    if claude_exists:
        if force or not _has_harness_entry(root / CLAUDE_FILE):
            actions.append(f"Append harness entry to {CLAUDE_FILE}")
    else:
        actions.append(f"Create {CLAUDE_FILE}")

    actions.append(f"Create .harness/ (full template)")

    # 预览
    console.print(Panel(
        Text.assemble(
            ("Directory: ", "dim"), (str(root), "bold"), ("\n", ""),
            ("Status: ", "dim"), ("No .harness/ found", THEME["warning"]), ("\n\n", ""),
            ("Will:\n", "bold"),
            *[(f"  - {a}\n", "") for a in actions],
        ),
        title="Harness Init",
        border_style=THEME["primary"],
    ))

    if dry_run:
        return

    # 确认
    if not force:
        answer = typer.confirm("Proceed?", default=True)
        if not answer:
            console.print("[dim]Cancelled.[/]")
            return

    # 执行
    # 1. 处理 AGENTS.md
    if force and agents_exists:
        _replace_harness_entry(root / AGENTS_FILE)
        print_success(f"Updated harness entry in {AGENTS_FILE}")
    elif agents_exists:
        if _append_harness_entry(root / AGENTS_FILE):
            print_success(f"Appended harness entry to {AGENTS_FILE}")
        else:
            print_info(f"{AGENTS_FILE} already has harness entry - skipped")
    else:
        (root / AGENTS_FILE).write_text(HARNESS_ENTRY_BLOCK + "\n", encoding="utf-8")
        print_success(f"Created {AGENTS_FILE}")

    # 2. 处理 CLAUDE.md
    if force and claude_exists:
        _replace_harness_entry(root / CLAUDE_FILE)
        print_success(f"Updated harness entry in {CLAUDE_FILE}")
    elif claude_exists:
        if _append_harness_entry(root / CLAUDE_FILE):
            print_success(f"Appended harness entry to {CLAUDE_FILE}")
        else:
            print_info(f"{CLAUDE_FILE} already has harness entry - skipped")
    else:
        (root / CLAUDE_FILE).write_text(HARNESS_ENTRY_BLOCK + "\n", encoding="utf-8")
        print_success(f"Created {CLAUDE_FILE}")

    # 3. 复制模板
    created = _copy_templates(root)
    print_success(f"Created .harness/ ({len(created)} files)")

    # 4. 最终校验
    if not no_validate:
        console.print()
        v = Validator(str(root))
        report = v.validate()
        print_validation(report)

    console.print()
    console.print("[bold]Next steps:[/]")
    console.print(f"  1. Edit .harness/rules/build.md to set your build/test commands")
    console.print(f"  2. Run 'bridle new <id> --intent FEATURE --risk MEDIUM' to start your first run")
