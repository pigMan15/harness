"""Tests for core/gates.py"""

from pathlib import Path

import pytest

from harness_cli.core.state import HarnessState
from harness_cli.core.gates import GateEvaluator, GateResult


class TestGateEvaluatorLoad:
    """测试 gates.yaml 加载"""

    def test_load(self, valid_harness: Path) -> None:
        ev = GateEvaluator.load(str(valid_harness))
        assert len(ev.definitions) >= 3

    def test_load_missing(self, temp_project: Path) -> None:
        with pytest.raises(FileNotFoundError):
            GateEvaluator.load(str(temp_project))


class TestGateEvaluatorEvaluate:
    """测试门禁评估"""

    def test_not_run(self, valid_harness: Path) -> None:
        """产物缺失时应为 NOT_RUN"""
        ev = GateEvaluator.load(str(valid_harness))
        state = HarnessState.load(str(valid_harness))
        result = ev.evaluate("G3_COMPILE", state, str(valid_harness))
        assert result.status == "NOT_RUN"

    def test_not_required(self, valid_harness: Path) -> None:
        """标记为 NOT_REQUIRED 的门禁"""
        ev = GateEvaluator.load(str(valid_harness))
        state = HarnessState.load(str(valid_harness))
        state.gates["G3_COMPILE"] = "NOT_REQUIRED"
        result = ev.evaluate("G3_COMPILE", state, str(valid_harness))
        assert result.status == "NOT_REQUIRED"

    def test_waived(self, valid_harness: Path) -> None:
        """标记为 WAIVED 的门禁"""
        ev = GateEvaluator.load(str(valid_harness))
        state = HarnessState.load(str(valid_harness))
        state.gates["G3_COMPILE"] = "WAIVED"
        result = ev.evaluate("G3_COMPILE", state, str(valid_harness))
        assert result.status == "WAIVED"

    def test_blocked(self, valid_harness: Path) -> None:
        """标记为 BLOCKED 的门禁"""
        ev = GateEvaluator.load(str(valid_harness))
        state = HarnessState.load(str(valid_harness))
        state.gates["G3_COMPILE"] = "BLOCKED"
        result = ev.evaluate("G3_COMPILE", state, str(valid_harness))
        assert result.status == "BLOCKED"

    def test_pass_downgrade_on_missing_artifact(self, valid_harness: Path) -> None:
        """标记为 PASS 但产物缺失时应降级为 FAIL"""
        ev = GateEvaluator.load(str(valid_harness))
        state = HarnessState.load(str(valid_harness))
        state.gates["G3_COMPILE"] = "PASS"
        result = ev.evaluate("G3_COMPILE", state, str(valid_harness))
        assert result.status == "FAIL"

    def test_pass_with_artifact(self, valid_harness: Path) -> None:
        """标记为 PASS 且产物存在时应为 PASS"""
        ev = GateEvaluator.load(str(valid_harness))
        state = HarnessState.load(str(valid_harness))
        state.gates["G3_COMPILE"] = "PASS"
        # 创建产物文件
        (valid_harness / state.phase_dir / "12-compile.md").parent.mkdir(parents=True, exist_ok=True)
        (valid_harness / state.phase_dir / "12-compile.md").write_text("compiled ok")
        result = ev.evaluate("G3_COMPILE", state, str(valid_harness))
        assert result.status == "PASS"


class TestGateEvaluatorBulk:
    """测试批量评估"""

    def test_evaluate_all(self, valid_harness: Path) -> None:
        ev = GateEvaluator.load(str(valid_harness))
        state = HarnessState.load(str(valid_harness))
        results = ev.evaluate_all(state, str(valid_harness))
        assert len(results) == len(ev.definitions)

    def test_summary(self, valid_harness: Path) -> None:
        ev = GateEvaluator.load(str(valid_harness))
        state = HarnessState.load(str(valid_harness))
        results = ev.evaluate_all(state, str(valid_harness))
        s = ev.summary(results)
        assert "not_run" in s
        assert s["not_run"] >= 3  # G3, G6, G8 all NOT_RUN

    def test_is_healthy(self, valid_harness: Path) -> None:
        ev = GateEvaluator.load(str(valid_harness))
        state = HarnessState.load(str(valid_harness))
        results = ev.evaluate_all(state, str(valid_harness))
        assert not ev.is_healthy(results)  # has NOT_RUN

        # 全部 PASS/WAIVED/NOT_REQUIRED
        for k in state.gates:
            state.gates[k] = "PASS"
        # 创建需要的产物
        for gid, defn in ev.definitions.items():
            for art in defn.required_artifacts:
                p = valid_harness / state.phase_dir / art
                p.parent.mkdir(parents=True, exist_ok=True)
                p.touch()
        results = ev.evaluate_all(state, str(valid_harness))
        assert ev.is_healthy(results)
