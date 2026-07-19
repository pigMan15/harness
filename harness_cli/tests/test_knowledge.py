"""Tests for core/knowledge.py"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness_cli.core.knowledge import (
    KnowledgeEntry, KnowledgeIndex, KnowledgeConfig, KnowledgePriority,
    KnowledgeDomain, SyncManager,
)
from harness_cli.constants import KNOWLEDGE_DIR


# ── fixtures ──

@pytest.fixture
def knowledge_project(temp_project: Path) -> Path:
    """在临时项目中创建知识库目录结构。"""
    kdir = temp_project / KNOWLEDGE_DIR
    for domain in ["architecture", "domain", "engineering", "operations", "runway", "private"]:
        d = kdir / domain
        d.mkdir(parents=True)
        (d / ".gitkeep").touch()
    (kdir / "private/.gitignore").write_text("*\n", encoding="utf-8")
    KnowledgeConfig().save(str(temp_project))
    (kdir / "index.md").write_text(
        "# Knowledge Index\n\n| ID | Title | Type | Priority | Domain |\n| --- | --- | --- | --- | --- |\n",
        encoding="utf-8",
    )
    return temp_project


# ── KnowledgeEntry ──

class TestKnowledgeEntry:
    """测试 KnowledgeEntry 数据模型"""

    def test_from_markdown(self) -> None:
        """应能解析 YAML frontmatter + markdown body"""
        text = """---
id: test-pitfall-001
title: Test Entry
type: pitfall
priority: P1
domain: engineering
source_run: test-run
author: bridle
created: 2026-01-01T00:00:00Z
updated: 2026-01-01T00:00:00Z
tags: [test, example]
related: []
confidence: 0.8
---

This is the body content.
"""
        entry = KnowledgeEntry.from_markdown_text(text)
        assert entry is not None
        assert entry.id == "test-pitfall-001"
        assert entry.title == "Test Entry"
        assert entry.type == "pitfall"
        assert entry.priority == KnowledgePriority.P1
        assert entry.domain == KnowledgeDomain.ENGINEERING
        assert entry.source_run == "test-run"
        assert entry.tags == ["test", "example"]
        assert entry.confidence == 0.8
        assert entry.body == "This is the body content."

    def test_to_markdown_roundtrip(self) -> None:
        """序列化再反序列化应保持一致"""
        entry = KnowledgeEntry(
            id="test-001", title="Roundtrip Test", type="case",
            priority=KnowledgePriority.P2, domain=KnowledgeDomain.DOMAIN,
            source_run="run-1", tags=["a", "b"], confidence=0.5,
            body="Roundtrip body.",
        )
        md = entry.to_markdown()
        parsed = KnowledgeEntry.from_markdown_text(md)
        assert parsed is not None
        assert parsed.id == entry.id
        assert parsed.title == entry.title
        assert parsed.type == entry.type
        assert parsed.body == entry.body

    def test_file_relpath(self) -> None:
        """根据 domain 和 id 推导正确的相对路径"""
        entry = KnowledgeEntry(
            id="adr-001-use-redis", title="ADR: Use Redis", type="adr",
            domain=KnowledgeDomain.ARCHITECTURE,
        )
        assert entry.file_relpath() == "architecture/adr-001-use-redis.md"

    def test_file_path(self, temp_project: Path) -> None:
        """推导绝对文件路径"""
        entry = KnowledgeEntry(
            id="test-entry", title="Test", type="case",
            domain=KnowledgeDomain.ENGINEERING,
        )
        expected = temp_project / KNOWLEDGE_DIR / "engineering/test-entry.md"
        assert entry.file_path(str(temp_project)) == expected

    def test_validate_missing_required(self) -> None:
        """缺少必需字段应返回错误列表"""
        entry = KnowledgeEntry(id="", title="", type="invalid")
        issues = entry.validate()
        assert len(issues) >= 3  # id, title, type

    def test_validate_valid(self) -> None:
        """完整有效条目应无错误"""
        entry = KnowledgeEntry(
            id="valid-001", title="Valid Entry", type="case",
            confidence=0.7,
        )
        assert entry.validate() == []

    def test_from_markdown_missing_frontmatter(self) -> None:
        """无 frontmatter 的文本应返回 None"""
        entry = KnowledgeEntry.from_markdown_text("Just some text")
        assert entry is None

    def test_from_markdown_missing_required_fields(self) -> None:
        """缺少 title 的 frontmatter 应返回 None"""
        text = """---
