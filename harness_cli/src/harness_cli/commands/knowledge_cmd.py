"""harness knowledge — 知识库管理子命令组。

bridle knowledge init       初始化知识库目录结构
bridle knowledge remote     绑定共享远程仓库
bridle knowledge extract    从 run 提取知识
bridle knowledge review     审阅候选知识条目
bridle knowledge accept     确认写入知识库
bridle knowledge list       列出知识条目
bridle knowledge search     搜索知识
bridle knowledge push       推送到共享仓库
bridle knowledge pull       从共享仓库拉取
bridle knowledge diff       查看待同步变更
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from ..constants import (
    THEME, KNOWLEDGE_DIR, KNOWLEDGE_DOMAINS, KNOWLEDGE_PROMOTION_ARTIFACT,
)
from ..core.knowledge import (
    KnowledgeEntry, KnowledgeIndex, KnowledgeConfig, KnowledgePriority, KnowledgeDomain, SyncManager,
)
from ..core.i18n import _
from ..ui.console import print_error, print_success, print_info

console = Console()
knowledge_app = typer.Typer(name="knowledge", help=_("knowledge.title"))


# ──────────────────────────────────────────────
# init
# ──────────────────────────────────────────────
@knowledge_app.command(name="init")
def knowledge_init(
    force: bool = typer.Option(False, "--force", "-f", help="Recreate even if exists"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview only"),
) -> None:
    """Initialize the knowledge base directory structure."""
    root = Path.cwd()
    knowledge_root = root / KNOWLEDGE_DIR

    if knowledge_root.exists() and not force:
        console.print(Panel(f"[yellow]{_('knowledge.init_exists')}[/]\n{knowledge_root}",
                            title=_("knowledge.init_title")))
        return

    if dry_run:
        console.print(Panel(_("knowledge.init_dry"), title=_("knowledge.init_title")))
        for d in KNOWLEDGE_DOMAINS:
            console.print(f"  {knowledge_root / d}/")
        return

    # 创建目录结构
    dirs_created: list[str] = []
    for domain in KNOWLEDGE_DOMAINS:
        d = knowledge_root / domain
        d.mkdir(parents=True, exist_ok=True)
        (d / ".gitkeep").touch(exist_ok=True)
        dirs_created.append(str(d))

    # private/.gitignore
    gitignore = knowledge_root / "private" / ".gitignore"
    gitignore.write_text("*\n", encoding="utf-8")

    # SYNC.yaml
    KnowledgeConfig().save(str(root))

    # index.md
    index_path = knowledge_root / "index.md"
    index_path.write_text(
        "# Knowledge Index\n\n"
        "| ID | Title | Type | Priority | Domain | Source | Updated |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n",
        encoding="utf-8",
    )

    console.print(Panel(
        f"[green]{_('knowledge.init_created', dir=str(knowledge_root))}[/]\n"
        + "\n".join(f"  [dim]✓[/] {d}" for d in dirs_created),
        title=_("knowledge.init_title"),
    ))


# ──────────────────────────────────────────────
# remote
# ──────────────────────────────────────────────
@knowledge_app.command(name="remote")
def knowledge_remote(
    url: str = typer.Argument("", help="Remote git URL for shared knowledge"),
) -> None:
    """Set or view the shared knowledge remote URL."""
    root = Path.cwd()
    cfg = KnowledgeConfig.load(str(root))

    if not url:
        if cfg.remote_url:
            console.print(f"[bold]{_('knowledge.remote_current', url=cfg.remote_url)}[/]")
        else:
            console.print(f"[dim]{_('knowledge.remote_none')}[/]")
        return

    # 基本 URL 校验
    if not (url.startswith("http://") or url.startswith("https://")
            or url.startswith("git@") or url.endswith(".git")):
        print_error(_("knowledge.remote_invalid", url=url))
        raise typer.Exit(1)

    cfg.remote_url = url
    cfg.save(str(root))
    print_success(_("knowledge.remote_set", url=url))


# ──────────────────────────────────────────────
# extract
# ──────────────────────────────────────────────
@knowledge_app.command(name="extract")
def knowledge_extract(
    run_id: str = typer.Argument(..., help="Run ID to extract knowledge from"),
) -> None:
    """Extract incremental engineering knowledge from a completed run."""
    root = Path.cwd()
    phase_dir = root / ".harness/phases" / run_id

    if not phase_dir.exists():
        print_error(_("knowledge.extract_no_run", id=run_id))
        raise typer.Exit(1)

    # 读取 run 的基本信息
    state_file = root / ".harness/runs" / run_id / "state.json"
    run_info: dict = {}
    if state_file.exists():
        try:
            run_info = json.loads(state_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    # 读取 evidence
    evidence = {}
    evidence_file = phase_dir / "15-evidence.json"
    if evidence_file.exists():
        try:
            evidence = json.loads(evidence_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    # 读取 acceptance report
    acceptance_text = ""
    acceptance_file = phase_dir / "18-acceptance-report.md"
    if acceptance_file.exists():
        acceptance_text = acceptance_file.read_text(encoding="utf-8")

    # 生成候选知识条目 —— 基于简单的模式提取
    # 实际 AI 驱动提取由 knowledge-keeper agent 完成
    candidates: list[dict] = []

    # 从 evidence 提取
    residual_risks = evidence.get("residual_risks", [])
    for risk in residual_risks:
        slug = re.sub(r"[^a-z0-9]+", "-", str(risk)[:60].lower()).strip("-")
        candidates.append({
            "id": f"risk-{run_id}-{slug[:40]}",
            "title": str(risk)[:120],
            "type": "pitfall",
            "priority": "P1",
            "domain": "engineering",
            "confidence": 0.6,
        })

    waivers = evidence.get("waivers", [])
    for waiver in waivers:
        slug = re.sub(r"[^a-z0-9]+", "-", str(waiver)[:60].lower()).strip("-")
        candidates.append({
            "id": f"waiver-{run_id}-{slug[:40]}",
            "title": str(waiver)[:120],
            "type": "case",
            "priority": "P2",
            "domain": "operations",
            "confidence": 0.4,
        })

    # 写入 19-knowledge-promotion.md
    promotion_lines = [
        "# 知识沉淀草稿",
        "",
        "## 来源",
        "",
        f"- RunId: {run_id}",
        f"- Intent: {run_info.get('intent', '?')}",
        f"- Risk: {run_info.get('risk', '?')}",
    ]

    if candidates:
        promotion_lines += [
            "",
            "## 候选知识",
            "",
            "| 类型 | 标题 | 优先级 | 领域 | 置信度 |",
            "| --- | --- | --- | --- | --- |",
        ]
        for c in candidates:
            promotion_lines.append(
                f"| {c['type']} | {c['title'][:60]} | {c['priority']} | {c['domain']} | {c['confidence']} |"
            )
        promotion_lines += [
            "",
            "## 待用户确认",
            "",
            "- 请逐条审阅候选知识，确认后运行 `bridle knowledge accept <run-id>`",
        ]
    else:
        promotion_lines += [
            "",
            "## 无候选知识",
            "",
            "本次 run 未产生值得沉淀的增量工程知识。",
        ]

    promotion_text = "\n".join(promotion_lines)
    output_path = phase_dir / KNOWLEDGE_PROMOTION_ARTIFACT
    output_path.write_text(promotion_text, encoding="utf-8")

    table = Table(title=_("knowledge.extract_title"), border_style=THEME["primary"])
    table.add_column(_("knowledge.col_type"), style="cyan")
    table.add_column(_("knowledge.col_title"), style="bold")
    table.add_column(_("knowledge.col_priority"), style="yellow")
    table.add_column(_("knowledge.col_domain"), style="dim")
    for c in candidates:
        table.add_row(c["type"], c["title"][:60], c["priority"], c["domain"])

    if candidates:
        console.print(table)
    print_success(_("knowledge.extract_generated", file=KNOWLEDGE_PROMOTION_ARTIFACT, n=len(candidates)))


# ──────────────────────────────────────────────
# review
# ──────────────────────────────────────────────
@knowledge_app.command(name="review")
def knowledge_review(
    run_id: str = typer.Argument(..., help="Run ID to review promotion draft for"),
) -> None:
    """Review candidate knowledge entries from a run's promotion draft."""
    root = Path.cwd()
    draft_path = root / ".harness/phases" / run_id / KNOWLEDGE_PROMOTION_ARTIFACT

    if not draft_path.exists():
        print_error(_("knowledge.review_no_draft", id=run_id))
        raise typer.Exit(1)

    content = draft_path.read_text(encoding="utf-8")
    console.print(Panel(content, title=_("knowledge.review_title")))


