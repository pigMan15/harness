"""Tests for core/workflow.py"""

from pathlib import Path

import pytest

from harness_cli.core.workflow import Workflow


class TestWorkflowLoad:
    """测试 workflow.yaml 加载"""

    def test_load(self, valid_harness: Path) -> None:
        """加载合法的 workflow.yaml"""
        wf = Workflow.load(str(valid_harness))
        assert len(wf.nodes) >= 5
        assert "INTAKE" in wf.nodes
        assert "DEVELOPMENT" in wf.nodes

    def test_load_missing(self, temp_project: Path) -> None:
        """加载不存在的文件应抛异常"""
        with pytest.raises(FileNotFoundError):
            Workflow.load(str(temp_project))


class TestWorkflowRoute:
    """测试路由"""

    def test_route_feature_medium(self, valid_harness: Path) -> None:
        """FEATURE/MEDIUM 路由"""
        wf = Workflow.load(str(valid_harness))
        route = wf.route("FEATURE", "MEDIUM")
        assert "INTAKE" in route
        assert "DEVELOPMENT" in route
        assert "COMPILE" in route
        assert len(route) >= 5  # 具体长度取决于模板版本

    def test_route_bug_fix_low(self, valid_harness: Path) -> None:
        """BUG_FIX/LOW 路由"""
        wf = Workflow.load(str(valid_harness))
        route = wf.route("BUG_FIX", "LOW")
        assert len(route) >= 5

    def test_route_unknown(self, valid_harness: Path) -> None:
        """未知意图应返回空列表"""
        wf = Workflow.load(str(valid_harness))
        assert wf.route("UNKNOWN", "LOW") == []


class TestWorkflowNextNode:
    """测试 next_node"""

    def test_first_node(self, valid_harness: Path) -> None:
        """第一个节点"""
        wf = Workflow.load(str(valid_harness))
        required = ["INTAKE", "DEVELOPMENT", "COMPILE"]
        assert wf.next_node(required, set()) == "INTAKE"

    def test_second_node(self, valid_harness: Path) -> None:
        """第二个节点"""
        wf = Workflow.load(str(valid_harness))
        required = ["INTAKE", "DEVELOPMENT", "COMPILE"]
        assert wf.next_node(required, {"INTAKE"}) == "DEVELOPMENT"

    def test_all_done(self, valid_harness: Path) -> None:
        """全部完成返回 None"""
        wf = Workflow.load(str(valid_harness))
        required = ["INTAKE", "DEVELOPMENT"]
        assert wf.next_node(required, {"INTAKE", "DEVELOPMENT"}) is None


class TestWorkflowQuery:
    """测试查询方法"""

    def test_role_for(self, valid_harness: Path) -> None:
        wf = Workflow.load(str(valid_harness))
        assert wf.role_for("INTAKE") == "dispatcher"
        assert wf.role_for("DEVELOPMENT") == "developer"

    def test_artifact_for(self, valid_harness: Path) -> None:
        wf = Workflow.load(str(valid_harness))
        assert wf.artifact_for("INTAKE") == "00-intake.md"
        assert wf.artifact_for("NONEXISTENT") is None

    def test_all_node_ids(self, valid_harness: Path) -> None:
        wf = Workflow.load(str(valid_harness))
        ids = wf.all_node_ids()
        assert "INTAKE" in ids
        assert "DEVELOPMENT" in ids

    def test_all_gate_ids(self, valid_harness: Path) -> None:
        wf = Workflow.load(str(valid_harness))
        gates = wf.all_gate_ids()
        assert "G3_COMPILE" in gates

    def test_max_auto_retries(self, valid_harness: Path) -> None:
        wf = Workflow.load(str(valid_harness))
        assert wf.max_auto_retries() == 2

    def test_gate_to_node(self, valid_harness: Path) -> None:
        wf = Workflow.load(str(valid_harness))
        assert wf.gate_to_node("G3_COMPILE") == "DEVELOPMENT"
