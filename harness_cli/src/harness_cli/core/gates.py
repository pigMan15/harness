"""GateEvaluator 门禁评估器：基于 gates.yaml 规则评估每道门禁。

门禁通过条件：
- 应有产物文件存在于 phase_dir
- 证据文件中记录了 PASS 或 WAIVED
- NOT_REQUIRED 的情况由 workflow 路由决定
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ..constants import GATES_FILE
from .state import HarnessState


# ---- 数据模型 ----


@dataclass
class GateDefinition:
    """单道门禁的定义。"""
    gate_id: str
    description: str
    required_artifacts: list[str] = field(default_factory=list)
    pass_conditions: list[str] = field(default_factory=list)


@dataclass
class GateResult:
    """单道门禁的评估结果。"""
    gate_id: str
    status: str  # PASS | FAIL | WAIVED | NOT_RUN | NOT_REQUIRED | BLOCKED
    description: str = ""
    reason: str = ""


@dataclass
class GateEvaluator:
    """门禁评估器。

    加载 gates.yaml 并基于 HarnessState 评估每道门禁的状态。
    """

    definitions: dict[str, GateDefinition]

    # ── 工厂方法 ──

    @classmethod
    def load(cls, root: str = ".") -> "GateEvaluator":
        """从 .harness/evals/gates.yaml 加载门禁定义。

        Raises:
            FileNotFoundError: gates.yaml 不存在
            yaml.YAMLError: YAML 格式错误
        """
        gates_path = Path(root) / GATES_FILE
        if not gates_path.exists():
            raise FileNotFoundError(f"Gates file not found: {gates_path}")

        raw = yaml.safe_load(gates_path.read_text(encoding="utf-8"))
        if raw is None:
            raise ValueError(f"Gates file is empty: {gates_path}")

        definitions: dict[str, GateDefinition] = {}
        for gate_id, defn in raw.get("gates", {}).items():
            definitions[gate_id] = GateDefinition(
                gate_id=gate_id,
                description=defn.get("description", ""),
                required_artifacts=defn.get("required_artifacts", []),
                pass_conditions=defn.get("pass_conditions", []),
            )

        return cls(definitions=definitions)

    # ── 评估 ──

    def evaluate(self, gate_id: str, state: HarnessState, root: str = ".") -> GateResult:
        """评估单个门禁。

        逻辑：
        1. 如果 state.gates 中标记为 NOT_REQUIRED → NOT_REQUIRED
        2. 如果 state.gates 中标记为 WAIVED → WAIVED
        3. 如果 state.gates 中标记为 PASS → 验证产物存在性，缺失则降级为 FAIL
        4. 否则检查产物文件是否存在 → PASS 或 NOT_RUN
        """
        definition = self.definitions.get(gate_id)
        desc = definition.description if definition else ""

        current_status = state.gates.get(gate_id, "NOT_RUN")

        # 已明确标记的状态
        if current_status == "NOT_REQUIRED":
            return GateResult(gate_id=gate_id, status="NOT_REQUIRED", description=desc, reason="由流程路由标记为不要求")

        if current_status == "WAIVED":
            return GateResult(gate_id=gate_id, status="WAIVED", description=desc, reason="已记录豁免")

        if current_status == "BLOCKED":
            return GateResult(gate_id=gate_id, status="BLOCKED", description=desc, reason="门禁被阻断")

        # 检查产物存在性
        if definition and definition.required_artifacts:
            phase_path = Path(root) / state.phase_dir
            missing = []
            for artifact in definition.required_artifacts:
                if not (phase_path / artifact).exists():
                    missing.append(artifact)

            if missing:
                if current_status == "PASS":
                    return GateResult(
                        gate_id=gate_id, status="FAIL",
                        description=desc,
                        reason=f"产物缺失: {', '.join(missing)}（之前标记为 PASS）"
                    )
                return GateResult(
                    gate_id=gate_id, status="NOT_RUN",
                    description=desc,
                    reason=f"产物缺失: {', '.join(missing)}"
                )

        # 产物齐全
        if current_status == "PASS":
            return GateResult(gate_id=gate_id, status="PASS", description=desc, reason="产物齐全，标记为 PASS")

        return GateResult(gate_id=gate_id, status="NOT_RUN", description=desc, reason="尚未运行")

    def evaluate_all(self, state: HarnessState, root: str = ".") -> list[GateResult]:
        """评估全部已定义的门禁。"""
        return [self.evaluate(gid, state, root) for gid in self.definitions]

    # ── 聚合 ──

    @staticmethod
    def summary(results: list[GateResult]) -> dict[str, int]:
        """统计门禁结果: {pass, fail, waived, not_run, not_required, blocked}。"""
        counts: dict[str, int] = {"pass": 0, "fail": 0, "waived": 0, "not_run": 0, "not_required": 0, "blocked": 0}
        for r in results:
            key = r.status.lower()
            if key in counts:
                counts[key] += 1
        return counts

    @staticmethod
    def is_healthy(results: list[GateResult]) -> bool:
        """所有门禁均为 PASS、WAIVED 或 NOT_REQUIRED 视为健康。"""
        for r in results:
            if r.status not in ("PASS", "WAIVED", "NOT_REQUIRED"):
                return False
        return True

    # ── 查询 ──

    def all_gate_ids(self) -> set[str]:
        """返回所有已定义的门禁 ID。"""
        return set(self.definitions.keys())

    def definition_for(self, gate_id: str) -> GateDefinition | None:
        """返回门禁定义。"""
        return self.definitions.get(gate_id)