id: missing-title
type: case
---"""
        entry = KnowledgeEntry.from_markdown_text(text)
        assert entry is None


# ── KnowledgeIndex ──

class TestKnowledgeIndex:
    """测试 KnowledgeIndex 集合操作"""

    def test_load_empty(self, temp_project: Path) -> None:
        """空知识库应返回空索引"""
        idx = KnowledgeIndex.load(str(temp_project))
        assert len(idx) == 0

    def test_add_and_get(self, temp_project: Path) -> None:
        """添加后应能获取到"""
        idx = KnowledgeIndex()
        entry = KnowledgeEntry(id="e1", title="Entry 1", type="case")
        assert idx.add(entry) is True
        assert idx.get("e1") is entry

    def test_dedup_by_id(self, temp_project: Path) -> None:
        """重复 ID 添加应返回 False"""
        idx = KnowledgeIndex()
        entry1 = KnowledgeEntry(id="dup", title="First", type="case")
        entry2 = KnowledgeEntry(id="dup", title="Second", type="pitfall")
        assert idx.add(entry1) is True
        assert idx.add(entry2) is False
        assert idx.get("dup").title == "First"

    def test_search(self, temp_project: Path) -> None:
        """搜索应匹配 title, tags, body"""
        idx = KnowledgeIndex()
        idx.add(KnowledgeEntry(id="e1", title="Redis Cache Pattern", type="pattern", tags=["redis", "cache"], body="Use Redis for caching."))
        idx.add(KnowledgeEntry(id="e2", title="MySQL Query", type="case", tags=["sql"], body="Query optimization tips."))
        idx.add(KnowledgeEntry(id="e3", title="Unrelated", type="case", tags=[], body="Nothing to do with redis."))
        results = idx.search("redis")
        assert len(results) >= 1
        assert any("redis" in r.title.lower() or "redis" in r.body.lower() for r in results)

    def test_list_by_domain(self, temp_project: Path) -> None:
        """按领域过滤应正确"""
        idx = KnowledgeIndex()
        idx.add(KnowledgeEntry(id="a1", title="Arch Entry", type="adr", domain=KnowledgeDomain.ARCHITECTURE))
        idx.add(KnowledgeEntry(id="e1", title="Eng Entry", type="case", domain=KnowledgeDomain.ENGINEERING))
        idx.add(KnowledgeEntry(id="e2", title="Eng Entry 2", type="pitfall", domain=KnowledgeDomain.ENGINEERING))
        arch = idx.list_by_domain("architecture")
        eng = idx.list_by_domain("engineering")
        assert len(arch) == 1
        assert len(eng) == 2

    def test_remove(self, temp_project: Path) -> None:
        """删除条目"""
        idx = KnowledgeIndex()
        idx.add(KnowledgeEntry(id="r1", title="To Remove", type="case"))
        assert idx.remove("r1") is True
        assert idx.remove("r1") is False
        assert len(idx) == 0

    def test_load_from_disk(self, knowledge_project: Path) -> None:
        """应从磁盘加载知识条目"""
        # 写入一个知识条目
        entry = KnowledgeEntry(
            id="disk-test-001", title="Disk Test", type="case",
            domain=KnowledgeDomain.ENGINEERING, source_run="test",
        )
        filepath = entry.file_path(str(knowledge_project))
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(entry.to_markdown(), encoding="utf-8")

        idx = KnowledgeIndex.load(str(knowledge_project))
        assert len(idx) == 1
        assert idx.get("disk-test-001") is not None


# ── KnowledgeConfig ──

class TestKnowledgeConfig:
    """测试 SYNC.yaml 配置"""

    def test_load_defaults(self, temp_project: Path) -> None:
        """未配置时应返回默认值"""
        cfg = KnowledgeConfig.load(str(temp_project))
        assert cfg.remote_url == ""
        assert cfg.auto_pull is True
        assert cfg.last_pull is None

    def test_save_and_reload(self, knowledge_project: Path) -> None:
        """保存后重新加载应一致"""
        cfg = KnowledgeConfig(remote_url="git@github.com:team/knowledge.git", auto_pull=False)
        cfg.save(str(knowledge_project))
        loaded = KnowledgeConfig.load(str(knowledge_project))
        assert loaded.remote_url == "git@github.com:team/knowledge.git"
        assert loaded.auto_pull is False


# ── SyncManager ──

class TestSyncManager:
    """测试 Git 同步管理"""

    def test_has_remote_false_when_empty(self, temp_project: Path) -> None:
        """未配置 remote 时 has_remote 应为 False"""
        cfg = KnowledgeConfig()
        mgr = SyncManager(str(temp_project), cfg)
        assert mgr.has_remote() is False

    def test_has_remote_true(self, temp_project: Path) -> None:
        """配置了 remote 时应为 True"""
        cfg = KnowledgeConfig(remote_url="git@github.com:test/repo.git")
        mgr = SyncManager(str(temp_project), cfg)
        assert mgr.has_remote() is True

    def test_diff_empty(self, knowledge_project: Path) -> None:
        """干净的知识库 diff 应为空"""
        cfg = KnowledgeConfig()
        mgr = SyncManager(str(knowledge_project), cfg)
        output = mgr.diff()
        # 可能为空或 "no changes" 或需要先 git init
        assert output in ("", "no changes") or "Not a git repository" in output

    def test_pull_no_remote(self, knowledge_project: Path) -> None:
        """无 remote 时 pull 应返回 False"""
        cfg = KnowledgeConfig()
        mgr = SyncManager(str(knowledge_project), cfg)
        ok, msg = mgr.pull()
        assert ok is False


# ── KnowledgeEntry file persistence ──

class TestKnowledgeFilePersistence:
    """测试知识条目的文件持久化"""

    def test_write_and_read(self, knowledge_project: Path) -> None:
        """写入文件后能从磁盘读回"""
        entry = KnowledgeEntry(
            id="persist-001", title="Persistence Test", type="pitfall",
            priority=KnowledgePriority.P1, domain=KnowledgeDomain.ENGINEERING,
            source_run="test-run-001", tags=["pyinstaller"], confidence=0.9,
            body="Test body content.",
        )
        filepath = entry.file_path(str(knowledge_project))
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(entry.to_markdown(), encoding="utf-8")

        # 从磁盘读取
        loaded = KnowledgeEntry.from_markdown(filepath)
        assert loaded is not None
        assert loaded.id == "persist-001"
        assert loaded.title == "Persistence Test"
        assert loaded.confidence == 0.9
        assert loaded.body == "Test body content."