# ──────────────────────────────────────────────
# accept
# ──────────────────────────────────────────────
@knowledge_app.command(name="accept")
def knowledge_accept(
    run_id: str = typer.Argument(..., help="Run ID whose promotion draft to accept"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview only, don't write"),
    entry_id: Optional[str] = typer.Option(None, "--entry", "-e", help="Accept a single entry by id"),
) -> None:
    """Accept and write promotion draft entries to the knowledge base."""
    root = Path.cwd()
    draft_path = root / ".harness/phases" / run_id / KNOWLEDGE_PROMOTION_ARTIFACT

    if not draft_path.exists():
        print_error(_("knowledge.review_no_draft", id=run_id))
        raise typer.Exit(1)

    index = KnowledgeIndex.load(str(root))

    # 解析草稿中的候选条目
    content = draft_path.read_text(encoding="utf-8")
    entries: list[KnowledgeEntry] = []
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("| ") or line.startswith("| 类型") or line.startswith("| ---"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 5:
            continue

        eid = f"{cols[0]}-{run_id}-{re.sub(r'[^a-z0-9]+', '-', cols[1][:40].lower()).strip('-')}"
        if entry_id and eid != entry_id:
            continue

        entry = KnowledgeEntry(
            id=eid,
            title=cols[1][:120],
            type=cols[0],
            priority=KnowledgePriority(cols[2]) if cols[2] in ("P0", "P1", "P2") else KnowledgePriority.P2,
            domain=KnowledgeDomain(cols[3]) if cols[3] in (d.value for d in KnowledgeDomain) else KnowledgeDomain.ENGINEERING,
            source_run=run_id,
            confidence=float(cols[4]) if len(cols) > 4 else 0.5,
            body=f"来源: {run_id}\n\n{cols[1]}",
        )
        entries.append(entry)

    if dry_run:
        if entries:
            console.print(f"[dim]{_('knowledge.accept_dry', n=len(entries))}[/]")
            for e in entries:
                console.print(f"  [dim]→[/] {e.domain.value}/{e.id}.md  [cyan]{e.title}[/]")
        else:
            console.print("[dim]No entries to accept[/]")
        return

    written = 0
    skipped = 0
    for entry in entries:
        filepath = entry.file_path(str(root))
        filepath.parent.mkdir(parents=True, exist_ok=True)
        if filepath.exists():
            skipped += 1
            continue
        filepath.write_text(entry.to_markdown(), encoding="utf-8")
        index.add(entry)
        written += 1

    if written:
        print_success(_("knowledge.accept_written", n=written))
    if skipped:
        print_info(_("knowledge.accept_skipped", n=skipped))


# ──────────────────────────────────────────────
# list
# ──────────────────────────────────────────────
@knowledge_app.command(name="list")
def knowledge_list(
    domain: str = typer.Option("", "--domain", "-d", help="Filter by domain"),
    priority: str = typer.Option("", "--priority", "-p", help="Filter by priority (P0/P1/P2)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List all knowledge entries."""
    root = Path.cwd()
    index = KnowledgeIndex.load(str(root))

    entries = list(index.entries.values())
    if domain:
        entries = index.list_by_domain(domain)
    if priority:
        try:
            entries = [e for e in entries if e.priority == KnowledgePriority(priority)]
        except ValueError:
            pass

    if json_output:
        console.print(json.dumps([
            {"id": e.id, "title": e.title, "type": e.type, "priority": e.priority.value,
             "domain": e.domain.value, "source_run": e.source_run, "confidence": e.confidence}
            for e in entries
        ], indent=2, ensure_ascii=False))
        return

    if not entries:
        console.print(f"[dim]{_('knowledge.list_empty')}[/]")
        return

    table = Table(title=_("knowledge.list_title"), border_style=THEME["primary"])
    table.add_column(_("knowledge.col_type"), style="cyan")
    table.add_column(_("knowledge.col_title"), style="bold")
    table.add_column(_("knowledge.col_priority"), style="yellow")
    table.add_column(_("knowledge.col_domain"), style="dim")
    table.add_column(_("knowledge.col_source"), style="dim")
    for e in entries:
        table.add_row(e.type, e.title[:60], e.priority.value, e.domain.value, e.source_run)
    console.print(table)


# ──────────────────────────────────────────────
# search
# ──────────────────────────────────────────────
@knowledge_app.command(name="search")
def knowledge_search(
    query: str = typer.Argument(..., help="Search query"),
) -> None:
    """Search the knowledge base."""
    root = Path.cwd()
    index = KnowledgeIndex.load(str(root))
    results = index.search(query)

    if not results:
        console.print(f"[dim]{_('knowledge.search_empty', query=query)}[/]")
        return

    table = Table(title=_("knowledge.search_title", query=query), border_style=THEME["primary"])
    table.add_column(_("knowledge.col_type"), style="cyan")
    table.add_column(_("knowledge.col_title"), style="bold")
    table.add_column(_("knowledge.col_domain"), style="dim")
    for e in results:
        table.add_row(e.type, e.title[:60], e.domain.value)
    console.print(table)


# ──────────────────────────────────────────────
# push / pull / diff
# ──────────────────────────────────────────────
@knowledge_app.command(name="push")
def knowledge_push(
    message: str = typer.Option("", "--message", "-m", help="Commit message"),
) -> None:
    """Push local knowledge to the shared remote."""
    root = Path.cwd()
    cfg = KnowledgeConfig.load(str(root))
    if not cfg.remote_url:
        print_error(_("knowledge.push_no_remote"))
        raise typer.Exit(1)

    mgr = SyncManager(str(root), cfg)
    ok, msg = mgr.push(message)
    if ok:
        print_success(_("knowledge.push_ok", msg=msg))
    else:
        print_error(_("knowledge.push_fail", error=msg))
        raise typer.Exit(1)


@knowledge_app.command(name="pull")
def knowledge_pull() -> None:
    """Pull shared knowledge from the remote."""
    root = Path.cwd()
    cfg = KnowledgeConfig.load(str(root))
    if not cfg.remote_url:
        print_error(_("knowledge.push_no_remote"))
        raise typer.Exit(1)

    mgr = SyncManager(str(root), cfg)
    ok, msg = mgr.pull()
    if ok:
        print_success(_("knowledge.pull_ok", msg=msg))
    else:
        print_error(_("knowledge.pull_fail", error=msg))
        raise typer.Exit(1)


@knowledge_app.command(name="diff")
def knowledge_diff() -> None:
    """Show pending changes between local and remote knowledge."""
    root = Path.cwd()
    cfg = KnowledgeConfig.load(str(root))
    mgr = SyncManager(str(root), cfg)
    output = mgr.diff()

    if not output or output == "no changes":
        console.print(f"[dim]{_('knowledge.diff_empty')}[/]")
        return

    console.print(Panel(Syntax(output, "diff", theme="monokai"), title=_("knowledge.diff_title")))
