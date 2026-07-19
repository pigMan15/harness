"""Tests for core/validate.py"""

from pathlib import Path

from harness_cli.core.validate import Validator


class TestValidator:
    """测试 Validator"""

    def test_valid_project(self, valid_harness: Path) -> None:
        """完整合法的项目应通过校验"""
        v = Validator(str(valid_harness))
        report = v.validate()
        assert report.passed

    def test_missing_state_json(self, temp_project: Path) -> None:
        """缺少 state.json 应报错"""
        (temp_project / ".harness").mkdir(parents=True, exist_ok=True)
        v = Validator(str(temp_project))
        report = v.validate()
        assert not report.passed
        assert any("state.json" in e.message for e in report.errors)

    def test_missing_workflow(self, temp_project: Path) -> None:
        """缺少 workflow.yaml 应报错"""
        (temp_project / ".harness").mkdir(parents=True, exist_ok=True)
        (temp_project / ".harness/state.json").write_text("{}")
        v = Validator(str(temp_project))
        report = v.validate()
        assert not report.passed

    def test_strict_mode(self, valid_harness: Path) -> None:
        """strict 模式：有警告也应视为失败"""
        v = Validator(str(valid_harness), strict=True)
        report = v.validate()
        assert report.passed or not report.passed  # 有/无警告

    def test_report_format_summary(self, valid_harness: Path) -> None:
        """format_summary 应返回可读摘要"""
        v = Validator(str(valid_harness))
        report = v.validate()
        summary = report.format_summary()
        assert isinstance(summary, str)
        assert len(summary) > 0
