"""知识库核心数据模型：KnowledgeEntry, KnowledgeIndex, KnowledgeConfig, SyncManager。

遵循 core/state.py 的 dataclass + factory 方法模式。
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml


# ---- 常量 ----
DOMAIN_MAP: dict[str, str] = {
    "architecture": "architecture",
    "domain": "domain",
    "engineering": "engineering",
    "operations": "operations",
    "runway": "runway",
    "private": "private",
}


class KnowledgePriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class KnowledgeDomain(str, Enum):
    ARCHITECTURE = "architecture"
    DOMAIN = "domain"
    ENGINEERING = "engineering"
    OPERATIONS = "operations"
    RUNWAY = "runway"
    PRIVATE = "private"


@dataclass
class KnowledgeEntry:
    """单条知识条目。"""

    id: str
    title: str
    type: str  # case, pitfall, pattern, rule, adr
    priority: KnowledgePriority = KnowledgePriority.P2
    domain: KnowledgeDomain = KnowledgeDomain.ENGINEERING
    source_run: str = ""
    author: str = "bridle"
    created: str = ""
    updated: str = ""
    tags: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    confidence: float = 0.5  # 0.0 ~ 1.0
    body: str = ""

    def __post_init__(self) -> None:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if not self.created:
            self.created = now
        if not self.updated:
            self.updated = now

    @classmethod
    def from_markdown(cls, path: Path) -> Optional["KnowledgeEntry"]:
        """从 .md 文件解析 YAML frontmatter + body。"""
        if not path.exists():
            return None
        return cls.from_markdown_text(path.read_text(encoding="utf-8"), str(path))

    @classmethod
    def from_markdown_text(cls, text: str, source_path: str = "") -> Optional["KnowledgeEntry"]:
        """从 markdown 文本解析。"""
        text = text.strip()
        if not text.startswith("---"):
            return None

        parts = text.split("---", 2)
        if len(parts) < 3:
            return None

        try:
            meta = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError:
            return None

        body = parts[2].strip()
        required = ["id", "title", "type"]
        missing = [k for k in required if k not in meta]
        if missing:
            return None

        domain_raw = meta.get("domain", "engineering")
        domain = DOMAIN_MAP.get(domain_raw, "engineering")

        return cls(
            id=meta["id"],
            title=meta["title"],
            type=meta["type"],
            priority=KnowledgePriority(meta.get("priority", "P2")),
            domain=KnowledgeDomain(domain),
            source_run=str(meta.get("source_run", "")),
            author=str(meta.get("author", "bridle")),
            created=str(meta.get("created", "")),
            updated=str(meta.get("updated", "")),
            tags=list(meta.get("tags", [])),
            related=list(meta.get("related", [])),
            confidence=float(meta.get("confidence", 0.5)),
            body=body,
        )

    def to_markdown(self) -> str:
        """序列化为 YAML frontmatter + markdown body。"""
        meta: dict = {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "priority": self.priority.value,
            "domain": self.domain.value,
            "source_run": self.source_run,
            "author": self.author,
            "created": self.created,
            "updated": self.updated,
            "tags": self.tags,
            "related": self.related,
            "confidence": self.confidence,
        }
        yaml_str = yaml.dump(meta, allow_unicode=True, sort_keys=False, default_flow_style=False).strip()
        return f"---\n{yaml_str}\n---\n\n{self.body}\n"

    def file_relpath(self) -> str:
        """推导相对于 knowledge/ 的文件路径。"""
        return f"{self.domain.value}/{self.id}.md"

    def file_path(self, root: str) -> Path:
        """推导绝对文件路径。"""
        from ..constants import KNOWLEDGE_DIR
        return Path(root) / KNOWLEDGE_DIR / self.file_relpath()

    def validate(self) -> list[str]:
        """返回校验问题列表。"""
        issues: list[str] = []
        if not self.id:
            issues.append("id is required")
        if not self.title:
            issues.append("title is required")
        if self.type not in ("case", "pitfall", "pattern", "rule", "adr"):
            issues.append(f"invalid type: {self.type}")
        if self.domain.value not in DOMAIN_MAP:
            issues.append(f"invalid domain: {self.domain.value}")
        if self.confidence < 0.0 or self.confidence > 1.0:
            issues.append(f"confidence out of range: {self.confidence}")
        return issues


@dataclass
class KnowledgeConfig:
    """管理 .harness/knowledge/SYNC.yaml 配置。"""

    remote_url: str = ""
    auto_pull: bool = True
    last_pull: Optional[str] = None
    last_push: Optional[str] = None

    @classmethod
    def load(cls, root: str) -> "KnowledgeConfig":
        """从 SYNC.yaml 加载配置。"""
        from ..constants import KNOWLEDGE_SYNC_FILE
        path = Path(root) / KNOWLEDGE_SYNC_FILE
        if not path.exists():
            return cls()
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            return cls(
                remote_url=str(data.get("remote_url", "")),
                auto_pull=bool(data.get("auto_pull", True)),
                last_pull=data.get("last_pull"),
                last_push=data.get("last_push"),
            )
        except (yaml.YAMLError, OSError):
            return cls()

    def save(self, root: str) -> None:
        """保存配置到 SYNC.yaml。"""
        from ..constants import KNOWLEDGE_SYNC_FILE
        path = Path(root) / KNOWLEDGE_SYNC_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "remote_url": self.remote_url,
            "auto_pull": self.auto_pull,
            "last_pull": self.last_pull,
            "last_push": self.last_push,
        }
        path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


@dataclass
class KnowledgeIndex:
    """知识库索引。"""

    entries: dict[str, KnowledgeEntry] = field(default_factory=dict)

    @classmethod
    def load(cls, root: str) -> "KnowledgeIndex":
        """扫描 knowledge/ 目录加载所有条目。"""
        from ..constants import KNOWLEDGE_DIR
        idx = cls()
        knowledge_dir = Path(root) / KNOWLEDGE_DIR
        if not knowledge_dir.exists():
            return idx

        for md_file in knowledge_dir.rglob("*.md"):
            if md_file.name == "index.md":
                continue
            rel = md_file.relative_to(knowledge_dir)
            if str(rel).startswith("private") and md_file.name != ".gitkeep":
                continue
            entry = KnowledgeEntry.from_markdown(md_file)
            if entry:
                idx.entries[entry.id] = entry

        return idx

    def add(self, entry: KnowledgeEntry) -> bool:
        """添加条目。若 id 已存在返回 False。"""
        if entry.id in self.entries:
            return False
        self.entries[entry.id] = entry
        return True

    def remove(self, entry_id: str) -> bool:
        """删除条目。"""
        if entry_id in self.entries:
            del self.entries[entry_id]
            return True
        return False

    def get(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """按 id 获取条目。"""
        return self.entries.get(entry_id)

    def search(self, query: str) -> list[KnowledgeEntry]:
        """全文搜索（匹配 title, tags, body）。"""
        q = query.lower()
        results: list[KnowledgeEntry] = []
        for entry in self.entries.values():
            score = 0
            if q in entry.title.lower():
                score += 10
            if any(q in t.lower() for t in entry.tags):
                score += 5
            if q in entry.body.lower():
                score += 1
            if score > 0:
                results.append(entry)
        return results

    def list_by_domain(self, domain: str) -> list[KnowledgeEntry]:
        """按领域筛选。"""
        return [e for e in self.entries.values() if e.domain.value == domain]

    def list_by_priority(self, priority: KnowledgePriority) -> list[KnowledgeEntry]:
        """按优先级筛选。"""
        return [e for e in self.entries.values() if e.priority == priority]

    def __len__(self) -> int:
        return len(self.entries)


class SyncManager:
    """通过 git 管理知识库的拉取和推送。

    git 元数据存放在 .harness/knowledge-git/，工作树指向 .harness/knowledge/，
    避免嵌套 .git 目录污染项目仓库。
    """

    def __init__(self, root: str, config: KnowledgeConfig) -> None:
        self.root = root
        self.config = config
        from ..constants import KNOWLEDGE_DIR
        self.knowledge_dir = Path(root) / KNOWLEDGE_DIR
        self._git_dir = Path(root) / ".harness" / "knowledge-git"

    def has_remote(self) -> bool:
        """是否配置了远程仓库。"""
        return bool(self.config.remote_url)

    def _run_git(self, *args: str) -> tuple[int, str, str]:
        """执行 git 命令，指向独立 git-dir 和工作树。"""
        try:
            result = subprocess.run(
                ["git", "--git-dir", str(self._git_dir), "--work-tree", str(self.knowledge_dir), *args],
                capture_output=True,
                timeout=60,
            )
            stdout = (result.stdout or b"").decode("utf-8", errors="replace").strip()
            stderr = (result.stderr or b"").decode("utf-8", errors="replace").strip()
            return result.returncode, stdout, stderr
        except FileNotFoundError:
            return -1, "", "git not found in PATH"
        except subprocess.TimeoutExpired:
            return -1, "", "git command timed out"

    def _ensure_git_repo(self) -> tuple[bool, str]:
        """确保 knowledge-git 是一个 git 仓库。"""
        if not self._git_dir.exists():
            self.knowledge_dir.mkdir(parents=True, exist_ok=True)
            returncode, stdout, stderr = self._run_git("init", "-b", "main")
            if returncode != 0:
                returncode, stdout, stderr = self._run_git("init")
                if returncode != 0:
                    return False, f"git init failed: {stderr}"
            if self.config.remote_url:
                self._run_git("remote", "add", "origin", self.config.remote_url)
        else:
            returncode, stdout, stderr = self._run_git("remote", "get-url", "origin")
            if returncode != 0 and self.config.remote_url:
                self._run_git("remote", "add", "origin", self.config.remote_url)
            elif returncode == 0 and self.config.remote_url and stdout != self.config.remote_url:
                self._run_git("remote", "set-url", "origin", self.config.remote_url)
        return True, "ok"

    def pull(self) -> tuple[bool, str]:
        """从远程拉取知识。"""
        if not self.has_remote():
            return False, "No remote configured"

        ok, msg = self._ensure_git_repo()
        if not ok:
            return False, msg

        # 先 fetch
        returncode, stdout, stderr = self._run_git("fetch", "origin")
        if returncode != 0:
            err = stderr or stdout
            # 提供更清晰的错误信息
            if "Host key verification failed" in err:
                return False, f"SSH key not configured for remote. Use HTTPS URL instead, or set up SSH keys."
            if "could not read" in err.lower() or "could not resolve" in err.lower():
                return False, f"Cannot reach remote. Check your network and the URL."
            return False, f"git fetch failed: {err}"

        # 尝试 checkout remote main
        returncode, stdout, stderr = self._run_git("checkout", "-b", "main", "origin/main")
        if returncode != 0:
            # 或许已有 main 分支，尝试 reset
            returncode, stdout, stderr = self._run_git("checkout", "main")
            if returncode == 0:
                self._run_git("merge", "origin/main", "--allow-unrelated-histories")

        now = datetime.now(timezone.utc).isoformat()
        self.config.last_pull = now
        self.config.save(self.root)
        return True, stdout or "up to date"

    def push(self, message: str = "") -> tuple[bool, str]:
        """推送知识到远程。"""
        if not self.has_remote():
            return False, "No remote configured"

        ok, msg = self._ensure_git_repo()
        if not ok:
            return False, msg

        # 确保在 main 分支
        returncode, stdout, stderr = self._run_git("checkout", "main")
        if returncode != 0:
            self._run_git("checkout", "-b", "main")

        # git add all
        returncode, stdout, stderr = self._run_git("add", "-A")
        if returncode != 0:
            return False, f"git add failed: {stderr}"

        # git commit
        msg_text = message or "knowledge: sync entries"
        returncode, stdout, stderr = self._run_git("commit", "-m", msg_text)
        if returncode != 0 and "nothing to commit" not in (stdout + stderr):
            return False, f"git commit failed: {stderr}"

        # git push
        returncode, stdout, stderr = self._run_git("push", "-u", "origin", "main")
        if returncode != 0:
            return False, stderr or stdout or "push failed"

        now = datetime.now(timezone.utc).isoformat()
        self.config.last_push = now
        self.config.save(self.root)
        return True, stdout or "pushed"

    def diff(self) -> str:
        """返回 git diff 输出。"""
        ok, _ = self._ensure_git_repo()
        if not ok:
            return "Not a git repository"
        returncode, stdout, stderr = self._run_git("diff", "--stat")
        if returncode != 0:
            return stderr or "diff failed"
        return stdout or "no changes"

    def status(self) -> str:
        """返回 git status 短输出。"""
        returncode, stdout, stderr = self._run_git("status", "--short")
        return stdout if returncode == 0 else (stderr or "status failed")
