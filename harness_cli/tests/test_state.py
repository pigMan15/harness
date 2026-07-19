"""Tests for core/state.py"""

import json
from pathlib import Path

import pytest

from harness_cli.core.state import (
    HarnessState, Intent, Risk, RunStatus,
    list_runs, switch_run,
)


class TestHarnessStateLoad:
    """测试 state.json 加载"""

    def test_load_valid_state(self, valid_harness: Path) -> None:
        """加载合法 state.json 应该成功"""
        state = HarnessState.load(str(valid_harness))
        assert state.run_id == "test-run-001"
        assert state.intent == Intent.FEATURE
        assert state.risk == Risk.MEDIUM
        assert state.status == RunStatus.ROUTING
        assert state.current_node == "INTAKE"
        assert len(state.gates) == 8

    def test_load_missing_file(self, temp_project: Path) -> None:
        """加载不存在的 state.json 应抛异常"""
        with pytest.raises(FileNotFoundError):
            HarnessState.load(str(temp_project))

    def test_load_invalid_json(self, valid_harness: Path) -> None:
        """加载非法 JSON 应抛异常"""
        (valid_harness / ".harness/state.json").write_text("{invalid}", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            HarnessState.load(str(valid_harness))

    def test_load_invalid_schema(self, valid_harness: Path) -> None:
        """加载不符合 schema 的 JSON 应抛 ValidationError"""
        state_path = valid_harness / ".harness/state.json"
        raw = json.loads(state_path.read_text(encoding="utf-8"))
        del raw["run_id"]  # 缺少必需字段
        state_path.write_text(json.dumps(raw), encoding="utf-8")
        import jsonschema
        with pytest.raises(jsonschema.ValidationError):
            HarnessState.load(str(valid_harness))


class TestHarnessStateCreateNew:
    """测试 create_new 工厂方法"""

    def test_create_new(self) -> None:
        """create_new 应返回正确的初始状态"""
        state = HarnessState.create_new("feat-001", Intent.FEATURE, Risk.MEDIUM)
        assert state.run_id == "feat-001"
        assert state.intent == Intent.FEATURE
        assert state.risk == Risk.MEDIUM
        assert state.status == RunStatus.ROUTING
        assert state.current_node == "INTAKE"
        assert state.next_role == "dispatcher"
        assert state.phase_dir == ".harness/phases/feat-001"
        assert len(state.gates) == 8
        assert all(v == "NOT_RUN" for v in state.gates.values())


class TestHarnessStateSave:
    """测试保存"""

    def test_save(self, valid_harness: Path) -> None:
        """save 应写回 state.json"""
        state = HarnessState.load(str(valid_harness))
        state.notes = "updated"
        state.save(str(valid_harness))

        reloaded = HarnessState.load(str(valid_harness))
        assert reloaded.notes == "updated"

    def test_save_snapshot(self, valid_harness: Path) -> None:
        """save_snapshot 应创建 runs/<run_id>/state.json"""
        state = HarnessState.load(str(valid_harness))
        path = state.save_snapshot(str(valid_harness))
        assert path.exists()
        assert "runs/test-run-001" in str(path).replace("\\", "/")


class TestHarnessStateQuery:
    """测试查询方法"""

    def test_progress(self, valid_harness: Path) -> None:
        """progress() 应返回正确的完成/总数"""
        state = HarnessState.load(str(valid_harness))
        assert state.progress() == (0, 5)  # 0 completed, 5 required
        assert state.progress_pct() == 0.0

        state.completed_nodes = ["INTAKE", "DEVELOPMENT"]
        assert state.progress() == (2, 5)
        assert state.progress_pct() == 0.4

    def test_progress_zero(self) -> None:
        """空 required_nodes 应返回 0%"""
        state = HarnessState.create_new("t", Intent.QUERY, Risk.NA)
        assert state.progress_pct() == 0.0

    def test_next_required_node(self, valid_harness: Path) -> None:
        """next_required_node() 应返回第一个未完成节点"""
        state = HarnessState.load(str(valid_harness))
        assert state.next_required_node() == "INTAKE"

        state.completed_nodes = ["INTAKE"]
        assert state.next_required_node() == "DEVELOPMENT"

    def test_is_gate_pass(self, valid_harness: Path) -> None:
        """is_gate_pass() 应正确判断"""
        state = HarnessState.load(str(valid_harness))
        assert not state.is_gate_pass("G1_REQUIREMENTS")

        state.gates["G1_REQUIREMENTS"] = "PASS"
        assert state.is_gate_pass("G1_REQUIREMENTS")

    def test_all_gates_pass(self, valid_harness: Path) -> None:
        """all_gates_pass 应考虑 PASS/WAIVED/NOT_REQUIRED"""
        state = HarnessState.load(str(valid_harness))
        assert not state.all_gates_pass()

        for k in state.gates:
            state.gates[k] = "PASS"
        assert state.all_gates_pass()


class TestListRuns:
    """测试 list_runs"""

    def test_list_runs_empty(self, temp_project: Path) -> None:
        """没有 runs 时应返回空列表"""
        (temp_project / ".harness/runs").mkdir(parents=True, exist_ok=True)
        assert list_runs(str(temp_project)) == []

    def test_list_runs(self, valid_harness: Path) -> None:
        """应能列出保存的 runs"""
        state = HarnessState.load(str(valid_harness))
        state.save_snapshot(str(valid_harness))
        runs = list_runs(str(valid_harness))
        assert len(runs) >= 1
        assert any(r["run_id"] == "test-run-001" for r in runs)


class TestSwitchRun:
    """测试 switch_run"""

    def test_switch_run(self, valid_harness: Path) -> None:
        """switch_run 应恢复快照并写回 state.json"""
        state = HarnessState.load(str(valid_harness))
        state.save_snapshot(str(valid_harness))

        # 修改当前状态
        state.notes = "before switch"
        state.save(str(valid_harness))

        # 切换
        restored = switch_run("test-run-001", str(valid_harness))
        assert restored.run_id == "test-run-001"

        # 确认写回
        reloaded = HarnessState.load(str(valid_harness))
        assert reloaded.run_id == "test-run-001"

    def test_switch_nonexistent(self, temp_project: Path) -> None:
        """切换不存在的 run 应抛异常"""
        with pytest.raises(FileNotFoundError):
            switch_run("nonexistent", str(temp_project))
