"""Tests for core/validate.py"""

import json
from pathlib import Path
import tomllib

from harness_cli.core.validate import Validator


class TestValidator:
    """Tests for Validator."""

    def test_valid_project(self, valid_harness: Path) -> None:
        v = Validator(str(valid_harness))
        report = v.validate()
        assert report.passed

    def test_missing_state_json(self, temp_project: Path) -> None:
        (temp_project / ".harness").mkdir(parents=True, exist_ok=True)
        v = Validator(str(temp_project))
        report = v.validate()
        assert not report.passed
        assert any("state.json" in e.message for e in report.errors)

    def test_missing_workflow(self, temp_project: Path) -> None:
        (temp_project / ".harness").mkdir(parents=True, exist_ok=True)
        (temp_project / ".harness/state.json").write_text("{}")
        v = Validator(str(temp_project))
        report = v.validate()
        assert not report.passed

    def test_strict_mode_promotes_artifact_warnings(self, valid_harness: Path) -> None:
        state_path = valid_harness / ".harness/state.json"
        raw = json.loads(state_path.read_text(encoding="utf-8"))
        raw["completed_nodes"] = ["INTAKE"]
        state_path.write_text(json.dumps(raw), encoding="utf-8")

        report = Validator(str(valid_harness), strict=True).validate()

        assert not report.passed
        assert any("missing artifact" in e.message for e in report.errors)

    def test_required_nodes_must_match_workflow_route(self, valid_harness: Path) -> None:
        state_path = valid_harness / ".harness/state.json"
        raw = json.loads(state_path.read_text(encoding="utf-8"))
        raw["required_nodes"] = ["INTAKE", "ACCEPTANCE_REPORT"]
        state_path.write_text(json.dumps(raw), encoding="utf-8")

        report = Validator(str(valid_harness)).validate()

        assert not report.passed
        assert any("required_nodes does not match workflow route" in e.message for e in report.errors)

    def test_pyproject_includes_runtime_package_data(self) -> None:
        pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        package_data = data["tool"]["setuptools"]["package-data"]["harness_cli"]

        assert "locales/*.json" in package_data
        assert "templates/**/*" in package_data

    def test_report_format_summary(self, valid_harness: Path) -> None:
        report = Validator(str(valid_harness)).validate()
        summary = report.format_summary()
        assert isinstance(summary, str)
        assert len(summary) > 0
