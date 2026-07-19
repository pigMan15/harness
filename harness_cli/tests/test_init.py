"""Tests for harness init command — core logic only."""

from pathlib import Path

from harness_cli.constants import HARNESS_ENTRY_MARKER_START, HARNESS_ENTRY_MARKER_END, HARNESS_ENTRY_BLOCK
from harness_cli.commands.init_cmd import _has_harness_entry, _append_harness_entry, _replace_harness_entry


class TestHarnessEntryDetection:
    """测试 AGENTS.md/CLAUDE.md 标记块检测"""

    def test_no_entry(self, temp_project: Path) -> None:
        """不含标记块的文件返回 False"""
        f = temp_project / "test.md"
        f.write_text("# Hello\n", encoding="utf-8")
        assert not _has_harness_entry(f)

    def test_has_entry(self, temp_project: Path) -> None:
        """含标记块的文件返回 True"""
        f = temp_project / "test.md"
        f.write_text(f"# Hello\n\n{HARNESS_ENTRY_BLOCK}\n", encoding="utf-8")
        assert _has_harness_entry(f)

    def test_missing_file(self, temp_project: Path) -> None:
        """不存在的文件返回 False"""
        assert not _has_harness_entry(temp_project / "nonexistent.md")


class TestAppendEntry:
    """测试追加标记块"""

    def test_append_to_new_file(self, temp_project: Path) -> None:
        """追加到空文件"""
        f = temp_project / "test.md"
        result = _append_harness_entry(f)
        assert result
        content = f.read_text(encoding="utf-8")
        assert HARNESS_ENTRY_MARKER_START in content
        assert "AI Coding Harness" in content

    def test_append_to_existing_file(self, temp_project: Path) -> None:
        """追加到已有内容的文件"""
        f = temp_project / "test.md"
        f.write_text("# My Project\n\nSome content\n", encoding="utf-8")
        _append_harness_entry(f)
        content = f.read_text(encoding="utf-8")
        assert content.startswith("# My Project")
        assert HARNESS_ENTRY_MARKER_START in content

    def test_idempotent(self, temp_project: Path) -> None:
        """重复追加应幂等"""
        f = temp_project / "test.md"
        f.write_text("# My Project\n", encoding="utf-8")
        assert _append_harness_entry(f)  # 第一次：写入
        assert not _append_harness_entry(f)  # 第二次：跳过
        content = f.read_text(encoding="utf-8")
        assert content.count(HARNESS_ENTRY_MARKER_START) == 1


class TestReplaceEntry:
    """测试替换标记块"""

    def test_replace_old_entry(self, temp_project: Path) -> None:
        """替换旧版本标记块"""
        f = temp_project / "test.md"
        old_block = "<!-- HARNESS-ENTRY:START -->\nold content\n<!-- HARNESS-ENTRY:END -->\n"
        f.write_text(f"# My Project\n{old_block}More content\n", encoding="utf-8")
        _replace_harness_entry(f)
        content = f.read_text(encoding="utf-8")
        assert "# My Project" in content
        assert "More content" in content
        assert "old content" not in content
        assert "AI Coding Harness" in content

    def test_replace_no_old_entry(self, temp_project: Path) -> None:
        """无旧块时追加新块"""
        f = temp_project / "test.md"
        f.write_text("# My Project\n", encoding="utf-8")
        _replace_harness_entry(f)
        content = f.read_text(encoding="utf-8")
        assert "AI Coding Harness" in content
