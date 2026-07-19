"""Validator 结构校验器：完整性、引用一致性、路径安全。

整合所有校验逻辑，提供单次 validate() 调用返回结构化报告。
校验项：
1. 必需文件存在性
2. state.json 合法性和 schema 校验
3. workflow.yaml 引用完整性（节点、门禁、角色互相引用一致）
4. phase_dir 路径穿越防护
5. 已完成节点的产物存在性
6. 门禁引用有效性
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from ..constants import (
    REQUIRED_FILES, HARNESS_DIR, STATE_FILE, SCHEMA_FILE,
    WORKFLOW_FILE, GATES_FILE, PHASES_DIR,
)
from .state import HarnessState
from .workflow import Workflow
from .gates import GateEvaluator, GateDefinition


# ---- 数据模型 ----


@dataclass
class ValidationIssue:
    """单条校验问题。"""
    level: str  # "error" | "warning"
    message: str
    file: str | None = None
    detail: str | None = None


@dataclass
class ValidationReport:
    """校验报告：汇总所有 issues。"""
    passed: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    @property
    def issue_count(self) -> int:
        return len(self.errors) + len(self.warnings)

    def format_summary(self) -> str:
        """单行摘要。"""
        parts = []
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")
        if not parts:
            return "No issues found"
        return ", ".join(parts)


# ---- 校验器 ----


class Validator:
    """Harness 项目结构完整性校验器。

    用法:
        v = Validator(root=".", strict=False)
        report = v.validate()
        if not report.passed:
            print(report.format_summary())
    """

    def __init__(self, root: str = ".", strict: bool = False):
        """
        Args:
            root: 项目根目录（包含 .harness/ 的目录）
            strict: True 时警告也标记为 failure
        """
        self.root = Path(root).resolve()
        self.strict = strict

    # ── 主入口 ──

    def validate(self) -> ValidationReport:
        """运行全部校验，返回结构化报告。"""
        errors: list[ValidationIssue] = []
        warnings: list[ValidationIssue] = []

        errors.extend(self._check_required_files())
        errors.extend(self._check_state_json())
        errors.extend(self._check_workflow())
        errors.extend(self._check_phase_dir_safety())
        errors.extend(self._check_gate_definitions())
        errors.extend(self._check_artifacts())

        # strict 模式下警告升级为错误
        if self.strict:
            errors.extend(warnings)
            warnings = []

        passed = len(errors) == 0
        return ValidationReport(passed=passed, errors=errors, warnings=warnings)

    # ── 子校验 ──

    def _check_required_files(self) -> list[ValidationIssue]:
        """检查必需文件是否存在。"""
        issues: list[ValidationIssue] = []
        for rel_path in REQUIRED_FILES:
            full_path = self.root / rel_path
            if not full_path.exists():
                issues.append(ValidationIssue(
                    level="error",
                    message=f"Missing required file: {rel_path}",
                    file=rel_path,
                ))
        return issues

    def _check_state_json(self) -> list[ValidationIssue]:
        """检查 state.json 是否合法 JSON 且符合 schema。"""
        issues: list[ValidationIssue] = []
        state_path = self.root / STATE_FILE

        if not state_path.exists():
            issues.append(ValidationIssue(
                level="error",
                message="state.json not found — cannot perform schema validation",
                file=STATE_FILE,
            ))
            return issues

        # JSON 合法性
        try:
            raw = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            issues.append(ValidationIssue(
                level="error",
                message=f"state.json is not valid JSON: {e.msg}",
                file=STATE_FILE,
            ))
            return issues

        # Schema 合法性
        schema_path = self.root / SCHEMA_FILE
        if schema_path.exists():
            try:
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                jsonschema.validate(raw, schema)
            except jsonschema.ValidationError as e:
                issues.append(ValidationIssue(
                    level="error",
                    message=f"state.json schema validation failed: {e.message}",
                    file=STATE_FILE,
                ))

        # phase_dir 格式
        phase_dir = raw.get("phase_dir", "")
        normalized = str(phase_dir).replace("\\", "/")
        if not normalized.startswith(f".harness/phases/"):
            issues.append(ValidationIssue(
                level="error",
                message=f"phase_dir must be under .harness/phases/: {phase_dir}",
                file=STATE_FILE,
            ))

        return issues

    def _check_workflow(self) -> list[ValidationIssue]:
        """检查 workflow.yaml 引用完整性。"""
        issues: list[ValidationIssue] = []
        wf_path = self.root / WORKFLOW_FILE

        if not wf_path.exists():
            issues.append(ValidationIssue(
                level="error",
                message="workflow.yaml not found",
                file=WORKFLOW_FILE,
            ))
            return issues

        try:
            workflow = Workflow.load(str(self.root))
        except Exception as e:
            issues.append(ValidationIssue(
                level="error",
                message=f"workflow.yaml parse error: {e}",
                file=WORKFLOW_FILE,
            ))
            return issues

        node_ids = workflow.all_node_ids()

        # 角色文件存在性
        for node_id, node in workflow.nodes.items():
            if node.role:
                role_path = self.root / f".harness/agents/{node.role}.md"
                if not role_path.exists():
                    issues.append(ValidationIssue(
                        level="error",
                        message=f"Node '{node_id}' references missing role: {node.role}",
                        file=WORKFLOW_FILE,
                        detail=f"Expected file: .harness/agents/{node.role}.md",
                    ))

        # 路由引用的节点必须存在
        route_refs = workflow.route_nodes_referenced()
        for node_id in route_refs:
            if node_id not in node_ids:
                issues.append(ValidationIssue(
                    level="error",
                    message=f"Route references unknown node: {node_id}",
                    file=WORKFLOW_FILE,
                ))

        # 硬规则引用的节点必须存在
        hr_refs = workflow.hard_rule_nodes_referenced()
        for node_id in hr_refs:
            if node_id not in node_ids:
                issues.append(ValidationIssue(
                    level="error",
                    message=f"Hard rule references unknown node: {node_id}",
                    file=WORKFLOW_FILE,
                ))

        # 失败恢复中引用的节点和门禁
        g2n = workflow.failure_recovery.get("gate_to_node", {})
        for gate_id, node_id in g2n.items():
            if node_id not in node_ids:
                issues.append(ValidationIssue(
                    level="error",
                    message=f"failure_recovery references unknown node: {node_id} (gate: {gate_id})",
                    file=WORKFLOW_FILE,
                ))

        return issues

    def _check_phase_dir_safety(self) -> list[ValidationIssue]:
        """检查 phase_dir 是否在 .harness/phases/ 内（防止路径穿越）。"""
        issues: list[ValidationIssue] = []
        state_path = self.root / STATE_FILE

        if not state_path.exists():
            return issues

        try:
            raw = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return issues

        phase_dir = str(raw.get("phase_dir", ""))
        phase_path = (self.root / phase_dir).resolve()
        phases_root = (self.root / PHASES_DIR).resolve()

        try:
            phase_path.relative_to(phases_root)
        except ValueError:
            issues.append(ValidationIssue(
                level="error",
                message=f"phase_dir is outside .harness/phases/: {phase_dir}",
                file=STATE_FILE,
                detail=f"Resolved to: {phase_path}, expected under: {phases_root}",
            ))

        return issues

    def _check_gate_definitions(self) -> list[ValidationIssue]:
        """检查 gates.yaml 和 state.json 之间门禁 ID 的一致性。"""
        issues: list[ValidationIssue] = []
        gates_path = self.root / GATES_FILE
        state_path = self.root / STATE_FILE

        if not gates_path.exists():
            issues.append(ValidationIssue(
                level="error",
                message="gates.yaml not found",
                file=GATES_FILE,
            ))
            return issues

        if not state_path.exists():
            return issues

        try:
            evaluator = GateEvaluator.load(str(self.root))
            raw_state = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception as e:
            issues.append(ValidationIssue(
                level="error",
                message=f"Gate validation error: {e}",
                file=GATES_FILE,
            ))
            return issues

        defined_gates = evaluator.all_gate_ids()
        state_gates = set(raw_state.get("gates", {}).keys())

        # state.json 中引用的门禁必须已定义
        for gate_id in state_gates:
            if gate_id not in defined_gates:
                issues.append(ValidationIssue(
                    level="error",
                    message=f"state.json references unknown gate: {gate_id}",
                    file=STATE_FILE,
                ))

        return issues

    def _check_artifacts(self) -> list[ValidationIssue]:
        """检查已完成节点的产物文件是否存在。"""
        issues: list[ValidationIssue] = []
        state_path = self.root / STATE_FILE
        wf_path = self.root / WORKFLOW_FILE

        if not state_path.exists() or not wf_path.exists():
            return issues

        try:
            raw = json.loads(state_path.read_text(encoding="utf-8"))
            workflow = Workflow.load(str(self.root))
        except Exception:
            return issues

        phase_dir = str(raw.get("phase_dir", ""))
        phase_path = self.root / phase_dir
        completed = set(raw.get("completed_nodes", []))

        for node_id in completed:
            artifact = workflow.artifact_for(node_id)
            if artifact and not (phase_path / artifact).exists():
                issues.append(ValidationIssue(
                    level="warning",
                    message=f"Completed node '{node_id}' is missing artifact: {artifact}",
                    file=f"{phase_dir}/{artifact}",
                ))

        return issues
